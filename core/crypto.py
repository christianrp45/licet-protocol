"""
LICET — Módulo Criptográfico Core v2
Pipeline completo de autorização: três camadas biométricas + criptografia.

Fluxo de autorização:
  1. Gera Intent Hash (SHA256 da ação)
  2. Camada 1 — ECG morfologia QRS (identidade + vivacidade resistente a medicamentos)
  3. Camada 2 — EDA SCL/SCR (vivacidade simpática colinérgica)
  4. Check farmacológico (toxidrome beta-bloqueador / anticolinérgico / opioide)
  5. Camada 3 — Mahalanobis D² (desvio do baseline individual)
  6. Determina trust level L0–L3
  7. Gera Biometric Signature via HMAC-SHA256 + HKDF
  8. Retorna AuthorizationBundle completo
"""

import os
import time
import hmac
import hashlib
import json
import base64
from dataclasses import dataclass, asdict, field
from typing import Optional, List, TYPE_CHECKING

from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from hardware.sensor_interface import BiometricReading
from core.ecg_layer import evaluate_ecg_layer, ECGLayerResult
from core.eda_layer import evaluate_eda_layer, EDALayerResult
from core.pharmacological_check import check_pharmacological_interference, PharmacologicalCheckResult
from core.mahalanobis import evaluate_mahalanobis_layer, MahalanobisResult
from core.respiratory_periodicity import compute_respiratory_periodicity, RespiratoryPeriodicityResult
from zkp.proof import generate_proof, ZKProof


# ── Chave mestra (k_m) — GAP-O02: migrar para HSM + Shamir ──────────────────

def load_secret_key() -> bytes:
    """
    Carrega k_m (chave mestra para HKDF) do ambiente.

    GAP-O02 (pendente): k_m deve ser armazenado em HSM (AWS CloudHSM / Google HSM /
    YubiHSM) com Shamir Secret Sharing para recuperação de quórum.
    Atualmente em variável de ambiente — adequado apenas para desenvolvimento.
    """
    key_hex = os.getenv("LICET_SECRET_KEY")
    if not key_hex:
        raise EnvironmentError(
            "\n[LICET] LICET_SECRET_KEY não encontrada no ambiente.\n"
            "Execute uma vez para gerar sua chave:\n\n"
            "    python -c \"import secrets; print(secrets.token_hex(32))\"\n\n"
            "Cole o resultado no arquivo .env como:\n"
            "    LICET_SECRET_KEY=<chave_gerada>\n"
        )
    return bytes.fromhex(key_hex)


# ── Chave de assinatura Ed25519 (GAP-C02 fix) ─────────────────────────────────

def load_signing_key() -> Ed25519PrivateKey:
    """
    Carrega a chave privada Ed25519 para assinar attestations biométricas.

    GAP-C02 fix: substitui HMAC-SHA256 (simétrico, não auditável por terceiros)
    por assinatura Ed25519 (assimétrica — qualquer auditor com a chave pública
    pode verificar que o LICET server assinou aquela attestation).

    GAP-O02 (pendente): esta chave também deve migrar para HSM.
    """
    key_hex = os.getenv("LICET_SIGNING_KEY")
    if not key_hex:
        raise EnvironmentError(
            "\n[LICET] LICET_SIGNING_KEY não encontrada no ambiente.\n"
            "Execute uma vez para gerar sua chave Ed25519:\n\n"
            "    python -c \""
            "from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey; "
            "k = Ed25519PrivateKey.generate(); "
            "print(k.private_bytes_raw().hex())\"\n\n"
            "Cole o resultado no arquivo .env como:\n"
            "    LICET_SIGNING_KEY=<chave_gerada>\n"
        )
    return Ed25519PrivateKey.from_private_bytes(bytes.fromhex(key_hex))


def get_signing_public_key_b64() -> str:
    """
    Retorna a chave pública Ed25519 em Base64 (raw, 32 bytes).
    Distribuída aos auditores para verificação independente de attestations.
    """
    key = load_signing_key()
    raw = key.public_key().public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    return base64.b64encode(raw).decode()


# ── Derivação de chave de sessão ──────────────────────────────────────────────

