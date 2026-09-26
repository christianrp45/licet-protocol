---
title: "Volitional Liveness: A Multivariate Physiometric Protocol for Cryptographically-Bound Human Intent Authorization"
status: outline — em redação
session: 25/08/2026
authors: Christian Rodrigues Pereira (eColabs)
affiliation_target: UniEvangelica — Centro de Pesquisa e Tecnologia, Goiás
venues_target:
  - IEEE Transactions on Information Forensics and Security (TIFS) — impact factor 6.8
  - ACM CCS 2027 (deadline ~jan/2027)
  - USENIX Security 2027
  - IEEE Transactions on Affective Computing (TAFFC) — impact factor 11.2
  - Nature Digital Medicine — impact factor 15.2
---

# OUTLINE — Volitional Liveness Protocol (VLP)

## Título principal
**"Volitional Liveness: A Multivariate Physiometric Protocol for
Cryptographically-Bound Human Intent Authorization"**

## Título alternativo (versão tese PhD)
**"Bridging the Intent Gap: Formal Protocol Design, Security Analysis,
and Empirical Validation of Physiometric Volitional Authorization"**

---

## Contributions (numbered — obrigatório para venues A*)

1. **Definição formal de Intentional Liveness** — distinção entre presence
   liveness (ISO 30107) e volitional liveness; conceito novo sem equivalente
   em nenhum padrão ISO, RFC ou regulação existente.

2. **Protocolo LICET** — especificação formal de 4 camadas com primitivas
   criptográficas (Ed25519, HMAC-SHA256, HKDF, ZKP Schnorr, hash chain).

3. **Security analysis** — taxonomia de 6 classes de ataque com análise
   formal de resistência e limites explícitos.

4. **Second-order IP attack** — primeira modelagem formal de ataque de jitter
   respiratório contra índice de periodicidade (contribuição original;
   não coberta por nenhum paper existente).

5. **Temporal binding como marcador de agência em protocolo de segurança** —
   primeira implementação de Caspar & Haggard (2016) em protocolo de autorização.

6. **Validação empírica** — WESAD dataset + dados reais Samsung Galaxy Watch 6
   (135+ ledger entries).

---

## SEÇÃO 1 — INTRODUCTION

### 1.1 The Authorization Problem
- Autenticação de identidade ≠ prova de intenção: o gap conceitual central
- Custos reais: fraude por coerção, incapacidade cognitiva não detectada,
  automação mascarando agente humano
- Ref: Caspar & Haggard (2016), Brass & Haggard (2008)

### 1.2 The Intent Gap (definição formal proposta)
> "The semantic distance between cryptographic proof of identity and attestation
> of volitional autonomous action"

- Mapeamento dos 7 GAPs que nenhum padrão resolve:
  - **GAP-I1** Coerção física silenciosa
  - **GAP-I2** Incapacidade cognitiva temporária (álcool, fadiga, sedação)
  - **GAP-I3** Automatismo vs. ação deliberada
  - **GAP-I4** Ausência de framework legal para biometria fisiológica como evidência
  - **GAP-I5** Intentional liveness vs. presence liveness
  - **GAP-I6** Portabilidade de baseline entre sistemas
  - **GAP-I7** Granularidade temporal de evidência fisiológica
- Ref: WebAuthn L3 (W3C 2024), eIDAS 2024/1183, ISO 30107-3:2023, NIST SP 800-63-4

### 1.3 Contributions
*(lista numerada — ver acima)*

### 1.4 Paper Organization

---

## SEÇÃO 2 — BACKGROUND AND RELATED WORK

### 2.1 Authentication and Authorization Standards
- FIDO2/WebAuthn: User Presence vs. User Verification
- eIDAS 2.0: LoA Low / Substantial / High
- ISO/IEC 30107: Presentation Attack Detection — liveness de presença
- NIST SP 800-63-4: AAL1/AAL2/AAL3
- Argumento: todos cobrem L1+L2; nenhum cobre L3 (volitional liveness)
- Ref: W3C WebAuthn L3, RFC 8809, ISO 30107-1:2023, ISO 30107-3:2023,
       NIST SP 800-63-4, eIDAS (EU) 2024/1183

