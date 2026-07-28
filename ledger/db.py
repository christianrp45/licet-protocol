"""
LICET — Ledger Persistente v2
Registro imutável de todas as autorizações + tabelas de baseline individual.

Hash-chained: cada registro contém o hash do anterior,
tornando adulteração retroativa matematicamente detectável.

Tabelas:
  authorizations    — registro imutável de cada autorização
  user_baselines    — baseline individual de cada usuário (≥5 sessões)
  biometric_history — histórico de sessões de calibração (30 dias, purge automático)

Suporta SQLite (desenvolvimento) e PostgreSQL (produção).
Configurar via DATABASE_URL:
  SQLite:     sqlite:///licet_ledger.db   (padrão)
  PostgreSQL: postgresql://user:pass@host/dbname
"""

import hashlib
import json
import os
import secrets

from sqlalchemy import (
    create_engine, text, Column, Integer, Float, Boolean,
    String, Text, MetaData, Table
)
from sqlalchemy.pool import StaticPool

from core.crypto import AuthorizationBundle


# ── Conexão ───────────────────────────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///licet_ledger.db")

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL)

metadata = MetaData()


# ── Tabela: autorizações (ledger imutável) ────────────────────────────────────

authorizations = Table(
    "authorizations", metadata,
    Column("id",                        Integer, primary_key=True, autoincrement=True),
    Column("intent_hash",               String,  nullable=False),
    Column("bio_signature",             String,  nullable=False),
    Column("heart_rate",                Float),
    Column("spo2",                      Float),
    Column("hrv",                       Float),
    Column("coercion_risk",             String),
    Column("cognitive_state",           String),
    Column("coercion_cost_elevation",   String),
    Column("authorized",                Boolean, nullable=False),
    Column("denial_reason",             String),
    Column("agent_id",                  String,  nullable=False),
    Column("action",                    String,  nullable=False),
    Column("target",                    String,  nullable=False),
    Column("timestamp",                 Float,   nullable=False),
    # Camada 1 — ECG
    Column("layer1_ecg",                String),
    Column("layer1_ecg_cosine_sim",     Float),
    # Camada 2 — EDA
    Column("layer2_eda",                String),
    Column("layer2_eda_scl",            Float),
    Column("layer2_eda_scr",            Float),
    # Camada 3 — Mahalanobis
    Column("layer3_mahalanobis_status", String),
    Column("layer3_mahalanobis_d2",     Float),
    # Farmacológico
    Column("pharmacological_check",     String),
    Column("pharmacological_confidence",String),
    # Trust level
    Column("trust_level",               String),
    Column("baseline_maturity",         Float),
    # Hash chain
    Column("chain_hash",                String,  nullable=False),
    # GAP-C04: nonce gerado pelo servidor no momento do registro
    # Impede reescrita retroativa de timestamps sem quebrar o hash chain
    Column("server_nonce",              String),
    # GAP-A04: status do UI binding registrado no ledger
    Column("ui_binding_status",         String),
    # Revogação (GAP-O03 / GAP-H03): marcador de entrada revogada
    Column("revoked",                   Boolean, default=False),
    Column("revocation_reason",         String),
    Column("revoked_at",                Float),
    # CA-09: hash SHA256 da mensagem assinada pelo Ed25519 (intent_hash:bio_payload).
    # Permite auditores verificarem biometric_signature com a chave pública sem k_m.
    Column("bio_payload_hash",          String),
)


# ── Tabela: âncoras de transparência (GAP-C03) ───────────────────────────────

merkle_anchors = Table(
    "merkle_anchors", metadata,
    Column("id",                Integer, primary_key=True, autoincrement=True),
    Column("created_at",        Float,   nullable=False),
    Column("ledger_entry_from", Integer, nullable=False),  # primeiro id coberto
    Column("ledger_entry_to",   Integer, nullable=False),  # último id coberto
    Column("merkle_root",       String,  nullable=False),
    Column("calendars_used",    Text),    # JSON: ["url", ...]
    Column("calendar_proofs",   Text),    # JSON: ["hex", ...]
    Column("submitted",         Boolean, nullable=False),
    Column("errors",            Text),    # JSON: ["erro", ...]
)