def derive_session_key(master_key: bytes, context: str, salt: Optional[bytes] = None) -> bytes:
    """Deriva chave de sessão única por autorização via HKDF-SHA256.

    CA-06 fix: salt=None usava string vazia como salt (RFC 5869 §2.2), reduzindo
    a entropia efetiva da derivação. Agora recebe salt=SHA256(user_id+timestamp)
    gerado pelo caller (authorize()), único por sessão.
    """
    hkdf = HKDF(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        info=context.encode(),
        backend=default_backend(),
    )
    return hkdf.derive(master_key)


# ── UI Binding (GAP-A04 fix) ──────────────────────────────────────────────────

def compute_action_commitment(action: str, agent_id: str, target: str, nonce: str) -> str:
    """
    SHA256(action | agent_id | target | nonce) — hash de compromisso da ação.

    GAP-A04: O agente AI pode substituir o action descriptor após o usuário ver a UI.
    O cliente (app do usuário, não o agente) gera nonce aleatório, exibe a ação
    ao usuário, computa este commitment ANTES de qualquer coleta biométrica,
    e envia junto ao request.

    O servidor verifica que o commitment confere com (action, agent_id, target, nonce).
    Se o agente alterou qualquer campo, o commitment não bate → denial TAMPERING_DETECTED.

    Segurança completa exige que o commitment seja assinado pela chave do dispositivo
    do usuário (FIDO2/WebAuthn) para que o agente AI não possa gerar um commitment
    válido para uma ação adulterada. Isso é planejado como GAP-A04 v2 (FIDO2 binding).
    """
    payload = f"{action}|{agent_id}|{target}|{nonce}"
    return hashlib.sha256(payload.encode()).hexdigest()


def verify_action_commitment(
    action: str,
    agent_id: str,
    target: str,
    nonce: str,
    commitment: str,
) -> bool:
    """Verifica que o commitment corresponde exatamente aos campos da ação."""
    expected = compute_action_commitment(action, agent_id, target, nonce)
    return hmac.compare_digest(expected, commitment)


# ── Intent Hash ───────────────────────────────────────────────────────────────