### 2.2 Neuroscience of Voluntary Action
- Readiness Potential: Kornhuber & Deecke (1965), Libet et al. (1983),
  Schurger et al. (2012, PNAS)
- Modelo What/When/Whether: Brass & Haggard (2008, J. Neuroscience)
  → o "whether" desaparece sob coerção
- Neurociência da volição: Haggard (2019, Nature Reviews Neuroscience)
- Coerção e sentido de agência: Caspar et al. (2016, Current Biology),
  Caspar et al. (2020, Psychological Science)
- Temporal binding como marcador de agência voluntária

### 2.3 Physiological Correlates of Cognitive State
- HRV e função executiva: Thayer et al. (2012, Neuroscience & Biobehavioral Reviews),
  Hansen et al. (2003, Psychophysiology)
- Teoria polyvagal: Porges (2007, Biological Psychology)
  → HRV alta = dominância ventrovagal = engajamento voluntário
- EDA e arousal: Boucsein (2012, Springer), Critchley (2002, J. Neuroscience),
  Dawson et al. (2017, Handbook of Psychophysiology)
- Temperatura periférica e stress: Vinkers et al. (2013, Psychosomatic Medicine),
  Kreibig (2010, Biological Psychology)
- Stress agudo e tomada de decisão: Starcke & Brand (2012, Neuroscience & Biobehavioral Reviews),
  Porcelli & Delgado (2009, Psychological Science)
- Fusão multimodal: Schmidt et al. (2018, ACM ICMI — WESAD),
  Kim & André (2008, IEEE TPAMI), Can et al. (2019, Frontiers in Computer Science)

### 2.4 Wearable Biometric Authentication
- Validação PPG-HRV: Bent et al. (2020, npj Digital Medicine),
  Mannheimer et al. (2021, JMIR mHealth), Plews et al. (2017, IJSPP)
- Autenticação contínua: Vu et al. (2021, IEEE TIFS), Frank et al. (2013, IEEE TIFS)
- Limitações consumer-grade: Navalta et al. (2020), Stahl et al. (2016, JMIR mHealth)
- Laborde et al. (2017, Frontiers in Psychology) — RMSSD metodologia

### 2.5 Adversarial Attacks on Biometric Systems
- Replay BLE: Yan et al. (2020, IEEE TIFS), Conti et al. (2018, IEEE S&P)
- Baseline poisoning: Biggio et al. (2012, ICML), Rubinstein et al. (2009, IMC),
  Barreno et al. (2006, ACM CCS)
- Synthetic physiological signals: Golany & Radinsky (2019, AAAI),
  Hazra & Byun (2020, Biology)
- Mahalanobis robustness: Li & Li (2019, ArXiv), Roth et al. (2022, NeurIPS)
- Breathing pacing: Kreibig (2010), Shaffer & Ginsberg (2017, Frontiers in Public Health),
  De Geus et al. (2019)

### 2.6 Cryptographic Foundations
- Ed25519: Bernstein et al. (2011), RFC 8032
- HMAC-SHA256: RFC 2104, FIPS 198-1
- HKDF: RFC 5869 (Krawczyk & Eronen)
- ZKP Schnorr: Schnorr (1991), Maurer (2009)
- Hash chains: Lamport (1981)

---

## SEÇÃO 3 — THREAT MODEL

### 3.1 System Model
- Componentes: wearable sensor, mobile app, authorization server, ledger
- Canais e primitivas de proteção por canal
- Diagrama formal de arquitetura

### 3.2 Adversary Model (formal)
- Capacidades: acesso físico ao dispositivo, acesso ao canal BLE,
  conhecimento do baseline, acesso ao servidor
- Objetivos: forjar autorização, degradar protocolo, envenenar baseline,
  induzir falso positivo

### 3.3 Classes de Adversário

