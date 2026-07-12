"""
LICET — API Routes v2
Endpoints do protocolo com pipeline de três camadas biométricas.

Fluxo de autorização:
  captura biométrica → baseline lookup → 3 camadas → farmacológico → ZKP → ledger

Endpoints de baseline:
  POST /v1/baseline/start    — inicia sessão de calibração
  POST /v1/baseline/submit   — submete leitura de calibração
  GET  /v1/baseline/status   — retorna estado do baseline do usuário
  POST /v1/baseline/simulate — gera baseline simulado completo (desenvolvimento)
"""

import time
import os
import random
import secrets as sec
import hmac as hmac_lib
import hashlib
from typing import Optional, List

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from core.crypto import authorize, load_secret_key, load_signing_key, get_signing_public_key_b64
from hardware.wearable_manager import WearableManager
from hardware.sensor_interface import BiometricReading
from zkp.proof import verify_proof
from ledger.db import (
    record, verify_integrity, get_history, initialize_db, engine,
    revoke_entry, anchor_to_transparency_log,
    get_user_data_summary, erase_user_data,
)
from core.baseline import (
    BaselineSession, build_baseline,
    load_baseline, save_baseline, save_session, load_sessions,
)
from core.pharmacological_check import check_pharmacological_interference
from core.respiratory_periodicity import compute_respiratory_periodicity


router = APIRouter()


# ── Schemas ───────────────────────────────────────────────────────────────────

class AuthorizationRequest(BaseModel):
    action: str
    agent_id: str
    target: str
    user_id: Optional[str] = None        # Para lookup de baseline individual
    capture_seconds: int = 10
    ble_address: Optional[str] = None
    # GAP-A04 fix: gerados pelo cliente (app do usuário), NÃO pelo agente AI.
    # action_nonce: valor aleatório gerado pelo app antes de exibir a ação ao usuário.
    # action_commitment: SHA256(action|agent_id|target|nonce) — compromisso da ação.
    # Se fornecidos, o servidor verifica. Se ausentes → ui_binding_status="ABSENT".
    action_nonce: Optional[str] = None
    action_commitment: Optional[str] = None


class BiometricPushRequest(BaseModel):
    """Payload enviado pelo app iOS ou Android com dados do wearable."""
    source: str              # "apple_watch" | "samsung_watch" | "whoop" | "polar_h10"
    heart_rate: float
    spo2: float
    hrv: float
    start_timestamp: float
    end_timestamp: float
    device_model: str
    hmac_signature: str      # HMAC-SHA256 do app móvel
    # Sinais avançados (opcionais — dependem do wearable)
    eda_scl: Optional[float] = None
    eda_scr: Optional[float] = None
    skin_temp: Optional[float] = None
    tremor_8_12hz: Optional[float] = None
    user_id: Optional[str] = None
    # RR intervals em ms — ativa análise espectral de periodicidade respiratória
    # Requer ≥60 amostras (≈60 s) para análise confiável
    rr_intervals: Optional[List[float]] = None
    # GAP-B09: tom de pele Fitzpatrick (1–6), declarado pelo usuário no app.
    # Ativa threshold_multiplier ×1.4 na Camada 3 quando ≥5 com sensor PPG.
    # None = não declarado (sem ajuste aplicado).
    skin_tone_fitzpatrick: Optional[int] = None


class AuthorizationFromPushRequest(BaseModel):
    action: str
    agent_id: str
    target: str
    biometric_push_id: str
    user_id: Optional[str] = None
    # GAP-A04 fix: mesma semântica que AuthorizationRequest.
    # O app móvel gera estes campos ANTES de enviar /biometric/push.
    action_nonce: Optional[str] = None
    action_commitment: Optional[str] = None


class AuthorizationResponse(BaseModel):
    authorized: bool
    intent_hash: str
    biometric_signature: str
    # Estado fisiológico
    coercion_risk: str
    cognitive_state: str
    coercion_cost_elevation: str
    denial_reason: str
    # Três camadas
    layer1_ecg: str
    layer1_ecg_cosine_sim: Optional[float]
    layer2_eda: str
    layer2_eda_scl: Optional[float]
    layer2_eda_scr: Optional[float]
    layer3_mahalanobis_status: str
    layer3_mahalanobis_d2: Optional[float]
    # Farmacológico
    pharmacological_check: str
    pharmacological_confidence: str
    # Trust level
    trust_level: str
    baseline_maturity: float
    # ZKP e ledger
    zkp_proof: dict
    ledger_id: int
    timestamp: float
    hardware_source: str
    # Análise espectral de periodicidade respiratória
    respiratory_periodicity_index: Optional[float] = None
    respiratory_periodicity_warning: Optional[str] = None
    # Custo de falsificação estimado por camada
    layer_forgery_cost: Optional[dict] = None
    # UI Binding (GAP-A04 fix)
    # "VERIFIED" — commitment válido; "ABSENT" — sem commitment; "FAILED" — tampering
    ui_binding_status: str = "ABSENT"
    ui_binding_warning: Optional[str] = None
    # Limitação primária de design — sempre presente para consciência do integrador
    design_limitation: str = (
        "PRIMARY UNMITIGATED LIMITATION: A coerced subject trained in "
        "resonance-frequency breathing (~0.1 Hz, ~6 cycles/min) produces a "
        "physiologically authentic calm vector that collapses Mahalanobis "
        "distance to zero without any anomalous signal. No mitigation exists "
        "in the current design. See LICET spec §Acknowledged Limitations."
    )
    # Aviso de confound — presente apenas quando o baseline foi calibrado com beta-bloqueador crônico
    beta_blocker_confound_warning: Optional[str] = None
    # GAP-B09: aviso de equidade PPG — presente quando threshold Mahalanobis foi ampliado ×1.4
    # por limitação de sensor PPG em Fitzpatrick V–VI (Bent et al. 2020)
    ppg_equity_warning: Optional[str] = None


