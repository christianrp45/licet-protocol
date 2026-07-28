# LICET — Testes Profundos de Segurança
## Sessão 26/07/2026 — Continuação

**Ambiente:** Produção — https://licet.dev/v1 (revisão licet-00019-kgd)
**user_id de teste:** christian_watch6_real_v2 (baseline ativo, maturity=0.4)

---

## Teste A — Casos de Borda do Threshold IP=0.80

**Objetivo:** Encontrar a amplitude mínima de modulação periódica que ultrapassa o threshold de bloqueio.

**Método:** Sinal híbrido OU (ruído fisiológico) + componente sinusoidal a 0.1 Hz com amplitude variável.

| Amplitude (ms) | IP real | Resultado |
|---------------|---------|-----------|
| 0 (puro ruído) | 0.3731 | AUTORIZADO |
| 5 ms | 0.3577 | AUTORIZADO |
| 10 ms | 0.3131 | AUTORIZADO |
| 15 ms | 0.6925 | AUTORIZADO |
| **20 ms** | **0.8348** | **BLOQUEADO** ← limiar real |
| 25 ms | 0.8143 | BLOQUEADO |
| 30 ms | 0.8274 | BLOQUEADO |
| 40 ms | 0.9430 | BLOQUEADO |
| 80 ms (ataque pleno) | 0.9611 | BLOQUEADO |

**Watch 6 real (referência):** IP=0.6478, AUTORIZADO

**Achados:**
1. **Limiar real de bloqueio: ~20ms de modulação periódica a 0.1 Hz.** Amplitudes menores passam.
2. O IP não é linear com a amplitude — pequenas variações entre 10ms (IP=0.31) e 15ms (IP=0.69) mostram comportamento não-linear da DFT.
3. Um atacante com modulação controlada de apenas 20ms pico-a-vale seria bloqueado. Atletas treinados em respiração de ressonância atingem 60-100ms facilmente.
4. Repouso genuíno (OU puro, amp=0) produz IP=0.37 — bem abaixo do limiar.

**Implicação para falsos positivos:**
Amplitude de 20ms é pequena — respiração normal em repouso pode produzir RSA de 15-25ms. O threshold de 0.80 pode gerar falsos positivos em usuários com RSA naturalmente elevada. Recomenda-se calibração individual do threshold no baseline futuro.

---

## Teste B — Replay Attack

**Objetivo:** Verificar se um push_id pode ser reutilizado após uso legítimo.

| Tentativa | push_id | Resultado | HTTP |
|-----------|---------|-----------|------|
| Uso 1 (legítimo) | `07e0718c...` | AUTORIZADO (ledger_id=27) | 200 |
| Uso 2 (replay do mesmo push_id) | `07e0718c...` | REJEITADO | 404 |
| Uso 3 (push_id inventado) | `aaaa1111...` | REJEITADO | 404 |

**Conclusão:** O servidor invalida o push_id após primeiro uso (deleção do cache em memória). Replay attack ineficaz. push_id falso retorna 404 indistinguível — sem information leakage.

**Nota de limitação:** O cache de push_ids é em memória (dict Python). Em caso de restart do servidor, push_ids válidos não utilizados são perdidos. Solução futura: Redis ou banco de dados com TTL.

---

## Teste C — Integridade do HMAC

**Objetivo:** Verificar que qualquer adulteração da assinatura ou dos campos cobertos é rejeitada.

| Cenário | HTTP | Resultado |
|---------|------|-----------|
| HMAC correto | 200 | ACEITO |
| HMAC — primeiros 8 bytes adulterados | 401 | REJEITADO |
| HMAC — últimos 2 bytes adulterados | 401 | REJEITADO |
| HMAC completamente falso (aaaa...) | 401 | REJEITADO |
| Secret errado | 401 | REJEITADO |
| HR adulterado no payload (64→80, HMAC original) | 401 | REJEITADO |

**Conclusão:** HMAC-SHA256 protege integralmente os campos `source`, `heart_rate`, `spo2`, `hrv`, `start_timestamp`. Qualquer adulteração em qualquer campo coberto causa rejeição 401. O campo `rr_intervals` não está coberto pelo HMAC (apenas os campos escalares).

**Observação importante:** `rr_intervals` não está incluído no `sig_data`. Um atacante com acesso ao canal de transmissão poderia substituir os RR intervals sem invalidar o HMAC, desde que mantivesse os escalares (HR, HRV, SPO2) consistentes. Esta é uma limitação de design a documentar.

---

## Teste D — Coerção Simulada

**Objetivo:** Avaliar como o protocolo responde a diferentes perfis fisiológicos de estresse e manipulação farmacológica.

