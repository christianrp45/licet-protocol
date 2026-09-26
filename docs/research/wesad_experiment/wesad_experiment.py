"""
LICET — WESAD Validation Experiment
=====================================
Valida o protocolo LICET Layer 3 (Mahalanobis) contra o dataset WESAD
(Wearable Stress and Affect Detection).

Referência do dataset:
  Schmidt, P., Reiss, A., Duerichen, R., Marberger, C., & Van Laerhoven, K. (2018).
  Introducing WESAD, a Multimodal Dataset for Wearable Stress and Affect Detection.
  ICMI 2018. DOI: 10.1145/3242969.3242985

SETUP:
  1. Baixar o dataset em: https://uni-siegen.sciebo.de/s/HGdUkoNlW1Gy4em
     (requer cadastro gratuito — link alternativo: dataset solicitado via email)
  2. Extrair: os arquivos .pkl ficam em WESAD/S{id}/S{id}.pkl
  3. Ajustar WESAD_PATH abaixo
  4. `pip install cvxEDA` (opcional — decomposição tônica/fásica do EDA; sem ela o
     script cai para SCL via low-pass filter e pula SCR)
  5. Executar: python wesad_experiment.py

OUTPUTS:
  - results/wesad_results.json    — métricas por sujeito
  - results/wesad_summary.txt     — relatório para o paper (sensitivity, specificity, AUC)
  - results/wesad_per_subject.csv — tabela completa

SINAIS USADOS (mapeamento LICET ↔ WESAD, pulso Empatica E4 salvo não indicado):
  LICET RMSSD          ← WESAD wrist BVP (64 Hz) → picos → intervalos RR → RMSSD
  LICET EDA_SCL/EDA_SCR ← WESAD wrist EDA (4 Hz)  → cvxEDA (Greco et al. 2015):
                          componente tônica (SCL) e driver fásico (SCR)
  LICET SKIN_TEMP       ← WESAD wrist TEMP (4 Hz) → delta vs. média do baseline do sujeito
  LICET TREMOR_8_12HZ   ← WESAD wrist ACC (32 Hz) → potência espectral 8-12Hz da
                          aceleração resultante (após remover componente DC/gravidade)
  LICET IP (GAP-B01)    ← intervalos RR (mesma fonte do RMSSD) → core/respiratory_periodicity.py
                          (import direto do módulo de produção — mesma implementação)
  Ground-truth resp.    ← WESAD chest Resp (RespiBAN, 700 Hz) → frequência dominante
                          0.05-0.6 Hz — cross-check independente do IP (não usado no D²)

  Vetor Mahalanobis avaliado (5 sinais — vetor completo documentado em
  core/mahalanobis.py): [RMSSD, EDA_SCL, EDA_SCR, DELTA_TEMP, TREMOR_8_12HZ]
  usando core.mahalanobis.evaluate_mahalanobis_layer() diretamente — mesma
  função e mesmos limiares χ² da produção, não uma reimplementação.

  NOTA — achado durante a implementação: core/baseline.py rotula o sinal de
  temperatura como "SKIN_TEMP" (valor absoluto), mas core/mahalanobis.py só
  reconhece o rótulo "DELTA_TEMP" ao montar x_labels. Isso significa que em
  produção esse sinal nunca é alinhado ao baseline (é descartado silenciosamente
  no _d_squared). Este experimento usa "DELTA_TEMP" (delta vs. média do baseline
  do próprio sujeito) para ficar consistente com o que a função realmente espera —
  mas o mismatch em produção deveria ser corrigido separadamente.

Condições WESAD:
  Label 1 = Baseline (repouso, 20 min antes do TSST)
  Label 2 = Stress   (TSST — Trier Social Stress Test: discurso + aritmética pública)
  Label 3 = Amusement (videoclipes engraçados — estado positivo, NÃO coerção)
  Label 4 = Meditation (relaxamento guiado — baixo stress)

Hipóteses a validar:
  H1: D² stress > threshold → sensitivity alto (LICET detecta estresse como anomalia)
  H2: D² amusement < threshold → specificity alto (alegria não é coerção)
  H3: D² meditation < threshold → relaxamento correto como "dentro do baseline"
  H4: RMSSD stress < RMSSD baseline → HRV cai sob stress (literatura: p<0.001)
  H5 (novo — GAP-B01): IP não deve disparar falso-positivo em nenhuma condição
      genuína (baseline/amusement/meditation) — se disparar, é evidência de que
      o detector de periodicidade tem taxa de falso positivo real, não só teórica.
      Meditação guiada é o teste mais duro: respiração deliberadamente lenta e
      regular é o caso mais próximo de paced breathing sem ser um ataque.
"""

import os
import sys
import json
import csv
import math
import pickle
import warnings
import numpy as np
from pathlib import Path
from scipy import signal as sp_signal
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict, field

# Console Windows costuma abrir em cp1252 — força UTF-8 para os caracteres
# usados nos relatórios (χ², µ, ±, °, ≤, ×). Sem isso, print() quebra com
# UnicodeEncodeError no meio da execução.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

# ── Import direto dos módulos de produção (zero deps externas em ambos) ───────
_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))
from core.mahalanobis import evaluate_mahalanobis_layer, CHI2  # noqa: E402
from core.respiratory_periodicity import compute_respiratory_periodicity  # noqa: E402

try:
    import cvxEDA
    _HAS_CVXEDA = True
except ImportError:
    _HAS_CVXEDA = False
    warnings.warn(
        "cvxEDA não instalado (`pip install cvxEDA`) — EDA_SCR será omitido, "
        "EDA_SCL cai para low-pass filter simples. Vetor Mahalanobis reduz de "
        "5 para 4 sinais (χ²(4)=9.49 em vez de χ²(5)=11.07)."
    )

# ── Configuração ──────────────────────────────────────────────────────────────