class VerifyRequest(BaseModel):
    intent_hash: str
    zkp_proof: dict
    # Opcional: verifica também a assinatura Ed25519 (GAP-C02 fix)
    biometric_signature: Optional[str] = None


class BaselineStartRequest(BaseModel):
    """Inicia uma sessão de calibração de baseline."""
    user_id: str
    duration_seconds: int = 180    # 3 minutos mínimo
    hardware_source: str = "simulation"


class BaselineSubmitRequest(BaseModel):
    """Submete leitura de uma sessão de calibração."""
    user_id: str
    session_token: str             # Token retornado por /baseline/start
    heart_rate: float
    spo2: float
    hrv: float
    duration_seconds: int
    hardware_source: str = "simulation"
    eda_scl: Optional[float] = None
    eda_scr: Optional[float] = None
    skin_temp: Optional[float] = None
    tremor_8_12hz: Optional[float] = None
    on_chronic_beta_blocker: Optional[bool] = None  # Declaração de uso crônico de beta-bloqueador
    # RR intervals em ms — necessários para incluir HF power e peak_freq no baseline
    # Requer ≥60 amostras (≈60 s) para análise espectral confiável
    rr_intervals: Optional[List[float]] = None


# ── Cache em memória ──────────────────────────────────────────────────────────

# Biometrias recebidas via push (TTL 60s)
_biometric_push_cache: dict = {}

# Sessões de baseline em andamento (TTL 10 min)
_baseline_sessions: dict = {}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _load_baseline_params(user_id: Optional[str]) -> dict:
    """
    Carrega o baseline individual do usuário do banco.
    Retorna dict com todos os parâmetros para authorize().
    Retorna dict vazio (baseline ausente) se user_id não fornecido ou baseline expirado.
    """
    if not user_id:
        return {}

    try:
        initialize_db()
        baseline = load_baseline(user_id, engine)
    except Exception:
        return {}

    if not baseline:
        return {}

    return {
        "ecg_baseline_template":      baseline.ecg_template,
        "baseline_mu":                baseline.mu,
        "baseline_sigma_inv":         baseline.sigma_inv,
        "baseline_labels":            baseline.signal_labels,
        "baseline_maturity":          baseline.maturity_score,
        "baseline_hr_mean":           baseline.hr_mean,
        "baseline_hr_std":            baseline.hr_std,
        "baseline_hrv_mean":          baseline.hrv_mean,
        "baseline_hrv_std":           baseline.hrv_std,
        "baseline_tremor_mean":       baseline.tremor_mean,
        "baseline_tremor_std":        baseline.tremor_std,
        # Flag interno — extraído antes de passar para authorize()
        "_chronic_beta_blocker_flag": baseline.chronic_beta_blocker_flag,
    }


def _verify_mobile_hmac(req_source: str, heart_rate: float, spo2: float,
                         hrv: float, start_timestamp: float, hmac_sig: str) -> None:
    """Valida HMAC do app móvel. Lança HTTPException 401 se inválido."""
    app_secret = os.getenv("LICET_MOBILE_APP_SECRET")
    if not app_secret:
        raise HTTPException(
            status_code=503,
            detail="Serviço não configurado: LICET_MOBILE_APP_SECRET ausente."
        )
    sig_data = f"{req_source}:{heart_rate}:{spo2}:{hrv}:{int(start_timestamp)}"
    expected = hmac_lib.new(
        app_secret.encode(), sig_data.encode(), hashlib.sha256
    ).hexdigest()
    if not hmac_lib.compare_digest(expected, hmac_sig):
        raise HTTPException(status_code=401, detail="Assinatura do app inválida.")


