# LICET — Primeira Autorização Real com Galaxy Watch 6
## Sessão 28/07/2026

**Dispositivo:** Samsung Galaxy S (RXCX209Y1BP) + Galaxy Watch 6 SM-R930  
**App:** licet-android v1.0 (commits 4f1582b, bc52d39)  
**Backend:** https://licet.dev/v1 (Cloud Run southamerica-east1, revisão licet-00023+)  
**Executado por:** Christian Rodrigues Pereira, eColabs  
**Histórico:** Primeira autorização LICET com biometria de hardware real (não sintética).

---

## Contexto — O que foi diferente neste teste

Testes anteriores (26/07/2026) usaram dados biométricos derivados de export CSV do Samsung
Health com RR intervals gerados por processo Ornstein-Uhlenbeck. Este teste usa:

- **Frequência cardíaca real** — medida pelo Watch 6 em tempo real via Health Connect
- **SpO₂ real** — última medição pontual do Watch 6 sincronizada no Samsung Health
- **HRV real** — último valor RMSSD medido pelo Watch 6, sincronizado no Samsung Health
- **RR intervals derivados** do fluxo de FC contínuo via `HeartRateRecord` (Health Connect)
  - Método: `RR_ms = 60000 / BPM` por sample de FC
  - Filtro fisiológico: 200ms < RR < 2000ms
  - Janela usada: 24h (para capturar qualquer dado sincronizado)

---

## Configuração do Ambiente

### Correções aplicadas para chegar até aqui

| Problema | Causa | Solução |
|----------|-------|---------|
| HTTP 401 | `LICET_MOBILE_APP_SECRET` não setado no Cloud Run | `gcloud run services update --set-env-vars` |
| HTTP 401 persistente | `"%.1f".format()` usa locale pt-BR → vírgula decimal → HMAC mismatch | `String.format(Locale.US, "%.1f", value)` em `HMACGenerator.kt` |
| SpO₂=0 / HRV=0 → NEGADO | Watch 6 mede SpO₂/HRV pontualmente, não contínuo | Fallback 7 dias em `HealthConnectManager.captureReading()` |
| "Sem dados do wearable" | LICET app sem permissão no Health Connect | Conceder manualmente em: Health Connect → Permissões → Samsung Health → LICET |
| APK sem ícone | Faltava `mipmap-anydpi-v26/ic_launcher.xml` | Adicionado XML de ícone adaptativo |
| Warning 16KB page size | Libs nativas não alinhadas (Android 15) | `android:extractNativeLibs="true"` no AndroidManifest |

---

## Fluxo Completo Validado

```
Galaxy Watch 6
    ↓ (BLE + Samsung Health sync)
Samsung Health App
    ↓ (permissão explícita concedida)
Android Health Connect
    ↓ (HeartRateRecord, OxygenSaturationRecord, HeartRateVariabilityRmssdRecord)
licet-android (RXCX209Y1BP)
    ↓ POST /v1/biometric/push (HMAC-SHA256 com Locale.US)
licet.dev (Cloud Run southamerica-east1)
    ↓ verificação HMAC, cálculo IP/D²/trust_level
Ledger Imutável (Cloud SQL PostgreSQL)
```

---

## Resultado — Ledger #8 AUTORIZADO

**Botão:** "Teste Real (Watch 6)" no Dashboard do app licet-android.

### Dados biométricos enviados

| Campo | Valor | Fonte |
|-------|-------|-------|
| `heart_rate` | 64 BPM | Watch 6 — real, janela 24h |
| `spo2` | 98% | Watch 6 — última medição pontual (fallback 7 dias) |
| `hrv` | 45 ms RMSSD | Watch 6 — última medição pontual (fallback 7 dias) |
| `source` | `health_connect` | Health Connect API |
| `device_model` | Samsung Galaxy S | `android.os.Build.MODEL` |
| `rr_intervals` | ≥60 amostras | Derivado de FC contínua (`60000/BPM` por sample) |
| `start_timestamp` | timestamp − 86400s | Janela de 24h |

### Resposta da API