# ── Tabela: revogações (GAP-O03 / GAP-H03) ────────────────────────────────────

revocations = Table(
    "revocations", metadata,
    Column("id",              Integer, primary_key=True, autoincrement=True),
    Column("ledger_id",       Integer, nullable=False, index=True),
    Column("revoked_at",      Float,   nullable=False),
    Column("reason",          String,  nullable=False),
    # Prova de revogação: chain hash da entry de revogação (não quebra o hash chain original)
    Column("revocation_hash", String,  nullable=False),
)


# ── Tabela: baselines individuais ─────────────────────────────────────────────

user_baselines = Table(
    "user_baselines", metadata,
    Column("id",               Integer, primary_key=True, autoincrement=True),
    Column("user_id",          String,  nullable=False, index=True),
    Column("created_at",       Float,   nullable=False),
    Column("expires_at",       Float,   nullable=False),
    Column("session_count",    Integer),
    Column("maturity_score",   Float),
    # Vetores serializados como JSON
    Column("signal_labels",    Text),    # JSON: ["RMSSD", "SPO2", ...]
    Column("mu",               Text),    # JSON: [float, ...]
    Column("sigma_inv",        Text),    # JSON: [[float, ...], ...]
    # Parâmetros para z-scores farmacológicos
    Column("hr_mean",          Float),
    Column("hr_std",           Float),
    Column("hrv_mean",         Float),
    Column("hrv_std",          Float),
    Column("tremor_mean",      Float),
    Column("tremor_std",       Float),
    # Template ECG (opcional — None se sem hardware ECG)
    Column("ecg_template",              Text),    # JSON: [float, ...] | None
    Column("chronic_beta_blocker_flag", Boolean, default=False),
)


# ── Tabela: histórico de sessões de calibração ────────────────────────────────

biometric_history = Table(
    "biometric_history", metadata,
    Column("id",                   Integer, primary_key=True, autoincrement=True),
    Column("user_id",              String,  nullable=False, index=True),
    Column("timestamp",            Float,   nullable=False),
    Column("duration_seconds",     Integer),
    Column("hrv_rmssd",            Float),
    Column("spo2",                 Float),
    Column("eda_scl",              Float),
    Column("eda_scr",              Float),
    Column("skin_temp",            Float),
    Column("tremor_8_12hz",        Float),
    Column("hardware_source",      String),
    Column("is_valid",                  Boolean),
    Column("invalidation_reason",       String),
    Column("on_chronic_beta_blocker",   Boolean, default=False),
    Column("hf_power_ms2",              Float),
    Column("peak_freq_hz",              Float),
)


# ── Inicialização ─────────────────────────────────────────────────────────────

def initialize_db():
    """Cria todas as tabelas se não existirem e aplica migrações incrementais."""
    metadata.create_all(engine)
    _migrate_columns()


def _migrate_columns():
    """Adiciona colunas incrementais em DBs existentes (idempotente)."""
    migrations = [
        # Colunas históricas
        ("biometric_history", "on_chronic_beta_blocker",   "BOOLEAN DEFAULT 0"),
        ("user_baselines",    "chronic_beta_blocker_flag", "BOOLEAN DEFAULT 0"),
        ("biometric_history", "hf_power_ms2",              "REAL"),
        ("biometric_history", "peak_freq_hz",              "REAL"),
        # GAP-C04: nonce de servidor por entrada
        ("authorizations",    "server_nonce",              "TEXT"),
        # GAP-A04: status de UI binding
        ("authorizations",    "ui_binding_status",         "TEXT"),
        # GAP-O03: campos de revogação
        ("authorizations",    "revoked",                   "BOOLEAN DEFAULT 0"),
        ("authorizations",    "revocation_reason",         "TEXT"),
        ("authorizations",    "revoked_at",                "REAL"),
        # CA-09: hash do payload assinado para auditoria Ed25519
        ("authorizations",    "bio_payload_hash",          "TEXT"),
    ]
    with engine.begin() as conn:
        for table, column, coldef in migrations:
            try:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {column} {coldef}"))
            except Exception:
                pass  # Coluna já existe