WESAD_PATH = Path("WESAD")          # Ajuste para o caminho real do dataset
RESULTS_PATH = Path("results")
WINDOW_SEC = 60                     # Janela de 60s — padrão da literatura WESAD
OVERLAP = 0.5                       # 50% de sobreposição entre janelas
MIN_BASELINE_WINDOWS = 5            # Mínimo de janelas para construir baseline

# Condições de interesse
LABEL_BASELINE   = 1
LABEL_STRESS     = 2
LABEL_AMUSEMENT  = 3
LABEL_MEDITATION = 4

# Sujeitos disponíveis no WESAD (S2-S17, S12 removido por dados corrompidos)
ALL_SUBJECTS = [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 14, 15, 16, 17]

# ── Floors de variância mínima — idênticos a core/baseline.py::_MIN_VAR ───────
# (Plews et al. 2012, Bent et al. 2020 — ver layer3_canonical_params.md)
FLOOR_VAR = {
    "RMSSD":         100.0,   # ms²
    "EDA_SCL":       0.25,    # µS²
    "EDA_SCR":       0.01,    # µS²
    "DELTA_TEMP":    0.04,    # °C²
    "TREMOR_8_12HZ": 1e-6,    # g⁴
}
SIGNAL_ORDER = ["RMSSD", "EDA_SCL", "EDA_SCR", "DELTA_TEMP", "TREMOR_8_12HZ"]


@dataclass
class SubjectResult:
    subject_id: int
    n_baseline_windows: int
    n_stress_windows: int
    n_amusement_windows: int
    n_meditation_windows: int

    # Valores médios por condição
    mean_rmssd_baseline: float
    mean_rmssd_stress: float
    mean_eda_scl_baseline: float
    mean_eda_scl_stress: float
    mean_eda_scr_baseline: Optional[float]
    mean_eda_scr_stress: Optional[float]
    mean_tremor_baseline: float
    mean_tremor_stress: float

    # Métricas Layer 3
    stress_detected: int        # janelas stress com D² > threshold
    stress_total: int
    amusement_flagged: int      # janelas amusement erroneamente flagadas
    amusement_total: int
    meditation_flagged: int
    meditation_total: int

    sensitivity: float          # TPR: stress corretamente detectado
    specificity_amusement: float  # TNR: amusement não flagado
    specificity_meditation: float

    mean_d2_baseline: float
    mean_d2_stress: float
    threshold_used: float
    signals_used: List[str]
    n_signals: int

    # GAP-B01 — Índice de Periodicidade (respiratory_periodicity.py real)
    mean_ip_baseline: Optional[float]
    mean_ip_stress: Optional[float]
    mean_ip_amusement: Optional[float]
    mean_ip_meditation: Optional[float]
    ip_false_positive_rate_meditation: Optional[float]  # % janelas meditation com IP suspeito
    mean_ground_truth_resp_hz_baseline: Optional[float]
    mean_ground_truth_resp_hz_meditation: Optional[float]

    # Gate de artefato de movimento (rejeição de janelas contaminadas por
    # gesticulação/fala, calibrado no baseline do próprio sujeito)
    motion_threshold_g: float
    pct_windows_rejected_motion: float


# ── Funções de processamento de sinal ─────────────────────────────────────────

def _detect_rr_intervals(bvp: np.ndarray, fs: float = 64.0) -> Optional[np.ndarray]:
    """
    Detecta intervalos RR (ms) a partir do sinal BVP via band-pass + pico.
    Base compartilhada por RMSSD e pela análise de periodicidade (IP).
    """
    if len(bvp) < int(fs * 10):
        return None

    b, a = sp_signal.butter(4, [0.5 / (fs / 2), 4.0 / (fs / 2)], btype='band')
    bvp_filtered = sp_signal.filtfilt(b, a, bvp)

    min_distance = int(fs * 0.3)
    peaks, _ = sp_signal.find_peaks(
        bvp_filtered,
        distance=min_distance,
        height=np.percentile(bvp_filtered, 60)
    )
    if len(peaks) < 10:
        return None

    rr = np.diff(peaks) / fs * 1000.0
    rr = rr[(rr > 300) & (rr < 2000)]
    if len(rr) < 5:
        return None
    return rr


def compute_rmssd_from_bvp(bvp: np.ndarray, fs: float = 64.0) -> Optional[float]:
    """RMSSD = sqrt(mean((ΔRR_i)²)). Validação: ≥10 RR (Berntson et al. 1997)."""
    rr = _detect_rr_intervals(bvp, fs)
    if rr is None:
        return None
    rr_diffs = np.diff(rr)
    return float(np.sqrt(np.mean(rr_diffs ** 2)))


def compute_eda_tonic_phasic(
    eda: np.ndarray, fs: float = 4.0
) -> Tuple[Optional[float], Optional[float]]:
    """
    Decompõe EDA em componente tônica (SCL) e driver fásico (SCR) via cvxEDA
    (Greco et al. 2015, IEEE TBME — otimização convexa, método padrão-ouro).

    O solver espera entrada normalizada (z-score) por estabilidade numérica.
    Reescala de volta para µS para ficar compatível com os floors canônicos
    de core/baseline.py (EDA_SCL: 0.25µS², EDA_SCR: 0.01µS²):
      - tônica (t): reescala por std + soma a média (nível absoluto)
      - fásica (r): reescala só por std (já é centrada em zero por design;
        usamos o desvio-padrão da janela como amplitude do driver fásico)

    Se cvxEDA não estiver instalado ou o solver não convergir, retorna
    (scl_via_lowpass, None) — degrada graciosamente para 4 sinais no vetor.
    """
    y = np.asarray(eda, dtype=float)
    if len(y) < int(fs * 5):
        return float(np.mean(y)) if len(y) else None, None

    if not _HAS_CVXEDA:
        return _lowpass_scl_fallback(y, fs), None

    mean, std = float(y.mean()), float(y.std())
    if std < 1e-9:
        return mean, 0.0

    yn = (y - mean) / std
    try:
        r, p, t, l, d, e, obj = cvxEDA.cvxEDA(yn, 1.0 / fs)
    except Exception:
        return _lowpass_scl_fallback(y, fs), None

    scl_us = float(np.mean(t)) * std + mean
    scr_us = float(np.std(r)) * std
    return scl_us, scr_us


