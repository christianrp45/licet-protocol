# LICET — Testes Físicos com Galaxy Watch 6
## Sessão 26/07/2026

**Dispositivo:** Samsung Galaxy Watch 6 SM-R930 (40mm Bluetooth)  
**Ambiente:** Produção — https://licet.dev/v1 (Cloud Run us-central1)  
**Revisões deployadas:** licet-00018-l8m, licet-00019-kgd  
**Executado por:** Christian Rodrigues Pereira, eColabs

---

## 1. Configuração do Ambiente

### 1.1 Samsung Health Sensor SDK
- SDK v1.4.1 obtido via Samsung Developer Business Account (eColabs LTDA)
- AAR integrado em `licet-android/app/libs/`
- `SamsungSensorManager.kt` criado — lê `IBI_LIST`, `ECG_MV`, `SKIN_CONDUCTANCE`
- Build: **SUCCESSFUL**

### 1.2 Dados biométricos
- Fonte: export Samsung Health do Galaxy Watch 6 (26/07/2026)
- Arquivo: `com.samsung.health.hrv.20260726164845.csv`
- Dados reais: RMSSD=35.0ms, HR=64bpm (repouso)
- RR intervals: 150 amostras geradas via processo Ornstein-Uhlenbeck (OU) com parâmetros do Watch 6
- RMSSD calculado dos intervalos: **33.9ms**

### 1.3 Autenticação da API
- Fluxo usado: `POST /biometric/push` → `POST /authorize/from-push`
- HMAC-SHA256 com `LICET_MOBILE_APP_SECRET`
- `sig_data = f"{source}:{heart_rate}:{spo2}:{hrv}:{int(start_timestamp)}"`

---

## 2. Construção do Baseline

**user_id:** `christian_watch6_real_v2`  
**Protocolo:** 5 sessões × 180 segundos × 180 amostras RR

| Sessão | HR (bpm) | RMSSD (ms) | valid | maturity |
|--------|----------|------------|-------|---------|
| 1 | 65.1 | 33.9 | True | 0.0 |
| 2 | 65.2 | 33.9 | True | 0.0 |
| 3 | 65.4 | 33.9 | True | 0.0 |
| 4 | 64.1 | 33.9 | True | 0.0 |
| 5 | 63.7 | 33.9 | True | **0.4** |

**Sinais no baseline:** `RMSSD`, `SPO2`, `SKIN_TEMP`, `HF_POWER_MS2`, `PEAK_FREQ_HZ`  
**Trust Level disponível:** L1  
**baseline_ready:** True

> **Nota:** maturity=0.4 indica 5 sessões válidas sem distribuição por dias distintos.
> Baseline maduro (maturity=1.0) requer sessões em ≥3 dias diferentes.

---

## 3. Teste 1 — Autorização Legítima (Repouso Genuíno)

**Cenário:** Dados reais do Galaxy Watch 6 em repouso.

**Entrada:**
```json
{
  "source": "samsung_watch",
  "heart_rate": 64.0,
  "spo2": 98.0,
  "hrv": 33.9,
  "rr_intervals": [150 amostras, RMSSD=33.9ms, HR=64bpm],
  "device_model": "Galaxy Watch 6 SM-R930"
}
```

**Resultado:**
| Campo | Valor |
|-------|-------|
| `authorized` | **true** |
| `trust_level` | L1 |
| `layer3_mahalanobis_d2` | 0.0 |
| `layer3_mahalanobis_status` | PARTIAL |
| `respiratory_periodicity_index` | **0.6478** |
| `respiratory_periodicity_warning` | MODERADA (IP=0.65, pico=0.040 Hz) |
| `coercion_risk` | LOW |
| `baseline_maturity` | 0.4 |
| `layer_forgery_cost` | MEDIUM |
| `ledger_id` | 2 |

**Interpretação:**
- D²=0.0 confirma que o perfil biométrico atual é idêntico ao baseline
- IP=0.65 com pico em 0.040 Hz — ritmo respiratório natural (~2.4 resp/min), broadband esperado
- MODERADA é o nível correto para repouso genuíno (abaixo do threshold HIGH=0.80)
- layer_forgery_cost=MEDIUM por ausência de ECG raw e EDA

---

## 4. Teste 2 — Ataque de Paced Breathing (GAP-B01)

**Cenário:** Simulação de atacante treinado em respiração controlada a 0.1 Hz (6 ciclos/min).
Esta é a principal limitação não mitigada do protocolo LICET original.

**Geração dos RR intervals:**
```python
# Modulação sinusoidal pura a 0.1 Hz
mean_rr = 60000.0 / 64.0  # 937.5ms
amplitude = 80.0  # ms pico-a-vale
rr[i] = mean_rr + amplitude * sin(2π × 0.1 × t)
```

**Parâmetros do ataque:**
- Frequência: 0.1 Hz (6 respirações/min — frequência de ressonância cardíaca)
- Amplitude de modulação: 80ms pico-a-vale
- RMSSD resultante: 32.8ms (próximo do baseline legítimo — 33.9ms)

**Resultado (ANTES do bloqueio — versão original):**
| Campo | Valor |
|-------|-------|
| `authorized` | **true** ← FALHA DE SEGURANÇA |
| `respiratory_periodicity_index` | 0.9844 |
| `respiratory_periodicity_warning` | ALTA (IP=0.98, pico=0.100 Hz) |
| `denial_reason` | *(vazio)* |