def compute_intent_hash(action: str, agent_id: str, target: str, timestamp: float) -> str:
    """
    SHA256 da ação solicitada — único por evento.
    Qualquer alteração nos parâmetros gera hash completamente diferente (anti-replay).
    """
    payload = json.dumps(
        {"action": action, "agent_id": agent_id, "target": target, "timestamp": timestamp},
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


# ── Biometric Signature (GAP-C02 fix — Ed25519) ───────────────────────────────

def compute_biometric_signature(
    intent_hash: str,
    reading: BiometricReading,
    signing_key: Ed25519PrivateKey,
) -> tuple:
    """
    Ed25519(intent_hash ‖ biometrics, signing_key).

    GAP-C02 fix: substitui HMAC-SHA256(session_key, …) por assinatura Ed25519.
    - HMAC é simétrico: apenas o LICET server pode verificar (mesma chave gera e verifica).
    - Ed25519 é assimétrico: auditor com a chave pública verifica sem acesso a k_m.

    CA-09 fix: retorna (signature_b64, message_sha256_hex).
    O hash SHA256(message) é armazenado no ledger — permite que auditores com a chave
    pública Ed25519 verifiquem a assinatura sem reconstituir o payload biométrico completo.

    Auditabilidade: POST /signing-key expõe a chave pública para verificação independente.
    Dados brutos nunca são armazenados — apenas a assinatura e o hash do payload.
    """
    bio_payload = json.dumps(
        {
            "heart_rate": reading.heart_rate,
            "spo2": reading.spo2,
            "hrv": reading.hrv,
            "eda_scl": reading.eda_scl,
            "timestamp": reading.timestamp,
            "duration": reading.duration_seconds,
        },
        sort_keys=True,
    )
    message = f"{intent_hash}:{bio_payload}".encode()
    signature_bytes = signing_key.sign(message)
    payload_hash = hashlib.sha256(message).hexdigest()
    return base64.b64encode(signature_bytes).decode(), payload_hash


# ── Trust Level ───────────────────────────────────────────────────────────────

def _determine_trust_level(
    reading: BiometricReading,
    ecg: ECGLayerResult,
    eda: EDALayerResult,
    pharma: PharmacologicalCheckResult,
    maha: MahalanobisResult,
) -> str:
    """
    L0 — Simulação / sem atestação de hardware
    L1 — Atestação de plataforma (HealthKit / Health Connect / OS-level)
    L2 — Atestação de hardware (Titan M2 / Secure Enclave / Android Key Attestation)
    L3 — Sensor-to-TEE direto (trabalho futuro)
    """
    source = reading.hardware_source.lower()

    if source == "simulation":
        return "L0"

    # L2: hardware com atestação de chave de hardware
    if source in ("pixel_watch_2", "garmin_fenix"):
        return "L2"

    # L1: wearable com atestação de plataforma (HealthKit / Health Connect)
    if source in ("apple_watch", "samsung_watch", "whoop", "polar_h10", "max30102", "ble_generic"):
        return "L1"

    return "L0"


# ── AuthorizationBundle ───────────────────────────────────────────────────────

@dataclass
class AuthorizationBundle:
    """Pacote completo de uma autorização LICET v2."""
    # Identificação do evento
    intent_hash: str
    biometric_signature: str
    timestamp: float
    agent_id: str
    action: str
    target: str

    # Resultado
    authorized: bool
    denial_reason: str

    # Sinais base
    heart_rate: float
    spo2: float
    hrv: float

    # Estado fisiológico
    coercion_risk: str
    cognitive_state: str
    coercion_cost_elevation: str   # "NOMINAL" | "ELEVATED" | "HIGH"

    # Resultados das três camadas
    layer1_ecg: str                # PASS | FAIL | UNAVAILABLE | NO_BASELINE
    layer1_ecg_cosine_sim: Optional[float]
    layer2_eda: str                # PASS | FAIL | UNAVAILABLE
    layer2_eda_scl: Optional[float]
    layer2_eda_scr: Optional[float]
    layer3_mahalanobis_status: str # PASS | FAIL | NO_BASELINE | PARTIAL
    layer3_mahalanobis_d2: Optional[float]

    # Check farmacológico
    pharmacological_check: str     # "CLEAN" | "BETA_BLOCKER" | "ANTICHOLINERGIC" | "OPIOID"
    pharmacological_confidence: str

    # Periodicidade respiratória (análise espectral dos intervalos RR)
    respiratory_periodicity_index: Optional[float]   # None se RR intervals ausentes
    respiratory_periodicity_warning: Optional[str]   # None se IP < limiar ou não avaliado

    # Custo de falsificação por camada — para transparência ao integrador
    # Valores: "VERY_HIGH" | "HIGH" | "MEDIUM" | "LOW" | "NONE"
    # "NONE" significa que a camada não foi avaliada nesta sessão
    layer_forgery_cost: Optional[dict] = None        # {"ecg": ..., "eda": ..., "mahalanobis": ..., "overall": ...}

    # Trust level (L0–L3)
    trust_level: str = "L0"
    baseline_maturity: float = 0.0

    # UI Binding (GAP-A04 fix)
    # "VERIFIED" — commitment presente e válido (cliente construiu, não o agente AI)
    # "ABSENT"   — sem commitment; ação pode ter sido alterada pelo agente AI
    # "FAILED"   — commitment presente mas inválido (tampering detectado — denial obrigatório)
    ui_binding_status: str = "ABSENT"

    # ZKP Schnorr — gerado internamente com session_key como witness (GAP-C01 fix)
    # None apenas em casos de erro interno pré-derivação de chave
    zkp_proof: Optional[ZKProof] = None

    # GAP-B09: aviso de equidade PPG — presente quando threshold_multiplier > 1.0 foi aplicado.
    # Indica que o limiar Mahalanobis foi ampliado por limitação do sensor PPG em pele escura
    # (Fitzpatrick V–VI), para evitar falsos positivos discriminatórios.
    ppg_equity_warning: Optional[str] = None

    # CA-09: SHA256(intent_hash:bio_payload) — hash da mensagem assinada pelo Ed25519.
    # Permite auditores verificar biometric_signature com a chave pública sem acesso a k_m.
    # None em autorizações negadas (sem assinatura Ed25519 gerada).
    bio_payload_hash: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2)


# ── Pipeline principal de autorização ────────────────────────────────────────