def _lowpass_scl_fallback(eda: np.ndarray, fs: float) -> float:
    """SCL via low-pass Butterworth ≤0.05Hz — usado quando cvxEDA indisponível."""
    cutoff = 0.05 / (fs / 2)
    if cutoff >= 1.0:
        return float(np.mean(eda))
    b, a = sp_signal.butter(4, cutoff, btype='low')
    scl = sp_signal.filtfilt(b, a, eda)
    return float(np.mean(scl))


def compute_tremor_8_12hz(acc_window: np.ndarray, fs: float = 32.0) -> Optional[float]:
    """
    Potência espectral 8-12Hz da aceleração resultante — proxy de tremor.

    Args:
        acc_window: array (3, N) com eixos x/y/z do acelerômetro do pulso (g)
        fs:         frequência de amostragem (32Hz no E4)

    Returns:
        Potência em 8-12Hz (g²), ou None se janela curta demais.
    """
    if acc_window.shape[1] < int(fs * 2):
        return None

    net = np.sqrt(np.sum(acc_window ** 2, axis=0))
    net = net - np.mean(net)  # remove DC/gravidade

    f, pxx = sp_signal.periodogram(net, fs=fs)
    band = (f >= 8.0) & (f <= 12.0)
    if not np.any(band):
        return None
    return float(np.sum(pxx[band]))


def compute_motion_energy(acc_window: np.ndarray, fs: float = 32.0) -> Optional[float]:
    """
    Índice de movimento bruto (RMS da aceleração resultante, DC removido) —
    usado para descartar janelas contaminadas por gesticulação/fala, distinto
    do TREMOR_8_12HZ (banda estreita). Voluntary movement (falar, gesticular
    durante o TSST) tem energia de banda larga muito maior que tremor
    fisiológico, mesmo quando parte dela vaza para 8-12Hz.

    Args:
        acc_window: array (3, N) com eixos x/y/z do acelerômetro do pulso (g)
        fs:         frequência de amostragem (32Hz no E4)

    Returns:
        RMS da aceleração resultante sem DC (g), ou None se janela curta demais.
    """
    if acc_window.shape[1] < int(fs * 2):
        return None
    net = np.sqrt(np.sum(acc_window ** 2, axis=0))
    net = net - np.mean(net)
    return float(np.sqrt(np.mean(net ** 2)))


def compute_ground_truth_resp_hz(resp_window: np.ndarray, fs: float = 700.0) -> Optional[float]:
    """
    Frequência respiratória dominante a partir do canal Resp do RespiBAN (peito).
    Usada só como cross-check independente do IP — não entra no vetor Mahalanobis.
    Banda 0.05-0.6 Hz cobre 3-36 respirações/min.
    """
    if len(resp_window) < int(fs * 10):
        return None

    b, a = sp_signal.butter(2, [0.05 / (fs / 2), 0.6 / (fs / 2)], btype='band')
    filtered = sp_signal.filtfilt(b, a, resp_window)

    f, pxx = sp_signal.periodogram(filtered, fs=fs)
    band = (f >= 0.05) & (f <= 0.6)
    if not np.any(band):
        return None
    band_f, band_p = f[band], pxx[band]
    return float(band_f[np.argmax(band_p)])


def window_signal(
    data: np.ndarray,
    labels: np.ndarray,
    target_label: int,
    fs: float,
    window_sec: int = WINDOW_SEC,
    overlap: float = OVERLAP,
) -> List[np.ndarray]:
    """
    Extrai janelas do sinal para uma condição específica.

    Args:
        data:         Sinal (1D ou 2D, última dimensão = tempo)
        labels:       Labels reamostrados para a mesma fs do sinal
        target_label: Condição desejada (1=baseline, 2=stress, etc.)
        fs:           Frequência de amostragem
        window_sec:   Tamanho da janela em segundos
        overlap:      Sobreposição entre janelas (0.0–1.0)

    Returns:
        Lista de janelas (arrays)
    """
    window_samples = int(fs * window_sec)
    step_samples = int(window_samples * (1 - overlap))

    mask = (labels == target_label)
    indices = np.where(mask)[0]

    if len(indices) == 0:
        return []

    windows = []
    i = 0
    while i + window_samples <= len(labels):
        window_indices = np.arange(i, i + window_samples)
        if np.sum(mask[window_indices]) >= 0.8 * window_samples:
            if data.ndim == 1:
                windows.append(data[window_indices])
            else:
                windows.append(data[:, window_indices])
        i += step_samples

    return windows


def resample_labels(labels_orig: np.ndarray, orig_fs: float, target_fs: float) -> np.ndarray:
    """Reamostras labels de orig_fs para target_fs."""
    if orig_fs == target_fs:
        return labels_orig
    factor = target_fs / orig_fs
    new_len = int(len(labels_orig) * factor)
    indices = (np.arange(new_len) / factor).astype(int)
    indices = np.clip(indices, 0, len(labels_orig) - 1)
    return labels_orig[indices]


# ── Construção do baseline individual (5 sinais) ──────────────────────────────

