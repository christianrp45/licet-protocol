[//]: # (SPDX-License-Identifier: Apache-2.0)

# LICET — Security Considerations: Análise Exaustiva de Gaps

*Versão: 1.0 | Data: 2026-07-09 | Autor: Christian Rodrigues Pereira / NeuroTrust*
*Contexto: Documento de Security Considerations para o IETF draft-pereira-licet-human-intent*
*Total de gaps identificados: 45 | Dimensões: 7*

> **Nota sobre enquadramento:** O LICET deve ser consistentemente apresentado como
> "elevador do custo de subversão" e "evidência técnica de estado fisiológico" —
> jamais como "prova de intenção genuína" ou "detector de coerção".
> Essa distinção semântica é o que torna o protocolo juridicamente defensável.

---

## Sumário por Dimensão

| Dimensão | Gaps | Críticos | Insolúveis |
|---|:---:|:---:|:---:|
| C — Criptografia | 7 | 1 | 0 |
| B — Biometria e Saúde | 9 | 3 | 1 |
| H — Hardware | 5 | 0 | 0 |
| L — Legal e Regulatório | 6 | 2 | 0 |
| A — IA e Automação | 5 | 2 | 1 |
| O — Operacional | 6 | 1 | 0 |
| I — Estruturalmente Impossíveis | 8 | 5 | 8 |
| **Total** | **46** | **14** | **9** |

---

## DIMENSÃO C — CRIPTOGRAFIA

---

### GAP-C01 — ZKP Schnorr: Witness Computável Publicamente

**Severidade:** CRÍTICA

**Descrição:** O witness `w = SHA256(σ || h)` é derivado deterministicamente de `σ` (biometric signature) e `h` (intent hash), ambos armazenados no ledger e acessíveis a qualquer observador. Qualquer pessoa pode recalcular `w`, reconstruir `PK = w·G`, e verificar — ou forjar — provas. O Schnorr não demonstra posse de conhecimento exclusivo.

**Natureza:** Falha de design criptográfico. Um ZKP genuíno exige que o witness seja um segredo que o prover conhece exclusivamente.

**Mitigação:** Reestruturar o proof para que o witness seja `w = HKDF(k_m, σ || h)`, onde `k_m` é a chave mestre do servidor — nunca armazenada no ledger e inacessível a observadores. Alternativa: migrar para zk-SNARKs (Groth16/PLONK) com circuit auditável independentemente do witness.

**Prioridade de implementação:** IMEDIATA

---

### GAP-C02 — HMAC como "Biometric Signature": Não é Assinatura Verificável por Terceiros

**Severidade:** ALTA

**Descrição:** `σ = HMAC-SHA256(h || D_M || ρ_ECG || verdict || ℓ || ts, k_s)` é um MAC simétrico. O servidor que calcula `k_s = HKDF(k_m, h)` é simultaneamente gerador e verificador — pode forjar qualquer `σ` para qualquer entrada. Terceiros auditando o ledger não podem verificar `σ` sem acesso a `k_m`.

**Natureza:** Confusão arquitetural entre autenticação simétrica e assinatura assimétrica verificável. Para não-repúdio e auditabilidade de terceiros, é necessária assinatura assimétrica (Ed25519/ECDSA) com chave privada sob controle exclusivo da entidade atestante.

**Mitigação:** Assinatura EdDSA/ECDSA com chave privada no TEE (Secure Enclave/TPM/HSM), chave pública publicada em certificado verificável. O HMAC pode permanecer como mecanismo de integridade interno, mas não deve ser apresentado como "biometric signature" auditável.

**Prioridade:** IMEDIATA

---

### GAP-C03 — Hash-Chained Ledger: Integridade sem Irretratabilidade

**Severidade:** ALTA

**Descrição:** O ledger usa `L_n = SHA256(entry_n || L_{n-1})`. Detecta modificações retroativas mas não impede que o servidor reescreva toda a cadeia. Sem âncora externa, não há prova de que o ledger é completo ou original.

**Mitigação:** Publicar Merkle root periodicamente em log de transparência externo (RFC 6962 Certificate Transparency, OpenTimestamps, Ethereum event logs). O LICET já usa OpenTimestamps para o documento original — aplicar o mesmo padrão ao ledger em produção.

---

### GAP-C04 — Timestamp sem Fonte de Tempo Verificável

**Severidade:** MÉDIA-ALTA

**Descrição:** O protocolo não especifica quem gera o timestamp, com qual precisão e qual fonte de tempo confiável. Um cliente malicioso pode submeter timestamps retroativos ou futuros, comprometendo o replay resistance.

**Mitigação:** RFC 3161 (Trusted Timestamp Authority) ou geração de timestamp pelo servidor vinculada ao nonce da sessão. Nenhuma confiança deve ser depositada em timestamps fornecidos pelo cliente.

---

### GAP-C05 — Quantum Threat: BN128, HMAC-SHA256

**Severidade:** MÉDIA (horizonte de 10-15 anos)

**Descrição:** BN128 é vulnerável ao algoritmo de Shor. HMAC-SHA256 e SHA-256 têm resistência parcial (Grover reduz de 256 para 128 bits efetivos). Risco de harvest-now-decrypt-later: adversários capturam entradas do ledger hoje e quebram provas ZKP quando hardware quântico estiver disponível.

**Mitigação:** Migração para NIST PQC standards (FIPS 203/204/205 — ML-KEM, ML-DSA, SLH-DSA). Para ZKPs, migração para STARKs (baseados em hash, conjecturalmente quantum-safe).

---

### GAP-C06 — Replay Attack via Timestamp de Granularidade Insuficiente

**Severidade:** BAIXA-MÉDIA

**Descrição:** Se dois eventos com `a`, `id_A`, `tgt` idênticos ocorrem dentro de 1 segundo, o intent hash `h` pode colidir, resultando em `k_s` e `σ` idênticos — permitindo replay.

**Mitigação:** Timestamps com precisão de milissegundo/nanossegundo + nonce aleatório no intent hash: `h = SHA256(a || id_A || tgt || ts_ns || nonce || ℓ)`.

---

### GAP-C07 — Side-Channel na Computação Mahalanobis

**Severidade:** BAIXA

**Descrição:** A inversão da matriz de covariância `S^{-1}` varia em tempo de execução. Um adversário que mede latência da API pode inferir propriedades dos sinais biométricos submetidos.

**Mitigação:** Constant-time computation para operações criptográficas; padding artificial de latência de resposta.

---

## DIMENSÃO B — BIOMETRIA E SAÚDE

---

### GAP-B01 — Respiração Compassada (Volitional Vagal Enhancement): Ataque Primário

**Severidade:** CRÍTICA / SEM MITIGAÇÃO ROBUSTA CONHECIDA

**Descrição:** Um sujeito treinado em respiração ressonante a ~0.1 Hz (6 ciclos/min) produz um vetor fisiológico genuinamente calmo — RMSSD elevado, potência HF elevada, EDA reduzida, FC reduzida, temperatura estável — indistinguível de calma genuína pela distância Mahalanobis. A técnica é ensinável em 6-8 semanas via apps de biofeedback de HRV (HeartMath, Elisi).

**Natureza:** O sujeito literalmente produz o estado fisiológico de calma enquanto está sob coerção — não é falsificação, é manufatura volitiva do estado alvo.

**Mitigação especulativa (não validada):** Detectar pico espectral estreito em 0.1 Hz no espectro de potência RR-interval (calma genuína = HRV broadband; respiração ressonante = pico monocromático). Um adversário sofisticado pode variar a frequência para mascarar o pico.

**Declaração obrigatória:** Este gap deve ser nomeado como **limitação primária** em todos os documentos técnicos e legais do LICET.

*Referência:* Laborde, S. et al. (2022). Psychophysiology. DOI: 10.1111/psyp.13952

---

### GAP-B02 — ECG Replay: Ausência de Verificação Temporal

**Severidade:** CRÍTICA para T1/T2; ALTA para T2; MÉDIA para T3

**Descrição:** Em deployments L0/L1, não há verificação criptográfica de que dados ECG vieram do sensor físico no momento da sessão. App comprometido com App Attest pode injetar dados históricos de ECG enquanto passa na atestação de plataforma.

**Mitigação:** Protocolo de desafio-resposta com nonce incorporado no payload ECG (requer firmware do sensor com suporte a assinatura — T3, indisponível comercialmente em 2026). Curto prazo: verificar que timestamp dos dados ECG está dentro de janela estreita do timestamp da sessão.

---

### GAP-B03 — Deepfake de Sinal Fisiológico via Modelo Generativo

**Severidade:** ALTA (crescente com avanço de modelos generativos)

**Descrição:** Modelos generativos (GANs, Diffusion Models) treinados em dados de ECG/EDA/HRV reais já existem (PhysioGAN, HeartBEiT). Um adversário com dados biométricos históricos do alvo (via data breach de apps de saúde) pode sintetizar sinais plausíveis que passem pela verificação.

**Mitigação:** Artefatos fisiológicos genuínos não reproduzíveis (variabilidade caótica de ultra-baixa frequência, resposta a perturbações ambientais em tempo real). Em T3, signing no TEE elimina sinais sintéticos. Curto prazo: nenhuma robusta.

---

### GAP-B04 — Doenças que Alteram Permanentemente os Padrões Biométricos

**Severidade:** ALTA

**Descrição:** Arritmias (fibrilação atrial, flutter), miocardite pós-COVID, infarto do miocárdio, medicamentos psiquiátricos crônicos (antipsicóticos prolongam QTc; SSRIs alteram HRV), hipotireoidismo — todos alteram a morfologia ECG e/ou HRV de forma permanente ou persistente. Usuários com essas condições podem ser progressivamente excluídos do sistema.

**Mitigação:** Re-enrollment periódico supervisionado com processo clínico explícito para eventos médicos. O baseline de 30 dias mitiga parcialmente mas não resolve o caso de mudança súbita (ex: infarto).

---

### GAP-B05 — Medicamentos Legítimos que Ativam Falsos Positivos de Ataque Farmacológico

**Severidade:** ALTA (impacto operacional direto + risco legal de discriminação)

**Medicamentos que disparam falsos positivos:**
- **Beta-bloqueadores** (propranolol, metoprolol): ativam padrão BETA_BLOCKER
- **Atropina/Escopolamina** (anti-emético): ativa padrão ANTICHOLINERGIC
- **Opioides prescritos** (morfina pós-cirurgia): ativa padrão OPIOID
- **Benzodiazepínicos** (alprazolam): reduzem EDA e HRV — perfil similar a sedação
- **Cafeína em altas doses**: eleva EDA e HR — falso "ELEVATED"
- **Álcool**: suprime HRV, altera ECG em altas doses

**Impacto:** Um médico cardiologista que toma beta-bloqueadores para arritmia seria bloqueado sistematicamente — potencialmente configurando discriminação por condição médica (ADA, EU Employment Equality Directive, legislações equivalentes).

**Mitigação:** Processo formal de declaração de medicamento + re-calibração de baseline específica. Whitelist complexa de implementar sem criar vetor de exploit.

---

### GAP-B06 — Morte ou Incapacitação Súbita Durante a Sessão

**Severidade:** MÉDIA

**Descrição:** Parada cardíaca, síncope, AVC ou convulsão durante a janela de captura de 60+ segundos. Compressões de RCP produzem atividade elétrica detectável no ECG — o sistema pode interpretar como dados válidos.

**Mitigação:** Verificação de continuidade fisiológica ao longo da janela (descontinuidade súbita detectável). Timeout com re-verificação.

---

### GAP-B07 — Gêmeos Idênticos e ECG Morphology

**Severidade:** BAIXA-MÉDIA

**Descrição:** Gêmeos monozigóticos compartilham geometria cardíaca altamente similar. O threshold `ρ_ECG ≥ 0.85` pode ser satisfeito pelo gêmeo de um usuário enrollado.

**Mitigação:** Adicionar fatores de identidade múltiplos (ID digital, FIDO2) ao pipeline de identity anchor, tratando ECG como biométrico de alta confiança mas não único absoluto.

---

### GAP-B08 — Baseline Poisoning durante Enrollment

**Severidade:** ALTA

**Descrição:** Se o adversário controla as condições durante as sessões de enrollment, pode calibrar o baseline para aceitar estados coagidos como "normais". Aplica coerção suave durante enrollment, fazendo com que o baseline capture estado moderadamente estressado como "normal".

**Mitigação parcial:** Baseline anomaly detection (HR >15% acima do histórico, EDA <50% são flags). Porém adversário sofisticado pode calibrar exatamente dentro dos thresholds. Enrollment supervisionado em ambiente controlado contradiz o objetivo de acessibilidade consumer.

---

### GAP-B09 — PPG Menos Preciso em Peles Escuras

**Severidade:** ALTA (impacto de equidade)

**Descrição:** Sensores PPG de LED verde/vermelho têm precisão reduzida em peles de tons escuros (Fitzpatrick types V-VI) — erro de HRV de até 30-40% vs. ECG de referência. Usuários com peles escuras podem ter baselines sistematicamente incorretos, levando a falsos positivos de negação de acesso.

**Natureza legal:** Potencial discriminação por característica protegida (cor de pele).

**Mitigação:** LED infravermelho (menor absorção por melanina) ou ECG de canal único obrigatório para sistemas de alta consequência. Nunca usar PPG puro como único sinal em T3/T4.

---

## DIMENSÃO H — HARDWARE

---

### GAP-H01 — Vulnerabilidades TPM Documentadas

**Severidade:** ALTA

**Vulnerabilidades conhecidas:**
- **TPM-FAIL (2019):** Timing attack em implementações TPM expõe chaves ECDSA (CVE-2019-11090 para Intel fTPM; CVE-2019-16863 para STMicro)
- **CVE-2023-1017/1018:** Buffer overflow na especificação TPM 2.0 — potencialmente compromete todas as chaves armazenadas
- Titan M2 (Google Pixel Watch 2): sem CVEs públicos de timing até 2025, mas é o único device que atinge T3 hoje

**Mitigação:** Certificação de resistência a side-channel (FIPS 140-3 Level 3, CC EAL5+). Rotação periódica de chaves de attestation. LICET deve especificar mínimos de certificação de TPM para tiers T3/T4.

---

### GAP-H02 — Supply Chain: Firmware Wearable Malicioso

**Severidade:** ALTA para T2/T3; CRÍTICA para T4

**Descrição:** Um supply chain attack comprometendo o firmware do Apple Watch, Samsung Galaxy Watch ou WHOOP antes da entrega ao consumidor poderia substituir dados de sensor por valores sintéticos, extrair dados biométricos antes da criptografia, ou responder a comandos secretos com valores fixos.

**Mitigação:** Secure Boot com root of trust em fábrica; assinatura de firmware verificável pelo consumidor; IETF RFC 9019 SUIT (Trusted Platform Firmware Update).

---

### GAP-H03 — Clonagem de Dispositivo sem Protocolo de Revogação

**Severidade:** ALTA

**Descrição:** Wearable roubado ou chave de attestation extraída via side-channel poderia ser usado indefinidamente para forjar autorizações. Sem mecanismo de revogação especificado, o LICET não tem como invalidar um dispositivo comprometido.

**Mitigação:** CRL (Certificate Revocation List) ou OCSP para chaves de attestation de dispositivo, mantida pelo fabricante e consultada pelo LICET Verifier em cada sessão.

---

### GAP-H04 — Side-Channel no Smartphone (Lead Attester)

**Severidade:** ALTA

**Descrição:** Apps maliciosos em background podem usar cache timing, EM emissions ou análise de consumo de bateria para inferir dados biométricos sendo processados. O Secure Enclave isola a chave de App Attest mas não isola o pipeline de dados biométricos — dados brutos passam pelo application processor antes de qualquer criptografia em T2.

**Mitigação:** Processamento de dados biométricos em TEE (TrustZone) antes de transmissão. Requer apps TEE-native, indisponível em HealthKit/Samsung Health Connect padrão.

---

### GAP-H05 — Fault Injection em Wearables

**Severidade:** MÉDIA

**Descrição:** Voltage glitching, laser fault injection e EM fault injection contra microcontroladores de baixa potência de wearables foram demonstrados na literatura. Com acesso físico, possível bypassar verificações de segurança ou extrair chaves do TEE do MCU.

**Mitigação:** Sensores de tamper detection no MCU; proteções contra glitching no firmware; análise física de integridade.

---

## DIMENSÃO L — LEGAL E REGULATÓRIO

---

### GAP-L01 — GDPR: Base Legal para Dados Biométricos na UE

**Severidade:** CRÍTICA para deployments na UE

**Descrição:** Dados biométricos são Categoria Especial (GDPR Art. 9). O processamento de ECG, EDA, HRV e temperatura corporal requer base legal explícita. Consentimento não pode ser pré-requisito para serviços essenciais ou emprego (GDPR Recital 43). As demais bases do Art. 9(2) não se aplicam claramente ao contexto empresarial/financeiro.

**Mitigação:** DPIA (Data Protection Impact Assessment) formal obrigatório antes de qualquer deployment na UE. Consulta à DPA supervisionando para processos de alto risco. Articulação explícita de base legal por jurisdição.

---

### GAP-L02 — Illinois BIPA e Equivalentes (EUA)

**Severidade:** ALTA para deployments nos EUA

**Descrição:** BIPA (Illinois) e leis estaduais equivalentes (Texas, Washington, Nova York) exigem: consentimento escrito antes da coleta, política publicada de retenção e destruição, prazo máximo de retenção (BIPA: 3 anos), destruição obrigatória ao término, proibição de venda.

**Mitigação:** Política explícita de retenção e destruição; consentimento por escrito; DPO designado. Os dados brutos de baseline (covariance matrix server-side) precisam de política de retenção específica.

---

### GAP-L03 — Localização de Dados por Jurisdição

**Severidade:** ALTA para deployment global

**Jurisdições com restrições:**
- **China (PIPL):** dados de cidadãos chineses devem ser processados localmente
- **Rússia (Federal Law 242-FZ):** localização obrigatória
- **India (PDPB 2023):** dados sensíveis incluindo biometria
- **Saudi Arabia NDMO:** soberania de dados
- **Alemanha (BayDSG):** restrições estaduais sobre biometria em emprego

**Mitigação:** Arquitetura multi-regional com processamento e armazenamento local em cada jurisdição; edge deployment.

---

### GAP-L04 — Responsabilidade em Falso Negativo

**Severidade:** ALTA

**Descrição:** Se o LICET concede autorização e se descobre que o usuário estava sob coerção não detectada, quem é legalmente responsável? A prova criptográfica de que sinais fisiológicos estavam dentro dos limites aceitáveis não equivale a prova legal de intenção genuína.

**Mitigação:** Frameworks de responsabilidade explícitos no ToS. Clarificação de que o LICET fornece "evidência técnica de estado fisiológico" e não "prova jurídica de intenção". Alignment com EU AI Act Art. 17 para documentação de falhas.

---

### GAP-L05 — Negação de Acesso por Medicação = Discriminação

**Severidade:** CRÍTICA para deployments em contexto de emprego

**Descrição:** Profissional em uso de beta-bloqueadores prescritos sistematicamente bloqueado pelo detector de "BETA_BLOCKER attack pattern" pode configurar discriminação por condição médica (ADA, EU Employment Equality Directive, legislações equivalentes).

**Mitigação:** Processo formal de acomodação razoável; re-calibração supervisionada por medicamento; tier alternativo de verificação para canais afetados pela medicação.

---

### GAP-L06 — Competência Fisiológica ≠ Capacidade Jurídica

**Severidade:** MÉDIA

**Descrição:** Indivíduo com demência leve pode ter sinais fisiológicos dentro do range normal mas ser legalmente incapaz de contratar. Inversamente, doença cardíaca severa com sinais anômalos não implica incapacidade jurídica. O LICET não pode e não deve ser apresentado como verificador de capacidade legal.

**Mitigação:** Clarificação explícita em todos os documentos: o LICET verifica "estado fisiológico consistente com intenção voluntária não-coagida" — não "capacidade legal de contratar".

---

## DIMENSÃO A — IA E AUTOMAÇÃO

---

### GAP-A01 — LLMs Geram Conteúdo, Humano Apenas Assina

**Severidade:** CRÍTICA para caso de uso de "prova de autoria humana"

**Descrição:** O LICET prova que um humano autorizou algo em um estado fisiológico específico, não que um humano criou o conteúdo. Um humano pode revisar conteúdo gerado por LLM em 10 segundos e assinar com LICET — tecnicamente uma autorização LICET válida de conteúdo gerado por IA.

**Natureza:** Problema de definição — o protocolo foi construído para "atestação de autorização", não "atestação de autoria".

**Mitigação:** Re-enquadrar consistentemente como "atestação de autorização humana consciente". Para autoria, seria necessário monitoramento contínuo durante o processo de criação — técnica e eticamente mais complexo, fora do escopo atual.

---

### GAP-A02 — Ataques Adversariais na API Pública

**Severidade:** ALTA

**Descrição:** Um adversário com acesso à API pública `/v1/authorize` pode realizar black-box membership inference: submeter vetores de features sintéticos e observar os resultados para mapear as fronteiras de decisão do classificador Mahalanobis. Com esse mapa, pode craftar entradas que maximizam `ρ_ECG` e minimizam `D_M` sem produzir sinais biologicamente reais.

**Mitigação:** Rate limiting severo; input validation de plausibilidade fisiológica (ranges, correlações temporais, consistência entre canais); confidencialidade das thresholds exatas; differential privacy nas respostas.

---

### GAP-A03 — Co-authorship Humano+IA sem Granularidade

**Severidade:** ALTA

**Descrição:** O LICET binário (AUTHORIZED/DENIED) não captura o continuum de contribuição humana. Um jurista que usa IA para gerar 90% de um contrato e revisa 10% com LICET não é equivalente a um jurista que escreve 100% e assina com LICET.

**Mitigação:** Nenhuma dentro do escopo do LICET atual. Exigiria integração com ferramentas de provenance tracking por trecho de texto — fora do escopo do protocolo de autenticação fisiológica.

---

### GAP-A04 — Agente AI Manipula o Action Descriptor

**Severidade:** CRÍTICA

**Descrição:** Em cenários onde o agente AI constrói o request, pode submeter um `action descriptor` diferente do que foi apresentado ao humano na interface. O humano vê "autorizar transferência de $100" mas o protocolo assina "autorizar transferência de $100.000".

**Mitigação:** O intent hash deve ser construído pelo componente sob controle humano (app do usuário), não pelo agente AI. A UI que apresenta a ação ao usuário deve ser criptograficamente comprometida ao intent hash antes da coleta biométrica — UI binding criptográfico obrigatório.

**Prioridade:** IMEDIATA

---

### GAP-A05 — Servidor LICET como Dataset Biométrico

**Severidade:** ALTA

**Descrição:** Dados fisiológicos que passam pelo servidor LICET (mesmo brevemente) são extremamente valiosos para treinar modelos de síntese biométrica. Um operador LICET desonesto ou servidor comprometido poderia acumular um dataset e vender ou usar para ataques.

**Mitigação:** Processamento local no dispositivo (servidor recebe apenas features, não dados brutos); computação federada para treinamento de modelos; auditoria independente do servidor.

---

## DIMENSÃO O — OPERACIONAL

---

### GAP-O01 — Revogação de Credenciais Não Especificada

**Severidade:** ALTA

**Descrição:** O protocolo não especifica mecanismo de revogação para: right to erasure (GDPR Art. 17), dispositivo roubado/comprometido, chave mestre comprometida, ou descoberta de baseline poisoning retroativo. O hash chain garante que autorizações fraudulentas ficam permanentemente no ledger como "válidas".

**Mitigação:** CRL ou OCSP-like service para tokens LICET; "revocation proof" ao ledger que invalida entradas retroativas sem quebrar o hash chain; "valid until" timestamp em cada autorização.

---

### GAP-O02 — Perda da Chave Mestre `k_m`: Catástrofe sem Recovery

**Severidade:** CRÍTICA

**Descrição:** Se `k_m` é perdida, todo o histórico de autorizações no ledger torna-se inverificável. Se `k_m` é comprometida, todo o histórico pode ser reforjado. O protocolo não especifica rotação, backup seguro, HSM ou procedimento de disaster recovery para `k_m`.

**Mitigação:** HSM certificado (FIPS 140-3 Level 3) para armazenamento de `k_m`; Shamir Secret Sharing para split da chave entre múltiplos custodiantes geograficamente distribuídos; rotação periódica com re-derivação de ledger.

**Prioridade:** IMEDIATA

---

### GAP-O03 — Single Point of Failure: Servidor Centralizado

**Severidade:** ALTA

**Descrição:** A implementação de referência é um servidor único (Google Cloud Run `us-central1`). Cria: SPOF de disponibilidade, SPOF de confiança (servidor pode fabricar autorizações), SPOF de jurisdição (dados de usuários globais em us-central1), SPOF de ataque.

**Mitigação:** Multi-region deployment com replicação do ledger; threshold signing para `k_m` via MPC; o paper menciona decentralização via smart contracts como trabalho futuro.

---

### GAP-O04 — Baseline Expiry sem Continuidade Operacional

**Severidade:** ALTA para deployments de missão crítica

**Descrição:** O baseline expira em 30 dias e requer re-enrollment de 5 sessões de 3 minutos. Em ambientes 24h (médico de plantão, trader durante volatilidade, operador de infraestrutura em crise), expiração em momento crítico bloqueia autorização quando mais necessária.

**Mitigação:** Rolling baseline update — atualização incremental da covariance matrix com cada sessão bem-sucedida, sem exigir 5 sessões completas. Emergency procedure com trust level reduzido para casos de expiração em missão crítica.

---

### GAP-O05 — Múltiplos Dispositivos sem Portabilidade de Identidade

**Severidade:** MÉDIA

**Descrição:** ECG morphology match varia significativamente por posição de eletrodo e tipo de sensor. A covariance matrix Mahalanobis é específica por device. Troca de dispositivo = perda de baseline + re-enrollment.

**Mitigação:** Normalização de features cross-device; ECG feature extraction baseada apenas em features morfológicas invariantes de posição; portabilidade de identidade via chave pública do usuário que agrega múltiplos baselines.

---

### GAP-O06 — Auditoria de Terceiros Incompleta

**Severidade:** ALTA

**Descrição:** O endpoint `GET /v1/ledger/integrity` é verificado pelo próprio servidor. Um auditor externo não pode verificar que o ledger é completo — entradas podem ter sido omitidas sem quebrar o hash chain se a omissão é desde o início.

**Mitigação:** Publicação do Merkle root em log externo auditável (CT, blockchain); separação entre o servidor que gera autorizações e o servidor que mantém o ledger.

---

## DIMENSÃO I — ESTRUTURALMENTE IMPOSSÍVEIS

> Estes gaps não têm solução técnica com o estado atual da ciência.
> A resposta correta é declará-los explicitamente, não ignorá-los.

---

### GAP-I01 — Problema do Oráculo Fisiológico

**Severidade:** CRÍTICA / INSOLÚVEL

**Descrição:** A relação entre estado fisiológico e estado mental é probabilística, não determinística. Não existe nenhum conjunto de sinais fisiológicos externos que prove conclusivamente estados internos subjetivos. Um sujeito com alta variabilidade intraindividual pode estar em estado completamente não-voluntário com sinais dentro do range "calmo".

**Declaração obrigatória:** O LICET aumenta o custo de subversão mas nunca pode eliminar a incerteza fundamental. Deve ser apresentado como "evidência técnica de estado fisiológico", jamais como "prova de intenção genuína".

---

### GAP-I02 — Coerção Internalizada ou Sistêmica

**Severidade:** CRÍTICA / INSOLÚVEL

**Descrição:** O LICET detecta coerção aguda (ameaça imediata com arousal simpático). Coerção sistêmica, crônica ou internalizada é fisiologicamente indistinguível de voluntariedade genuína:
- Ameaça de demissão / pressão hierárquica → estado de resignação calma
- Coerção de dias antes, aceita "voluntariamente" no momento da assinatura
- Síndrome de Estocolmo
- Coerção econômica crônica

---

### GAP-I03 — Impossibilidade de Provar Ausência de IA no Loop Cognitivo

**Severidade:** CRÍTICA / INSOLÚVEL

**Descrição:** O LICET prova que um humano em estado fisiológico específico autorizou uma ação. Não pode provar que o humano deliberou de forma independente. Um humano fisiologicamente calmo, consciente e não-coagido que aprova automaticamente recomendações da IA satisfaz todos os requisitos LICET enquanto não exerce supervisão genuína em nenhum sentido substantivo.

**Relevância regulatória:** EU AI Act Art. 26(5) exige que supervisão humana seja "genuinamente exercida" — o LICET eleva o custo do "botão pressionado" mas não resolve o problema da supervisão substantiva.

---

### GAP-I04 — Indistinguibilidade Computacional: Humano Treinado vs. IA Incorporada

**Severidade:** INSOLÚVEL (horizonte de 10-20 anos para relevância prática)

**Descrição:** Robôs humanoides com sinais eletrofisiológicos sintéticos de alta fidelidade, ou sistemas com sensores biométricos simulados, poderiam em princípio passar por um sistema LICET. Mais imediatamente: a fronteira entre "humano tomando decisão assistida por IA" e "IA tomando decisão ratificada por humano" é indefinível fisiologicamente.

---

### GAP-I05 — Paradoxo da Delegação Genuína

**Severidade:** ALTA / INSOLÚVEL sem decisão de política

**Descrição:** Quando o humano genuinamente quer delegar (CEO que quer que CFO autorize sem supervisão; médico que quer que a IA decida enquanto descansa), o LICET cria fricção contra a intenção real. O protocolo resolve um problema técnico (presença fisiológica) mas não o problema político/organizacional (quando presença fisiológica deve ser obrigatória).

---

### GAP-I06 — ZKP Indistinguível com Adversário Quântico

**Severidade:** INSOLÚVEL com BN128; mitigável com migração

**Descrição:** Com adversário quântico (algoritmo de Shor), o DDH assumption sobre BN128 colapsa e a zero-knowledge property deixa de ser garantida. O witness `w` torna-se extraível do proof público.

**Mitigação de longo prazo:** STARKs (baseados em hash — conjecturalmente quantum-safe) substituem Schnorr/BN128.

---

### GAP-I07 — Continuidade de Identidade ao Longo do Tempo

**Severidade:** MÉDIA / PARCIALMENTE INSOLÚVEL

**Descrição:** O coração envelhece; cirurgia cardíaca (ablação, angioplastia, marca-passo) muda permanentemente a morfologia ECG; gravidez altera ECG de forma significativa e transitória; treinamento físico intenso muda morfologia mensalmente. O threshold estático `ρ_ECG ≥ 0.85` pode progressivamente excluir usuários com mudanças cardíacas legítimas.

**Mitigação parcial:** Re-enrollment periódico supervisionado para populações com mudanças cardíacas rápidas.

---

### GAP-I08 — Estados Alterados Voluntários vs. Incapacidade

**Severidade:** ALTA / PARCIALMENTE INSOLÚVEL

**Descrição:** Estados meditativos profundos, flow states e treinamento de elite produzem perfis fisiológicos que o Mahalanobis detector pode interpretar como anomalia ou sedação:
- Meditação profunda: alterações radicais em HRV, EDA, ECG
- Flow state (Csikszentmihalyi): alta performance com EDA baixa e HR moderada
- Pilotos de caça/cirurgiões/traders veteranos: execução de alta precisão com arousal mínimo

**Mitigação parcial:** Personalização extrema de baseline para populações de elite.

---

## Hierarquia de Prioridade de Ação

### Urgente (resolver antes de qualquer auditoria externa)

| Gap | Ação Imediata |
|---|---|
| **GAP-C01** | Redesign do ZKP — witness secreto genuíno usando `k_m` |
| **GAP-C02** | Migrar "biometric signature" para Ed25519 com chave no HSM/TEE |
| **GAP-O02** | HSM + Shamir Secret Sharing para `k_m` |
| **GAP-A04** | UI binding criptográfico para o action descriptor |
| **GAP-L01** | DPIA formal + base legal por jurisdição antes do primeiro cliente europeu |

### Alto (afetam adoção em setores regulados)

GAP-C03, GAP-C04, GAP-H03, GAP-O01, GAP-L04, GAP-L05, GAP-B09, GAP-B08, GAP-A05, GAP-O03

### Estruturalmente insolúveis (re-enquadramento semântico, não técnico)

GAP-I01, GAP-I02, GAP-I03 — Declarar explicitamente em todos os documentos técnicos e legais:
> *"O LICET fornece evidência técnica de estado fisiológico e eleva o custo de subversão.
> Não constitui prova de intenção genuína nem detector de coerção em todos os contextos possíveis."*

---

## Tabela Mestre — Todos os Gaps

| Gap | Título | Dimensão | Severidade | Mitigação Existe? |
|---|---|---|---|---|
| C01 | Witness ZKP computável publicamente | Criptografia | CRÍTICA | Sim (redesign) |
| C02 | HMAC não é assinatura verificável | Criptografia | ALTA | Sim (EdDSA) |
| C03 | Hash chain sem irretratabilidade | Criptografia | ALTA | Sim (âncora externa) |
| C04 | Timestamp não verificável | Criptografia | MÉDIA-ALTA | Sim (RFC 3161) |
| C05 | Quantum threat em BN128 | Criptografia | MÉDIA | Sim (migração PQC/STARK) |
| C06 | Replay via timestamp collision | Criptografia | BAIXA-MÉDIA | Sim (nonce) |
| C07 | Side-channel na API pública | Criptografia | BAIXA | Sim (padding) |
| B01 | Respiração compassada | Biometria | CRÍTICA | Não (nenhuma robusta) |
| B02 | ECG replay sem verificação temporal | Biometria | CRÍTICA/ALTA | Parcial (T3 futuro) |
| B03 | Deepfake de sinal fisiológico | Biometria | ALTA | Parcial |
| B04 | Doenças que alteram padrões biométricos | Saúde | ALTA | Parcial (re-enrollment) |
| B05 | Medicamentos legítimos = falso positivo | Saúde/Legal | ALTA | Parcial (whitelist) |
| B06 | Morte/incapacitação durante sessão | Saúde | MÉDIA | Parcial |
| B07 | Gêmeos idênticos e ECG | Biometria | BAIXA-MÉDIA | Sim (multi-fator) |
| B08 | Baseline poisoning durante enrollment | Biometria | ALTA | Parcial |
| B09 | PPG impreciso em peles escuras | Biometria/Equidade | ALTA | Sim (ECG obrigatório) |
| H01 | TPM vulnerabilities documentadas | Hardware | ALTA | Sim (certificação) |
| H02 | Supply chain: firmware wearable | Hardware | ALTA/CRÍTICA | Parcial (L3 spec) |
| H03 | Clonagem de dispositivo sem revogação | Hardware | ALTA | Sim (CRL) |
| H04 | Side-channel no smartphone | Hardware | ALTA | Parcial (TEE nativo) |
| H05 | Fault injection em wearables | Hardware | MÉDIA | Parcial |
| L01 | GDPR: base legal para biometria na UE | Legal | CRÍTICA (UE) | Sim (DPIA) |
| L02 | BIPA e retention de dados | Legal | ALTA (EUA) | Sim (política) |
| L03 | Localização de dados por jurisdição | Legal | ALTA (global) | Sim (multi-região) |
| L04 | Responsabilidade em falso negativo | Legal | ALTA | Parcial (ToS) |
| L05 | Negação de acesso por medicação = discriminação | Legal | CRÍTICA (emprego) | Parcial |
| L06 | Competência fisiológica ≠ capacidade legal | Legal | MÉDIA | Sim (clarificação) |
| A01 | LLMs geram conteúdo, humano apenas assina | IA | CRÍTICA | Não (design change) |
| A02 | Ataques adversariais na API pública | IA | ALTA | Parcial |
| A03 | Co-authorship humano+IA sem granularidade | IA | ALTA | Não |
| A04 | Agente AI manipula action descriptor | IA | CRÍTICA | Sim (UI binding) |
| A05 | Servidor LICET como dataset biométrico | IA | ALTA | Sim (processamento local) |
| O01 | Revogação de credenciais não especificada | Operacional | ALTA | Sim (CRL) |
| O02 | Perda de k_m: catástrofe sem recovery | Operacional | CRÍTICA | Sim (HSM + SSS) |
| O03 | Single point of failure centralizado | Operacional | ALTA | Sim (multi-region) |
| O04 | Baseline expiry sem continuidade | Operacional | ALTA | Sim (rolling update) |
| O05 | Múltiplos dispositivos sem portabilidade | Operacional | MÉDIA | Sim (normalização) |
| O06 | Auditoria de terceiros incompleta | Operacional | ALTA | Sim (CT log externo) |
| I01 | Problema do oráculo fisiológico | Estrutural | CRÍTICA / INSOLÚVEL | Não |
| I02 | Coerção internalizada/sistêmica | Estrutural | CRÍTICA / INSOLÚVEL | Não |
| I03 | Impossibilidade de provar ausência de IA no loop | Estrutural | CRÍTICA / INSOLÚVEL | Não |
| I04 | Indistinguibilidade humano/IA incorporada | Estrutural | INSOLÚVEL | Não |
| I05 | Paradoxo da delegação genuína | Estrutural | ALTA / INSOLÚVEL | Não (política) |
| I06 | ZKP indistinguível com adversário quântico | Estrutural | INSOLÚVEL com BN128 | Sim (STARKs) |
| I07 | Continuidade de identidade ao longo do tempo | Estrutural | MÉDIA / PARCIAL | Parcial |
| I08 | Estados alterados voluntários vs. incapacidade | Estrutural | ALTA / PARCIAL | Parcial |

---

*Este documento deve ser incorporado à seção "Security Considerations" do IETF draft-pereira-licet-human-intent.*
*Revisão recomendada: a cada versão major do protocolo ou quando gaps estruturalmente insolúveis evoluírem com novas evidências científicas.*