| Cenário | authorized | coercion_risk | pharma | cognitive | denial |
|---------|------------|---------------|--------|-----------|--------|
| Repouso normal | true | LOW | CLEAN(MEDIUM) | NORMAL | — |
| Taquicardia (HR=105, HRV=18) | true | **MEDIUM** | CLEAN(MEDIUM) | NORMAL | — |
| Beta-bloqueador (HR=52, HRV=8) | **false** | LOW | ANTICHOLINERGIC(MEDIUM) | NORMAL | INTERFERENCIA_FARMACOLOGICA |
| Tríade anticolinérgica (HR alto + EDA flat) | true | MEDIUM | CLEAN(HIGH) | NORMAL | — |
| Hipotermia (skin_temp=34.2°C) | true | LOW | CLEAN(MEDIUM) | NORMAL | — |
| Perfil forjado (clone exato do baseline) | true | LOW | CLEAN(MEDIUM) | NORMAL | — |

**Análise por cenário:**

**Taquicardia:** Detectada como `coercion_risk=MEDIUM` — o sistema sinaliza mas não bloqueia. Taquicardia isolada não é critério de negação (pode ser atividade física ou ansiedade genuína).

**Beta-bloqueador:** BLOQUEADO. HR=52 + HRV=8ms configura padrão farmacológico detectável. A combinação HR suprimido + HRV abolido é consistente com beta-bloqueador de alta dose — dificilmente ocorre em repouso genuíno.

**Tríade anticolinérgica (HR=102 + EDA_SCL=0.2 + EDA_SCR=0.05):** AUTORIZADO com `pharma=CLEAN(HIGH)`. Paradoxo — a confiança HIGH indica que o algoritmo farmacológico está certo de que é CLEAN, mas deveria detectar a tríade. Investigar: possível que EDA_SCL=0.2µS não seja considerado "plano" pelo threshold da Camada 2 ou que a tríade requeira combinação específica de todos os 3 sinais simultaneamente no check farmacológico.

**Hipotermia:** Não detectada. `skin_temp=34.2°C` é registrada mas não configura critério de bloqueio no código atual. Limitação a documentar.

**Perfil forjado (clone exato):** AUTORIZADO com D²=0.0 — matematicamente impossível de distinguir do dono. Este é o limite teórico do protocolo: um adversário com acesso ao perfil biométrico exato do usuário e sem detecção de vivacidade (liveness) passaria.

---

## Resumo Consolidado — Todos os Testes

| Categoria | Teste | Resultado | Observação |
|-----------|-------|-----------|------------|
| Autorização legítima | Watch 6 real | PASS | IP=0.65, D²=0.0 |
| GAP-B01 | Paced breathing 0.1Hz, amp=80ms | BLOQUEADO | IP=0.98 |
| Borda IP | amp=15ms | AUTORIZADO | IP=0.69 |
| Borda IP | amp=20ms | BLOQUEADO | IP=0.83 — limiar real |
| Replay | Reutilização de push_id | REJEITADO | 404 |
| Replay | push_id falso | REJEITADO | 404 |
| HMAC | 6 variações de adulteração | REJEITADO | 401 todos |
| Coerção | Taquicardia | SINALIZADO | coercion=MEDIUM |
| Coerção | Beta-bloqueador | BLOQUEADO | pharma=ANTICHOLINERGIC |
| Coerção | Tríade anticolinérgica | AUTORIZADO | Bug potencial |
| Coerção | Perfil clone | AUTORIZADO | Limite teórico |
| Ledger | 5+ registros mistos | INTACT | Cadeia íntegra |

---

## Vulnerabilidades e Gaps Identificados

### V1 — rr_intervals não cobertos pelo HMAC (NOVO)
`sig_data` cobre apenas escalares. Atacante com acesso ao canal pode substituir RR intervals.
**Severidade:** MÉDIA — requer acesso ao canal de transmissão (não trivial em BLE/HTTPS).
**Mitigação:** Incluir hash dos RR intervals no `sig_data`.

### V2 — Tríade anticolinérgica não bloqueada com EDA baixo
`EDA_SCL=0.2µS + HR=102 + HRV=15ms` deveria configurar tríade mas resulta em CLEAN(HIGH).
**Severidade:** BAIXA — requer EDA disponível (Watch 6 tem EDA spot, não contínua).

### V3 — Hipotermia não detectada
`skin_temp=34.2°C` não gera bloqueio.
**Severidade:** BAIXA — contexto incomum, documentar como limitação.

### V4 — Clone perfeito do perfil
D²=0.0 para dados idênticos ao baseline — sem liveness detection.
**Severidade:** ALTA teórica / BAIXA prática — adversário precisaria de acesso completo ao perfil.

---

## Próximos Passos

1. **Incluir hash(rr_intervals) no sig_data** — mitigar V1
2. **Investigar tríade anticolinérgica** — revisar thresholds EDA no check farmacológico
3. **Calibração individual do threshold IP** — evitar falsos positivos em RSA elevada
4. **Dashboard Android** — exibir todos estes campos na UI do app

---

*Documento gerado em 26/07/2026. NeuroTrust / LICET Protocol.*
*DOI: 10.5281/zenodo.21345045*