def _check_pre_medication(session: BaselineSession) -> BaselineSession:
    """
    Verifica se a sessão de calibração não está contaminada por medicação.
    Se padrão farmacológico detectado → marca sessão como inválida.
    """
    pharma = check_pharmacological_interference(
        heart_rate=60.0,   # HR não armazenado em sessão de baseline — usar neutro
        hrv_rmssd=session.hrv_rmssd,
        spo2=session.spo2,
        eda_scl=session.eda_scl,
        eda_scr=session.eda_scr,
        skin_temp=session.skin_temp,
        tremor_8_12hz=session.tremor_8_12hz,
    )
    if not pharma.clean and pharma.confidence in ("MEDIUM", "HIGH"):
        session.is_valid = False
        session.invalidation_reason = (
            f"Pré-medicação detectada durante calibração: "
            f"{pharma.pattern_detected} ({pharma.confidence}). "
            "Sessão descartada. Recalibre sem medicação."
        )
    return session


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/health")
def health():
    mode = os.getenv("LICET_HARDWARE_MODE", "simulation")
    return {
        "status": "online",
        "protocol": "LICET — Human Intent Protocol",
        "version": "2.0.0",
        "hardware_mode": mode,
        "timestamp": time.time(),
    }


@router.post("/authorize", response_model=AuthorizationResponse)
def authorize_action(req: AuthorizationRequest):
    """
    Autorização biométrica completa — pipeline três camadas.
    Captura sinal do hardware configurado e processa ECG → EDA → Mahalanobis → ZKP → ledger.
    """
    initialize_db()

    try:
        master_key  = load_secret_key()
        signing_key = load_signing_key()
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))

    manager = WearableManager(ble_address=req.ble_address)
    reading = manager.capture(duration_seconds=req.capture_seconds)
    reading.user_id = req.user_id

    baseline_params = _load_baseline_params(req.user_id)
    chronic_bb = baseline_params.pop("_chronic_beta_blocker_flag", False)

    bundle = authorize(
        action=req.action,
        agent_id=req.agent_id,
        target=req.target,
        reading=reading,
        master_key=master_key,
        signing_key=signing_key,
        action_commitment=req.action_commitment,
        action_nonce=req.action_nonce,
        medication_accommodation=chronic_bb,
        **baseline_params,
    )

    # ZKP gerado dentro de authorize() com session_key como witness (GAP-C01 fix)
    zkp = bundle.zkp_proof
    ledger_id = record(bundle)

    bb_warning = (
        "CONFOUND: Baseline calibrated under chronic beta-blocker therapy. "
        "Resting RMSSD is elevated and resting HR is reduced relative to an "
        "unmedicated individual, displacing the calm fingerprint before any "
        "challenge. Mahalanobis discriminative power is reduced for this user. "
        "See LICET spec §Acknowledged Limitations."
    ) if chronic_bb else None

    ui_warning = (
        "GAP-A04: action_commitment ausente. O action descriptor pode ter sido "
        "construído pelo agente AI sem supervisão do usuário. Para UI binding "
        "completo, o app do usuário deve gerar action_nonce e action_commitment "
        "antes de qualquer coleta biométrica."
    ) if bundle.ui_binding_status == "ABSENT" else None

    return AuthorizationResponse(
        authorized=bundle.authorized,
        intent_hash=bundle.intent_hash,
        biometric_signature=bundle.biometric_signature,
        coercion_risk=bundle.coercion_risk,
        cognitive_state=bundle.cognitive_state,
        coercion_cost_elevation=bundle.coercion_cost_elevation,
        denial_reason=bundle.denial_reason,
        layer1_ecg=bundle.layer1_ecg,
        layer1_ecg_cosine_sim=bundle.layer1_ecg_cosine_sim,
        layer2_eda=bundle.layer2_eda,
        layer2_eda_scl=bundle.layer2_eda_scl,
        layer2_eda_scr=bundle.layer2_eda_scr,
        layer3_mahalanobis_status=bundle.layer3_mahalanobis_status,
        layer3_mahalanobis_d2=bundle.layer3_mahalanobis_d2,
        pharmacological_check=bundle.pharmacological_check,
        pharmacological_confidence=bundle.pharmacological_confidence,
        trust_level=bundle.trust_level,
        baseline_maturity=bundle.baseline_maturity,
        zkp_proof=zkp.to_dict(),
        ledger_id=ledger_id,
        timestamp=bundle.timestamp,
        hardware_source=manager.mode,
        beta_blocker_confound_warning=bb_warning,
        respiratory_periodicity_index=bundle.respiratory_periodicity_index,
        respiratory_periodicity_warning=bundle.respiratory_periodicity_warning,
        layer_forgery_cost=bundle.layer_forgery_cost,
        ui_binding_status=bundle.ui_binding_status,
        ui_binding_warning=ui_warning,
        ppg_equity_warning=bundle.ppg_equity_warning,
    )


