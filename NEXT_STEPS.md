---
updatedAt: 2026-08-01
---

# LICET — Próximos Passos

## ✅ CONCLUÍDO até 01/08/2026

### Backend / Segurança
- **CA-01** ✅ `verify_admin_token()` com `hmac.compare_digest()`
- **CA-02** ✅ `key_hex` removido do response
- **CA-03** ✅ `rr_intervals` obrigatório para `source != "simulation"`
- **CA-04** ✅ HMAC v3 cobre todos os campos críticos
- **CA-05** ✅ Rate limiting via `SlowAPIMiddleware`
- **CA-06** ✅ HKDF salt = `SHA256(user_id + timestamp)` por sessão
- **CA-07** ✅ Floats HMAC com `Locale.US` no Android (fix 401 pt-BR)
- **CA-09** ✅ `bio_payload_hash` no ledger
- **V2 bug** ✅ Tríade anticolinérgica corrigida (`EDA_SCL is not None` gate)
- **Threshold IP individual** ✅ `mean + 2σ` do baseline por usuário (floor=0.80)
- **Cloud SQL** ✅ Baseline persistente entre deploys (PostgreSQL 15, us-central1-a)
- **Floor RMSSD=100ms²** ✅ GAP-B10 ×1.3 aplicados — validados Ledger #60

### Android App (`licet-android/`)
- **Dashboard** ✅ Métricas LICET em tempo real (`trust_level`, `IP`, `D²`, `forgery_cost`)
- **Settings screen** ✅ Provisionar `LICET_MOBILE_APP_SECRET` via EncryptedSharedPreferences
- **Health Connect** ✅ Fallback 7 dias para SpO₂/HRV (Watch 6 mede pontualmente)
- **Fix IP falso positivo** ✅ `rrIntervals = emptyList()` — elimina PACED_BREATHING_DETECTED espúrio
- **Fix block pós-emptyList** ✅ Removido gate `rrIntervals.size < 60` no DashboardViewModel
- **Fix µ_RMSSD drift** ✅ `importHistory` usa janelas 24h + HRV rolling 7 dias (sem fallback fixo)
- **Filtro canônico** ✅ `activityLevel <= 2`, `hrv >= 10.0` em recalibração
- **Opção B aprovada** ✅ Ledger #69 AUTORIZADO — Watch 6 real, HRV=9.24ms, D²=4.2169

### Publicações
- **Zenodo** ✅ DOI 10.5281/zenodo.21345045 (v2.0, CC BY 4.0)
- **IACR ePrint** ✅ 2026/110546 (13/07/2026)
- **SSRN** ✅ Abstract ID 7018458
- **MDPI Cryptography** ✅ Submetido (aguardando revisão)
- **IETF draft** ✅ draft-pereira-licet-human-intent-01

---

## EM ANDAMENTO — Maturidade do baseline (Layer 3)

Baseline zerado em 01/08/2026 (erasure após contamination µ≈45ms).
`BaselineCollectionService` está coletando sessões passivamente via `captureReading(180)`.

| Meta | Status |
|------|--------|
| 5 sessões | Coleta passiva em andamento |
| maturity=0.4 | Aguardando |
| maturity=0.7 | Aguardando |
| 3 dias distintos → maturity=1.0 | ~3 dias de uso normal |

**Não usar "Recalibrar com Watch 6"** — importa dados de sono (µ≈45ms, contexto errado).
Deixar coleta passiva agir.

---

## PRÓXIMO — Opção A: `licet-wear` (Wear OS nativo)

> Pré-requisito: Opção B aprovada ✅ — prontos para iniciar após maturidade 1.0.

| # | Tarefa | Esforço |
|---|--------|---------|
| A1 | Criar projeto Android Studio — Wear OS module para Galaxy Watch 6 | 1 dia |
| A2 | Implementar coleta raw de IBI/ECG via `SensorManager` (Wear OS) | 1–2 dias |
| A3 | BLE companion — Watch envia IBI para phone via `DataClient` / `MessageClient` | 1 dia |
| A4 | Phone-side: empacotar IBI + HMAC e enviar à API LICET | 4h |

**Como retomar:** dizer "vamos para Opção A"

---

## SEGURANÇA — Pendências críticas antes de produção real

| # | Tarefa | Impacto |
|---|--------|---------|
| S1 | Trocar `LICET_MOBILE_APP_SECRET` (`dev_secret_change_in_production`) | ALTO |
| S2 | Trocar `LICET_SECRET_KEY` (`temp_key_troque_depois`) | ALTO |

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## PUBLICAÇÕES — Fila

| # | Tarefa | Depende de |
|---|--------|-----------|
| P1 | Aguardar retorno MDPI | — |
| P2 | Recurso arXiv cs.CR (submit/7765569) | DOI MDPI |
| P3 | PR #97 IETF merge (David Condrey) | David |
| P4 | INPI Classe 42 | R$355 |

---

## ROADMAP CRIPTOGRÁFICO (não urgente)

1. **ZKP:** Schnorr → ZK-SERIES (arXiv:2506.19393) → Groth16+Pedersen (BioZero)
2. **Assinatura PQC:** Ed25519 → híbrido Ed25519+ML-DSA-44 (2026) → ML-DSA-44 only (2028)
3. **Anti-clone V4:** OPRF via BFRB (IACR 2025/1211)
4. **Layer 1:** ECG liveness cross-modal com EDA

---

## Como retomar em sessão futura

- `"vamos para Opção A"` → criar projeto `licet-wear` (Wear OS)
- `"continua os próximos passos"` → lê este arquivo
- `"trocar secrets de produção"` → gerar novos + `gcloud run services update`
- `"recurso arXiv"` → submeter appeal com DOI MDPI quando disponível
- `"como está o baseline?"` → `curl https://licet.dev/v1/baseline/status?user_id=6103c0171723584a`