| Campo | Valor |
|-------|-------|
| `authorized` | **true** |
| `trust_level` | L0 (último resultado) |
| `max_authorization_level` | **L2** (maturity 60/100 habilita até L2) |
| `respiratory_periodicity_index` | **0.375** |
| `respiratory_periodicity_warning` | Baixa — sem risco de paced breathing |
| `layer3_mahalanobis_d2` | 0.13 |
| `layer3_mahalanobis_status` | **NO_BASELINE** |
| `coercion_risk` | **LOW** |
| `cognitive_state` | **NORMAL** |
| `forgery_cost` | **LOW** |
| `ledger_id` | **8** |
| `hardware_source` | `health_connect` |

### Histórico de autorizações visível no app

| Ledger | Status | Hash (prefixo) |
|--------|--------|----------------|
| #8 | **OK** | `890dfa4709161020f1d04f24…` |
| #7 | NEGADO | `1f0f84016aace6ea8c2bd133…` |
| #6 | NEGADO | `46c890821d0d7521fe74f12b…` |
| #5 | NEGADO | *(parcialmente visível)* |

Ledgers #5–#7 negados correspondem às tentativas anteriores ao fix do HMAC Locale.US
e à concessão das permissões do Health Connect.

### Bug de UI identificado

O campo `action` aparece como `null` na lista "Últimas Autorizações" (ex: "#8 — null").
O `action` é enviado corretamente à API (`"teste_real_watch6"`), mas não está sendo
retornado no response de `GET /ledger/history` ou não está sendo exibido pelo app.
**A corrigir:** verificar se `LedgerRecord` expõe o campo `action` e exibi-lo na lista.

### Interpretação

- **IP=0.375** — bem abaixo do threshold de bloqueio (0.80). Respiração natural, sem periodicidade suspeita.
- **D²=0.13 / NO_BASELINE** — baseline em calibração (maturity 60/100). D² calculado mas dados insuficientes para status definitivo.
- **Trust Level L0** — resultado da última autorização. Nível máximo disponível é L2.
- **coercion_risk=LOW** — nenhum sinal de estresse ou coerção nos dados fisiológicos.
- **forgery_cost=LOW** — sem ECG raw e EDA contínua (limitação da Opção B via Health Connect).
- **AUTORIZADO** — protocolo funcionando com biometria de hardware real.

---

## Significância

Este é o **primeiro registro no ledger LICET com biometria de hardware real**:

1. **Prova de conceito completa** — o fluxo Watch→Health Connect→API→Ledger funciona end-to-end
2. **Dados são do dono** — FC/SpO₂/HRV medidos pelo sensor PPG do Watch 6, não sintéticos
3. **HMAC válido** — assinatura gerada pelo Android com dados reais e verificada pelo servidor
4. **Ledger imutável** — Ledger #8 registrado em Cloud SQL com hash chain íntegro

---

## Estado do Baseline após o Teste

| Métrica | Valor | Meta |
|---------|-------|------|
| Sessões válidas | ~10 | ≥30 para maturity=100 |
| Maturity score | ~60/100 | 100 (Trust Level L4) |
| D² status | NO_BASELINE | NORMAL quando maduro |
| Trust Level disponível | L0 | L4 com baseline maduro |
| Dias distintos | 1 | ≥3 para maturidade real |

O baseline amadurece automaticamente conforme o monitoramento contínuo do app coleta
leituras a cada 60 segundos em background.

---

## Comparativo com Testes Anteriores

| Sessão | Data | Fonte dados | Ledger | authorized | IP | D² |
|--------|------|-------------|--------|------------|----|----|
| Testes 26/07 (físicos) | 26/07/2026 | Sintético (OU process) | 1–5 | true | 0.65 | 0.0 |
| Testes 26/07 (paced breathing) | 26/07/2026 | Sintético (ataque) | 4 | **false** | 0.98 | — |
| **Primeiro teste real** | 28/07/2026 | **Watch 6 real** | **8** | **true** | **0.375** | 0.13 |

---

## Próximo Passo — Opção A (Wear OS nativo)

Com Opção B validada, o próximo passo é `licet-wear`:
- App nativo no Watch 6 com acesso direto ao `SensorManager` do Wear OS
- Coleta beat-to-beat real (`IBI_LIST`) em vez de inferência por FC média
- Transmissão via `DataClient` / `MessageClient` para o phone companion
- Elimina dependência de sincronização Samsung Health e janela estendida

---

*Documento gerado em 28/07/2026. eColabs / LICET Protocol.*  
*DOI de referência: 10.5281/zenodo.21345045*  
*IACR ePrint: 2026/110546*