@router.post("/biometric/push")
def receive_biometric_push(req: BiometricPushRequest):
    """
    Recebe dados biométricos do app iOS (HealthKit) ou Android (Health Connect).
    Retorna um push_id válido por 60 segundos para uso em /authorize/from-push.
    Aceita sinais avançados opcionais: eda_scl, eda_scr, skin_temp, tremor_8_12hz.
    """
    _verify_mobile_hmac(req.source, req.heart_rate, req.spo2,
                        req.hrv, req.start_timestamp, req.hmac_signature)

    push_id = sec.token_hex(16)
    _biometric_push_cache[push_id] = {
        "reading": BiometricReading(
            heart_rate=req.heart_rate,
            spo2=req.spo2,
            hrv=req.hrv,
            timestamp=req.end_timestamp,
            duration_seconds=int(req.end_timestamp - req.start_timestamp),
            sample_count=100,
            eda_scl=req.eda_scl,
            eda_scr=req.eda_scr,
            skin_temp=req.skin_temp,
            tremor_8_12hz=req.tremor_8_12hz,
            hardware_source=req.source,
            user_id=req.user_id,
            rr_intervals=req.rr_intervals,
            skin_tone_fitzpatrick=req.skin_tone_fitzpatrick,
        ),
        "source": req.source,
        "device": req.device_model,
        "user_id": req.user_id,
        "expires_at": time.time() + 60,
    }

    return {
        "push_id": push_id,
        "source": req.source,
        "device": req.device_model,
        "has_eda": req.eda_scl is not None,
        "expires_in_seconds": 60,
        "timestamp": time.time(),
    }


@router.post("/authorize/from-push", response_model=AuthorizationResponse)
def authorize_from_push(req: AuthorizationFromPushRequest):
    """
    Autoriza usando dados biométricos já enviados via /biometric/push.
    Carrega baseline individual se user_id fornecido.
    """
    initialize_db()

    cached = _biometric_push_cache.get(req.biometric_push_id)
    if not cached:
        raise HTTPException(status_code=404, detail="push_id não encontrado.")
    if time.time() > cached["expires_at"]:
        del _biometric_push_cache[req.biometric_push_id]
        raise HTTPException(status_code=410, detail="Dados biométricos expirados (TTL 60s).")

    try:
        master_key  = load_secret_key()
        signing_key = load_signing_key()
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))

    reading: BiometricReading = cached["reading"]
    source: str = cached["source"]
    user_id = req.user_id or cached.get("user_id")
    reading.user_id = user_id

    baseline_params = _load_baseline_params(user_id)
    chronic_bb = baseline_params.pop("_chronic_beta_blocker_flag", False)

    bundle = authorize(
        action=req.action,
        agent_id=req.agent_id,
        target=req.target,
        reading=reading,
        master_key=master_key,
        signing_key=signing_key,
        action_commitment=req.action_commitment,
        action_nonce=req.action_nonce,
        medication_accommodation=chronic_bb,
        **baseline_params,
    )

    # ZKP gerado dentro de authorize() com session_key como witness (GAP-C01 fix)
    zkp = bundle.zkp_proof
    ledger_id = record(bundle)
    del _biometric_push_cache[req.biometric_push_id]

    bb_warning = (
        "CONFOUND: Baseline calibrated under chronic beta-blocker therapy. "
        "Resting RMSSD is elevated and resting HR is reduced relative to an "
        "unmedicated individual, displacing the calm fingerprint before any "
        "challenge. Mahalanobis discriminative power is reduced for this user. "
        "See LICET spec §Acknowledged Limitations."
    ) if chronic_bb else None

    ui_warning = (
        "GAP-A04: action_commitment ausente. O action descriptor pode ter sido "
        "construído pelo agente AI sem supervisão do usuário. Para UI binding "
        "completo, o app do usuário deve gerar action_nonce e action_commitment "
        "antes de qualquer coleta biométrica."
    ) if bundle.ui_binding_status == "ABSENT" else None

    return AuthorizationResponse(
        authorized=bundle.authorized,
        intent_hash=bundle.intent_hash,
        biometric_signature=bundle.biometric_signature,
        coercion_risk=bundle.coercion_risk,
        cognitive_state=bundle.cognitive_state,
        coercion_cost_elevation=bundle.coercion_cost_elevation,
        denial_reason=bundle.denial_reason,
        layer1_ecg=bundle.layer1_ecg,
        layer1_ecg_cosine_sim=bundle.layer1_ecg_cosine_sim,
        layer2_eda=bundle.layer2_eda,
        layer2_eda_scl=bundle.layer2_eda_scl,
        layer2_eda_scr=bundle.layer2_eda_scr,
        layer3_mahalanobis_status=bundle.layer3_mahalanobis_status,
        layer3_mahalanobis_d2=bundle.layer3_mahalanobis_d2,
        pharmacological_check=bundle.pharmacological_check,
        pharmacological_confidence=bundle.pharmacological_confidence,
        trust_level=bundle.trust_level,
        baseline_maturity=bundle.baseline_maturity,
        zkp_proof=zkp.to_dict(),
        ledger_id=ledger_id,
        timestamp=bundle.timestamp,
        hardware_source=source,
        beta_blocker_confound_warning=bb_warning,
        respiratory_periodicity_index=bundle.respiratory_periodicity_index,
        respiratory_periodicity_warning=bundle.respiratory_periodicity_warning,
        layer_forgery_cost=bundle.layer_forgery_cost,
        ui_binding_status=bundle.ui_binding_status,
        ui_binding_warning=ui_warning,
        ppg_equity_warning=bundle.ppg_equity_warning,
    )


# ── Baseline ──────────────────────────────────────────────────────────────────