| Classe | Capacidade | Objetivo |
|--------|-----------|----------|
| A1 — Remote attacker | Canal de rede | Replay/inject |
| A2 — Physical attacker | Dispositivo físico | Sensor spoofing |
| A3 — Coercing party | Presença física | Forçar autorização aparentemente voluntária |
| A4 — Insider | Acesso ao enrollment | Baseline poisoning |
| A5 — Trained adversary | Biofeedback + device | Breathing pacing / EDA manipulation |

### 3.4 O que o protocolo NÃO protege (obrigatório para credibilidade)
- Coerção psicológica crônica (acostumação autonômica)
- Adversário com baixa reatividade autonômica (sociopatia)
- Ataques físicos ao sensor PPG (LED IR injection, ~$50)
- Coerção não distinguível de arousal positivo elevado sem contexto temporal

---

## SEÇÃO 4 — THE LICET PROTOCOL — ESPECIFICAÇÃO FORMAL

### 4.1 Formal Definitions

```
Baseline B ~ N(μ, Σ)  onde μ ∈ ℝⁿ, Σ ∈ ℝⁿˣⁿ
Mahalanobis: D²(x, B) = (x - μ)ᵀ Σ⁻¹ (x - μ)
Threshold: χ²(n, α=0.05) por número n de sinais ativos
Volitional Liveness Score: VLS = f(D², IP, ΔT, tremor_freq)
Authorization: GRANTED iff VLS ≤ θ ∧ IP ≤ ip_threshold ∧ maturity ≥ 1.0
```

### 4.2 Layer Architecture

```
L4 — Ledger Integrity       Hash chain imutável (Lamport 1981)
L3 — Volitional Liveness    Mahalanobis + IP + ΔT + tremor
L2 — Identity Verification  Ed25519 + HMAC-SHA256 + HKDF
L1 — Presence & Liveness    Wearable contínuo + anti-replay
```

Posicionamento vs. padrões existentes:
- L1 equivale a: WebAuthn UP + ISO 30107 PAD
- L2 equivale a: WebAuthn UV + FIDO2 AAL2
- L3 é INEXISTENTE em qualquer padrão ← contribuição principal
- L4 é INEXISTENTE em qualquer padrão ← contribuição secundária