def build_individual_baseline(
    rmssd_values: List[float],
    eda_scl_values: List[float],
    eda_scr_values: List[Optional[float]],
    delta_temp_values: List[float],
    tremor_values: List[Optional[float]],
) -> Tuple[List[float], List[List[float]], List[str]]:
    """
    Constrói baseline individual (µ, Σ⁻¹) para um sujeito, com o vetor completo
    de 5 sinais quando disponível (EDA_SCR e TREMOR degradam graciosamente se
    ausentes em alguma janela — mesmo princípio de core/baseline.py::_include).

    Floors de variância aplicados = FLOOR_VAR (idênticos a core/baseline.py).
    """
    signals = {
        "RMSSD": rmssd_values,
        "EDA_SCL": eda_scl_values,
        "EDA_SCR": eda_scr_values,
        "DELTA_TEMP": delta_temp_values,
        "TREMOR_8_12HZ": tremor_values,
    }

    # Sinal entra no vetor se presente em ≥80% das janelas de baseline (mesmo
    # critério de core/baseline.py::_include)
    n = len(rmssd_values)
    labels: List[str] = []
    columns: List[List[float]] = []
    for lbl in SIGNAL_ORDER:
        vals = signals[lbl]
        present = [v for v in vals if v is not None]
        if len(present) >= 0.8 * n:
            labels.append(lbl)
            mean_fill = float(np.mean(present))
            columns.append([v if v is not None else mean_fill for v in vals])

    values = np.array(columns).T  # shape (N, p)
    mu = values.mean(axis=0).tolist()

    cov = np.cov(values.T)
    cov = np.atleast_2d(cov)
    for i, lbl in enumerate(labels):
        floor = FLOOR_VAR.get(lbl, 0.01)
        if cov[i, i] < floor:
            cov[i, i] = floor

    try:
        sigma_inv = np.linalg.inv(cov).tolist()
    except np.linalg.LinAlgError:
        sigma_inv = np.diag([1.0 / cov[i, i] for i in range(len(labels))]).tolist()

    return mu, sigma_inv, labels


# ── Processamento de um sujeito ───────────────────────────────────────────────