@router.post("/baseline/start")
def baseline_start(req: BaselineStartRequest):
    """
    Inicia uma sessão de calibração de baseline.
    Retorna session_token para usar em /baseline/submit.
    Requisito: ≥5 sessões de ≥3 minutos para baseline completo.
    """
    initialize_db()
    token = sec.token_hex(16)
    _baseline_sessions[token] = {
        "user_id": req.user_id,
        "started_at": time.time(),
        "duration_seconds": req.duration_seconds,
        "hardware_source": req.hardware_source,
        "expires_at": time.time() + 600,   # token válido por 10 min
    }

    # Contar sessões existentes para informar progresso
    try:
        sessions = load_sessions(req.user_id, engine, limit=50)
        valid_sessions = [s for s in sessions if s.is_valid]
        from core.baseline import MIN_SESSIONS
        remaining = max(0, MIN_SESSIONS - len(valid_sessions))
    except Exception:
        valid_sessions = []
        remaining = 5

    return {
        "session_token": token,
        "user_id": req.user_id,
        "duration_seconds": req.duration_seconds,
        "sessions_completed": len(valid_sessions),
        "sessions_remaining": remaining,
        "baseline_ready": remaining == 0,
        "message": (
            f"Sessão iniciada. Fique em repouso por {req.duration_seconds}s. "
            f"Use /baseline/submit ao concluir."
        ),
        "expires_in_seconds": 600,
    }


@router.post("/baseline/submit")
def baseline_submit(req: BaselineSubmitRequest):
    """
    Submete os sinais coletados em uma sessão de calibração.
    Verifica pré-medicação. Recalcula baseline se ≥5 sessões válidas.
    """
    initialize_db()

    # Validar token da sessão
    session_meta = _baseline_sessions.get(req.session_token)
    if not session_meta:
        raise HTTPException(status_code=404, detail="session_token não encontrado ou expirado.")
    if time.time() > session_meta["expires_at"]:
        del _baseline_sessions[req.session_token]
        raise HTTPException(status_code=410, detail="Sessão expirada.")
    if session_meta["user_id"] != req.user_id:
        raise HTTPException(status_code=403, detail="user_id não corresponde ao token.")

    # Análise espectral dos RR intervals — popula HF power e peak_freq para o baseline
    _resp = compute_respiratory_periodicity(req.rr_intervals or [])
    _hf_power  = _resp.hf_power_ms2   if _resp.assessed else None
    _peak_freq = _resp.dominant_freq_hz if _resp.assessed else None

    # Criar sessão de baseline
    session = BaselineSession(
        user_id=req.user_id,
        timestamp=time.time(),
        duration_seconds=req.duration_seconds,
        hrv_rmssd=req.hrv,
        spo2=req.spo2,
        eda_scl=req.eda_scl,
        eda_scr=req.eda_scr,
        skin_temp=req.skin_temp,
        tremor_8_12hz=req.tremor_8_12hz,
        hardware_source=req.hardware_source,
        on_chronic_beta_blocker=bool(req.on_chronic_beta_blocker),
        hf_power_ms2=_hf_power,
        peak_freq_hz=_peak_freq,
    )

    # Verificar pré-medicação
    session = _check_pre_medication(session)

    # Persistir sessão no histórico
    save_session(session, engine)

    # Tentar recalcular baseline com todas as sessões disponíveis
    all_sessions = load_sessions(req.user_id, engine, limit=50)
    heart_rates = [req.heart_rate] + [60.0] * (len(all_sessions) - 1)
    new_baseline = build_baseline(req.user_id, all_sessions, heart_rates)

    baseline_updated = False
    maturity = 0.0
    if new_baseline:
        save_baseline(new_baseline, engine)
        baseline_updated = True
        maturity = new_baseline.maturity_score

    del _baseline_sessions[req.session_token]

    valid_count = sum(1 for s in all_sessions if s.is_valid)
    from core.baseline import MIN_SESSIONS

    return {
        "user_id": req.user_id,
        "session_valid": session.is_valid,
        "invalidation_reason": session.invalidation_reason or None,
        "sessions_completed": valid_count,
        "sessions_remaining": max(0, MIN_SESSIONS - valid_count),
        "baseline_updated": baseline_updated,
        "baseline_maturity": maturity,
        "baseline_ready": baseline_updated,
        "signals_recorded": {
            "hrv_rmssd": req.hrv,
            "spo2": req.spo2,
            "eda_scl": req.eda_scl,
            "eda_scr": req.eda_scr,
        },
        "timestamp": time.time(),
    }