def authorize(
    action: str,
    agent_id: str,
    target: str,
    reading: BiometricReading,
    master_key: bytes,
    signing_key: Ed25519PrivateKey,
    # Baseline individual (carregado por api/routes.py via core/baseline.py)
    ecg_baseline_template: Optional[List[float]] = None,
    baseline_mu: Optional[List[float]] = None,
    baseline_sigma_inv: Optional[List[List[float]]] = None,
    baseline_labels: Optional[List[str]] = None,
    baseline_maturity: float = 0.0,
    # Parâmetros individuais para z-scores farmacológicos
    baseline_hr_mean: Optional[float] = None,
    baseline_hr_std: Optional[float] = None,
    baseline_hrv_mean: Optional[float] = None,
    baseline_hrv_std: Optional[float] = None,
    baseline_tremor_mean: Optional[float] = None,
    baseline_tremor_std: Optional[float] = None,
    # UI Binding (GAP-A04 fix) — gerados pelo cliente (app do usuário), não pelo agente AI
    action_commitment: Optional[str] = None,
    action_nonce: Optional[str] = None,
    # GAP-L05 fix: acomodação razoável por medicação prescrita
    # Quando True, padrão BETA_BLOCKER não gera denial — gera "BETA_BLOCKER_ACCOMMODATED".
    # Definido pelo caller (api/routes.py) com base em baseline.chronic_beta_blocker_flag.
    medication_accommodation: bool = False,
) -> AuthorizationBundle:
    """
    Pipeline completo de autorização LICET v2.

    Retorna AuthorizationBundle com resultado de cada camada,
    trust level e assinatura criptográfica.

    GAP-A04: se action_commitment e action_nonce forem fornecidos, o servidor verifica
    que SHA256(action|agent_id|target|nonce) == action_commitment. Se o agente AI
    adulterou qualquer campo após o usuário ver a UI, o commitment falha → denial.
    Se ausentes, autorização prossegue com ui_binding_status="ABSENT" e aviso.
    """
    timestamp   = time.time()
    intent_hash = compute_intent_hash(action, agent_id, target, timestamp)
    # CA-06 fix: salt=SHA256(user_id+timestamp) — único por sessão, aumenta entropia HKDF
    _salt_material = f"{reading.user_id or ''}:{int(timestamp)}".encode()
    _hkdf_salt = hashlib.sha256(_salt_material).digest()
    session_key = derive_session_key(master_key, intent_hash, salt=_hkdf_salt)

    # ── GAP-A04: verificar UI binding antes de qualquer coleta biométrica ────
    if action_commitment is not None and action_nonce is not None:
        if verify_action_commitment(action, agent_id, target, action_nonce, action_commitment):
            _ui_binding_status = "VERIFIED"
        else:
            # Commitment presente mas inválido → tampering detectado → denial imediato
            _ui_binding_status = "FAILED"
    else:
        # Sem commitment — ação pode ter sido construída pelo agente sem supervisão do usuário
        _ui_binding_status = "ABSENT"

    # GAP-C01 fix: ZKP gerado com session_key (derivado de k_m via HKDF) como witness.
    # session_key nunca é armazenado no ledger — não é recalculável por auditores externos.
    zkp_proof = generate_proof(session_key, intent_hash)

    # Determina se o baseline inclui sinais espectrais (HF power) para o forgery cost
    _has_spectral_baseline = bool(
        baseline_labels and "HF_POWER_MS2" in baseline_labels
    )

    # ── GAP-B09: calcular threshold_multiplier por limitação PPG em pele escura ─
    # Executado antes de qualquer denial para que _deny possa referenciar as variáveis.
    # Fontes PPG (LED verde/vermelho): erro de HRV de 30–40% em Fitzpatrick V–VI.
    # Fontes ECG (polar_h10, pixel_watch_2) não são afetadas por tom de pele.
    _PPG_SOURCES = {"apple_watch", "samsung_watch", "whoop", "max30102", "ble_generic", "simulation"}
    _fitz = reading.skin_tone_fitzpatrick
    _is_ppg = reading.hardware_source.lower() in _PPG_SOURCES
    _ppg_equity_applied = bool(_fitz and _fitz >= 5 and _is_ppg)
    _threshold_multiplier = 1.4 if _ppg_equity_applied else 1.0
    _ppg_equity_warning: Optional[str] = (
        f"GAP-B09: Threshold Mahalanobis ampliado ×1.4 (Fitzpatrick {_fitz}, PPG {reading.hardware_source}). "
        "Bent et al. 2020 demonstram erro de HRV de 30–40% em peles Fitzpatrick V–VI com sensores PPG. "
        "Este ajuste evita falsos positivos discriminatórios. Recomendado: sensor ECG (Polar H10 / Pixel Watch 2)."
    ) if _ppg_equity_applied else None

    def _deny(reason: str, ecg: ECGLayerResult, eda: EDALayerResult,
              pharma: PharmacologicalCheckResult, maha: MahalanobisResult,
              trust: str) -> AuthorizationBundle:
        return AuthorizationBundle(
            intent_hash=intent_hash,
            biometric_signature="",
            timestamp=timestamp,
            agent_id=agent_id,
            action=action,
            target=target,
            authorized=False,
            denial_reason=reason,
            heart_rate=reading.heart_rate,
            spo2=reading.spo2,
            hrv=reading.hrv,
            coercion_risk=reading.coercion_risk,
            cognitive_state=reading.cognitive_state,
            coercion_cost_elevation=_coercion_elevation(reading),
            layer1_ecg=ecg.status,
            layer1_ecg_cosine_sim=ecg.cosine_similarity,
            layer2_eda=eda.status,
            layer2_eda_scl=eda.scl,
            layer2_eda_scr=eda.scr,
            layer3_mahalanobis_status=maha.status,
            layer3_mahalanobis_d2=maha.d_squared,
            pharmacological_check=pharma.pattern_detected or "CLEAN",
            pharmacological_confidence=pharma.confidence,
            respiratory_periodicity_index=resp_index,
            respiratory_periodicity_warning=resp_warning,
            layer_forgery_cost=_compute_forgery_cost(
                ecg, eda, maha, baseline_maturity, _has_spectral_baseline
            ),
            trust_level=trust,
            baseline_maturity=baseline_maturity,
            ui_binding_status=_ui_binding_status,
            zkp_proof=zkp_proof,
            ppg_equity_warning=_ppg_equity_warning,
        )

    # ── GAP-A04: denial imediato se commitment presente mas inválido ──────────
    # Tampering detectado antes de qualquer coleta biométrica.
    if _ui_binding_status == "FAILED":
        return AuthorizationBundle(
            intent_hash=intent_hash,
            biometric_signature="",
            timestamp=timestamp,
            agent_id=agent_id,
            action=action,
            target=target,
            authorized=False,
            denial_reason="UI_BINDING_TAMPERING_DETECTED",
            heart_rate=reading.heart_rate,
            spo2=reading.spo2,
            hrv=reading.hrv,
            coercion_risk=reading.coercion_risk,
            cognitive_state=reading.cognitive_state,
            coercion_cost_elevation=_coercion_elevation(reading),
            layer1_ecg="UNAVAILABLE",
            layer1_ecg_cosine_sim=None,
            layer2_eda="UNAVAILABLE",
            layer2_eda_scl=None,
            layer2_eda_scr=None,
            layer3_mahalanobis_status="NO_BASELINE",
            layer3_mahalanobis_d2=None,
            pharmacological_check="CLEAN",
            pharmacological_confidence="LOW",
            respiratory_periodicity_index=None,
            respiratory_periodicity_warning=None,
            layer_forgery_cost=None,
            trust_level="L0",
            baseline_maturity=baseline_maturity,
            ui_binding_status="FAILED",
            zkp_proof=zkp_proof,
        )

    # ── Análise de periodicidade respiratória ────────────────────────────────────
    # IP ≥ 0.80 → bloqueio automático (GAP-B01 mitigado).
    # Paced breathing treinado a ~0.1 Hz produz IP ≥ 0.80 com pico espectral concentrado.
    # Repouso genuíno: IP típico < 0.60, broadband.
    resp_result = compute_respiratory_periodicity(reading.rr_intervals or [])
    resp_index   = resp_result.periodicity_index
    resp_warning = resp_result.reason if resp_result.is_suspicious else None

    if resp_index is not None and resp_index >= 0.80:
        return _deny(
            f"PACED_BREATHING_DETECTED_IP={resp_index:.2f}",
            _empty_ecg(), _empty_eda(), _empty_pharma(), _empty_maha(),
            _determine_trust_level(reading, _empty_ecg(), _empty_eda(), _empty_pharma(), _empty_maha()),
        )

    # GAP-A05: zerar RR intervals brutos após análise espectral
    # rr_intervals contêm padrão cardíaco detalhado — dado biométrico sensível.
    # Após extração de hf_power_ms2 e dominant_freq_hz, os dados brutos são eliminados.
    if reading.privacy_mode:
        reading.rr_intervals = None

    # ── Pré-validação fisiológica básica ─────────────────────────────────────
    _ecg0   = _empty_ecg()
    _eda0   = _empty_eda()
    _pharma0 = _empty_pharma()
    _maha0  = _empty_maha()

    if not reading.is_physiologically_valid:
        return _deny("SINAL_FISIOLOGICO_INVALIDO", _ecg0, _eda0, _pharma0, _maha0, "L0")

    # ── GAP-A05: minimização de dados — zerar campos brutos pós-extração ────────
    # ecg_waveform e rr_intervals são usados apenas para feature extraction.
    # Após as camadas 1 e 3 extraírem o que precisam, os dados brutos são eliminados
    # da memória do servidor para minimizar a superfície de dados biométricos.
    # Controlado por reading.privacy_mode (default True).
    # Importante: esta zeragem ocorre APÓS a análise de periodicidade respiratória
    # (que usa rr_intervals) e ANTES de qualquer serialização ou ledger record.

    # Camada 1 — ECG Morfologia ─────────────────────────────────────────────
    ecg_result = evaluate_ecg_layer(
        ecg_waveform=reading.ecg_waveform,
        ecg_baseline_template=ecg_baseline_template,
    )
    # GAP-A05: após extração da Camada 1, zerar waveform ECG bruto
    if reading.privacy_mode:
        reading.ecg_waveform = None

    if ecg_result.status == "FAIL":
        return _deny("CAMADA1_ECG_MORFOLOGIA_INCOMPATIVEL", ecg_result, _eda0, _pharma0, _maha0,
                     _determine_trust_level(reading, ecg_result, _eda0, _pharma0, _maha0))

    # ── Camada 2 — EDA ────────────────────────────────────────────────────────
    eda_result = evaluate_eda_layer(
        eda_scl=reading.eda_scl,
        eda_scr=reading.eda_scr,
    )
    if eda_result.status == "FAIL":
        return _deny("CAMADA2_EDA_PLANA_ANTICHOLINERGICO", ecg_result, eda_result, _pharma0, _maha0,
                     _determine_trust_level(reading, ecg_result, eda_result, _pharma0, _maha0))

    # ── Check farmacológico ───────────────────────────────────────────────────
    pharma_result = check_pharmacological_interference(
        heart_rate=reading.heart_rate,
        hrv_rmssd=reading.hrv,
        spo2=reading.spo2,
        eda_scl=reading.eda_scl,
        eda_scr=reading.eda_scr,
        skin_temp=reading.skin_temp,
        tremor_8_12hz=reading.tremor_8_12hz,
        baseline_hr_mean=baseline_hr_mean,
        baseline_hr_std=baseline_hr_std,
        baseline_hrv_mean=baseline_hrv_mean,
        baseline_hrv_std=baseline_hrv_std,
        baseline_tremor_mean=baseline_tremor_mean,
        baseline_tremor_std=baseline_tremor_std,
        medication_accommodation=medication_accommodation,
    )
    if not pharma_result.clean and pharma_result.confidence in ("MEDIUM", "HIGH"):
        # Tríade autoincriminante recebe código de negação dedicado —
        # nenhum estado genuíno de calma produz EDA plana + RMSSD abolido + taquicardia.
        denial_code = (
            "ANTICHOLINERGIC_SELF_INCRIMINATING_TRIAD"
            if pharma_result.self_incriminating
            else f"INTERFERENCIA_FARMACOLOGICA_{pharma_result.pattern_detected}"
        )
        return _deny(
            denial_code,
            ecg_result, eda_result, pharma_result, _maha0,
            _determine_trust_level(reading, ecg_result, eda_result, pharma_result, _maha0),
        )

    # ── Camada 3 — Mahalanobis ────────────────────────────────────────────────
    maha_result = evaluate_mahalanobis_layer(
        hrv_rmssd=reading.hrv,
        spo2=reading.spo2,
        eda_scl=reading.eda_scl,
        eda_scr=reading.eda_scr,
        skin_temp_delta=None,   # ΔTemp calculado pela Camada 3 quando baseline disponível
        tremor_8_12hz=reading.tremor_8_12hz,
        # Sinais espectrais do HRV — enriquecem o baseline individual com comportamento espectral
        hf_power_ms2=resp_result.hf_power_ms2,
        peak_freq_hz=resp_result.dominant_freq_hz,
        baseline_mu=baseline_mu,
        baseline_sigma_inv=baseline_sigma_inv,
        baseline_labels=baseline_labels,
        threshold_multiplier=_threshold_multiplier,
        ppg_equity_applied=_ppg_equity_applied,
    )
    if maha_result.status == "FAIL":
        return _deny("CAMADA3_DESVIO_BASELINE_INDIVIDUAL", ecg_result, eda_result, pharma_result, maha_result,
                     _determine_trust_level(reading, ecg_result, eda_result, pharma_result, maha_result))

    # ── Verificação de coerção legada (compatibilidade com L0) ───────────────
    if reading.coercion_risk == "HIGH":
        return _deny("RISCO_COERCAO_DETECTADO", ecg_result, eda_result, pharma_result, maha_result,
                     _determine_trust_level(reading, ecg_result, eda_result, pharma_result, maha_result))

    if reading.cognitive_state == "IMPAIRED":
        return _deny("ESTADO_COGNITIVO_COMPROMETIDO", ecg_result, eda_result, pharma_result, maha_result,
                     _determine_trust_level(reading, ecg_result, eda_result, pharma_result, maha_result))

    # ── Tudo passou — gerar assinatura Ed25519 (GAP-C02 fix) ─────────────────
    trust_level = _determine_trust_level(reading, ecg_result, eda_result, pharma_result, maha_result)
    # CA-09: compute_biometric_signature agora retorna (signature, payload_hash)
    signature, bio_payload_hash = compute_biometric_signature(intent_hash, reading, signing_key)

    return AuthorizationBundle(
        intent_hash=intent_hash,
        biometric_signature=signature,
        timestamp=timestamp,
        agent_id=agent_id,
        action=action,
        target=target,
        authorized=True,
        denial_reason="",
        heart_rate=reading.heart_rate,
        spo2=reading.spo2,
        hrv=reading.hrv,
        coercion_risk=reading.coercion_risk,
        cognitive_state=reading.cognitive_state,
        coercion_cost_elevation=_coercion_elevation(reading),
        layer1_ecg=ecg_result.status,
        layer1_ecg_cosine_sim=ecg_result.cosine_similarity,
        layer2_eda=eda_result.status,
        layer2_eda_scl=eda_result.scl,
        layer2_eda_scr=eda_result.scr,
        layer3_mahalanobis_status=maha_result.status,
        layer3_mahalanobis_d2=maha_result.d_squared,
        pharmacological_check=pharma_result.pattern_detected or "CLEAN",
        pharmacological_confidence=pharma_result.confidence,
        respiratory_periodicity_index=resp_index,
        respiratory_periodicity_warning=resp_warning,
        layer_forgery_cost=_compute_forgery_cost(
            ecg_result, eda_result, maha_result, baseline_maturity, _has_spectral_baseline
        ),
        trust_level=trust_level,
        baseline_maturity=baseline_maturity,
        ui_binding_status=_ui_binding_status,
        zkp_proof=zkp_proof,
        ppg_equity_warning=_ppg_equity_warning,
        bio_payload_hash=bio_payload_hash,
    )