# ── Hash chain ────────────────────────────────────────────────────────────────

def _get_last_chain_hash() -> str:
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT chain_hash FROM authorizations ORDER BY id DESC LIMIT 1")
        ).fetchone()
        return row[0] if row else "GENESIS"


def _compute_chain_hash(bundle: AuthorizationBundle, prev_hash: str, server_nonce: str) -> str:
    """
    Hash da cadeia: SHA256(entry || prev_hash || server_nonce).

    GAP-C04 fix: server_nonce é gerado pelo servidor em `record()` usando
    secrets.token_hex(16). Impede que um servidor comprometido reescreva
    timestamps retroativamente sem quebrar a cadeia — o nonce é irretratável
    pois está registrado no DB junto com a entrada.
    """
    content = json.dumps(
        {
            "intent_hash":     bundle.intent_hash,
            "bio_signature":   bundle.biometric_signature,
            "bio_payload_hash": bundle.bio_payload_hash,   # CA-09: hash do payload assinado
            "authorized":      bundle.authorized,
            "timestamp":       bundle.timestamp,
            "trust_level":     bundle.trust_level,
            "server_nonce":    server_nonce,
            "prev":            prev_hash,
        },
        sort_keys=True,
    )
    return hashlib.sha256(content.encode()).hexdigest()


# ── Operações do ledger ───────────────────────────────────────────────────────

def record(bundle: AuthorizationBundle) -> int:
    """
    Persiste uma autorização no ledger e retorna o ID do registro.

    GAP-C04: gera server_nonce via secrets.token_hex(16) neste momento.
    O nonce é incluído no chain_hash, tornando reescrita retroativa detectável.
    """
    initialize_db()
    server_nonce = secrets.token_hex(16)
    prev_hash    = _get_last_chain_hash()
    chain_hash   = _compute_chain_hash(bundle, prev_hash, server_nonce)

    with engine.begin() as conn:
        result = conn.execute(
            authorizations.insert().values(
                intent_hash=bundle.intent_hash,
                bio_signature=bundle.biometric_signature,
                heart_rate=bundle.heart_rate,
                spo2=bundle.spo2,
                hrv=bundle.hrv,
                coercion_risk=bundle.coercion_risk,
                cognitive_state=bundle.cognitive_state,
                coercion_cost_elevation=bundle.coercion_cost_elevation,
                authorized=bundle.authorized,
                denial_reason=bundle.denial_reason,
                agent_id=bundle.agent_id,
                action=bundle.action,
                target=bundle.target,
                timestamp=bundle.timestamp,
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
                chain_hash=chain_hash,
                server_nonce=server_nonce,
                ui_binding_status=bundle.ui_binding_status,
                bio_payload_hash=bundle.bio_payload_hash,
            )
        )
        return result.inserted_primary_key[0]