def process_subject(subject_id: int, wesad_path: Path) -> Optional[SubjectResult]:
    """
    Processa um sujeito do WESAD end-to-end.

    Estrutura do .pkl:
        data['signal']['wrist']['BVP']   → 64 Hz
        data['signal']['wrist']['EDA']   → 4 Hz
        data['signal']['wrist']['TEMP']  → 4 Hz
        data['signal']['wrist']['ACC']   → 32 Hz, shape (N, 3)
        data['signal']['chest']['Resp']  → 700 Hz (RespiBAN — ground truth)
        data['label']                    → 700 Hz
    """
    pkl_path = wesad_path / f"S{subject_id}" / f"S{subject_id}.pkl"
    if not pkl_path.exists():
        print(f"  [SKIP] S{subject_id}: arquivo não encontrado ({pkl_path})")
        return None

    print(f"  Processando S{subject_id}...", end=" ", flush=True)

    with open(pkl_path, 'rb') as f:
        data = pickle.load(f, encoding='latin1')

    bvp   = data['signal']['wrist']['BVP'].flatten()          # 64 Hz
    eda   = data['signal']['wrist']['EDA'].flatten()          # 4 Hz
    temp  = data['signal']['wrist']['TEMP'].flatten()         # 4 Hz
    acc   = data['signal']['wrist']['ACC'].T                  # (3, N) — 32 Hz
    resp_chest = data['signal']['chest']['Resp'].flatten()    # 700 Hz
    labels_700hz = data['label'].flatten()                    # 700 Hz

    labels_bvp  = resample_labels(labels_700hz, 700.0, 64.0)
    labels_eda  = resample_labels(labels_700hz, 700.0, 4.0)
    labels_acc  = resample_labels(labels_700hz, 700.0, 32.0)
    # labels_700hz já serve para TEMP (mesma fs=4Hz que EDA) e Resp (700Hz nativo)

    def extract_windows_for_condition(label: int) -> Dict[str, list]:
        bvp_w  = window_signal(bvp, labels_bvp, label, fs=64.0)
        eda_w  = window_signal(eda, labels_eda, label, fs=4.0)
        temp_w = window_signal(temp, labels_eda, label, fs=4.0)
        acc_w  = window_signal(acc, labels_acc, label, fs=32.0)
        resp_w = window_signal(resp_chest, labels_700hz, label, fs=700.0)

        n = min(len(bvp_w), len(eda_w), len(temp_w), len(acc_w), len(resp_w))
        out = {
            "rmssd": [], "eda_scl": [], "eda_scr": [], "temp": [],
            "tremor": [], "ip": [], "ground_truth_resp_hz": [], "motion_energy": [],
        }
        for i in range(n):
            rr = _detect_rr_intervals(bvp_w[i], fs=64.0)
            rmssd = None
            if rr is not None:
                rmssd = float(np.sqrt(np.mean(np.diff(rr) ** 2)))
            scl, scr = compute_eda_tonic_phasic(eda_w[i], fs=4.0)
            tremor = compute_tremor_8_12hz(acc_w[i], fs=32.0)
            motion = compute_motion_energy(acc_w[i], fs=32.0)
            gt_resp = compute_ground_truth_resp_hz(resp_w[i], fs=700.0)

            ip_result = None
            if rr is not None:
                ip_result = compute_respiratory_periodicity(rr.tolist())

            out["rmssd"].append(rmssd)
            out["eda_scl"].append(scl)
            out["eda_scr"].append(scr)
            out["temp"].append(float(np.mean(temp_w[i])))
            out["tremor"].append(tremor)
            out["ip"].append(ip_result)
            out["ground_truth_resp_hz"].append(gt_resp)
            out["motion_energy"].append(motion)
        return out

    baseline_w   = extract_windows_for_condition(LABEL_BASELINE)
    stress_w     = extract_windows_for_condition(LABEL_STRESS)
    amusement_w  = extract_windows_for_condition(LABEL_AMUSEMENT)
    meditation_w = extract_windows_for_condition(LABEL_MEDITATION)

    # ── Gate de artefato de movimento ──────────────────────────────────────
    # Limiar derivado da distribuição de movimento do PRÓPRIO baseline (estado
    # quieto de referência) do sujeito — aplicado igualmente a todas as
    # condições para não introduzir viés (mesmo critério absoluto para
    # baseline/stress/amusement/meditation).
    baseline_motion = [m for m in baseline_w["motion_energy"] if m is not None]
    if len(baseline_motion) >= MIN_BASELINE_WINDOWS:
        med = float(np.median(baseline_motion))
        mad = float(np.median(np.abs(np.array(baseline_motion) - med)))
        motion_threshold = med + 3 * 1.4826 * mad if mad > 0 else med * 3.0
    else:
        motion_threshold = float("inf")  # sinal insuficiente para calibrar — não filtra

    def apply_motion_gate(win: Dict[str, list]) -> Tuple[Dict[str, list], int, int]:
        n = len(win["motion_energy"])
        keep = [
            i for i in range(n)
            if win["motion_energy"][i] is not None and win["motion_energy"][i] <= motion_threshold
        ]
        filtered = {k: [win[k][i] for i in keep] for k in win}
        return filtered, len(keep), n

    baseline_w,   n_base_kept,  n_base_total  = apply_motion_gate(baseline_w)
    stress_w,     n_stress_kept, n_stress_tot = apply_motion_gate(stress_w)
    amusement_w,  n_amus_kept,  n_amus_tot    = apply_motion_gate(amusement_w)
    meditation_w, n_medit_kept, n_medit_tot   = apply_motion_gate(meditation_w)
    n_kept_total  = n_base_kept + n_stress_kept + n_amus_kept + n_medit_kept
    n_total_total = n_base_total + n_stress_tot + n_amus_tot + n_medit_tot
    pct_rejected_motion = 1.0 - (n_kept_total / n_total_total) if n_total_total > 0 else 0.0

    # Janelas de baseline válidas (RMSSD obrigatório, após gate de movimento)
    valid_idx = [i for i, r in enumerate(baseline_w["rmssd"]) if r is not None]
    if len(valid_idx) < MIN_BASELINE_WINDOWS:
        print(f"SKIP (baseline insuficiente após gate de movimento: {len(valid_idx)} janelas)")
        return None

    baseline_temp_mean = float(np.mean([baseline_w["temp"][i] for i in valid_idx]))

    def delta_temp(temp_list: List[float]) -> List[float]:
        return [t - baseline_temp_mean for t in temp_list]

    rmssd_b   = [baseline_w["rmssd"][i] for i in valid_idx]
    eda_scl_b = [baseline_w["eda_scl"][i] for i in valid_idx]
    eda_scr_b = [baseline_w["eda_scr"][i] for i in valid_idx]
    dtemp_b   = delta_temp([baseline_w["temp"][i] for i in valid_idx])
    tremor_b  = [baseline_w["tremor"][i] for i in valid_idx]

    mu, sigma_inv, sig_labels = build_individual_baseline(
        rmssd_b, eda_scl_b, eda_scr_b, dtemp_b, tremor_b
    )
    threshold = CHI2.get(len(sig_labels), CHI2[2])

    def evaluate_condition(win: Dict[str, list]) -> Tuple[List[float], int, int]:
        """Retorna (d2_values, n_detected, n_total) usando core.mahalanobis diretamente."""
        d2_values, detected, total = [], 0, 0
        n = len(win["rmssd"])
        dtemps = delta_temp(win["temp"])
        for i in range(n):
            if win["rmssd"][i] is None:
                continue
            total += 1
            result = evaluate_mahalanobis_layer(
                hrv_rmssd=win["rmssd"][i],
                spo2=98.0,  # não usado no D² — SPO2 não está em sig_labels
                eda_scl=win["eda_scl"][i],
                eda_scr=win["eda_scr"][i],
                skin_temp_delta=dtemps[i],
                tremor_8_12hz=win["tremor"][i],
                baseline_mu=mu,
                baseline_sigma_inv=sigma_inv,
                baseline_labels=sig_labels,
            )
            if result.d_squared is not None:
                d2_values.append(result.d_squared)
                if result.status == "FAIL":
                    detected += 1
        return d2_values, detected, total

    d2_stress,     stress_det,  stress_total  = evaluate_condition(stress_w)
    d2_amusement,  amus_flag,   amus_total    = evaluate_condition(amusement_w)
    d2_meditation, medit_flag,  medit_total   = evaluate_condition(meditation_w)
    d2_baseline_vals, _, _ = evaluate_condition(
        {k: [baseline_w[k][i] for i in valid_idx] for k in baseline_w}
    )

    sensitivity     = stress_det / stress_total if stress_total > 0 else 0.0
    spec_amusement  = 1.0 - (amus_flag / amus_total) if amus_total > 0 else 1.0
    spec_meditation = 1.0 - (medit_flag / medit_total) if medit_total > 0 else 1.0

    mean_rmssd_stress = float(np.mean([r for r in stress_w["rmssd"] if r is not None])) \
        if any(r is not None for r in stress_w["rmssd"]) else 0.0

    # ── GAP-B01 — agregação do IP por condição ────────────────────────────────
    def mean_ip(win: Dict[str, list]) -> Optional[float]:
        vals = [r.periodicity_index for r in win["ip"] if r is not None and r.assessed]
        return float(np.mean(vals)) if vals else None

    def suspicious_rate(win: Dict[str, list]) -> Optional[float]:
        assessed = [r for r in win["ip"] if r is not None and r.assessed]
        if not assessed:
            return None
        return sum(1 for r in assessed if r.is_suspicious) / len(assessed)

    def mean_gt_resp(win: Dict[str, list]) -> Optional[float]:
        vals = [v for v in win["ground_truth_resp_hz"] if v is not None]
        return float(np.mean(vals)) if vals else None

    result = SubjectResult(
        subject_id=subject_id,
        n_baseline_windows=len(valid_idx),
        n_stress_windows=stress_total,
        n_amusement_windows=amus_total,
        n_meditation_windows=medit_total,
        mean_rmssd_baseline=float(np.mean(rmssd_b)),
        mean_rmssd_stress=mean_rmssd_stress,
        mean_eda_scl_baseline=float(np.mean([v for v in eda_scl_b if v is not None])) if any(v is not None for v in eda_scl_b) else 0.0,
        mean_eda_scl_stress=float(np.mean([v for v in stress_w["eda_scl"] if v is not None])) if any(v is not None for v in stress_w["eda_scl"]) else 0.0,
        mean_eda_scr_baseline=float(np.mean([v for v in eda_scr_b if v is not None])) if any(v is not None for v in eda_scr_b) else None,
        mean_eda_scr_stress=float(np.mean([v for v in stress_w["eda_scr"] if v is not None])) if any(v is not None for v in stress_w["eda_scr"]) else None,
        mean_tremor_baseline=float(np.mean([v for v in tremor_b if v is not None])) if any(v is not None for v in tremor_b) else 0.0,
        mean_tremor_stress=float(np.mean([v for v in stress_w["tremor"] if v is not None])) if any(v is not None for v in stress_w["tremor"]) else 0.0,
        stress_detected=stress_det,
        stress_total=stress_total,
        amusement_flagged=amus_flag,
        amusement_total=amus_total,
        meditation_flagged=medit_flag,
        meditation_total=medit_total,
        sensitivity=sensitivity,
        specificity_amusement=spec_amusement,
        specificity_meditation=spec_meditation,
        mean_d2_baseline=float(np.mean(d2_baseline_vals)) if d2_baseline_vals else 0.0,
        mean_d2_stress=float(np.mean(d2_stress)) if d2_stress else 0.0,
        threshold_used=threshold,
        signals_used=sig_labels,
        n_signals=len(sig_labels),
        mean_ip_baseline=mean_ip({k: [baseline_w[k][i] for i in valid_idx] for k in baseline_w}),
        mean_ip_stress=mean_ip(stress_w),
        mean_ip_amusement=mean_ip(amusement_w),
        mean_ip_meditation=mean_ip(meditation_w),
        ip_false_positive_rate_meditation=suspicious_rate(meditation_w),
        mean_ground_truth_resp_hz_baseline=mean_gt_resp({k: [baseline_w[k][i] for i in valid_idx] for k in baseline_w}),
        mean_ground_truth_resp_hz_meditation=mean_gt_resp(meditation_w),
        motion_threshold_g=motion_threshold,
        pct_windows_rejected_motion=pct_rejected_motion,
    )

    print(
        f"sens={sensitivity:.2%} | spec_amus={spec_amusement:.2%} | "
        f"D²_stress={result.mean_d2_stress:.2f} | D²_base={result.mean_d2_baseline:.2f} | "
        f"sinais={len(sig_labels)} | IP_medit_FP={suspicious_rate(meditation_w)} | "
        f"motion_rej={pct_rejected_motion:.1%}"
    )
    return result