# ── Custo de falsificação por camada ─────────────────────────────────────────

_FORGERY_ORDER = ["NONE", "LOW", "MEDIUM", "HIGH", "VERY_HIGH"]


def _compute_forgery_cost(
    ecg: "ECGLayerResult",
    eda: "EDALayerResult",
    maha: "MahalanobisResult",
    baseline_maturity: float,
    has_spectral_baseline: bool,
) -> dict:
    """
    Estima o custo adversarial de falsificar cada camada biométrica do LICET.

    Esta estimativa é QUALITATIVA e destinada a comunicar transparência ao integrador.
    Não substitui análise formal de segurança.

    Escala:
      VERY_HIGH — exige conhecimento profundo de fisiologia + hardware especializado
                  (ex: replay de ECG com template calibrado + inibidor farmacológico seletivo)
      HIGH      — difícil sem equipamento especializado
      MEDIUM    — possível com treinamento biofeedback ou fármaco acessível
      LOW       — acessível a um adversário motivado sem conhecimento técnico especial
      NONE      — camada não avaliada nesta sessão
    """
    # ── ECG (Camada 1) ────────────────────────────────────────────────────────
    if ecg.status == "UNAVAILABLE":
        ecg_cost = "NONE"
    elif ecg.cosine_similarity is not None:
        # Template calibrado disponível — falsificação requer ECG morfologicamente idêntico
        ecg_cost = "VERY_HIGH"
    else:
        # Verificação de vivacidade sem template — apenas anomalias grosseiras detectadas
        ecg_cost = "HIGH"

    # ── EDA (Camada 2) ────────────────────────────────────────────────────────
    if eda.status == "UNAVAILABLE":
        eda_cost = "NONE"
    elif eda.scr is not None and eda.scl is not None:
        # SCL + SCR: biofeedback treinado pode elevar SCL; anticolinérgicos suprimem
        # Custo moderado — acessível com preparação farmacológica específica
        eda_cost = "MEDIUM"
    else:
        eda_cost = "LOW"

    # ── Mahalanobis (Camada 3) ────────────────────────────────────────────────
    if maha.status == "NO_BASELINE":
        maha_cost = "LOW"         # Apenas médias populacionais — fácil de satisfazer
    elif maha.status in ("PASS", "PARTIAL"):
        if baseline_maturity >= 0.8 and has_spectral_baseline:
            # Baseline maduro com HF power — paced breathing desloca HF power do baseline
            maha_cost = "HIGH"
        elif baseline_maturity >= 0.4:
            maha_cost = "MEDIUM"
        else:
            maha_cost = "LOW"
    else:
        maha_cost = "LOW"

    # ── Overall — limitado pela camada mais fraca avaliada ───────────────────
    assessed = [c for c in (ecg_cost, eda_cost, maha_cost) if c != "NONE"]
    if not assessed:
        overall = "NONE"
    else:
        overall = min(assessed, key=lambda c: _FORGERY_ORDER.index(c))

    return {
        "ecg":          ecg_cost,
        "eda":          eda_cost,
        "mahalanobis":  maha_cost,
        "overall":      overall,
        "note": (
            "Qualitative estimate for integrator transparency. "
            "Primary unmitigated attack: resonance-frequency breathing collapses "
            "Mahalanobis D² without pharmacological or ECG anomaly."
        ),
    }