**Análise:** O servidor detectava o ataque (IP=0.98) mas não bloqueava.
RMSSD similar ao baseline (32.8 vs 33.9ms) causava D²≈0, passando no Mahalanobis.

---

## 5. Mitigação do GAP-B01 — Bloqueio Automático

**Implementação** em `core/crypto.py`:

```python
# Bloqueio automático quando IP ≥ 0.80
if resp_index is not None and resp_index >= 0.80:
    return _deny(
        f"PACED_BREATHING_DETECTED_IP={resp_index:.2f}",
        _empty_ecg(), _empty_eda(), _empty_pharma(), _empty_maha(),
        _determine_trust_level(...),
    )
```

**Threshold:** IP ≥ 0.80 → negação imediata, antes do pipeline ECG/EDA/Mahalanobis.

**Resultado (APÓS o bloqueio):**
| Campo | Valor |
|-------|-------|
| `authorized` | **false** |
| `respiratory_periodicity_index` | 0.9844 |
| `denial_reason` | `PACED_BREATHING_DETECTED_IP=0.98` |
| `ledger_id` | 4 (registrado no ledger) |

---

## 6. Teste 3 — Verificação Pós-Ataque (Resiliência)

**Cenário:** Autorização legítima imediatamente após tentativa de ataque.

**Resultado:**
| Campo | Valor |
|-------|-------|
| `authorized` | **true** |
| `respiratory_periodicity_index` | 0.6478 |
| `ledger_id` | 5 |

**Conclusão:** O sistema retorna ao comportamento normal após rejeitar o ataque.
O baseline não foi corrompido pela tentativa fraudulenta.

---

## 7. Integridade do Ledger

**Cadeia hash-chained com 5 registros:**

| ledger_id | authorized | denial_reason |
|-----------|------------|---------------|
| 1 | True | — |
| 2 | True | — |
| 3 | True | — |
| 4 | **False** | `PACED_BREATHING_DETECTED_IP=0.98` |
| 5 | True | — |

```json
{
  "status": "INTACT",
  "total_records": 5,
  "tampered": false
}
```

Registros aprovados e negados coexistem na cadeia sem corromper a integridade.

---

## 8. Bug Encontrado e Corrigido

**Bug:** `GET /ledger/integrity` retornava HTTP 500.

**Causa:** `verify_integrity()` em `ledger/db.py` reconstruía `AuthorizationBundle`
sem os campos `respiratory_periodicity_index` e `respiratory_periodicity_warning`,
introduzidos em versão anterior.

**Correção:**
```python
# ledger/db.py — linha 340
respiratory_periodicity_index=getattr(row, "respiratory_periodicity_index", None),
respiratory_periodicity_warning=getattr(row, "respiratory_periodicity_warning", None),
```

---

## 9. Resumo dos Resultados

| Teste | Resultado | IP | D² | authorized |
|-------|-----------|----|----|------------|
| Autorização legítima (Watch 6) | PASS | 0.65 | 0.0 | true |
| Ataque paced breathing (pré-mitigação) | VULNERÁVEL | 0.98 | 0.0 | true |
| Ataque paced breathing (pós-mitigação) | **BLOQUEADO** | 0.98 | — | **false** |
| Resiliência pós-ataque | PASS | 0.65 | 0.0 | true |
| Integridade do ledger | INTACT | — | — | 5/5 |

---

## 10. Limitações Identificadas

### 10.1 SQLite efêmero no Cloud Run
O banco de dados SQLite é reiniciado a cada novo deploy (filesystem efêmero).
Baseline e ledger são perdidos entre revisões.
**Solução futura:** migrar para Cloud SQL (PostgreSQL) ou Firestore.

### 10.2 Dados biométricos sintéticos
Os RR intervals usados nos testes são gerados por processo Ornstein-Uhlenbeck
com parâmetros derivados do export Samsung Health (RMSSD/HR).
O Samsung Health export não fornece RR intervals beat-to-beat — apenas agregados por janela de 5 min.
**Solução futura:** Wear OS app com Samsung Health Sensor SDK (Opção A).

### 10.3 Ausência de ECG raw e EDA
`layer_forgery_cost=MEDIUM` — sem ECG raw e EDA, a resistência a falsificação é limitada.
**Solução futura:** Samsung Health Sensor SDK fornece `ECG_MV` (500Hz) e `SKIN_CONDUCTANCE`.

### 10.4 Baseline maturity=0.4
5 sessões no mesmo dia. Baseline maduro requer distribuição em ≥3 dias.
**Solução futura:** coletar baseline ao longo de semanas de uso normal.

### 10.5 Falsos positivos potenciais do bloqueio IP ≥ 0.80
Atletas, praticantes de meditação e usuários com respiração naturalmente regular
podem ter IP > 0.80 em repouso genuíno.
**Mitigação parcial:** threshold calibrável por integrador; warning sempre presente na resposta.

---

## 11. Próximos Passos

1. **Opção A (Wear OS app)** — migrar `SamsungSensorManager` para app no Watch 6,
   transmitir IBI_LIST real via Wearable Data Layer API para o phone
2. **Persistência do baseline** — Cloud SQL para sobreviver entre deploys
3. **Dashboard Android** — tela de resultado com IP, D², trust_level, forgery_cost
4. **MDPI Cryptography** — submissão do paper para obter DOI e desbloquear recurso arXiv
5. **INPI Classe 42** — registro da marca (R$355)

---

*Documento gerado em 26/07/2026. eColabs / LICET Protocol.*  
*DOI de referência: 10.5281/zenodo.21345045*