def verify_integrity() -> dict:
    """
    Verifica integridade do ledger recalculando toda a cadeia de hashes.

    GAP-C04: inclui server_nonce na verificação do chain_hash.
    GAP-O03: informa entradas revogadas mas não as exclui do hash chain
    (revogação é aditiva — entrada de revogação é adicionada, não modifica original).
    """
    initialize_db()
    with engine.connect() as conn:
        rows = conn.execute(
            authorizations.select().order_by(authorizations.c.id)
        ).fetchall()

    if not rows:
        return {"status": "EMPTY", "records": 0, "tampered": False}

    prev_hash   = "GENESIS"
    revoked_ids = set()
    n_revoked   = 0
    for row in rows:
        bundle = AuthorizationBundle(
            intent_hash=row.intent_hash,
            biometric_signature=row.bio_signature,
            timestamp=row.timestamp,
            agent_id=row.agent_id,
            action=row.action,
            target=row.target,
            authorized=bool(row.authorized),
            denial_reason=row.denial_reason or "",
            heart_rate=row.heart_rate,
            spo2=row.spo2,
            hrv=row.hrv,
            coercion_risk=row.coercion_risk or "LOW",
            cognitive_state=row.cognitive_state or "NORMAL",
            coercion_cost_elevation=row.coercion_cost_elevation or "NOMINAL",
            layer1_ecg=row.layer1_ecg or "UNAVAILABLE",
            layer1_ecg_cosine_sim=row.layer1_ecg_cosine_sim,
            layer2_eda=row.layer2_eda or "UNAVAILABLE",
            layer2_eda_scl=row.layer2_eda_scl,
            layer2_eda_scr=row.layer2_eda_scr,
            layer3_mahalanobis_status=row.layer3_mahalanobis_status or "NO_BASELINE",
            layer3_mahalanobis_d2=row.layer3_mahalanobis_d2,
            pharmacological_check=row.pharmacological_check or "CLEAN",
            pharmacological_confidence=row.pharmacological_confidence or "LOW",
            trust_level=row.trust_level or "L0",
            baseline_maturity=row.baseline_maturity or 0.0,
            ui_binding_status=getattr(row, "ui_binding_status", None) or "ABSENT",
            respiratory_periodicity_index=getattr(row, "respiratory_periodicity_index", None),
            respiratory_periodicity_warning=getattr(row, "respiratory_periodicity_warning", None),
        )
        # GAP-C04: usar server_nonce armazenado (None para entradas antigas)
        nonce = getattr(row, "server_nonce", None) or ""
        expected = _compute_chain_hash(bundle, prev_hash, nonce)
        if expected != row.chain_hash:
            return {
                "status": "TAMPERED",
                "records": len(rows),
                "tampered": True,
                "tampered_at_id": row.id,
            }
        if getattr(row, "revoked", False):
            n_revoked += 1
            revoked_ids.add(row.id)
        prev_hash = row.chain_hash

    return {
        "status": "INTACT",
        "records": len(rows),
        "tampered": False,
        "revoked_count": n_revoked,
        "revoked_ids": sorted(revoked_ids),
    }


def revoke_entry(ledger_id: int, reason: str) -> dict:
    """
    GAP-O03 / GAP-H03: Revoga uma entrada do ledger.

    Revogação é ADITIVA — não modifica nem remove a entrada original (que preserva
    o hash chain). Marca a entrada como revogada e registra em `revocations`.
    O ledger permanece verificável por auditores; a entrada revogada é distinguível.

    Casos de uso:
    - Dispositivo comprometido (GAP-H03)
    - Right to erasure GDPR Art. 17 (marca como revogada; dados ficam no hash chain
      para auditoria mas são marcados como inválidos para reprocessamento)
    - Baseline poisoning detectado retroativamente
    - Chave mestre comprometida
    """
    initialize_db()
    import time as _time

    with engine.begin() as conn:
        # Verificar que a entrada existe
        row = conn.execute(
            text("SELECT id, chain_hash, revoked FROM authorizations WHERE id = :id"),
            {"id": ledger_id}
        ).fetchone()
        if not row:
            raise ValueError(f"Ledger entry {ledger_id} não encontrada")
        if row.revoked:
            raise ValueError(f"Ledger entry {ledger_id} já está revogada")

        revoked_at = _time.time()

        # Proof de revogação: hash(ledger_id || reason || revoked_at || original_chain_hash)
        revocation_content = json.dumps({
            "ledger_id":          ledger_id,
            "reason":             reason,
            "revoked_at":         revoked_at,
            "original_chain_hash": row.chain_hash,
        }, sort_keys=True)
        revocation_hash = hashlib.sha256(revocation_content.encode()).hexdigest()

        # Marcar entrada como revogada (não apaga dados — preserva hash chain)
        conn.execute(
            text(
                "UPDATE authorizations SET revoked=1, revocation_reason=:reason, "
                "revoked_at=:revoked_at WHERE id=:id"
            ),
            {"reason": reason, "revoked_at": revoked_at, "id": ledger_id}
        )

        # Registrar na tabela de revogações
        conn.execute(
            revocations.insert().values(
                ledger_id=ledger_id,
                revoked_at=revoked_at,
                reason=reason,
                revocation_hash=revocation_hash,
            )
        )

    return {
        "revoked": True,
        "ledger_id": ledger_id,
        "revocation_hash": revocation_hash,
        "revoked_at": revoked_at,
        "note": (
            "Entrada marcada como revogada. Hash chain original preservado — "
            "integridade histórica mantida. Auditores veem a revogação explicitamente."
        ),
    }