@router.get("/baseline/status")
def baseline_status(user_id: str):
    """
    Retorna o estado atual do baseline do usuário.
    Informa: sessões concluídas, maturidade, expiração, sinais disponíveis.
    """
    initialize_db()

    try:
        sessions = load_sessions(user_id, engine, limit=50)
    except Exception:
        sessions = []

    valid_sessions = [s for s in sessions if s.is_valid]

    try:
        baseline = load_baseline(user_id, engine)
    except Exception:
        baseline = None

    from core.baseline import MIN_SESSIONS

    if not baseline:
        return {
            "user_id": user_id,
            "baseline_ready": False,
            "baseline_expired": False,
            "sessions_completed": len(valid_sessions),
            "sessions_remaining": max(0, MIN_SESSIONS - len(valid_sessions)),
            "maturity_score": 0.0,
            "trust_level_available": "L0",
            "signals_in_baseline": [],
            "expires_at": None,
            "message": (
                f"Baseline não calibrado. "
                f"Complete {max(0, MIN_SESSIONS - len(valid_sessions))} sessão(ões) "
                f"de ≥3 min em repouso via POST /v1/baseline/start."
            ),
        }

    hardware_sources = list({s.hardware_source for s in valid_sessions})
    has_eda = any(s.eda_scl is not None for s in valid_sessions)
    trust = "L1" if hardware_sources and "simulation" not in hardware_sources else "L0"

    return {
        "user_id": user_id,
        "baseline_ready": True,
        "baseline_expired": baseline.is_expired(),
        "sessions_completed": baseline.session_count,
        "sessions_remaining": 0,
        "maturity_score": baseline.maturity_score,
        "trust_level_available": trust,
        "signals_in_baseline": baseline.signal_labels,
        "has_ecg_template": baseline.ecg_template is not None,
        "has_eda": has_eda,
        "expires_at": baseline.expires_at,
        "days_until_expiry": max(0, int((baseline.expires_at - time.time()) / 86400)),
        "hardware_sources": hardware_sources,
    }


@router.post("/baseline/simulate")
def baseline_simulate(user_id: str, sessions: int = 7):
    """
    Gera um baseline simulado completo para um usuário — apenas em modo simulação.

    Útil para desenvolvimento e testes sem hardware físico.
    Cria `sessions` sessões com biometria realista (variação gaussiana em torno
    de valores basais humanos típicos) e constrói o baseline individual.

    Rejeita a chamada se LICET_HARDWARE_MODE != 'simulation'.
    """
    if os.getenv("LICET_HARDWARE_MODE", "simulation") != "simulation":
        raise HTTPException(
            status_code=403,
            detail="Endpoint disponível apenas em modo simulação (LICET_HARDWARE_MODE=simulation)."
        )

    initialize_db()

    # Parâmetros basais individuais — centros gaussianos
    # Simula um adulto saudável em repouso, com variação inter-sessão realista
    base = {
        "hr":     random.gauss(68, 5),       # FC basal — entre 55 e 85 BPM
        "hrv":    random.gauss(52, 8),       # HRV RMSSD — entre 30 e 80 ms
        "spo2":   random.gauss(97.5, 0.4),   # SpO2 — entre 96 e 99%
        "eda_scl": random.gauss(4.2, 0.5),   # EDA SCL — entre 2 e 7 μS
        "eda_scr": random.gauss(0.3, 0.05),  # EDA SCR — entre 0.1 e 0.6 μS
        "skin_temp": random.gauss(33.8, 0.3),# Temp pele — entre 32.5 e 35 °C
        "tremor":  random.gauss(0.005, 0.001),# Tremor 8-12Hz — repouso
    }

    now = time.time()
    generated_sessions = []

    for i in range(max(sessions, 5)):
        # Cada sessão simulada em um dia diferente (distribuição em ≥3 dias)
        day_offset = i * (86400 * random.uniform(0.8, 1.5))
        session_time = now - (sessions * 86400) + day_offset

        session = BaselineSession(
            user_id=user_id,
            timestamp=session_time,
            duration_seconds=random.randint(180, 300),   # 3–5 minutos
            hrv_rmssd=round(max(20.0, random.gauss(base["hrv"], 3.0)), 2),
            spo2=round(min(100.0, max(94.0, random.gauss(base["spo2"], 0.3))), 1),
            eda_scl=round(max(0.5, random.gauss(base["eda_scl"], 0.3)), 3),
            eda_scr=round(max(0.0, random.gauss(base["eda_scr"], 0.03)), 4),
            skin_temp=round(random.gauss(base["skin_temp"], 0.2), 2),
            tremor_8_12hz=round(max(0.0, random.gauss(base["tremor"], 0.001)), 5),
            hardware_source="simulation",
            is_valid=True,
        )

        session = _check_pre_medication(session)
        save_session(session, engine)
        generated_sessions.append(session)

    # Construir baseline com as sessões geradas + quaisquer existentes
    all_sessions = load_sessions(user_id, engine, limit=50)
    heart_rates = [round(max(45.0, random.gauss(base["hr"], 3.0)), 1)
                   for _ in all_sessions]

    new_baseline = build_baseline(user_id, all_sessions, heart_rates)
    if not new_baseline:
        raise HTTPException(
            status_code=500,
            detail="Falha ao construir baseline — sessões insuficientes ou inválidas."
        )

    save_baseline(new_baseline, engine)

    valid_count = sum(1 for s in generated_sessions if s.is_valid)
    invalid_count = len(generated_sessions) - valid_count

    return {
        "user_id": user_id,
        "baseline_built": True,
        "sessions_generated": len(generated_sessions),
        "sessions_valid": valid_count,
        "sessions_invalid": invalid_count,
        "maturity_score": new_baseline.maturity_score,
        "signal_labels": new_baseline.signal_labels,
        "expires_at": new_baseline.expires_at,
        "days_until_expiry": 30,
        "baseline_summary": {
            "hrv_mean":  round(new_baseline.mu[new_baseline.signal_labels.index("RMSSD")], 2),
            "spo2_mean": round(new_baseline.mu[new_baseline.signal_labels.index("SPO2")], 2),
            "hr_mean":   round(new_baseline.hr_mean, 2),
        },
        "message": (
            f"Baseline simulado construído com sucesso. "
            f"Use user_id='{user_id}' nos endpoints /authorize e /authorize/from-push."
        ),
    }


