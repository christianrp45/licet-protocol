[//]: # (SPDX-License-Identifier: Apache-2.0)

# LICET — Biological Sensor Device Matrix

*Versão: 1.0 | Data: 2026-07-09 | Autor: Christian Rodrigues Pereira / NeuroTrust*
*Contexto: Pesquisa exaustiva de dispositivos com sensores biológicos para integração ao protocolo LICET v2.0*

---

## Campos LICET Relevantes — Referência Rápida

| Campo LICET | Descrição | Tier mínimo |
|---|---|---|
| `physical-liveness` (key 18) | Sinal fisiológico capturado no momento do evento | T2 |
| `hrv-rmssd` | Root Mean Square of Successive Differences (ms) | T2 |
| `eda-tonic` | Nível de condutância eletrodérmica basal (µS) | T3 |
| `eda-phasic` | Respostas phasic (SCR — skin conductance response) | T3 |
| `ecg-morphology` | Morfologia da onda P-QRS-T (fingerprint anatômico) | T3/T4 |
| `skin-temp-deviation` | Desvio de temperatura em relação à baseline | T2 |
| `entropy-behavioral` | Entropia de padrões motores/tipagem | T1/T2 |
| Hardware Trust Anchor | Secure element com attestation | T3/T4 |

**Tiers LICET:**
- **T1** — Software only; nenhum hardware verificado
- **T2** — Wearable consumer com BLE; sem secure element certificado
- **T3** — Wearable/sensor com secure enclave ou chip certificado (EAL4+); precisão clínica
- **T4** — Dispositivo médico implantado ou BCI com hardware attestation formal

---

## CATEGORIA 1 — Wearables de Consumo

### 1.1 Apple Watch Series 10 / Ultra 2

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Apple Inc. |
| **Tier LICET** | T2/T3 |
| **Sinais** | PPG (HR, HRV), ECG 1-lead, EDA (sessões discretas), SpO2, skin temp, acelerômetro |
| **ECG** | 512 Hz; FDA-cleared; 30s de gravação |
| **EDA** | 4 eletrodos no verso; ~0.01–20 µS; 1 Hz (sessões Mindfulness) |
| **HRV RMSSD** | Correlação r=0.94 com Holter (npj Digital Medicine, 2021) |
| **Hardware anchor** | Secure Enclave no chip S10 (equivalente EAL4+) |
| **API/SDK** | HealthKit (`HKElectrocardiogram`, `HKQuantityTypeIdentifierElectrodermalActivity`); App Attest |
| **Latência** | <1s via BLE |
| **Custo** | Series 10: ~$399; Ultra 2: ~$799 |
| **Resistência à falsificação** | ALTA — ECG requer eletrodo físico em contato; EDA requer condutância galvânica real |
| **Limitação** | EDA não é streaming contínuo — coleta em sessões discretas |

**Campos LICET preenchíveis:**
- `physical-liveness`: PPG contínuo + acelerômetro
- `hrv-rmssd`: via HealthKit HKLiveWorkoutBuilder
- `eda-tonic`: via HKElectrodermalActivity (sessão pré-evento)
- `ecg-morphology`: snapshot 30s ECG (fingerprint T3)
- `skin-temp-deviation`: Series 8+

**Proposta de integração:**
```
1. Usuário inicia autorização LICET no iPhone
2. Apple Watch coleta 30s ECG + snapshot EDA
3. Dados processados no Secure Enclave do Watch
4. Hash criptográfico enviado ao iPhone via BLE autenticado
5. LICET Attester valida morfologia ECG + jitter HRV
```

---

### 1.2 Oura Ring Gen 4

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Oura Health (Finlândia) |
| **Tier LICET** | T2 |
| **Sinais** | PPG infravermelho (HR, HRV, SpO2), skin temp digital, acelerômetro, giroscópio |
| **HRV RMSSD** | Correlação r=0.96 com ECG Holter (Frontiers in Physiology, 2022) |
| **Diferencial** | PPG no dedo (artéria digital) — SNR superior ao PPG de pulso |
| **Sem EDA** | Ausência crítica para LICET |
| **Hardware anchor** | Nenhum secure element documentado |
| **API/SDK** | Oura API v2 (REST): `/v2/usercollection/hrv`; sem streaming em tempo real |
| **Latência** | ~5 min (sync periódico, não tempo real) |
| **Custo** | Gen 4: ~$349 + $5.99/mês |
| **Uso ideal** | Baseline biométrica noturna (HRV circadiano, temperatura) |

**Campos LICET preenchíveis:**
- `hrv-rmssd`: alta precisão (melhor que Apple Watch pelo posicionamento digital)
- `skin-temp-deviation`: muito preciso para baseline deviation
- `physical-liveness`: PPG digital contínuo

**Limitação:** Latência da API impede uso em tempo real durante evento de autorização.

---

### 1.3 WHOOP 4.0

| Atributo | Detalhe |
|---|---|
| **Fabricante** | WHOOP Inc. (Boston, MA) |
| **Tier LICET** | T2 (limitado por API fechada) |
| **Sinais** | PPG 5-LED (100 Hz), EDA/GSR (via Stress Monitor), skin temp, acelerômetro, giroscópio |
| **HRV RMSSD** | Correlação r=0.97 com Polar H10 (IJSPP, 2022) |
| **EDA** | Eletrodos no verso; habilitado via firmware no Stress Monitor |
| **Hardware anchor** | Nenhum documentado |
| **API/SDK** | WHOOP API v1 — HRV como campo agregado; **EDA não exposta publicamente** |
| **Custo** | ~$239 + $30/mês |
| **Limitação crítica** | API fechada impede integração direta; EDA raw inacessível |

**Estratégia de integração:** Parceria enterprise com WHOOP para acesso a dados granulares via SDK empresarial.

---

### 1.4 Fitbit Sense 2

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Google (Fitbit) |
| **Tier LICET** | T2 |
| **Sinais** | PPG (128 Hz), ECG 1-lead, EDA (EDA Scan sessions 3 min), skin temp, SpO2 |
| **EDA** | Via EDA Scan — **único wearable consumer com EDA via API pública aberta** |
| **ECG** | FDA-cleared; sensibilidade 98.7% para AFib |
| **Hardware anchor** | Nenhum documentado |
| **API/SDK** | Fitbit Web API (OAuth 2.0): inclui EDA scan; Google Health Connect (Android) |
| **Latência** | ~1 min (sync periódico) |
| **Custo** | ~$249 |

**Proposta de integração:**
```
Protocolo de "pré-autorização EDA":
- Usuário faz EDA Scan (3 min) antes do evento de alto risco
- Resultado incluído no token LICET como prova de estado emocional basal
- API: GET /1/user/-/activities/heart/date/today/1d/1sec.json
```

---

### 1.5 Samsung Galaxy Watch Ultra

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Samsung Electronics |
| **Tier LICET** | T2/T3 |
| **Sinais** | PPG (BioActive Sensor), ECG 1-lead, bioimpedância (BIA), skin temp, acelerômetro |
| **ECG** | FDA-cleared; BioActive Sensor com eletrodo no touchscreen |
| **Sem EDA** | BIA (bioimpedância) mas não EDA/GSR |
| **Hardware anchor** | **Knox Vault — Exynos W1000; Common Criteria EAL2+ (alguns perfis); equivalente EAL5+ para operações críticas** |
| **API/SDK** | Samsung Health SDK; Privileged Health SDK (parceria); Wear OS |
| **Latência** | <1s via BLE |
| **Custo** | ~$649 |
| **Diferencial** | Knox Vault = único wearable consumer com secure element com certificação formal |

**Proposta:**
```
Samsung Knox como Component Attester RATS:
- ECG fingerprint assinado pelo Knox Vault como evidência de liveness T3
- Knox attestation API disponível para enterprise
- Combinado com Galaxy S25 Ultra = stack T3 Android completo
```

---

### 1.6 Samsung Galaxy Ring

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Samsung Electronics |
| **Tier LICET** | T2 |
| **Sinais** | PPG óptico (HR, HRV, SpO2), skin temp, acelerômetro |
| **Sem ECG, sem EDA** | Focado em monitoramento de sono |
| **Hardware anchor** | Knox integrado no chipset |
| **API/SDK** | Samsung Health SDK; sem API pública independente |
| **Custo** | ~$399 (sem assinatura mensal com dispositivos Galaxy) |

---

### 1.7 Polar H10 (Cinta Torácica)

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Polar Electro (Finlândia) |
| **Tier LICET** | T2 (sinal T3-grade sem secure element) |
| **Sinais** | ECG torácico (1000 Hz), RR intervals (±1 ms), acelerômetro |
| **ECG** | **Padrão ouro de HRV em pesquisa** — 1000 Hz captura morfologia completa P-QRS-T |
| **HRV RMSSD** | Correlação r=0.999 com ECG de referência de 12 derivações |
| **Hardware anchor** | Nenhum |
| **API/SDK** | Polar BLE SDK (iOS/Android); UUID GATT aberto para ECG stream |
| **Latência** | <100 ms |
| **Custo** | ~$95 |

**Proposta:**
```
Polar H10 + iPhone Secure Enclave = Component Attester T3:
- H10 fornece ECG raw a 1000 Hz — melhor fingerprint anatômico disponível
- iPhone assina com Secure Enclave
- Ideal para eventos de altíssimo risco (trigger manual T3/T4)
```

---

## CATEGORIA 2 — Dispositivos Médicos Portáteis

### 2.1 AliveCor KardiaMobile 6L

| Atributo | Detalhe |
|---|---|
| **Fabricante** | AliveCor Inc. (Mountain View, CA) |
| **Tier LICET** | T3 |
| **Sinais** | **ECG 6 derivações** (I, II, III, aVR, aVL, aVF); 300 Hz; FDA-cleared Class II |
| **Acurácia** | AFib: sensibilidade 99%, especificidade 97% (JAMA Cardiology, 2019); QTc: r=0.98 |
| **Resistência à falsificação** | MUITO ALTA — 6 derivações + 3 pontos de contato físico simultâneos |
| **Hardware anchor** | Processamento no smartphone (Secure Enclave iPhone / Knox Android) |
| **API/SDK** | KardiaMobile SDK (parceiros); KardiaAPI (HL7 FHIR) |
| **Custo** | ~$149 + $99/ano KardiaCare |

**Proposta de integração T3:**
```
Evento de alto risco dispara solicitação de ECG KardiaMobile 6L:
1. Usuário coloca dispositivo em posição padrão (30s)
2. ECG 6-lead raw processado para vector de morphology
3. Comparação com baseline armazenada criptograficamente
4. Fingerprint assinado pelo Secure Enclave iPhone
5. Score de similaridade incluído no token LICET como ecg-morphology T3
```

---

### 2.2 Dexcom G7 / Abbott FreeStyle Libre 3 (CGM)

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Dexcom Inc. / Abbott Laboratories |
| **Tier LICET** | T3 |
| **Sinais** | Glicose intersticial (mg/dL); tendência glicêmica; 1 leitura/min |
| **Invasividade** | Sensor de 0.4 mm inserido no braço; semipermanente 10-14 dias |
| **Acurácia** | Dexcom G7: MARD 8.2%; FDA iCGM clearance |
| **Resistência à falsificação** | **MÁXIMA** — requer sensor físico inserido sob a pele; impossível replay attack |
| **Hardware anchor** | Nenhum no sensor; transmissor BLE |
| **API/SDK** | Dexcom Developer API (REST, OAuth 2.0); latência ~3 min |
| **Custo** | G7: ~$89/mês; Libre 3: ~$75/mês |

**Novo campo LICET proposto:**
```json
"glucose-liveness": {
  "value_mg_dl": 94,
  "trend": "stable",
  "delta_15min": 2,
  "sensor_age_hours": 72,
  "sensor_type": "dexcom-g7-subcutaneous",
  "confidence": "subcutaneous-verified"
}
```

---

### 2.3 Empatica E4 / Embrace Plus

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Empatica Inc. (Boston, MA / Milão) |
| **Tier LICET** | T3 (padrão ouro de pesquisa) |
| **Sinais** | **EDA a 64 Hz** (Ag/AgCl), BVP/PPG a 64 Hz, skin temp a 4 Hz, acelerômetro a 32 Hz |
| **EDA** | **Padrão ouro — correlação r=0.97 com eletrodos de gel clínicos** |
| **HRV** | De BVP a 64 Hz — alta resolução temporal |
| **Hardware anchor** | Nenhum |
| **API/SDK** | E4 BLE streaming; Empatica Connect REST; OSC/LSL para pesquisa |
| **Latência** | <100 ms |
| **Custo** | E4: ~$2.500; Embrace Plus: ~$1.900/ano |

**Papel no LICET:** Dispositivo de **referência e validação clínica** — base para calibrar e validar os algoritmos Mahalanobis contra outros wearables.

**Campos LICET preenchíveis (mais completos de qualquer wearable não-invasivo):**
- `eda-tonic` + `eda-phasic`: 64 Hz — detecta SCRs com fidelidade clínica
- `hrv-rmssd`: de BVP a 64 Hz
- `skin-temp-deviation`: contínuo

---

### 2.4 BioIntelliSense BioButton / BioSticker

| Atributo | Detalhe |
|---|---|
| **Fabricante** | BioIntelliSense Inc. (Centennial, CO) |
| **Tier LICET** | T3 |
| **Sinais** | ECG 1-lead (500 Hz), respiração (impedância), skin temp (±0.2°C), acelerômetro |
| **Uso** | Patch adesivo peitoral; 7-30 dias de uso contínuo; FDA-cleared para uso hospitalar e domiciliar |
| **API/SDK** | BioCloud API (HL7 FHIR); integra com Epic, Cerner |
| **Custo** | ~$99/patch (7 dias) |
| **Uso ideal no LICET** | Baseline biométrica de ECG-morphology ultra-robusta (7-30 dias de dados) |

---

## CATEGORIA 3 — Implantes e Dispositivos Subcutâneos

### 3.1 Pacemakers / ICDs com Telemetria

| Atributo | Detalhe |
|---|---|
| **Fabricantes** | Medtronic, Abbott (St. Jude), Boston Scientific, Biotronik |
| **Tier LICET** | T4 |
| **Sinais** | EGM intracardíaco (eletrodos endocárdicos), acelerômetro, impedância torácica, temperatura interna |
| **ECG** | Sinal 100-1000x mais limpo que ECG de superfície — **fingerprint anatômico mais preciso possível** |
| **Resistência à falsificação** | **IMPOSSÍVEL sem cirurgia cardíaca** |
| **API/SDK** | Medtronic CareLink (HL7 FHIR para alguns partners); sem API de developer |
| **Custo** | Cirúrgico — coberto por seguro saúde |
| **Desafio crítico** | Latência de 24h; parceria com fabricante obrigatória; questões éticas com população vulnerável |

---

## CATEGORIA 4 — EEG e Brain-Computer Interfaces (BCIs)

### 4.1 Neuralink N1

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Neuralink Corp. (Fremont, CA) |
| **Tier LICET** | T4 |
| **Status** | First-in-human PRIME Study; FDA breakthrough device 2023; 8+ pacientes (2025) |
| **Sinais** | 1024 eletrodos neurais; action potentials individuais (20 kHz/canal); LFP (1-300 Hz) |
| **Resistência à falsificação** | **ABSOLUTA** — requer implante cirúrgico (craniotomia) |
| **API/SDK** | Nenhuma pública (2025); BCI SDK anunciado para parceiros |
| **Custo** | Procedimento cirúrgico; não comercializado; estimativa futura $10k-50k |
| **Timeline LICET** | 2027-2030 para integração prática |

**Campos LICET potenciais:**
```json
"neural-liveness": {
  "action_potential_signature": "...",
  "cognitive_state": "alert-focused",
  "coercion_indicator": "none-detected",
  "lfp_amygdala_arousal": 0.12
}
```

---

### 4.2 OpenBCI Cyton + Daisy (16 canais)

| Atributo | Detalhe |
|---|---|
| **Fabricante** | OpenBCI Inc. (Nova York, NY) |
| **Tier LICET** | T3 |
| **Sinais** | EEG 16 canais; 250 Hz; 24-bit ADC; chip ADS1299 (Texas Instruments) |
| **Hardware** | Open-source — esquemático e firmware públicos |
| **API/SDK** | BrainFlow SDK (Python/C++/Java/C#); OpenBCI GUI com LSL |
| **Latência** | <4 ms |
| **Custo** | Cyton: ~$1.499 + capacete ~$200-500 |

**Proposta revolucionária para LICET — P300 Liveness Challenge:**
```
1. LICET exibe sequência de caracteres aleatória na tela
2. Usuário observa conscientemente
3. EEG registra P300 para cada caractere alvo (resposta involuntária única)
4. Timestamp do P300 vinculado ao evento de autorização
5. P300 impossível de simular sem atenção consciente real
```

```json
"neural-liveness": {
  "p300_latency_ms": 312,
  "p300_amplitude_uv": 8.4,
  "alpha_power_relative": 0.42,
  "cognitive_state": "alert-focused",
  "device": "openbci-cyton-16ch"
}
```

---

### 4.3 Emotiv EPOC X

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Emotiv Inc. (San Francisco, CA) |
| **Tier LICET** | T2/T3 |
| **Sinais** | EEG 14 canais; 256 Hz; Performance Metrics (valência, arousal, engajamento) |
| **API/SDK** | Cortex API (WebSocket); Emotiv SDK para EEG raw |
| **Custo** | EPOC X: ~$849 + SDK $299/ano |

---

### 4.4 Muse S

| Atributo | Detalhe |
|---|---|
| **Fabricante** | InteraXon Inc. (Toronto) |
| **Tier LICET** | T2 |
| **Sinais** | EEG 4 canais (256 Hz), PPG, acelerômetro, giroscópio |
| **API/SDK** | LibMuse SDK (Android); OSC; BrainFlow |
| **Custo** | ~$349 |
| **Diferencial** | Melhor ergonomia entre BCIs — headband forma-fator similar a fone de ouvido |

---

## CATEGORIA 5 — rPPG (Fotopletismografia Remota via Câmera)

### 5.1 Binah.ai

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Binah.ai (Israel/EUA) |
| **Tier LICET** | T1 |
| **Sinais** | HR (±3 bpm), HRV SDNN/RMSSD (±10 ms), SpO2 (±2%), frequência respiratória, stress score |
| **Método** | rPPG via câmera frontal; 30s de vídeo |
| **FDA** | Breakthrough designation (alguns módulos); CE Mark |
| **API/SDK** | iOS, Android, Web (JavaScript); REST API |
| **Custo** | $2-10/usuário/mês (enterprise) |
| **Resistência à falsificação** | BAIXA — vulnerável a deepfakes de vídeo |

**Uso no LICET:** First-factor liveness T1 sem hardware adicional; nunca usar como único sinal em T3/T4.

---

### 5.2 Apple Face ID (TrueDepth Camera)

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Apple Inc. |
| **Tier LICET** | T2/T3 |
| **Sinais** | Geometria 3D facial (30.000 pontos IR); detecção de liveness com movimentos aleatórios |
| **Hardware anchor** | Secure Enclave — chave liberada apenas após autenticação biométrica bem-sucedida |
| **API/SDK** | LocalAuthentication (`LAContext.evaluatePolicy`); dados raw não acessíveis a terceiros |

**Proposta:**
```swift
// Face ID como gate para chave de sessão LICET
let context = LAContext()
context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, ...)
// Secure Enclave libera chave privada → assina claim LICET
```

---

## CATEGORIA 6 — Biometria Comportamental (Teclado/Mouse)

### 6.1 TypingDNA

| Atributo | Detalhe |
|---|---|
| **Fabricante** | TypingDNA (Romênia) |
| **Tier LICET** | T1 |
| **Sinais** | Keystroke dynamics: dwell time, flight time, digraph latency (não captura caracteres) |
| **Acurácia** | EER ~3-5% (texto livre); <1% (texto fixo) |
| **Resistência à falsificação** | Moderada — bots replicam timing médio; microvariações <5ms são difíceis |
| **GDPR** | Compliant — armazena apenas timings, não conteúdo |
| **API/SDK** | JavaScript SDK (browser); REST API |
| **Custo** | Free tier disponível; enterprise sob consulta |

**Proposta — implementação T1 de custo zero:**
```
Durante interação de autorização:
1. TypingDNA JS SDK captura timings enquanto usuário digita frase de autorização
2. Comparação com baseline do usuário
3. Score de matching incluído em entropy-behavioral

Novo campo LICET:
"keystroke-entropy": {
  "dwell_mean_ms": 87,
  "flight_coefficient_of_variation": 0.34,
  "entropy_bits": 4.2,
  "session_match_score": 0.91,
  "provider": "typingdna-v3"
}
```

---

### 6.2 BioCatch

| Atributo | Detalhe |
|---|---|
| **Fabricante** | BioCatch (Israel) |
| **Tier LICET** | T1 |
| **Sinais** | Keystroke + mouse movement + touch patterns — behavioral biometrics enterprise |
| **Uso atual** | Prevenção de fraude em bancos (Barclays, Citi, HSBC) |
| **API/SDK** | Enterprise SDK — integração via parceria |

---

### 6.3 Fujitsu PalmSecure

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Fujitsu Ltd. (Japão) |
| **Tier LICET** | T3 (como identity anchor) |
| **Sinais** | Padrão de veias palmares por infravermelho próximo (850 nm) |
| **Acurácia** | FAR <0.00008%; FRR <0.01% — entre os mais precisos sistemas biométricos existentes |
| **Liveness** | Natural — requer mão viva com circulação sanguínea ativa |
| **Papel no LICET** | Complemento/substituto para ECG morphology na Layer 1 (identity anchor) |

---

## CATEGORIA 7 — Smartphones com Sensores Avançados

### 7.1 iPhone 15 Pro / 16 Pro

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Apple Inc. |
| **Tier LICET** | T2/T3 |
| **Sensores relevantes** | TrueDepth IR (Face ID), LiDAR, acelerômetro/giroscópio, barômetro |
| **Hardware anchor** | **Secure Enclave (T2 chip)** — nunca exporta chaves privadas; equivalente FIPS 140-2 Level 3 |
| **API/SDK** | LocalAuthentication; App Attest API; DeviceCheck; HealthKit |

**Arquitetura LICET no iPhone:**
```
iPhone como Lead Attester no modelo RATS Composite Device:
- Face ID = liveness detection com 3D IR (anti-deepfake)
- Secure Enclave = hardware trust anchor T3
- HealthKit = data layer para wearables (Apple Watch, Oura, Dexcom)
- App Attest = prova de integridade do app LICET
```

---

### 7.2 Samsung Galaxy S25 Ultra

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Samsung Electronics |
| **Tier LICET** | T2/T3 |
| **Sensores relevantes** | Fingerprint ultrassônico 3D (Qualcomm 3D Sonic Max), câmera frontal |
| **Hardware anchor** | **Knox Vault** — Common Criteria EAL5+ em alguns modelos |
| **API/SDK** | Samsung Knox Attestation API; Samsung Health SDK; Google SafetyNet |

---

## CATEGORIA 8 — Dispositivos Industriais e Militares

### 8.1 Zephyr BioHarness 3.0

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Medtronic (adquiriu Zephyr Technology) |
| **Tier LICET** | T3 |
| **Sinais** | ECG têxtil (250 Hz), respiração (impedância), skin temp, acelerômetro, postura |
| **Certificação** | IP67; MIL-STD-810 (durabilidade militar) |
| **API/SDK** | BioHarness BT SDK; Zephyr OmniSense REST API; ANT+ |
| **Uso** | USSOCOM; controle de infraestrutura crítica; operadores nucleares |
| **Custo** | ~$800 |

---

### 8.2 Hexoskin Smart Shirt

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Hexoskin / Carré Technologies (Montreal, Canada) |
| **Tier LICET** | T2/T3 |
| **Sinais** | ECG têxtil (256 Hz), respiração torácica + abdominal, acelerômetro |
| **API/SDK** | Hexoskin API (REST + OAuth 2.0); Hexoskin Libre (dados raw); LSL |
| **Custo** | Camiseta ~$499 + módulo ~$399 |

---

### 8.3 Masimo Root + Rainbow SET

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Masimo Corporation (Irvine, CA) |
| **Tier LICET** | T3/T4 (ambiente clínico) |
| **Sinais** | SpO2 (±1.5%), hemoglobina total (SpHb), metahemoglobina (SpMet), carboxihemoglobina (SpCO), frequência respiratória |
| **Diferencial** | 8 comprimentos de onda — detecta intoxicação por CO, drogas que alteram estado de consciência |
| **API/SDK** | HL7 FHIR |
| **Relevância LICET** | SpMet + SpCO detectam envenenamento/drogas — suporte direto ao pharmacological attack pattern detection |

---

## CATEGORIA 9 — Tecnologias Emergentes (2025-2026)

### 9.1 Radar Biométrico mmWave (Google Soli)

| Atributo | Detalhe |
|---|---|
| **Tecnologia** | Radar FMCW 57-64 GHz sem contato |
| **Sinais** | HR (±2 bpm), frequência respiratória (±1 rpm), HRV (±5 ms em condições ideais), micro-movimentos |
| **Produtos** | Google Nest Hub Gen 2 (ativo); TI IWR6843; Infineon BGT60TR13C |
| **Tier LICET** | T1/T2 |
| **Resistência à falsificação** | Moderada — requer presença física real |

```json
"radar-liveness": {
  "heart_rate_bpm": 68,
  "respiratory_rate_rpm": 14,
  "presence_confirmed": true,
  "sensor_type": "mmwave-60ghz"
}
```

---

### 9.2 PKvitality K'Watch Glucose (Glicose Não-Invasiva)

| Atributo | Detalhe |
|---|---|
| **Fabricante** | PKvitality (França) |
| **Tier LICET** | T2/T3 |
| **Tecnologia** | Micro-agulhas de 0.5 mm no verso do relógio — glicose intersticial sem CGM implantado |
| **Disponibilidade** | Europa, 2024 |
| **Custo** | ~€499 |
| **Relevância** | Sinal glicêmico em wearable = autenticidade biológica sem implante de 14 dias |

---

### 9.3 E-Tattoos de Grafeno (EDA de Alta Precisão)

| Atributo | Detalhe |
|---|---|
| **Pesquisa** | University of Texas Austin; Nature Nanotechnology, 2022 |
| **Tecnologia** | Sensores de grafeno aplicados diretamente na pele — resistência de interface 10x menor que gel |
| **Sinais** | EDA com precisão de laboratório; ECG/EMG simultâneos |
| **Status** | Pesquisa pré-comercial; produto consumer estimado para 2027-2030 |
| **Tier LICET potencial** | T3 (precisão clínica sem implante) |

---

### 9.4 Kernel Flow (fNIRS)

| Atributo | Detalhe |
|---|---|
| **Fabricante** | Kernel (Los Angeles, CA) |
| **Tier LICET** | T3 |
| **Tecnologia** | fNIRS (near-infrared spectroscopy) com 52 optodes — mede perfusão hemoglobínica cerebral |
| **Sinais** | Oxigenação prefrontal (atenção, tomada de decisão), state cognitivo |
| **Custo** | ~$5.000 (pesquisa) |

```json
"fnirs-prefrontal": {
  "oxy_hb_delta_micromolar": 0.23,
  "deoxy_hb_delta_micromolar": -0.18,
  "attention_index": 0.67,
  "cognitive_state": "alert-focused",
  "device": "kernel-flow"
}
```

---

## Matriz Comparativa Consolidada

### Cobertura de Sinais por Dispositivo

| Dispositivo | HR/PPG | HRV RMSSD | EDA | ECG Morph. | Skin Temp | SpO2 | Neural | Tier |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Apple Watch S10 | ✅ | ✅ | ⚠️¹ | ✅ 1-lead | ✅ | ✅ | — | T2/T3 |
| Oura Ring Gen 4 | ✅ | ✅ | — | — | ✅ | ✅ | — | T2 |
| WHOOP 4.0 | ✅ | ✅ | ⚠️² | — | ✅ | ✅ | — | T2 |
| Fitbit Sense 2 | ✅ | ✅ | ✅ | ✅ 1-lead | ✅ | ✅ | — | T2 |
| Samsung Galaxy Watch Ultra | ✅ | ✅ | — | ✅ 1-lead | ✅ | ✅ | — | T2/T3³ |
| Polar H10 | ✅ | ✅✅ | — | ✅ 1-lead | — | — | — | T2⁴ |
| Empatica E4 | ✅ | ✅✅ | ✅✅ | — | ✅ | — | — | T3 |
| AliveCor KardiaMobile 6L | — | ✅ | — | ✅✅ 6-lead | — | — | — | T3 |
| Dexcom G7 / Libre 3 | — | — | — | — | — | — | — | T3⁵ |
| Implante cardíaco | ✅ | ✅ | — | ✅✅ EGM | — | — | — | T4 |
| Neuralink N1 | — | ✅ | — | — | — | — | ✅✅ | T4 |
| OpenBCI (16ch) | — | — | — | — | — | — | ✅ | T3 |
| Muse S | ✅ | ✅ | — | — | — | — | ✅ | T2 |
| Binah.ai (rPPG) | ⚠️ | ⚠️ | — | — | — | ⚠️ | — | T1 |
| TypingDNA | — | — | — | — | — | — | — | T1⁶ |
| Zephyr BioHarness | ✅ | ✅ | — | ✅ | ✅ | — | — | T3 |
| Masimo Rainbow | ✅ | ✅ | — | — | — | ✅✅ | — | T3/T4 |
| Radar mmWave | ✅ | ⚠️ | — | — | — | — | — | T1 |

**Notas:**
1. ⚠️ EDA em sessões discretas (Mindfulness app); acesso via HealthKit
2. ⚠️ EDA via Stress Monitor — API não exposta publicamente
3. Knox Vault = hardware attestation certificado (diferencial único em wearable consumer)
4. ✅✅ Melhor HRV; ECG raw a 1000 Hz; mas sem secure element
5. Glicose subcutânea = alta confiança biológica sem ECG/HRV
6. Behavioral biometric; cobre entropy-behavioral sem hardware adicional
✅✅ = padrão ouro na categoria

---

### Viabilidade de Integração

| Dispositivo | API Pública | SDK | Tempo Real | Secure Element | Custo | Viabilidade |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Apple Watch S10 + iPhone | ✅ | ✅ | <1s | ✅ Secure Enclave | $399 | **MUITO ALTA** |
| Fitbit Sense 2 | ✅ | ✅ | ~1 min | — | $249 | **ALTA** |
| Samsung Galaxy Watch Ultra | ✅ | ✅ | <1s | ✅ Knox EAL5+ | $649 | **ALTA** |
| Polar H10 | ✅ GATT | ✅ | <100 ms | — | $95 | **ALTA** |
| TypingDNA | ✅ | ✅ JS SDK | <1s | — | $0 extra | **MUITO ALTA** |
| Dexcom G7 | ✅ | ✅ | 3 min | — | $89/mês | **ALTA** |
| Oura Ring Gen 4 | ✅ | — | ~5 min | — | $349 | **MÉDIA** |
| AliveCor KardiaMobile 6L | Parceiro | Parceiro | 30s coleta | — | $149 | **MÉDIA** |
| Empatica E4 | ✅ | ✅ | <100 ms | — | $2.500 | **PESQUISA** |
| Muse S | ✅ | ✅ | <100 ms | — | $349 | **ALTA** |
| OpenBCI Cyton | ✅ | ✅ open | <4 ms | — | $1.700 | **MÉDIA** |
| Neuralink N1 | Parceiro futuro | — | <1 ms | ✅ Chip N1 | cirúrgico | **FUTURA** |

---

## Stack Recomendado por Tier

### T1 — Implementação imediata, custo zero
```
TypingDNA SDK (keystroke dynamics)
+ Binah.ai SDK (rPPG via câmera)
+ Acelerômetro do smartphone

Campos LICET: entropy-behavioral, physical-liveness (básico)
Tempo de implementação: ~1 semana
```

### T2 — Wearable consumer (disponível hoje)
```
OPÇÃO A (iOS):  Apple Watch S10 + iPhone (HealthKit + Secure Enclave + App Attest)
OPÇÃO B (Android):  Samsung Galaxy Watch Ultra + Galaxy S25 Ultra (Knox Vault)
OPÇÃO C (universal):  Fitbit Sense 2 (única API pública com EDA)

Campos LICET: hrv-rmssd + eda-tonic + skin-temp-deviation + ecg-morphology (1-lead)
```

### T3 — Precisão clínica
```
OPÇÃO A (não-invasivo máximo):
Empatica E4 (EDA padrão ouro)
+ KardiaMobile 6L (ECG 6 derivações)
+ iPhone 16 Pro (Secure Enclave + Face ID + App Attest)

OPÇÃO B (integrada ao smartphone):
Apple Watch Ultra 2 + iPhone 16 Pro + TypingDNA

Todos os campos LICET populados com precisão clínica
```

### T4 — Hardware implantado (roadmap 2027+)
```
Implante cardíaco Medtronic/Abbott (EGM intracardíaco)
+ CGM Dexcom G7 (glicose intersticial)
+ Neuralink N1 (futuro)

Requer: parceria com fabricante + aprovação regulatória específica
Uso: infraestrutura crítica; prescrição médica autônoma de alto risco
```

---

## Novos Campos LICET Propostos (v2.1)

```json
{
  "licet_extension_bio_v2_1": {
    "glucose-liveness": {
      "value_mg_dl": 94,
      "trend": "stable",
      "delta_15min": 2,
      "sensor_type": "dexcom-g7-subcutaneous",
      "sensor_age_hours": 72,
      "confidence": "subcutaneous-verified"
    },
    "keystroke-entropy": {
      "dwell_mean_ms": 87,
      "flight_coefficient_of_variation": 0.34,
      "entropy_bits": 4.2,
      "session_match_score": 0.91,
      "provider": "typingdna-v3"
    },
    "radar-liveness": {
      "heart_rate_bpm": 68,
      "respiratory_rate_rpm": 14,
      "presence_confirmed": true,
      "sensor_type": "mmwave-60ghz"
    },
    "neural-liveness": {
      "p300_latency_ms": 312,
      "alpha_power_relative": 0.42,
      "cognitive_state": "alert-focused",
      "device": "openbci-cyton-16ch"
    },
    "fnirs-prefrontal": {
      "oxy_hb_delta_micromolar": 0.23,
      "attention_index": 0.67,
      "device": "kernel-flow"
    },
    "spectral-oximetry": {
      "spo2_percent": 98,
      "met_hb_percent": 0.3,
      "co_hb_percent": 0.8,
      "pharmacological_flags": [],
      "device": "masimo-rainbow"
    }
  }
}
```

---

## Arquitetura RATS — Hierarquia de Component Attesters

```
Composite Attester (LICET Hub — smartphone)
├── Component Attester A: Wearable
│   ├── Apple Watch S10 / Samsung Galaxy Watch Ultra
│   ├── Evidence: HRV RMSSD timeseries + EDA + ECG
│   └── Attestation Key: Secure Enclave / Knox Vault
├── Component Attester B: Sensor de precisão
│   ├── KardiaMobile 6L / Empatica E4 / Polar H10
│   ├── Evidence: ECG morphology vector (6-lead) / EDA 64 Hz
│   └── Attestation: hash assinado pelo smartphone hub
├── Component Attester C: Behavioral
│   ├── TypingDNA SDK
│   ├── Evidence: keystroke entropy score
│   └── Attestation: signed by app (App Attest / Knox)
├── Component Attester D: Metabólico (opcional)
│   ├── Dexcom G7 / FreeStyle Libre 3
│   ├── Evidence: glucose-liveness (subcutaneous-verified)
│   └── Attestation: Dexcom API OAuth token
└── Verifier: LICET Server
    ├── Verifica: cada Evidence individualmente
    ├── Fusão: Mahalanobis distance multi-canal
    └── Emite: LICET Authorization Token
```

---

*Próxima revisão: quando dispositivos da geração 2025-2026 (Apple Watch Series 11, Samsung Galaxy Watch 8) forem lançados com specs completas.*
*Referência: RFC 9334 (RATS Architecture); LICET v2.0 spec; CPoE draft-condrey-cpoe-protocol*