# ── Relatório agregado ─────────────────────────────────────────────────────────

def aggregate_results(results: List[SubjectResult]) -> Dict:
    """
    Agrega métricas de todos os sujeitos.

    Métricas para o paper:
      - Sensitivity (TPR): % de janelas stress corretamente detectadas
      - Specificity (TNR): % de janelas amusement/meditation não flagadas
      - Balanced Accuracy: (sensitivity + specificity) / 2
      - Cohen's d: separação entre distribuições D² baseline e stress
      - GAP-B01: taxa de falso positivo do IP em meditação (o caso mais duro)
    """
    sensitivities = [r.sensitivity for r in results]
    spec_amus     = [r.specificity_amusement for r in results if r.amusement_total > 0]
    spec_medit    = [r.specificity_meditation for r in results if r.meditation_total > 0]

    mean_sensitivity = float(np.mean(sensitivities))
    std_sensitivity  = float(np.std(sensitivities))
    mean_spec_amus   = float(np.mean(spec_amus)) if spec_amus else None
    mean_spec_medit  = float(np.mean(spec_medit)) if spec_medit else None

    balanced_acc = (mean_sensitivity + (mean_spec_amus or 0.0)) / 2

    d2_baseline_all = [r.mean_d2_baseline for r in results]
    d2_stress_all   = [r.mean_d2_stress for r in results]
    pooled_std = float(np.std(d2_baseline_all + d2_stress_all))
    cohens_d = (np.mean(d2_stress_all) - np.mean(d2_baseline_all)) / pooled_std \
        if pooled_std > 0 else 0.0

    rmssd_base_all   = [r.mean_rmssd_baseline for r in results]
    rmssd_stress_all = [r.mean_rmssd_stress   for r in results if r.mean_rmssd_stress > 0]

    try:
        from scipy import stats
        _, p_rmssd = stats.wilcoxon(
            [r.mean_rmssd_baseline for r in results if r.mean_rmssd_stress > 0],
            [r.mean_rmssd_stress   for r in results if r.mean_rmssd_stress > 0]
        )
        _, p_d2 = stats.wilcoxon(d2_baseline_all, d2_stress_all)
    except Exception:
        p_rmssd = None
        p_d2    = None

    # GAP-B01 — IP por condição
    ip_baseline   = [r.mean_ip_baseline for r in results if r.mean_ip_baseline is not None]
    ip_stress     = [r.mean_ip_stress for r in results if r.mean_ip_stress is not None]
    ip_meditation = [r.mean_ip_meditation for r in results if r.mean_ip_meditation is not None]
    ip_fp_medit   = [r.ip_false_positive_rate_meditation for r in results
                      if r.ip_false_positive_rate_meditation is not None]

    n_signals_mode = int(np.median([r.n_signals for r in results])) if results else 0
    mean_pct_rejected_motion = float(np.mean([r.pct_windows_rejected_motion for r in results])) if results else 0.0

    return {
        "n_subjects": len(results),
        "mean_pct_windows_rejected_motion": round(mean_pct_rejected_motion, 4),
        "n_signals_used": n_signals_mode,
        "cvxeda_available": _HAS_CVXEDA,
        "sensitivity_mean": round(mean_sensitivity, 4),
        "sensitivity_std":  round(std_sensitivity, 4),
        "specificity_amusement_mean": round(mean_spec_amus, 4) if mean_spec_amus else None,
        "specificity_meditation_mean": round(mean_spec_medit, 4) if mean_spec_medit else None,
        "balanced_accuracy": round(balanced_acc, 4),
        "cohens_d_d2_stress_vs_baseline": round(cohens_d, 4),
        "rmssd_baseline_mean_ms": round(float(np.mean(rmssd_base_all)), 2),
        "rmssd_stress_mean_ms":   round(float(np.mean(rmssd_stress_all)), 2) if rmssd_stress_all else None,
        "d2_baseline_mean": round(float(np.mean(d2_baseline_all)), 4),
        "d2_stress_mean":   round(float(np.mean(d2_stress_all)), 4),
        "chi2_threshold": CHI2.get(n_signals_mode, CHI2[2]),
        "wilcoxon_p_rmssd": round(p_rmssd, 6) if p_rmssd is not None else None,
        "wilcoxon_p_d2":    round(p_d2, 6)    if p_d2    is not None else None,
        "gap_b01_mean_ip_baseline": round(float(np.mean(ip_baseline)), 4) if ip_baseline else None,
        "gap_b01_mean_ip_stress": round(float(np.mean(ip_stress)), 4) if ip_stress else None,
        "gap_b01_mean_ip_meditation": round(float(np.mean(ip_meditation)), 4) if ip_meditation else None,
        "gap_b01_ip_false_positive_rate_meditation": round(float(np.mean(ip_fp_medit)), 4) if ip_fp_medit else None,
        "per_subject": [asdict(r) for r in results],
    }


