"""
LICET — Protocolo de Baseline Individual
Gerencia calibração, armazenamento e validação do estado basal de cada usuário.

Requisitos para baseline válido:
  - ≥ 5 sessões de calibração
  - ≥ 3 minutos cada sessão
  - Todas em estado de repouso calmo (sem exercício, sem estresse agudo)
  - Renovação automática se > 30 dias sem nova sessão

Detecção pré-medicação durante calibração:
  Se os sinais durante calibração já indicam toxidrome, o baseline é rejeitado
  com aviso ao usuário — garante que o "normal" do usuário não seja calibrado
  sobre um estado farmacologicamente alterado.

Integração com DB (ledger/db.py):
  - Tabela: user_baselines
  - Tabela: biometric_history (últimas 30 sessões por usuário)
"""

import json
import math
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, List, Dict, Any, Tuple


@dataclass
class BaselineSession:
    """Uma sessão de calibração individual."""
    user_id: str
    timestamp: float
    duration_seconds: int
    hrv_rmssd: float
    spo2: float
    eda_scl: Optional[float]
    eda_scr: Optional[float]
    skin_temp: Optional[float]
    tremor_8_12hz: Optional[float]
    hardware_source: str
    is_valid: bool = True       # False se pré-medicação detectada nesta sessão
    invalidation_reason: str = ""
    on_chronic_beta_blocker: bool = False  # Usuário declarou uso crônico de beta-bloqueador
    hf_power_ms2: Optional[float] = None  # Potência HF (0.15–0.40 Hz) calculada dos RR intervals
    peak_freq_hz: Optional[float] = None  # Frequência dominante do espectro HRV (Hz)
    periodicity_index: Optional[float] = None  # IP da sessão — para threshold individual (CA-08)


@dataclass
class UserBaseline:
    """Baseline consolidado de um usuário (calculado sobre ≥5 sessões válidas)."""
    user_id: str
    created_at: float
    expires_at: float            # created_at + 30 dias
    session_count: int
    maturity_score: float        # 0.0 – 1.0 (1.0 = 5+ sessões, distribuídas em ≥3 dias)

    # Vetor médio μ e labels
    signal_labels: List[str]     # ex: ["RMSSD", "SPO2", "EDA_SCL", "EDA_SCR"]
    mu: List[float]              # vetor médio

    # Matriz de covariância inversa Σ⁻¹ (serializada como lista de listas)
    sigma_inv: List[List[float]]

    # Parâmetros individuais para z-scores do check farmacológico
    hr_mean: float
    hr_std: float
    hrv_mean: float
    hrv_std: float
    tremor_mean: Optional[float]
    tremor_std: Optional[float]

    # Template ECG médio (Camada 1) — None se sem hardware ECG
    ecg_template: Optional[List[float]]

    # Flag de beta-bloqueador crônico — reduz poder discriminativo do detector Mahalanobis
    # (RMSSD basal elevado + HR basal reduzida deslocam o fingerprint de calma antes
    # de qualquer desafio — confound documentado em Lampert et al., Am J Cardiol 2003)
    chronic_beta_blocker_flag: bool = False

    # GAP-B08: assessment de poisoning registrado no momento do enrollment
    poisoning_risk: str = "LOW"          # "LOW" | "MEDIUM" | "HIGH"
    poisoning_flags: List[str] = field(default_factory=list)
    enrollment_days_covered: int = 0

    # Threshold IP individual — calculado a partir das sessões de baseline.
    # Usuários com respiração naturalmente mais rítmica têm IP basal mais alto;
    # o threshold global de 0.80 gera falsos positivos para esses usuários.
    # threshold_ip = max(0.70, min(0.95, ip_mean + 2 * ip_std))
    # None se <3 sessões com IP disponível — usa threshold global (0.80).
    ip_mean: Optional[float] = None
    ip_std: Optional[float] = None
    ip_threshold: Optional[float] = None  # Valor calculado; recomputado em load_baseline

    def is_expired(self) -> bool:
        return time.time() > self.expires_at

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