# ── Utilitários internos ──────────────────────────────────────────────────────

def _coercion_elevation(reading: BiometricReading) -> str:
    if reading.coercion_risk == "HIGH":
        return "HIGH"
    if reading.coercion_risk == "MEDIUM":
        return "ELEVATED"
    return "NOMINAL"


def _empty_ecg() -> ECGLayerResult:
    from core.ecg_layer import ECGLayerResult
    return ECGLayerResult(status="UNAVAILABLE", cosine_similarity=None,
                          threshold=0.85, reason="Não avaliado")


def _empty_eda() -> EDALayerResult:
    from core.eda_layer import EDALayerResult
    return EDALayerResult(status="UNAVAILABLE", scl=None, scr=None, reason="Não avaliado")


def _empty_pharma() -> PharmacologicalCheckResult:
    from core.pharmacological_check import PharmacologicalCheckResult
    return PharmacologicalCheckResult(clean=True, pattern_detected=None,
                                      confidence="LOW", signals_evaluated=0, reason="Não avaliado")


def _empty_maha() -> MahalanobisResult:
    from core.mahalanobis import MahalanobisResult
    return MahalanobisResult(status="NO_BASELINE", d_squared=None, threshold=5.99,
                             signals_used=[], n_signals=0, reason="Não avaliado")