def anchor_to_transparency_log() -> dict:
    """
    GAP-C03: Computa Merkle root do ledger e submete ao OpenTimestamps.
    Armazena prova em merkle_anchors.
    """
    from ledger.transparency import compute_merkle_root, submit_to_opentimestamps
    import time as _time

    initialize_db()
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT id, chain_hash FROM authorizations ORDER BY id")
        ).fetchall()

    if not rows:
        return {"status": "EMPTY", "message": "Ledger vazio — nada a ancorar"}

    chain_hashes = [row.chain_hash for row in rows]
    first_id     = rows[0].id
    last_id      = rows[-1].id

    merkle_root = compute_merkle_root(chain_hashes)
    ots_result  = submit_to_opentimestamps(merkle_root)

    with engine.begin() as conn:
        result = conn.execute(
            merkle_anchors.insert().values(
                created_at=_time.time(),
                ledger_entry_from=first_id,
                ledger_entry_to=last_id,
                merkle_root=merkle_root,
                calendars_used=json.dumps(ots_result["calendars_used"]),
                calendar_proofs=json.dumps(ots_result["calendar_proofs"]),
                submitted=ots_result["submitted"],
                errors=json.dumps(ots_result["errors"]),
            )
        )
        anchor_id = result.inserted_primary_key[0]

    return {
        "anchor_id":       anchor_id,
        "merkle_root":     merkle_root,
        "entries_covered": len(chain_hashes),
        "ledger_id_range": [first_id, last_id],
        "submitted":       ots_result["submitted"],
        "calendars_used":  ots_result["calendars_used"],
        "errors":          ots_result["errors"],
        "upgrade_note":    ots_result["upgrade_note"],
    }


def get_history(limit: int = 50) -> list:
    """Retorna os últimos N registros do ledger."""
    initialize_db()
    with engine.connect() as conn:
        rows = conn.execute(
            authorizations.select()
            .order_by(authorizations.c.id.desc())
            .limit(limit)
        ).fetchall()
    return [row._asdict() for row in rows]


# ── GDPR (GAP-A05) ───────────────────────────────────────────────────────────