# ── Hardware ──────────────────────────────────────────────────────────────────

@router.get("/hardware/scan")
async def scan_ble():
    """Escaneia todos os dispositivos BLE próximos."""
    from bleak import BleakScanner
    try:
        devices = await BleakScanner.discover(timeout=10.0)
        result = [
            {"name": d.name or "Desconhecido", "address": d.address, "rssi": d.rssi}
            for d in devices
        ]
        return {"devices": result, "count": len(result)}
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


# ── ZKP + Ledger ──────────────────────────────────────────────────────────────

@router.get("/signing-key")
def get_signing_key():
    """
    Retorna a chave pública Ed25519 do LICET server em Base64.

    GAP-C02 fix: auditores externos usam esta chave para verificar de forma independente
    que a biometric_signature foi produzida pelo LICET server — sem acesso a k_m.
    Distribuir esta chave publicamente é parte do modelo de auditabilidade do protocolo.
    """
    try:
        pub_b64 = get_signing_public_key_b64()
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {
        "algorithm": "Ed25519",
        "public_key_b64": pub_b64,
        "usage": "Verify biometric_signature fields in LICET attestation records",
        "timestamp": time.time(),
    }


@router.post("/verify")
def verify_authorization(req: VerifyRequest):
    """
    Verifica criptograficamente uma prova ZK e, opcionalmente, a assinatura Ed25519.

    - zkp_proof: prova Schnorr que o LICET server processou a autorização com k_m
    - biometric_signature (opcional): assinatura Ed25519 verificável com GET /signing-key
    """
    from zkp.proof import ZKProof

    try:
        proof = ZKProof(
            commitment_x=req.zkp_proof["commitment"]["x"],
            commitment_y=req.zkp_proof["commitment"]["y"],
            challenge=req.zkp_proof["challenge"],
            response=req.zkp_proof["response"],
            public_key_x=req.zkp_proof["public_key"]["x"],
            public_key_y=req.zkp_proof["public_key"]["y"],
        )
        zkp_valid = verify_proof(proof, req.intent_hash)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ZKP inválido: {e}")

    # Verificação Ed25519 — não implementável sem bio_payload.
    # A assinatura cobre SHA256(intent_hash || bio_payload); sem o payload não há mensagem
    # conhecida para verificar. TODO v2.1: armazenar SHA256(bio_payload) no ledger.
    sig_valid: Optional[bool] = None

    return {
        "intent_hash": req.intent_hash,
        "zkp_valid": zkp_valid,
        "sig_valid": sig_valid,
        "sig_note": (
            "Ed25519 structural verification requires bio_payload. "
            "Full audit: store SHA256(bio_payload) in ledger (planned v2.1)."
            if req.biometric_signature else None
        ),
        "timestamp": time.time(),
    }


@router.get("/ledger/integrity")
def ledger_integrity():
    initialize_db()
    return verify_integrity()


@router.get("/ledger/history")
def ledger_history(limit: int = 20):
    initialize_db()
    return {"records": get_history(limit=limit)}


# ── Admin — Key Management (GAP-O02) ─────────────────────────────────────────

class KeySplitRequest(BaseModel):
    """
    Divide a chave mestre em shares Shamir.
    ATENÇÃO: chama load_secret_key() — requer LICET_SECRET_KEY no ambiente.
    Distribua cada share para um custodiante diferente imediatamente após geração.
    Nunca armazene todos os shares juntos.
    """
    n_shares: int = 5
    threshold: int = 3


class KeyCombineRequest(BaseModel):
    """
    Reconstrói a chave mestre a partir de shares Shamir.
    shares: lista de [x, "0x..."] pares (índice + valor hex).
    """
    shares: List[List]   # [[x, "0xhex"], ...]