def write_paper_summary(agg: Dict, output_path: Path) -> None:
    """Gera texto pronto para colar na Seção 6 do paper VLP."""
    lines = [
        "=" * 70,
        "LICET WESAD VALIDATION — RESULTADOS PARA O PAPER",
        "=" * 70,
        "",
        f"Sujeitos processados: {agg['n_subjects']} / 15",
        f"Dataset: WESAD (Schmidt et al., ICMI 2018)",
        f"Protocolo: Layer 3 Mahalanobis (core.mahalanobis.evaluate_mahalanobis_layer, "
        f"import direto — não reimplementação), threshold χ²({agg['n_signals_used']}, p=0.05) = {agg['chi2_threshold']}",
        f"Sinais: até 5 — RMSSD, EDA_SCL, EDA_SCR{'  (cvxEDA)' if agg['cvxeda_available'] else '  (cvxEDA indisponível — SCR omitido)'}, "
        f"DELTA_TEMP, TREMOR_8_12HZ | Janela: {WINDOW_SEC}s, overlap {int(OVERLAP*100)}%",
        f"Gate de artefato de movimento: limiar calibrado por sujeito (mediana + 3xMAD do "
        f"baseline) — {agg['mean_pct_windows_rejected_motion']:.1%} das janelas rejeitadas em média",
        "",
        "── MÉTRICAS PRINCIPAIS ──────────────────────────────────────",
        f"Sensitivity (stress detection rate): {agg['sensitivity_mean']:.1%} ± {agg['sensitivity_std']:.1%}",
        f"Specificity (amusement not flagged): {agg['specificity_amusement_mean']:.1%}" if agg['specificity_amusement_mean'] else "Specificity (amusement): N/A",
        f"Balanced Accuracy:                   {agg['balanced_accuracy']:.1%}",
        f"Cohen's d (D² stress vs baseline):   {agg['cohens_d_d2_stress_vs_baseline']:.2f}",
        "",
        "── RMSSD (HRV) ──────────────────────────────────────────────",
        f"Baseline: {agg['rmssd_baseline_mean_ms']:.1f} ms",
        f"Stress:   {agg['rmssd_stress_mean_ms']:.1f} ms" if agg['rmssd_stress_mean_ms'] else "Stress: N/A",
        f"Wilcoxon p: {agg['wilcoxon_p_rmssd']:.4f}" if agg['wilcoxon_p_rmssd'] else "Wilcoxon p: N/A",
        "",
        "── D² MAHALANOBIS ───────────────────────────────────────────",
        f"D² baseline: {agg['d2_baseline_mean']:.3f}",
        f"D² stress:   {agg['d2_stress_mean']:.3f}",
        f"Threshold:   {agg['chi2_threshold']:.2f}",
        f"Wilcoxon p: {agg['wilcoxon_p_d2']:.4f}" if agg['wilcoxon_p_d2'] else "Wilcoxon p: N/A",
        "",
        "── GAP-B01 — ÍNDICE DE PERIODICIDADE (paced breathing) ──────",
        f"IP médio baseline:   {agg['gap_b01_mean_ip_baseline']:.3f}" if agg['gap_b01_mean_ip_baseline'] else "IP baseline: N/A",
        f"IP médio stress:     {agg['gap_b01_mean_ip_stress']:.3f}" if agg['gap_b01_mean_ip_stress'] else "IP stress: N/A",
        f"IP médio meditation: {agg['gap_b01_mean_ip_meditation']:.3f}" if agg['gap_b01_mean_ip_meditation'] else "IP meditation: N/A",
        f"Taxa de falso positivo (IP suspeito em meditação genuína): "
        f"{agg['gap_b01_ip_false_positive_rate_meditation']:.1%}" if agg['gap_b01_ip_false_positive_rate_meditation'] is not None else "FP rate: N/A",
        "",
        "── TEXTO PARA O PAPER (Section 6 — Empirical Validation) ───",
        "",
        "We validated LICET's Layer 3 (Mahalanobis distance) on the WESAD",
        "benchmark dataset [Schmidt2018], comprising N=XX subjects undergoing",
        "the Trier Social Stress Test (TSST). Using 60-second windows with 50%",
        "overlap, we extracted RMSSD from wrist photoplethysmography (BVP, 64 Hz),",
        "tonic/phasic EDA decomposition via cvxEDA [Greco2015], temperature",
        "deviation, and 8-12Hz accelerometer power, building individual baselines",
        "from the pre-stress resting phase.",
        "",
        f"The LICET protocol achieved sensitivity of {agg['sensitivity_mean']:.1%}",
        f"(±{agg['sensitivity_std']:.1%}) for stress detection and specificity of",
        f"{agg['specificity_amusement_mean']:.1%} for the amusement condition," if agg['specificity_amusement_mean'] else "",
        f"yielding balanced accuracy of {agg['balanced_accuracy']:.1%}.",
        f"Mean RMSSD decreased from {agg['rmssd_baseline_mean_ms']:.1f} ms (baseline) to",
        f"{agg['rmssd_stress_mean_ms']:.1f} ms (stress) (Wilcoxon p={agg['wilcoxon_p_rmssd']:.4f})." if agg['rmssd_stress_mean_ms'] and agg['wilcoxon_p_rmssd'] else "",
        f"Mahalanobis D² increased from {agg['d2_baseline_mean']:.2f} to {agg['d2_stress_mean']:.2f}",
        f"(Cohen's d={agg['cohens_d_d2_stress_vs_baseline']:.2f}, Wilcoxon p={agg['wilcoxon_p_d2']:.4f})." if agg['wilcoxon_p_d2'] else "",
        "",
        f"To test the GAP-B01 paced-breathing limitation, we evaluated the "
        f"periodicity index on the guided-meditation condition — the genuine "
        f"state physiologically closest to a paced-breathing attack. The "
        f"index flagged {agg['gap_b01_ip_false_positive_rate_meditation']:.1%} of meditation windows as "
        f"suspicious." if agg['gap_b01_ip_false_positive_rate_meditation'] is not None else "",
        "",
        "=" * 70,
    ]
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nRelatório escrito em: {output_path}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("LICET — WESAD Validation Experiment")
    print("=" * 50)
    if not _HAS_CVXEDA:
        print("[AVISO] cvxEDA indisponível — vetor Mahalanobis roda com 4 sinais (sem EDA_SCR).")

    if not WESAD_PATH.exists():
        print(f"\n[ERRO] Dataset não encontrado em: {WESAD_PATH.absolute()}")
        print("\nINSTRUÇÕES:")
        print("  1. Baixar WESAD em: https://uni-siegen.sciebo.de/s/HGdUkoNlW1Gy4em")
        print("     (cadastro gratuito — pode demorar até 1 dia de aprovação)")
        print("  2. Extrair os arquivos mantendo a estrutura: WESAD/S{id}/S{id}.pkl")
        print(f"  3. Garantir que o caminho WESAD_PATH='{WESAD_PATH.absolute()}' aponta para a pasta")
        print("  4. Executar novamente: python wesad_experiment.py")
        print()
        print("ALTERNATIVAS SE O LINK ORIGINAL ESTIVER INDISPONÍVEL:")
        print("  - Solicitar dataset via email aos autores: philip.schmidt@uni-siegen.de")
        print("  - UCI ML Repository: search 'WESAD'")
        sys.exit(1)

    RESULTS_PATH.mkdir(exist_ok=True)

    subjects_to_run = [s for s in ALL_SUBJECTS
                       if (WESAD_PATH / f"S{s}" / f"S{s}.pkl").exists()]
    print(f"Sujeitos encontrados: {subjects_to_run}")
    print()

    results = []
    for sid in subjects_to_run:
        result = process_subject(sid, WESAD_PATH)
        if result is not None:
            results.append(result)

    if not results:
        print("\n[ERRO] Nenhum sujeito processado com sucesso.")
        sys.exit(1)

    print(f"\n{'='*50}")
    print(f"Sujeitos processados: {len(results)}")

    agg = aggregate_results(results)

    json_path = RESULTS_PATH / "wesad_results.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(agg, f, indent=2, ensure_ascii=False)
    print(f"Resultados JSON: {json_path}")

    csv_path = RESULTS_PATH / "wesad_per_subject.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=asdict(results[0]).keys())
            writer.writeheader()
            for r in results:
                writer.writerow(asdict(r))
    print(f"CSV por sujeito: {csv_path}")

    summary_path = RESULTS_PATH / "wesad_summary.txt"
    write_paper_summary(agg, summary_path)

    print(f"\nSensitivity:  {agg['sensitivity_mean']:.1%} ± {agg['sensitivity_std']:.1%}")
    if agg['specificity_amusement_mean']:
        print(f"Specificity:  {agg['specificity_amusement_mean']:.1%}")
    print(f"Balanced Acc: {agg['balanced_accuracy']:.1%}")
    print(f"Cohen's d:    {agg['cohens_d_d2_stress_vs_baseline']:.2f}")
    if agg['gap_b01_ip_false_positive_rate_meditation'] is not None:
        print(f"GAP-B01 IP false positive rate (meditation): {agg['gap_b01_ip_false_positive_rate_meditation']:.1%}")


if __name__ == "__main__":
    main()