def get_user_data_summary(user_id: str) -> dict:
    """
    GAP-A05: Retorna resumo de todos os dados armazenados para um usuário.
    GDPR Art. 15 — direito de acesso.

    Não retorna dados brutos (ecg_waveform, rr_intervals — nunca armazenados no ledger).
    Retorna metadados de calibração + contagem de entradas do ledger.
    """
    initialize_db()

    with engine.connect() as conn:
        # Baseline
        bl_row = conn.execute(
            text("SELECT id, created_at, expires_at, session_count, maturity_score, "
                 "signal_labels FROM user_baselines WHERE user_id = :uid ORDER BY id DESC LIMIT 1"),
            {"uid": user_id}
        ).fetchone()

        # Sessões de calibração
        sessions = conn.execute(
            text("SELECT COUNT(*) as n, MIN(timestamp) as first_ts, MAX(timestamp) as last_ts "
                 "FROM biometric_history WHERE user_id = :uid"),
            {"uid": user_id}
        ).fetchone()

        # Entradas do ledger com este user_id (via agent_id não é adequado —
        # o ledger não armazena user_id diretamente por privacidade)
        ledger_count = 0  # Por design, user_id não é armazenado no ledger

    baseline_info = None
    if bl_row:
        baseline_info = {
            "baseline_id":    bl_row.id,
            "created_at":     bl_row.created_at,
            "expires_at":     bl_row.expires_at,
            "session_count":  bl_row.session_count,
            "maturity_score": bl_row.maturity_score,
            "signal_labels":  json.loads(bl_row.signal_labels) if bl_row.signal_labels else [],
        }

    return {
        "user_id":           user_id,
        "data_categories": [
            "baseline_model (μ, Σ⁻¹, ECG template)",
            "biometric_history (sessões de calibração — HRV, SpO2, EDA, temp, tremor)",
        ],
        "baseline":          baseline_info,
        "calibration_sessions": {
            "count":    sessions.n if sessions else 0,
            "first_at": sessions.first_ts if sessions else None,
            "last_at":  sessions.last_ts if sessions else None,
        },
        "ledger_entries":    ledger_count,
        "note": (
            "Dados brutos (ECG waveform, RR intervals) nunca são persistidos no servidor — "
            "apenas features derivadas (HRV RMSSD, HF power). GDPR Art. 25 — privacy by design."
        ),
    }


def erase_user_data(user_id: str) -> dict:
    """
    GAP-A05: Apaga todos os dados biométricos de um usuário.
    GDPR Art. 17 — direito ao esquecimento.

    Ações tomadas (em ordem):
    1. Apaga baseline (μ, Σ⁻¹, ECG template)
    2. Apaga histórico de sessões de calibração
    3. Ledger de autorizações: user_id nunca é armazenado por design —
       entradas de autorização são pseudônimas (intent_hash, agent_id).
       Não há entradas de ledger vinculadas a user_id para apagar.

    Nota de compliance:
    O ledger de autorizações é um registro de auditoria imutável para fins
    regulatórios (Lei Geral das Proteções de Dados Art. 16 II — guarda por
    obrigação legal). Entradas do ledger são pseudônimas e não contêm dados
    biométricos brutos. Elas podem ser revogadas (GAP-O03) mas não apagadas
    sem quebrar o hash chain (que seria um obstáculo à auditoria regulatória).
    """
    initialize_db()
    import time as _time

    deleted = {
        "baseline_rows":           0,
        "biometric_history_rows":  0,
    }

    with engine.begin() as conn:
        # 1. Apagar baseline
        result = conn.execute(
            text("DELETE FROM user_baselines WHERE user_id = :uid"),
            {"uid": user_id}
        )
        deleted["baseline_rows"] = result.rowcount

        # 2. Apagar sessões de calibração
        result = conn.execute(
            text("DELETE FROM biometric_history WHERE user_id = :uid"),
            {"uid": user_id}
        )
        deleted["biometric_history_rows"] = result.rowcount

    return {
        "user_id":    user_id,
        "erased_at":  _time.time(),
        "deleted":    deleted,
        "ledger_note": (
            "Entradas do ledger de autorizações são pseudônimas (sem user_id) e "
            "constituem registro de auditoria regulatória (LGPD Art. 16 II). "
            "Não foram apagadas. Podem ser revogadas individualmente via "
            "POST /admin/revoke/{ledger_id} se necessário."
        ),
        "gdpr_basis": "LGPD Art. 17 / GDPR Art. 17 — Right to Erasure",
    }
