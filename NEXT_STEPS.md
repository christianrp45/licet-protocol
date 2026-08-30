---
updatedAt: 2026-08-25
---

# LICET — Próximos Passos

## ✅ CONCLUÍDO até 25/08/2026

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
- **S1+S2** ✅ Secrets de produção rotacionados (18/08/2026)
- **SpO2 fallback** ✅ Campo `spo2_is_fallback` em `BaselineSubmitRequest`

### Android — Opção B (Health Connect / `licet-android/app/`)

- **Dashboard** ✅ Métricas LICET em tempo real
- **Settings screen** ✅ Provisionar `LICET_MOBILE_APP_SECRET`
- **Health Connect** ✅ Fallback 7 dias para SpO₂/HRV
- **Fix IP falso positivo** ✅ `rrIntervals = emptyList()` — Opção B
- **Fix µ_RMSSD drift** ✅ janelas 24h + HRV rolling 7 dias
- **Fix baseline 0 sessões** ✅ `hardware_source`, `duration_seconds=180`, `BaselineCollectionService.start()`
- **SpO2 fallback flag** ✅ `spo2IsFallback` em `BiometricReading`
- **Ledger #125 AUTORIZADO** ✅ 23/08/2026 — Watch 6 real, pipeline end-to-end

### Android — Opção A (`licet-android/wear/`)

- **Retry automático** ✅ 1× após 3s para DNS/timeout em `runWearAuthorization()`
- **Detecção de rede** ✅ `UnknownHostException` + `SocketTimeoutException` → mensagem legível
- **`getLatestHrv()`** ✅ Adicionado ao `HealthConnectManager` — lê HC 7 dias
- **HC HRV sempre** ✅ `runWearAuthorization()` usa `getLatestHrv()` (mesma fonte do baseline)

### Baseline — 25/08/2026

| Meta | Status |
| ---- | ------ |
| Baseline zerado (contexto sono) | ✅ 23/08/2026 |
| 31 sessões acumuladas (acordado) | ✅ 25/08/2026 |
| maturity=1.0, L1 ativo | ✅ 25/08/2026 |

### Publicações

- **Zenodo** ✅ DOI 10.5281/zenodo.21345045 (v2.0)
- **IACR ePrint** ✅ 2026/110546
- **SSRN** ✅ Abstract ID 7018458
- **MDPI Cryptography** ✅ Submetido (aguardando revisão)
- **IETF draft** ✅ draft-pereira-licet-human-intent-01
- **PR #103** ✅ Respondido — aguardando 2º passe David Condrey
- **INPI Processo 944297536** ✅ Publicado RPI 2901 (11/08/2026), oposição até ~10/10/2026

---

## 🔴 URGENTE — Bug #10: APK licet-wear quebrado

**Estado:** APK instalado em 25/08/2026 envia `rr_intervals = null`
com `source = "samsung_watch"` → servidor retorna **HTTP 422** (CA-03).
Nenhuma autorização via licet-wear funciona até correção.

### Causa raiz

`TYPE_HEART_RATE` do Wear OS entrega BPM suavizado (~1 Hz).
`60000/BPM` não é IBI real — causa dois problemas simultâneos:

1. **RMSSD ≠ baseline:** baseline HC usa IBI real do Samsung Health (µ≈35ms);
   BPM→RR dá 6–11ms → D² alto → `CAMADA3_DESVIO_BASELINE_INDIVIDUAL`
2. **IP falso positivo:** variação de BPM em frequência respiratória (RSA normal)
   aparece como paced breathing → IP=0.86 > floor 0.80 → `PACED_BREATHING_DETECTED`

**Tensão de segurança:** remover RR intervals (fix do #2) viola CA-03 (Laborde 2022, BIO-03).

### Decisão pendente — escolher uma das opções abaixo

| Opção | Descrição | Prós | Contras |
| ----- | --------- | ---- | ------- |
| **A** | Reverter para `wearData.rrIntervals` | Mantém CA-03; simples | IP falsos positivos frequentes |
| **B** | Novo source `samsung_watch_bpm_only` isentado de CA-03 no servidor | Documenta limitação formalmente sem enfraquecer o protocolo principal | Requer mudança no backend + Android |
| **C** | IBI real via `ExerciseClient` (Health Services for Wear OS) | Solução correta; elimina ambos os problemas | Mais complexo; verificar compatibilidade Watch 6 |

**Recomendação:** Opção B como bridge + Opção C no roadmap do licet-wear.

**Para retomar:** dizer `"continua o bug #10 do licet-wear"`

---

## PUBLICAÇÕES — Fila

| # | Tarefa | Depende de |
| - | ------ | ---------- |
| P1 | Aguardar retorno MDPI | — |
| P2 | Recurso arXiv cs.CR (submit/7765569) | DOI MDPI |
| P3 | PR #103 IETF merge (David Condrey — 2º passe pendente) | David |

---

## ROADMAP CRIPTOGRÁFICO (não urgente — alinhar antes de implementar)

1. **ZKP:** Schnorr → ZK-SERIES (arXiv:2506.19393) → Groth16+Pedersen (BioZero)
2. **Assinatura PQC:** Ed25519 → híbrido Ed25519+ML-DSA-44 (2026) → ML-DSA-44 only (2028)
3. **Anti-clone V4:** OPRF via BFRB (IACR 2025/1211)
4. **licet-wear IBI real:** `ExerciseClient` ou Samsung Health Sensor SDK (verificar compatibilidade Watch 6 antes)

---

## Como retomar em sessão futura

- `"continua o bug #10 do licet-wear"` → resolver conflito CA-03 vs IP falso positivo
- `"como está o baseline?"` → `curl https://licet.dev/v1/baseline/status?user_id=6103c0171723584a`
- `"status do ledger"` → `curl https://licet.dev/v1/ledger/history?limit=5`
- `"status PR #103"` → `gh pr view 103 --repo LF-Decentralized-Trust-labs/proof-of-effort`
- `"recurso arXiv"` → submeter appeal com DOI MDPI quando disponível