### 4.3 Baseline Enrollment Protocol
- Especificação formal do processo
- Filtros de qualidade: activityLevel≤2, hrv≥10.0, hr∈[40,110]
- Requisito mínimo: n≥10 sessões (Biggio 2012: 1 sessão = 10% do baseline)
- Detecção de outlier entre sessões: Z-score inter-sessão
- Floors de variância mínima validados (Ledger #60, 01/08/2026):

| Sinal | Floor | Fonte |
|-------|-------|-------|
| RMSSD | 100 ms² | Plews 2012 + Bent 2020 |
| SpO2 | 0.25 %² | Resolução PPG ±0.5% |
| HF_POWER_MS2 | 10000 ms⁴ | Variância espectral inter-sessão |
| PEAK_FREQ_HZ | 0.002 Hz² | FFT Δf = 1/180s |
| EDA_SCL | 0.25 µS² | Variabilidade basal EDA |

### 4.4 Authorization Protocol
- Sequência de mensagens (diagrama formal)
- Janela temporal ótima: 3-5 minutos (Can et al. 2019, Frontiers)
- Cálculo de VLS
- Decisão e registro no ledger com bio_payload_hash

### 4.5 Cryptographic Binding
- HMAC v3: campos cobertos e justificativa
- HKDF salt = SHA256(user_id ‖ timestamp): razão criptográfica
- Ed25519 signature sobre payload completo
- bio_payload_hash no ledger

### 4.6 Volitional Liveness — Definição Formal (nova)

> "Volitional Liveness (VL) is the property of a biometric authorization
> event whereby the authorizing subject's measured autonomic profile at
> time t falls within a defined statistical neighborhood of their established
> baseline profile, as determined by Mahalanobis distance under χ² distribution,
> and simultaneously satisfies constraints on respiratory periodicity (IP),
> peripheral temperature delta (ΔT), and micro-tremor frequency (f_tremor),
> thereby attesting autonomic state compatibility with uncoerced voluntary action."

### 4.7 Temporal Binding Implementation (contribuição original)
- Caspar & Haggard (2016): ações voluntárias → menor binding que coagidas
- Definição: intervalo [trigger → confirmation gesture] em ms
- Hipótese formal: E[binding_voluntary] < E[binding_coerced]
- Implementação: medição de latência de gesto no wearable
- Integração com VLS como feature adicional

---

## SEÇÃO 5 — SECURITY ANALYSIS

### 5.1 Formal Security Properties
- Unforgeability (definição formal)
- Replay resistance (prova por construção — nonce + timestamp)
- Baseline integrity (definição de poisoning resistance)

### 5.2 Attack Analysis — 6 Classes

**Attack 1 — BLE Replay**
- Ref: Yan et al. 2020, Conti et al. 2018
- Condições: canal BLE não autenticado
- Mitigação: Ed25519 + timestamp no payload
- Limitação residual: sensor-level pre-signing attack

**Attack 2 — Baseline Poisoning**
- Ref: Biggio et al. 2012, Rubinstein et al. 2009
- Análise: n=10 sessões → 1 sessão corrompida = 10% do baseline
- Mitigação: Z-score inter-sessão + filtros de qualidade de enrollment

**Attack 3 — Breathing Pacing (básico)**
- Ref: Kreibig 2010, Shaffer & Ginsberg 2017, De Geus et al. 2019
- Mecanismo: respiração a 6rpm eleva RMSSD 40-80% em 90s
- Mitigação: IP (Periodicity Index) — respiração paced → IP alto

**Attack 4 — Second-Order IP Attack (CONTRIBUIÇÃO ORIGINAL)**
- *Primeiro paper a modelar este ataque formalmente*
- Mecanismo: jitter intencional de cadência respiratória reduz IP
  mantendo HF power elevado
- Condições necessárias: treino de biofeedback avançado
- Análise de viabilidade: alta habilidade necessária; detectável por
  análise espectral de variância do IP em janela temporal
- Mitigação proposta: IP variance window analysis

**Attack 5 — EDA Manipulation**
- Ref: Boucsein 2012, Greco et al. 2017
- SCL como escalar: adversário via exercício/drogas pode targetear range
- Limitação: EDA não distingue valência — combinação multivariada mitiga

**Attack 6 — Synthetic Signal Generation**
- Ref: Golany & Radinsky 2019 (AAAI), Hazra & Byun 2020 (Biology)
- Estado: FAR atual 4-18% contra autenticação real em 2025
- Não é ataque prático no horizonte de 2025-2026

### 5.3 Threat Model Coverage Matrix

| Ataque | Adversário | Mitigação | Limitação residual |
|--------|-----------|-----------|-------------------|
| BLE Replay | A1 | Ed25519+timestamp | Pre-signing |
| Baseline Poisoning | A4 | Z-score + filtros | n pequeno |
| Breathing Pacing | A5 | IP threshold | 2ª ordem |
| Second-order IP | A5 treinado | IP variance analysis | Alta habilidade |
| EDA manipulation | A3/A5 | Multivariado | SCL isolado |
| Synthetic signal | A1/A2 | FAR residual 4-18% | Evolução de GANs |

---

## SEÇÃO 6 — EMPIRICAL VALIDATION

### 6.1 WESAD Dataset Experiments
- Ref: Schmidt et al. (2018, ACM ICMI)
- 15 participantes, Empatica E4, condições: baseline / stress (TSST) / amusement
- Metodologia: aplicar pipeline LICET ao WESAD; calcular D² por estado
- Hipótese: D²(stress) >> D²(baseline) com p < 0.01
- Métricas: FAR, FRR, AUC, Wilcoxon signed-rank, Cohen's d

### 6.2 Real-World Validation — Samsung Galaxy Watch 6
- Dataset: 135+ ledger entries reais
- Análise: D² distribution por status (AUTHORIZED / DENIED por classe)
- Análise: IP distribution — separação entre sessões aprovadas e negadas
- Análise: temperatura delta em sessões negadas por CAMADA3

### 6.3 Statistical Analysis
- Wilcoxon signed-rank test (D² stress vs. baseline)
- ROC curves: sinal individual vs. fusão multivariada
- Leave-one-out cross-validation
- Effect size (Cohen's d) por marcador
- Bland-Altman analysis: PPG-HRV vs. ECG de referência (Bent 2020 como proxy)

### 6.4 Limitations (honestidade científica)
- n=15 no WESAD (pequeno)
- Ausência de condição de coerção controlada (razões éticas)
- Consumer PPG vs. Empatica E4: erro 15-30% (Bent 2020)
- Ausência de adversário treinado em breathing pacing nos experimentos
- **Wrist-PPG RMSSD unreliability under acute perturbation (achado 25/09/2026):**
  RMSSD subiu (em vez de cair) sob stress agudo (TSST) em 13/15 sujeitos do WESAD,
  mesmo após gate de rejeição de artefato de movimento (limiar por acelerômetro,
  mediana+3×MAD do baseline do próprio sujeito) — o gate não corrigiu a direção,
  descartando movimento grosseiro como causa primária. Literatura convergente:
  Sinichi et al. (2025, *Psychophysiology*) testou o mesmo dispositivo (Empatica E4)
  sob tarefa aritmética (análoga ao componente do TSST) e reporta colapso de
  correlação RMSSD (r=0.31, MAAPE=88%), atribuído a fala/tensão muscular sutil,
  não movimento grosseiro; Xu et al. (2026, *Sensors*) confirma RMSSD/HF como as
  métricas de HRV mais propensas a erro sistemático via PPG mesmo com
  processamento refinado. Ver `wesad_experiment/literature_review_rmssd_amusement.md`
  para revisão completa.
- **Specificity de amusement abaixo do esperado (achado 25/09/2026, revisado):**
  ~48-50% das janelas de amusement (vs. 70-85% esperado) foram flagadas como
  anomalia. Hipótese inicial de "ambiguidade de arousal" foi **refutada** —
  Wu et al. (2019, *Frontiers in Neuroscience*) mostra que amusement tem HR
  menor e RMSSD maior que fear/anger/neutral (mais parecido com relaxamento
  que com stress). O mecanismo correto e mais específico: Kreibig (2010,
  *Biological Psychology*) estabelece que EDA/SCL/SCR é cego a valência por
  design fisiológico (sobe tanto em amusement quanto em fear/anger) — é o
  RMSSD que deveria diferenciar os dois estados, mas como o RMSSD via PPG de
  pulso já está comprometido (ver limitação acima), essa diferenciação não
  ocorre. Não recomendado reportar como resultado forte de specificity sem
  esta ressalva explícita no texto.
- **Circular data source (GAP-L3-01):** quando o sensor de autorização é a
  mesma fonte que construiu o baseline (ex: Health Connect HRV cache), o
  poder discriminativo da Layer 3 é degradado — D² ≈ 0 sistematicamente.
  Health Connect entrega HRV como média suavizada dos últimos 7 dias; o
  baseline é construído com esses mesmos valores, resultando em x ≈ µ.
  Fix correto: IBI beat-to-beat em tempo real via ExerciseClient (Opção C,
  roadmap). Enquanto não implementado, a Layer 3 opera em modo de
  detecção de desvios grosseiros apenas (D² > 0 somente quando o estado
  fisiológico difere significativamente da janela de 7 dias do HC).

---

## SEÇÃO 7 — ETHICAL AND LEGAL ANALYSIS

### 7.1 O que o protocolo afirma e o que não afirma
- Attestation de estado autonômico ≠ prova de culpabilidade legal
- Claim correto: "estado autonômico compatível com autonomia volicional"
- Ref: E-SIGN Act, LGPD Art. 8, GDPR Art. 4(11), eIDAS Art. 26

### 7.2 Privacidade e LGPD/GDPR
- Dado biométrico: categoria especial (LGPD Art. 11, GDPR Art. 9)
- Tensão: ledger imutável vs. direito ao esquecimento
- Proposta de arquitetura: hash do payload no ledger, dado biométrico off-chain

### 7.3 Limites Éticos do Protocolo
- Sociopatia: baixa reatividade autonômica mascara coerção
- Coerção crônica: acostumação autonômica reduz sinal diferencial
- Condições médicas: diabetes autonômica, PTSD, medicações vagolíticas

### 7.4 Responsabilização Humana — A Visão Central
- O protocolo cria evidência técnica que suporta responsabilização
- Se VLS ≤ θ: o estado era compatível com autonomia → "o algoritmo não decidiu"
- Ref: Brass & Haggard (2008) — "whether" component,
       Caspar (2016) — sense of agency

---

## SEÇÃO 8 — ROADMAP: REFERENCE SENSOR SYSTEM

### 8.1 Limitações dos Consumer Wearables Atuais
- PPG error budget: ±20-40ms RMSSD (Bent 2020, Navalta 2020)
- Ausência de EDA na maioria dos smartwatches
- Sensor placement subótimo: pulso vs. palma para EDA
- Temperatura confundida por ambiente e posição

### 8.2 Reference Sensor Specification

| Sinal | Sensor ideal | Resolução mínima | Placement |
|-------|-------------|-----------------|-----------|
| RR intervals | ECG lead I ou II | 1ms | Tronco |
| EDA | GSR 2 eletrodos | 0.01 µS | Palma/dedos |
| Temperatura | Termistor + IR | 0.05°C | Múltiplos pontos |
| Tremor | IMU 6-DOF 1kHz | 0.001g | Punho dominante |
| SpO2 | PPG dual wavelength | 0.5% | Dedo ou testa |
| Temporal binding | Touch sensor capacitivo | 1ms | Superfície de interação |

### 8.3 Research Agenda

```
Fase 1 (atual):      Validar protocolo com sensores existentes
                     Watch 6 + WESAD (Empatica E4)
Fase 2 (2027):       Protótipo de pesquisa
                     Empatica E4 + Android custom + UniEvangelica lab
Fase 3 (2028+):      Hardware dedicado com certificação
Fase 4 (longo prazo): Miniaturização e integração comercial
```

---

## SEÇÃO 9 — DISCUSSION

### 9.1 Contribuições vs. Estado da Arte (tabela comparativa)

| Dimensão | WebAuthn | eIDAS High | ISO 30107 | VC/SSI | LICET |
|----------|---------|------------|-----------|--------|-------|
| Identidade | Parcial | Completa | N/A | Parcial | Via baseline |
| Presença física | Sim | Sim | Sim | Não | Sim |
| Liveness biológica | Limitado | Delegado | Sim | Não | Sim |
| Ausência de coerção | **Não** | **Não** | **Não** | **Não** | **Parcial** |
| Estado cognitivo | **Não** | **Não** | **Não** | **Não** | **Parcial** |
| Intenção voluntária | **Não** | **Não** | **Não** | **Não** | **Parcial** |
| Prova criptográfica | Sim | Sim | Não | Sim | Sim |
| Ledger imutável | Não | Não | Não | Não | **Sim** |

### 9.2 Posicionamento no Landscape de Pesquisa
- WESAD (Schmidt 2018): LICET como aplicação de segurança da linha de pesquisa
- BCI authentication: LICET como alternativa prática sem EEG
- Worldcoin/World ID: complementar (unicidade humana vs. estado volicional)

### 9.3 Limitações e Trabalho Futuro
*(honestidade completa sobre o que não foi resolvido)*

---

## SEÇÃO 10 — CONCLUSION

- O Intent Gap é um problema real, não resolvido por nenhum padrão existente
- Volitional Liveness como contribuição definitória ao campo
- Separação clara: o que foi provado vs. o que permanece como hipótese
- Chamada para adoção, extensão, e padronização pela comunidade

---

## REFERENCES — Consolidadas (50+ papers)

### Neurociência e Volição
1. Kornhuber & Deecke (1965). Pflügers Archiv. — Readiness Potential
2. Libet et al. (1983). Brain. — Conscious intention timing
3. Schurger et al. (2012). PNAS. — Accumulator model RP
4. Haggard (2019). Nature Reviews Neuroscience. — Neurocognitive basis of volition
5. Brass & Haggard (2008). Journal of Neuroscience. — What/When/Whether model
6. Caspar et al. (2016). Current Biology. — Coercion and sense of agency
7. Caspar et al. (2020). Psychological Science. — Coercion replication
8. Coricelli et al. (2005). Nature Neuroscience. — Regret and agency

### HRV e Cognição
9. Thayer & Lane (2000). Neuroscience & Biobehavioral Reviews. — Neurovisceral model
10. Thayer et al. (2012). Neuroscience & Biobehavioral Reviews. — HRV meta-analysis
11. Laborde et al. (2017). Frontiers in Psychology. — HRV methodological review
12. Hansen et al. (2003). Psychophysiology. — HRV and working memory
13. Appelhans & Luecken (2006). Psychosomatic Medicine. — HRV and emotional regulation
14. Porges (2007). Biological Psychology. — Polyvagal theory
15. Geisler et al. (2013). Biological Psychology. — HRV and self-regulation
16. Cribbet et al. (2014). Psychophysiology. — HRV and impulsivity

### EDA e Estado Afetivo
17. Boucsein (2012). Electrodermal Activity. Springer (2ª ed.). — Referência canônica EDA
18. Critchley (2002). Journal of Neuroscience. — EDA brain correlates
19. Braithwaite et al. (2013). Psychophysiology. — EDA analysis guide
20. Dawson et al. (2017). Handbook of Psychophysiology (Cambridge 4ª ed.). — EDA review

### Temperatura e Stress
21. Vinkers et al. (2013). Psychosomatic Medicine. — Temperature and stress
22. Kreibig (2010). Biological Psychology. — ANS activity in emotion (meta-review)
23. Neumann & Waldstein (2001). J. Psychosomatic Research. — Threat vs. challenge

### Stress Agudo e Decisão
24. Starcke & Brand (2012). Neuroscience & Biobehavioral Reviews. — Decision under stress
25. Porcelli & Delgado (2009). Psychological Science. — Stress and risk taking
26. Mather & Lighthall (2012). Current Directions in Psychological Science. — Stress and reward

### Fusão Multimodal e Wearables
27. Schmidt et al. (2018). ACM ICMI. — WESAD dataset
28. Kim & André (2008). IEEE TPAMI. — Emotion recognition multimodal
29. Wijsman et al. (2011). J. Neuroengineering and Rehabilitation. — Stress wearable
30. Smets et al. (2018). Sensors (MDPI). — Wild vs. lab physiological detection
31. Can et al. (2019). Frontiers in Computer Science. — Wearables stress survey
32. Gjoreski et al. (2017). IEEE Pervasive Computing. — Stress detection
33. Greco et al. (2017). IEEE TAFFC. — EDA and HRV classification

### Validação de Consumer Wearables
34. Bent et al. (2020). npj Digital Medicine. — Wearable HRV validation (referência principal)
35. Mannheimer et al. (2021). JMIR mHealth. — Fitzpatrick bias validation
36. Plews et al. (2017). IJSPP. — Polar vs. Apple Watch athletes
37. Navalta et al. (2020). IJES. — Wearable HRV systematic review
38. Stahl et al. (2016). JMIR mHealth. — Apple Watch 1 validation
38a. Xu, Liu, Liu, Su & Gu (2026). Sensors, 26(16):5192. — PPG-PRV vs ECG-HRV meta-analysis, RMSSD/HF systematic error
38b. Sinichi, Gevonden & Krabbendam (2025). Psychophysiology, 62(2):e70004. — Empatica E4 RMSSD accuracy collapse sob tarefa cognitiva/aritmética
38c. Wu, Gu, Yang & Luo (2019). Frontiers in Neuroscience, 13:1131. — Amusement vs. anger/fear HR/RMSSD (amusement = mais parassimpático, não parecido com stress)

### Ataques e Segurança Biométrica
39. Yan et al. (2020). IEEE TIFS. — Wearable authentication vulnerabilities
40. Conti et al. (2018). IEEE S&P. — BLE security
41. Biggio et al. (2012). ICML. — Poisoning attacks on SVM
42. Rubinstein et al. (2009). IMC. — Poisoning anomaly detectors
43. Barreno et al. (2006). ACM CCS. — Can ML be secure?
44. Li & Li (2019). ArXiv. — Adversarial Mahalanobis
45. Roth et al. (2022). NeurIPS. — Mahalanobis OOD detection
46. Golany & Radinsky (2019). AAAI. — PGANs ECG synthesis
47. Hazra & Byun (2020). Biology. — SynSigGAN physiological synthesis
48. Karimian et al. (2021). IEEE IoT Journal. — Sensor fingerprinting PPG
49. Bhidayasiri (2005). Parkinsonism & Related Disorders. — Tremor classification

### Padrões e Frameworks Legais
50. W3C WebAuthn Level 3 (2024). W3C Recommendation.
51. ISO/IEC 30107-1:2023. Biometric PAD — Framework.
52. ISO/IEC 30107-3:2023. Biometric PAD — Testing and reporting.
53. NIST SP 800-63-4 (2024). Digital Identity Guidelines.
54. EU Regulation 2024/1183. eIDAS 2.0 Amendment.
55. RFC 8032. Edwards-Curve Digital Signature Algorithm (EdDSA).
56. RFC 5869. HMAC-based Key Derivation Function (HKDF).
57. RFC 2104. HMAC: Keyed-Hashing for Message Authentication.
58. LGPD — Lei 13.709/2018. Art. 8 (consentimento), Art. 11 (dado sensível).
59. GDPR (EU) 2016/679. Art. 4(11), Art. 9.
60. E-SIGN Act. 15 U.S.C. §7001. Intent to sign.

### Criptografia
61. Schnorr (1991). Journal of Cryptology. — Schnorr signatures
62. Bernstein et al. (2011). — Ed25519
63. Krawczyk & Eronen. RFC 5869. — HKDF
64. Lamport (1981). — Hash chains

---

## NOTAS PARA REDAÇÃO

### Claim correto (validado pela pesquisa)
> "The LICET protocol attests that the subject's autonomic profile at the
> moment of authorization was consistent with voluntary, uncoerced,
> cognitively stable decision-making, as measured by a multivariate
> physiological profile (HRV/EDA/temperature/tremor) normalized to the
> individual's established baseline, and cryptographically bound to
> the authorization event via Ed25519 signature and immutable ledger."

### O que NUNCA afirmar no paper
- "Prova intenção consciente" → sensores periféricos são proxy, não prova direta
- "Impossível de falsificar" → existem vetores de ataque documentados
- "Detecta coerção" → detecta estado autonômico incompatível com volição

### Sequência de redação recomendada
1. Seção 3 (Threat Model) — mais técnica, menos sujeita a mudança
2. Seção 4 (Protocol Spec) — especificação formal existente
3. Seção 5 (Security Analysis) — inclui contribuição original (Ataque 4)
4. Seção 2 (Background) — baseada nas referências consolidadas
5. Seção 1 (Introduction) — redigir por último para refletir o paper completo
6. Seção 6 (Empirical) — depende da execução do WESAD experiment
7. Seções 7-10 — após validação empírica

### Afiliação institucional alvo
- UniEvangelica — Centro de Pesquisa e Tecnologia, Goiás
- Contato pendente para co-autoria ou orientação
- Necessário para submissão em IEEE TIFS / ACM CCS / USENIX Security