# ── GAP-B08: Detecção de Baseline Poisoning ──────────────────────────────────

@dataclass
class BaselinePoisoningAssessment:
    """
    Resultado da análise de integridade do enrollment.

    GAP-B08: Um adversário que controla as condições durante o enrollment
    pode calibrar o baseline para aceitar estados coagidos como "normais".
    Este assessment detecta padrões suspeitos nas sessões de calibração.
    """
    poisoning_risk: str              # "LOW" | "MEDIUM" | "HIGH"
    flags: List[str]                 # Lista de flags levantadas
    sessions_evaluated: int
    days_covered: int
    rmssd_cv: Optional[float]        # Coeficiente de variação do RMSSD (suspicioso se < 5%)
    outlier_sessions: List[int]      # Índices de sessões outlier (>2σ do grupo)
    trend_detected: bool             # True se há tendência monotônica (stress acumulado)
    spread_adequate: bool            # True se sessões em ≥3 dias distintos
    population_plausible: bool       # True se RMSSD médio em range humano plausível
    notes: str


def detect_baseline_poisoning(sessions: List["BaselineSession"]) -> BaselinePoisoningAssessment:
    """
    Analisa as sessões de calibração em busca de padrões de poisoning.

    Checks implementados:
    1. Spread temporal: sessões devem cobrir ≥3 dias distintos
    2. Plausibilidade populacional: RMSSD médio deve estar em 15–100 ms (repouso adulto)
    3. Consistência entre sessões: CV do RMSSD muito baixo sugere controle artificial
    4. Outlier detection: sessões com RMSSD >2σ do grupo são suspeitas
    5. Trend monotônico: RMSSD decrescente ao longo das sessões = estresse progressivo

    Limitação documentada: adversário sofisticado pode calibrar exatamente dentro
    dos thresholds. Enrollment supervisionado em ambiente clínico seria mais seguro
    mas contradiz o objetivo de acessibilidade consumer.
    """
    valid = [s for s in sessions if s.is_valid and s.duration_seconds >= MIN_DURATION_SECONDS]
    if len(valid) < 2:
        return BaselinePoisoningAssessment(
            poisoning_risk="LOW",
            flags=[],
            sessions_evaluated=len(valid),
            days_covered=0,
            rmssd_cv=None,
            outlier_sessions=[],
            trend_detected=False,
            spread_adequate=False,
            population_plausible=False,
            notes="Sessões insuficientes para avaliação.",
        )

    hrv_vals = [s.hrv_rmssd for s in valid]
    n        = len(hrv_vals)
    mu_hrv   = sum(hrv_vals) / n
    var_hrv  = sum((v - mu_hrv) ** 2 for v in hrv_vals) / max(n - 1, 1)
    std_hrv  = math.sqrt(var_hrv)

    flags: List[str] = []

    # ── Check 1: spread temporal ──────────────────────────────────────────────
    days = len({int(s.timestamp // 86400) for s in valid})
    spread_ok = days >= 3
    if not spread_ok:
        flags.append(
            f"TEMPORAL_CLUSTERING: todas as {n} sessões em apenas {days} dia(s). "
            "Enrollment em sessão única é suspeito — adversário pode controlar ambiente."
        )

    # ── Check 2: plausibilidade populacional ──────────────────────────────────
    # RMSSD de repouso em adultos saudáveis: ~15–100 ms (Shaffer & Ginsberg, 2017)
    pop_ok = 15.0 <= mu_hrv <= 100.0
    if not pop_ok:
        flags.append(
            f"POPULATION_IMPLAUSIBLE: RMSSD médio={mu_hrv:.1f} ms fora do range "
            "esperado para adulto em repouso (15–100 ms). "
            "Valores extremos podem indicar estado farmacológico durante enrollment."
        )

    # ── Check 3: variabilidade inter-sessão suspeita ──────────────────────────
    # CV = σ/μ — muito baixo (<5%) sugere sinais artificialmente controlados
    cv = (std_hrv / mu_hrv * 100) if mu_hrv > 0 else None
    if cv is not None and cv < 5.0:
        flags.append(
            f"LOW_INTER_SESSION_VARIANCE: CV do RMSSD = {cv:.1f}% (< 5%). "
            "Variabilidade suspeita baixa entre sessões — possível controle artificial "
            "do estado fisiológico (ex: paced breathing consistente em todas as sessões)."
        )

    # ── Check 4: outliers por sessão ─────────────────────────────────────────
    outlier_idxs = []
    if std_hrv > 0:
        for i, v in enumerate(hrv_vals):
            if abs(v - mu_hrv) > 2.0 * std_hrv:
                outlier_idxs.append(i)
    if outlier_idxs:
        flags.append(
            f"OUTLIER_SESSIONS: {len(outlier_idxs)} sessão(ões) com RMSSD >2σ do grupo "
            f"(índices: {outlier_idxs}). Verificar se sessão foi realizada em estado atípico."
        )

    # ── Check 5: tendência monotônica (estresse progressivo) ─────────────────
    # Pearson rank monotonic: se RMSSD decresce consistentemente, usuário estava
    # acumulando estresse ao longo do enrollment
    trend = False
    if n >= 4:
        # Correlação de Spearman simplificada (ranks)
        sorted_by_time = sorted(valid, key=lambda s: s.timestamp)
        time_ranks   = list(range(n))
        rmssd_sorted = [s.hrv_rmssd for s in sorted_by_time]
        mu_r = (n - 1) / 2
        cov  = sum((time_ranks[i] - mu_r) * (rmssd_sorted[i] - mu_hrv) for i in range(n))
        var_t = sum((r - mu_r) ** 2 for r in time_ranks)
        if var_t > 0 and std_hrv > 0:
            corr = cov / (math.sqrt(var_t) * std_hrv * n)
            if corr < -0.7:   # correlação negativa forte: RMSSD caindo com o tempo
                trend = True
                flags.append(
                    f"MONOTONIC_STRESS_TREND: correlação tempo-RMSSD = {corr:.2f}. "
                    "RMSSD decrescente ao longo das sessões sugere estresse acumulado "
                    "durante o período de enrollment. Baseline pode não refletir estado genuíno."
                )

    # ── Risco global ──────────────────────────────────────────────────────────
    n_flags = len(flags)
    if n_flags >= 3 or (not pop_ok and n_flags >= 1):
        risk = "HIGH"
    elif n_flags >= 1:
        risk = "MEDIUM"
    else:
        risk = "LOW"

    notes = (
        "Limitação: adversário sofisticado pode manter-se dentro dos thresholds. "
        "Enrollment supervisionado em ambiente clínico oferece garantia superior."
    ) if risk != "LOW" else "Nenhum padrão de poisoning detectado."

    return BaselinePoisoningAssessment(
        poisoning_risk=risk,
        flags=flags,
        sessions_evaluated=n,
        days_covered=days,
        rmssd_cv=round(cv, 2) if cv is not None else None,
        outlier_sessions=outlier_idxs,
        trend_detected=trend,
        spread_adequate=spread_ok,
        population_plausible=pop_ok,
        notes=notes,
    )


# ── Álgebra linear mínima ─────────────────────────────────────────────────────

def _mean(values: List[float]) -> float:
    return sum(values) / len(values)


def _variance(values: List[float], mu: Optional[float] = None) -> float:
    if mu is None:
        mu = _mean(values)
    return sum((x - mu) ** 2 for x in values) / max(len(values) - 1, 1)


def _std(values: List[float]) -> float:
    return math.sqrt(_variance(values))


def _cov_matrix(data: List[List[float]]) -> List[List[float]]:
    """
    Calcula matriz de covariância p×p a partir de n observações (cada linha = uma obs.).
    data: lista de n vetores de p dimensões.
    """
    n = len(data)
    p = len(data[0])
    if n < 2:
        return [[1.0 if i == j else 0.0 for j in range(p)] for i in range(p)]

    means = [_mean([row[j] for row in data]) for j in range(p)]
    cov = [[0.0] * p for _ in range(p)]
    for row in data:
        diff = [row[j] - means[j] for j in range(p)]
        for i in range(p):
            for j in range(p):
                cov[i][j] += diff[i] * diff[j]
    denom = max(n - 1, 1)
    return [[cov[i][j] / denom for j in range(p)] for i in range(p)]


def _invert_2x2(m: List[List[float]]) -> Optional[List[List[float]]]:
    """Inversão analítica de matriz 2×2."""
    det = m[0][0] * m[1][1] - m[0][1] * m[1][0]
    if abs(det) < 1e-12:
        return None
    inv_det = 1.0 / det
    return [
        [ m[1][1] * inv_det, -m[0][1] * inv_det],
        [-m[1][0] * inv_det,  m[0][0] * inv_det],
    ]


def _invert_diagonal(m: List[List[float]]) -> List[List[float]]:
    """Assume diagonal dominante — inverte cada elemento da diagonal."""
    n = len(m)
    inv = [[0.0] * n for _ in range(n)]
    for i in range(n):
        inv[i][i] = 1.0 / m[i][i] if abs(m[i][i]) > 1e-12 else 0.0
    return inv


def _safe_invert(m: List[List[float]]) -> List[List[float]]:
    """
    Tenta inversão analítica 2×2 ou usa regularização diagonal como fallback.
    Para n>2 sem numpy: usa a diagonal da covariância (approximação conservadora).
    """
    n = len(m)
    if n == 2:
        result = _invert_2x2(m)
        if result:
            return result
    # Fallback: inversão diagonal (assume covariâncias cruzadas pequenas)
    # Isso é conservador — superestima D² — melhor falso positivo que falso negativo
    return _invert_diagonal(m)


# ── Construção do baseline ────────────────────────────────────────────────────

MIN_SESSIONS = 5
MIN_DURATION_SECONDS = 180    # 3 minutos por sessão
BASELINE_TTL_DAYS = 30


def _maturity_score(sessions: List[BaselineSession]) -> float:
    """
    Score de maturidade 0.0–1.0:
      - 0.4 base por ter ≥5 sessões
      - +0.3 por ter sessões distribuídas em ≥3 dias distintos
      - +0.3 por ter ≥10 sessões
    """
    score = 0.0
    if len(sessions) >= MIN_SESSIONS:
        score += 0.4
    days = len({int(s.timestamp // 86400) for s in sessions})
    if days >= 3:
        score += 0.3
    if len(sessions) >= 10:
        score += 0.3
    return round(min(score, 1.0), 2)


def build_baseline(
    user_id: str,
    sessions: List[BaselineSession],
    heart_rates: Optional[List[float]] = None,   # FC de cada sessão (para z-score farmacológico)
) -> Optional[UserBaseline]:
    """
    Calcula o baseline individual a partir das sessões de calibração.

    Args:
        user_id:      Identificador do usuário.
        sessions:     Lista de sessões válidas (is_valid=True).
        heart_rates:  FC média de cada sessão correspondente (mesmo índice que sessions).

    Returns:
        UserBaseline se ≥5 sessões válidas, None caso contrário.
    """
    valid = [s for s in sessions if s.is_valid and s.duration_seconds >= MIN_DURATION_SECONDS]

    if len(valid) < MIN_SESSIONS:
        return None

    # ── Sinais sempre presentes ───────────────────────────────────────────────
    hrv_vals  = [s.hrv_rmssd for s in valid]
    spo2_vals = [s.spo2      for s in valid]

    labels: List[str]         = ["RMSSD", "SPO2"]
    observations: List[List[float]] = [[s.hrv_rmssd, s.spo2] for s in valid]

    # ── Sinais opcionais — incluir se ≥80% das sessões os tiveram ────────────
    def _include(attr: str) -> bool:
        return sum(1 for s in valid if getattr(s, attr) is not None) >= 0.8 * len(valid)

    def _fill(attr: str, default: float = 0.0) -> List[float]:
        return [getattr(s, attr) or default for s in valid]

    if _include("eda_scl"):
        labels.append("EDA_SCL")
        scl_vals = _fill("eda_scl")
        for i, row in enumerate(observations):
            row.append(scl_vals[i])

    if _include("eda_scr"):
        labels.append("EDA_SCR")
        scr_vals = _fill("eda_scr")
        for i, row in enumerate(observations):
            row.append(scr_vals[i])

    if _include("skin_temp"):
        labels.append("SKIN_TEMP")
        temp_vals = _fill("skin_temp", 33.5)
        for i, row in enumerate(observations):
            row.append(temp_vals[i])

    if _include("tremor_8_12hz"):
        labels.append("TREMOR_8_12HZ")
        tremor_vals = _fill("tremor_8_12hz", 0.005)
        for i, row in enumerate(observations):
            row.append(tremor_vals[i])

    if _include("hf_power_ms2"):
        labels.append("HF_POWER_MS2")
        hf_vals = _fill("hf_power_ms2", 0.0)
        for i, row in enumerate(observations):
            row.append(hf_vals[i])

    if _include("peak_freq_hz"):
        labels.append("PEAK_FREQ_HZ")
        pf_vals = _fill("peak_freq_hz", 0.1)
        for i, row in enumerate(observations):
            row.append(pf_vals[i])

    # ── Calcular μ e Σ⁻¹ ─────────────────────────────────────────────────────
    p   = len(labels)
    mu  = [_mean([obs[j] for obs in observations]) for j in range(p)]
    cov = _cov_matrix(observations)

    # Floor mínimo de variância diagonal por sinal — evita sigma_inv zerado
    # quando poucas sessões produzem variância degenerada (ex: SpO₂=98 em todas).
    # Valores calibrados na resolução do sensor: SpO₂ PPG ±0.5%, RMSSD ±2ms.
    _MIN_VAR: dict = {
        "RMSSD":          4.0,    # std mínimo = 2 ms (resolução PPG derivada)
        "SPO2":           0.25,   # std mínimo = 0.5 % (resolução PPG ±0.5%)
        "EDA_SCL":        0.01,   # std mínimo = 0.1 µS
        "EDA_SCR":        0.001,
        "SKIN_TEMP":      0.04,   # std mínimo = 0.2 °C
        "TREMOR_8_12HZ":  1e-6,
        "HF_POWER_MS2":   1.0,
        "PEAK_FREQ_HZ":   0.0001,
    }
    for i, lbl in enumerate(labels):
        floor = _MIN_VAR.get(lbl, 1e-4)
        if cov[i][i] < floor:
            cov[i][i] = floor

    sigma_inv = _safe_invert(cov)

    # ── Parâmetros para check farmacológico ──────────────────────────────────
    hr_list = heart_rates if heart_rates and len(heart_rates) == len(valid) else [60.0] * len(valid)
    hr_mean = _mean(hr_list)
    hr_std  = _std(hr_list) or 5.0   # fallback mínimo

    hrv_mean = _mean(hrv_vals)
    hrv_std  = _std(hrv_vals) or 10.0

    tremor_mean: Optional[float] = None
    tremor_std:  Optional[float] = None
    if _include("tremor_8_12hz"):
        t_vals      = _fill("tremor_8_12hz", 0.005)
        tremor_mean = _mean(t_vals)
        tremor_std  = _std(t_vals) or 0.001

    # Flag de beta-bloqueador crônico: verdadeiro se ≥50% das sessões válidas o indicam
    bb_sessions = sum(1 for s in valid if s.on_chronic_beta_blocker)
    chronic_bb = (bb_sessions / len(valid)) >= 0.5

    # GAP-B08: detectar padrões de baseline poisoning no conjunto de sessões
    poisoning = detect_baseline_poisoning(valid)

    # ── Threshold IP individual ──────────────────────────────────────────────
    # Requer ≥3 sessões com IP medido para estatística estável.
    # threshold = clamp(ip_mean + 2*ip_std, 0.70, 0.95)
    # Floor 0.70: proteção mínima mantida mesmo para usuários rítmicos.
    # Cap  0.95: impede inflação por enrollment com respiração paced.
    # Floor = global threshold (0.80): threshold individual só ativa quando mean+2σ > 0.80.
    # Isso garante que usuários com IP basal baixo não ficam mais protegidos que o necessário,
    # e que usuários com IP basal naturalmente ALTO (ex: 0.76 ± 0.04 → 0.84) se beneficiam
    # do threshold personalizado, que reduz falsos positivos para eles.
    _IP_FLOOR = 0.80
    _IP_CAP   = 0.95
    _ip_vals = [s.periodicity_index for s in valid if s.periodicity_index is not None]
    ip_mean: Optional[float] = None
    ip_std:  Optional[float] = None
    ip_threshold: Optional[float] = None
    if len(_ip_vals) >= 3:
        ip_mean = _mean(_ip_vals)
        ip_std  = _std(_ip_vals) if len(_ip_vals) > 1 else 0.05
        ip_threshold = round(max(_IP_FLOOR, min(_IP_CAP, ip_mean + 2 * ip_std)), 4)

    now = time.time()
    return UserBaseline(
        user_id=user_id,
        created_at=now,
        expires_at=now + BASELINE_TTL_DAYS * 86400,
        session_count=len(valid),
        maturity_score=_maturity_score(valid),
        signal_labels=labels,
        mu=mu,
        sigma_inv=sigma_inv,
        hr_mean=hr_mean,
        hr_std=hr_std,
        hrv_mean=hrv_mean,
        hrv_std=hrv_std,
        tremor_mean=tremor_mean,
        tremor_std=tremor_std,
        ecg_template=None,   # Preenchido por hardware ECG separadamente
        chronic_beta_blocker_flag=chronic_bb,
        poisoning_risk=poisoning.poisoning_risk,
        poisoning_flags=poisoning.flags,
        enrollment_days_covered=poisoning.days_covered,
        ip_mean=round(ip_mean, 4) if ip_mean is not None else None,
        ip_std=round(ip_std, 4) if ip_std is not None else None,
        ip_threshold=ip_threshold,
    )


# ── Persistência via DB ───────────────────────────────────────────────────────

def save_baseline(baseline: UserBaseline, db_engine) -> None:
    """Persiste o baseline na tabela user_baselines (ver ledger/db.py)."""
    from sqlalchemy import text
    data = baseline.to_dict()
    # Serializar listas como JSON para SQLite/PostgreSQL
    data["signal_labels"]  = json.dumps(data["signal_labels"])
    data["mu"]             = json.dumps(data["mu"])
    data["sigma_inv"]      = json.dumps(data["sigma_inv"])
    data["ecg_template"]   = json.dumps(data["ecg_template"]) if data["ecg_template"] else None

    with db_engine.begin() as conn:
        # Upsert: remove baseline anterior do usuário e insere novo
        conn.execute(text("DELETE FROM user_baselines WHERE user_id = :uid"), {"uid": baseline.user_id})
        conn.execute(
            text("""
                INSERT INTO user_baselines (
                    user_id, created_at, expires_at, session_count, maturity_score,
                    signal_labels, mu, sigma_inv,
                    hr_mean, hr_std, hrv_mean, hrv_std,
                    tremor_mean, tremor_std, ecg_template,
                    chronic_beta_blocker_flag,
                    ip_mean, ip_std, ip_threshold
                ) VALUES (
                    :user_id, :created_at, :expires_at, :session_count, :maturity_score,
                    :signal_labels, :mu, :sigma_inv,
                    :hr_mean, :hr_std, :hrv_mean, :hrv_std,
                    :tremor_mean, :tremor_std, :ecg_template,
                    :chronic_beta_blocker_flag,
                    :ip_mean, :ip_std, :ip_threshold
                )
            """),
            data,
        )


def load_baseline(user_id: str, db_engine) -> Optional[UserBaseline]:
    """Carrega o baseline do usuário do banco. Retorna None se não existe ou expirado."""
    from sqlalchemy import text
    with db_engine.connect() as conn:
        row = conn.execute(
            text("SELECT * FROM user_baselines WHERE user_id = :uid ORDER BY created_at DESC LIMIT 1"),
            {"uid": user_id},
        ).fetchone()

    if not row:
        return None

    row = row._asdict()
    baseline = UserBaseline(
        user_id=row["user_id"],
        created_at=row["created_at"],
        expires_at=row["expires_at"],
        session_count=row["session_count"],
        maturity_score=row["maturity_score"],
        signal_labels=json.loads(row["signal_labels"]),
        mu=json.loads(row["mu"]),
        sigma_inv=json.loads(row["sigma_inv"]),
        hr_mean=row["hr_mean"],
        hr_std=row["hr_std"],
        hrv_mean=row["hrv_mean"],
        hrv_std=row["hrv_std"],
        tremor_mean=row["tremor_mean"],
        tremor_std=row["tremor_std"],
        ecg_template=json.loads(row["ecg_template"]) if row.get("ecg_template") else None,
        chronic_beta_blocker_flag=bool(row.get("chronic_beta_blocker_flag") or False),
        ip_mean=row.get("ip_mean"),
        ip_std=row.get("ip_std"),
        ip_threshold=row.get("ip_threshold"),
    )

    if baseline.is_expired():
        return None   # Expirado — novo baseline necessário

    return baseline


def save_session(session: BaselineSession, db_engine) -> None:
    """Persiste uma sessão de calibração na tabela biometric_history."""
    from sqlalchemy import text
    with db_engine.begin() as conn:
        conn.execute(
            text("""
                INSERT INTO biometric_history (
                    user_id, timestamp, duration_seconds,
                    hrv_rmssd, spo2, eda_scl, eda_scr,
                    skin_temp, tremor_8_12hz, hardware_source,
                    is_valid, invalidation_reason, on_chronic_beta_blocker,
                    hf_power_ms2, peak_freq_hz, periodicity_index
                ) VALUES (
                    :user_id, :timestamp, :duration_seconds,
                    :hrv_rmssd, :spo2, :eda_scl, :eda_scr,
                    :skin_temp, :tremor_8_12hz, :hardware_source,
                    :is_valid, :invalidation_reason, :on_chronic_beta_blocker,
                    :hf_power_ms2, :peak_freq_hz, :periodicity_index
                )
            """),
            asdict(session),
        )
        # Purge automático: manter apenas os últimos 30 dias por usuário
        conn.execute(
            text("""
                DELETE FROM biometric_history
                WHERE user_id = :uid
                AND timestamp < :cutoff
            """),
            {"uid": session.user_id, "cutoff": time.time() - 30 * 86400},
        )


def load_sessions(user_id: str, db_engine, limit: int = 50) -> List[BaselineSession]:
    """Carrega sessões de calibração do banco para recalcular baseline."""
    from sqlalchemy import text
    with db_engine.connect() as conn:
        rows = conn.execute(
            text("""
                SELECT * FROM biometric_history
                WHERE user_id = :uid
                ORDER BY timestamp DESC
                LIMIT :lim
            """),
            {"uid": user_id, "lim": limit},
        ).fetchall()

    return [
        BaselineSession(
            user_id=row.user_id,
            timestamp=row.timestamp,
            duration_seconds=row.duration_seconds,
            hrv_rmssd=row.hrv_rmssd,
            spo2=row.spo2,
            eda_scl=row.eda_scl,
            eda_scr=row.eda_scr,
            skin_temp=row.skin_temp,
            tremor_8_12hz=row.tremor_8_12hz,
            hardware_source=row.hardware_source,
            is_valid=bool(row.is_valid),
            invalidation_reason=row.invalidation_reason or "",
            on_chronic_beta_blocker=bool(getattr(row, "on_chronic_beta_blocker", False) or False),
            hf_power_ms2=getattr(row, "hf_power_ms2", None),
            peak_freq_hz=getattr(row, "peak_freq_hz", None),
            periodicity_index=getattr(row, "periodicity_index", None),
        )
        for row in rows
    ]