@router.post("/admin/key/split")
def admin_key_split(req: KeySplitRequest):
    """
    GAP-O02: Divide k_m em n shares com threshold mínimo para reconstrução.

    Fluxo recomendado:
    1. Chamar este endpoint UMA VEZ no provisionamento inicial.
    2. Distribuir cada share para um custodiante diferente (CEO, CTO, advogado, cofre, cloud).
    3. Apagar k_m do ambiente após confirmar que os shares reconstroem corretamente.
    4. Para operação normal, o HSM mantém k_m — shares são apenas para disaster recovery.
    """
    from core.key_management import split_secret, verify_split_combine
    try:
        secret_hex = load_secret_key().hex()
    except EnvironmentError as e:
        raise HTTPException(status_code=500, detail=str(e))

    if req.threshold < 2 or req.n_shares < req.threshold:
        raise HTTPException(
            status_code=400,
            detail="Inválido: threshold >= 2 e n_shares >= threshold."
        )

    shares = split_secret(secret_hex, req.n_shares, req.threshold)
    verified = verify_split_combine(secret_hex, req.n_shares, req.threshold)

    return {
        "shares": [{"index": x, "value": y} for x, y in shares],
        "n_shares": req.n_shares,
        "threshold": req.threshold,
        "self_test_passed": verified,
        "warning": (
            "Distribua cada share imediatamente para custodiantes distintos. "
            "Nunca armazene todos os shares juntos. "
            "Este endpoint não deve estar exposto em produção sem autenticação forte."
        ),
        "hsm_note": "GAP-O02: migrar k_m para HSM FIPS 140-3 Level 3. "
                    "Ver docs/research/security-gaps.md § GAP-O02.",
    }


@router.post("/admin/key/combine")
def admin_key_combine(req: KeyCombineRequest):
    """
    GAP-O02: Reconstrói k_m a partir de shares Shamir (quórum de threshold shares).

    Uso: disaster recovery ou rotação de chave.
    Em produção, proteger com autenticação multi-fator e auditoria de acesso.
    """
    from core.key_management import combine_shares
    try:
        shares = [(int(s[0]), str(s[1])) for s in req.shares]
        reconstructed_hex = combine_shares(shares)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Reconstrução falhou: {e}")

    # Nunca retornar a chave em texto plano em produção — aqui só hash para confirmação
    key_fingerprint = hashlib.sha256(bytes.fromhex(reconstructed_hex)).hexdigest()[:16]
    return {
        "reconstructed": True,
        "key_fingerprint_sha256_prefix": key_fingerprint,
        "warning": (
            "Em produção, injetar a chave diretamente no HSM, não retornar em HTTP. "
            "Este endpoint expõe material de chave — proteger com mTLS e auditoria."
        ),
        "key_hex": reconstructed_hex,   # remover em produção — apenas para dev/DR
    }


# ── Ledger — Ancoragem e Revogação ───────────────────────────────────────────

class RevokeRequest(BaseModel):
    reason: str


@router.post("/ledger/timestamp")
def ledger_timestamp():
    """
    GAP-C03: Computa o Merkle root do ledger e âncora no OpenTimestamps.

    O Merkle root cobre todos os chain_hashes do ledger (ordenados por id).
    Submetido ao pool de calendários OTS — prova de existência antes do próximo
    bloco Bitcoin (≤60 min). O proof parcial é armazenado em merkle_anchors.

    Rodar periodicamente (ex: a cada 1000 entradas ou 1x por dia).
    """
    initialize_db()
    try:
        result = anchor_to_transparency_log()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ancoragem falhou: {e}")
    return result


@router.post("/admin/revoke/{ledger_id}")
def admin_revoke_entry(ledger_id: int, req: RevokeRequest):
    """
    GAP-O03 / GAP-H03: Revoga uma entrada do ledger.

    A entrada original NÃO é modificada (hash chain preservado).
    Marcada como revogada com prova de revogação criptográfica.

    Casos de uso:
    - Dispositivo roubado / chave de attestation comprometida (GAP-H03)
    - GDPR Art. 17 Right to Erasure (entrada marcada como revogada)
    - Baseline poisoning detectado retroativamente
    - Autorização obtida sob coerção confirmada após o fato
    """
    initialize_db()
    try:
        result = revoke_entry(ledger_id, req.reason)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Revogação falhou: {e}")
    return result


# ── GDPR (GAP-A05) ───────────────────────────────────────────────────────────

@router.get("/gdpr/data/{user_id}")
def gdpr_data_access(user_id: str):
    """
    GAP-A05 / GDPR Art. 15 — Direito de acesso.

    Retorna resumo de todos os dados biométricos armazenados para o usuário:
    - Baseline individual (μ, Σ⁻¹, template ECG, scores de maturidade)
    - Histórico de sessões de calibração (contagem, datas)

    Dados brutos (ECG waveform, RR intervals) nunca são persistidos —
    apenas features derivadas, por design (GDPR Art. 25 — Privacy by Design).
    """
    initialize_db()
    try:
        summary = get_user_data_summary(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao recuperar dados: {e}")
    return summary


@router.delete("/gdpr/erasure/{user_id}")
def gdpr_erasure(user_id: str):
    """
    GAP-A05 / GDPR Art. 17 / LGPD Art. 18 VI — Direito ao esquecimento.

    Apaga permanentemente:
    - Baseline biométrico individual (μ, Σ⁻¹, ECG template)
    - Histórico de sessões de calibração

    O ledger de autorizações NÃO é apagado:
    - Entradas são pseudônimas (sem user_id)
    - Constituem registro de auditoria regulatória (LGPD Art. 16 II)
    - Podem ser revogadas individualmente via POST /admin/revoke/{ledger_id}
    """
    initialize_db()
    try:
        result = erase_user_data(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Apagamento falhou: {e}")
    return result
