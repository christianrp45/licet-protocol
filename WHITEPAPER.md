# LICET — Human Intent Protocol
## Whitepaper Técnico v2.0
**"Nenhuma IA age sem você."**

**Autor:** Christian Rodrigues Pereira  
**Organização:** NeuroTrust  
**Data:** 13 de julho de 2026 (atualizado — submetido ao arXiv cs.CR)  
**URL de referência:** https://licet.dev  
**Anterioridade:** NeuroTrust_Master_Protocol_v1.pdf.ots — 25/02/2026 (OpenTimestamps)  
**IACR ePrint:** 2026/110546 (submetido 13/07/2026 — Cryptographic Protocols — CC BY)  
**IETF Internet-Draft:** draft-pereira-licet-human-intent-01 (submetido 02/07/2026)  
**SSRN:** Abstract ID 7018458 v2 (atualizado 02/07/2026)

---

## Resumo Executivo

O LICET é um protocolo de middleware que garante que nenhuma ação crítica executada por um agente de inteligência artificial ocorra sem a confirmação fisiológica consciente de um ser humano.

Diferente de sistemas tradicionais de autenticação — que verificam *quem você é* (senha, biometria estática) — o LICET verifica *como você está* no exato momento da autorização. Um humano sob coerção, incapacitado ou inconsciente não consegue autorizar uma ação, mesmo que possua as credenciais corretas.

A versão 2.0 do protocolo introduz **três camadas biométricas independentes**, projetadas para resistir a ataques farmacológicos e elevar o custo de coerção a um nível operacionalmente inviável:

1. **Camada 1 — Morfologia ECG:** análise da forma de onda eletrocardiográfica (complexo QRS, intervalos PR e QT). Determinada anatomicamente e resistente a betabloqueadores. Capturada via Apple Watch Series 4+ através do HealthKit HKElectrocardiogram (512 Hz). Comparação por similaridade de cosseno contra baseline individual inscrito.

2. **Camada 2 — Atividade Eletrodérmica (EDA):** inervação colinérgica simpática da pele — imune a bloqueio beta-adrenérgico. Capturada continuamente via WHOOP 5 ou em spot-check via Samsung Galaxy Watch 7. Mede resposta galvânica (SCR) e nível de condutância (SCL) com resolução sub-milissegundo.

3. **Camada 3 — Distância de Mahalanobis multivariada:** D_M = √((z − μ_calm)ᵀ S⁻¹ (z − μ_calm)) sobre cinco sinais simultâneos: RMSSD, EDA-SCL, EDA-SCR, delta de temperatura cutânea e tremor na banda 8–12 Hz. Baseline personalizado (≥ 5 sessões × ≥ 3 min, validade 30 dias). Não é detecção binária: é *elevação do custo de coerção* — o adversário precisa manipular cinco sinais independentes ao mesmo tempo.

O protocolo combina essas três camadas com:
- **Assinatura criptográfica assimétrica** — Intent Hash + Biometric Signature (Ed25519) — verificável por terceiros sem acesso ao servidor
- **UI Binding criptográfico** — commitment SHA256(action|agent_id|target|nonce) comprometido antes da captura biométrica, impedindo manipulação por agente AI
- **Prova de Conhecimento Zero (ZKP)** — auditabilidade sem exposição de dados biométricos; witness = HKDF(k_m, intent_hash), nunca exposto no ledger
- **Ledger hash-chained com ancoragem externa** — Merkle root publicado no OpenTimestamps (3 calendários); server_nonce por entrada impede reescrita retroativa
- **Hierarquia de confiança L0-L3** — alinhada ao RFC 9334 (IETF RATS)
- **Shamir Secret Sharing (5,3)** — proteção da chave mestre k_m contra perda catastrófica
- **Minimização de dados biométricos** — ecg_waveform e rr_intervals zerados pós-extração; endpoints GDPR Art. 15/17 e LGPD Art. 18 VI

---

## 1. O Problema

### 1.1 A autonomia crescente dos agentes de IA

Agentes de inteligência artificial estão deixando de ser ferramentas passivas para se tornarem sistemas autônomos capazes de executar ações com consequências reais e irreversíveis: administrar medicamentos, transferir recursos financeiros, modificar infraestrutura crítica, tomar decisões jurídicas.

Os mecanismos de controle humano atuais — botões de confirmação, senhas, assinaturas digitais — foram projetados para um mundo onde o humano está presente, consciente e livre de coerção. Eles respondem à pergunta *"quem autorizou?"*, mas não respondem à pergunta *"esse humano estava realmente em condições de autorizar?"*

### 1.2 O gap de intenção

Existe um gap fundamental entre *identidade* e *intenção consciente*:

| Sistema atual | O que verifica |
|---|---|
| Senha | Você conhece o segredo |
| Biometria estática | Você é a pessoa certa |
| Assinatura digital | Você possui a chave privada |
| **LICET** | **Você está vivo, consciente e livre de coerção neste exato momento** |

### 1.3 Cenários de risco real

- **Saúde:** agente de IA prescreve dose de insulina ao receber autorização de médico sob pressão extrema
- **Finanças:** agente executa transferência ao receber aprovação de usuário incapacitado
- **Jurídico:** agente assina contrato com base em autorização de pessoa coagida
- **Infraestrutura:** agente modifica sistema crítico com base em comando de operador com comprometimento cognitivo

---

## 2. O Protocolo LICET

### 2.1 Princípio fundamental

> *A autorização de uma ação por uma IA deve ser criptograficamente vinculada ao estado fisiológico do autorizante no momento exato da autorização.*

### 2.2 Fluxo completo de autorização

```
Agente de IA solicita ação
         ↓
LICET inicia captura biométrica (≥ 60 segundos)
         ↓
┌─────────────────────────────────────────────────┐
│  CAMADA 1 — Morfologia ECG                      │
│  Apple Watch 4+ / HealthKit / 512 Hz            │
│  Similaridade de cosseno vs. baseline inscrito  │
│  cosine_sim < limiar? → RECUSA (não é você)     │
└─────────────────────────────────────────────────┘
         ↓ (ECG aprovado)
┌─────────────────────────────────────────────────┐
│  CAMADA 2 — EDA (Atividade Eletrodérmica)       │
│  WHOOP 5 (contínuo) / Samsung GW7 (spot)        │
│  SCL (nível tônico) + SCR (resposta fásica)     │
│  EDA plana com HRV elevado? → CHECK farmacológico│
└─────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────┐
│  CHECK FARMACOLÓGICO                            │
│  Betabloqueador: tremor suprimido + FC elevada  │
│  Anticolinérgico: EDA plana + pele quente       │
│  Opioide: bradicardia + depressão respiratória  │
│  Padrão de toxidrome detectado? → RECUSA        │
└─────────────────────────────────────────────────┘
         ↓ (sem toxidrome)
┌─────────────────────────────────────────────────┐
│  CAMADA 3 — Mahalanobis Multivariado            │
│  D_M sobre {RMSSD, EDA-SCL, EDA-SCR,           │
│             ΔTemp cutânea, tremor 8-12Hz}       │
│  D_M > limiar_individual? → RECUSA (estado      │
│  fisiológico incompatível com autorização)      │
└─────────────────────────────────────────────────┘
         ↓ (todas as camadas aprovadas)
UI Binding Check
SHA256(action | agent_id | target | nonce) — comprometido antes da captura
ui_binding_status: VERIFIED | ABSENT | FAILED
         ↓
Geração do Intent Hash
H(ação + agente + alvo + timestamp)
         ↓
Derivação de chave de sessão
HKDF(chave_mestre, intent_hash)
         ↓
Assinatura Biométrica Assimétrica (Ed25519)
Ed25519(intent_hash + biometria_resumida, chave_privada_servidor)
— verificável por qualquer auditor com a chave pública (GET /signing-key)
         ↓
Zero-Knowledge Proof (Schnorr/BN128)
witness = HKDF(k_m, intent_hash) — nunca armazenado no ledger
Prova sem revelar biometria
         ↓
Registro no Ledger Hash-Chained
server_nonce = secrets.token_hex(16)  — gerado pelo servidor por entrada
SHA256(conteúdo + hash_anterior + server_nonce)
         ↓
Ancoragem no OpenTimestamps (Merkle root — 3 calendários independentes)
         ↓
AUTORIZADO ✓
```

### 2.3 Componentes técnicos

#### 2.3.1 Captura biométrica — Três camadas de hardware

O LICET v2.0 suporta fontes de hardware estratificadas por camada biométrica:

| Camada | Sinal | Hardware primário | Hardware alternativo | Método |
|---|---|---|---|---|
| **1 — ECG** | Morfologia QRS, PR, QT | Apple Watch Series 4+ | — | HealthKit HKElectrocardiogram (512 Hz) |
| **2 — EDA** | EDA-SCL, EDA-SCR | WHOOP 5 (contínuo) | Samsung Galaxy Watch 7 (spot-check) | WHOOP API / Health Connect |
| **3 — Multi** | RMSSD, ΔTemp, tremor 8-12Hz | Combinação dos acima | Sensor MAX30102 + acelerômetro | Fusão de sensores |
| **Dev** | Todos (simulados) | Simulador de software | — | Desenvolvimento/QA |

**Janela de captura:** mínimo de **60 segundos** por sessão de autorização (v1.0 usava 10 segundos — insuficiente para análise de morfologia ECG e cálculo robusto de RMSSD).

**Métricas da Camada 3 em detalhe:**
- **RMSSD:** raiz quadrada da média dos quadrados das diferenças entre intervalos R-R sucessivos — indicador parassimpático/vagal. Nota: betabloqueadores NÃO suprimem o RMSSD (mecanismo vagal, não beta-adrenérgico).
- **EDA-SCL:** nível tônico de condutância eletrodérmica — reflete arousal basal do sistema nervoso simpático colinérgico.
- **EDA-SCR:** componente fásico (respostas galvânicas pontuais) — reflete reatividade simpática aguda.
- **ΔTemp cutânea:** desvio da temperatura da pele em relação ao baseline — vasoconstrição periférica indica estresse simpático.
- **Tremor 8-12 Hz:** potência espectral de acelerometria do pulso na banda fisiológica de tremor essencial.

#### 2.3.2 Detecção de coerção — Arquitetura três camadas com Mahalanobis

A v1.0 utilizava limiares fixos absolutos (FC > 130 e HRV < 20). Esta abordagem tem falsos positivos inaceitáveis em atletas, pacientes com betabloqueadores, e falsos negativos com drogas que suprimem sinais individualmente. A v2.0 substitui esse modelo por uma abordagem personalizada e multivariada.

**Distância de Mahalanobis:**

```
D_M = sqrt( (z - μ_calm)ᵀ × S⁻¹ × (z - μ_calm) )
```

onde:
- `z` = vetor de 5 sinais da sessão atual: [RMSSD, EDA-SCL, EDA-SCR, ΔTemp, tremor₈₋₁₂Hz]
- `μ_calm` = média do vetor de 5 sinais nas sessões de baseline (estado calmo)
- `S` = matriz de covariância entre os 5 sinais nas sessões de baseline
- `S⁻¹` = inversa da matriz de covariância (captura correlações entre sinais)

**Vantagem sobre z-score univariado:** a distância de Mahalanobis leva em conta as correlações naturais entre sinais. Se RMSSD e EDA-SCL normalmente co-variam, um estado onde um está alto e o outro está artificialmente suprimido produz alta D_M mesmo que cada sinal individualmente pareça aceitável — exatamente o padrão deixado por ataques farmacológicos.

**Interpretação:**
```python
if D_M <= 2.0:
    return "ESTADO_CALMO"          # dentro de 2σ multivariado
elif D_M <= 3.5:
    return "ESTADO_ELEVADO"        # estresse normal — requer confirmação adicional
else:
    return "ESTADO_INCOMPATÍVEL"   # RECUSA — fisiologia inconsistente com autorização
```

**Base fisiológica:** sob coerção aguda, o sistema nervoso simpático eleva FC e suprime RMSSD simultaneamente com ativação EDA. Ataques farmacológicos que bloqueiam um canal tipicamente perturbam as correlações entre canais, aumentando D_M mesmo sem exceder limiares individuais.

#### 2.3.3 Intent Hash

Identificador único e imutável da ação solicitada:

```
intent_hash = SHA256(ação + agente_id + alvo + timestamp)
```

Qualquer alteração em qualquer parâmetro gera um hash completamente diferente. O Intent Hash é o que vincula matematicamente a autorização biométrica à ação específica.

#### 2.3.4 Assinatura Biométrica Assimétrica (Ed25519)

A versão anterior usava HMAC-SHA256 simétrico — o servidor que gerava a assinatura era simultaneamente o único capaz de verificá-la, tornando a auditoria por terceiros impossível sem acesso à chave mestre (GAP-C02, implementado 09/07/2026).

```
session_key    = HKDF(chave_mestre, intent_hash)
bio_signature  = Ed25519.sign(
                     intent_hash + {RMSSD, EDA-SCL, EDA-SCR, ΔTemp, tremor, ECG_cosine, timestamp},
                     server_private_key
                 )
```

**Chave pública disponível para auditores:** `GET /signing-key` retorna a chave pública Ed25519 do servidor, permitindo que qualquer auditor independente verifique a assinatura sem acesso a segredos do servidor.

**Propriedades:**
- Única por evento — não pode ser reutilizada
- Vinculada à ação específica — não pode ser transferida
- Temporalmente situada — o timestamp é parte da assinatura
- Não reversível — os dados biométricos brutos não podem ser recuperados da assinatura
- **Verificável por terceiros** — auditor externo valida com chave pública; servidor não pode negar ter produzido a assinatura

#### 2.3.4a Proteção da Chave Mestre — Shamir Secret Sharing (GAP-O02)

A chave mestre `k_m` é o segredo central do protocolo. Sua perda tornaria todo o histórico de autorizações inverificável; seu comprometimento permitiria reforjar qualquer assinatura histórica.

Implementado em 09/07/2026: Shamir Secret Sharing sobre GF(2^256+297), configuração (n=5, threshold=3):

```
POST /admin/key/split   — divide k_m em 5 shares; qualquer 3 reconstroem a chave
POST /admin/key/combine — reconstrução (restrita a ambiente de recuperação controlado)
```

**Propriedade:** nenhum custodiano individual possui k_m. Um adversário precisaria comprometer pelo menos 3 dos 5 custodiantes geograficamente distribuídos. Perda de até 2 shares não compromete a recuperação.

#### 2.3.5 Zero-Knowledge Proof (Schnorr / BN128)

O LICET implementa uma prova Schnorr sobre a curva elíptica BN128 (a mesma usada pelo Ethereum).

**Witness seguro (GAP-C01, implementado 09/07/2026):** o witness é derivado como `w = HKDF(k_m, intent_hash)` — nunca armazenado no ledger e inacessível a observadores. Versões anteriores usavam `SHA256(bio_signature || intent_hash)`, computável por qualquer observador do ledger, invalidando a propriedade zero-knowledge.

```
# Geração da prova
secret    = HKDF(k_m, intent_hash) mod order   # witness secreto — não no ledger
public_key = secret × G          # Ponto público na curva
r          = random nonce
R          = r × G               # Commitment
challenge  = SHA256(R || PK || intent_hash)   # Fiat-Shamir
response   = (r - challenge × secret) mod order

# Verificação (sem conhecer o segredo)
s×G + challenge×PK == R  →  VÁLIDO
```

**O que isso garante:** um auditor pode verificar matematicamente que "uma entidade com conhecimento da assinatura biométrica autorizou esta ação específica" sem nunca ter acesso aos dados biométricos reais.

#### 2.3.6 Ledger Hash-Chained com Irretratabilidade (GAP-C03, GAP-C04)

Cada registro no ledger contém o hash do registro anterior e um nonce gerado pelo servidor:

```
server_nonce[n] = secrets.token_hex(16)   # gerado pelo servidor, não pelo cliente
chain_hash[n]   = SHA256(conteúdo[n] + chain_hash[n-1] + server_nonce[n])
chain_hash[0]   = SHA256(conteúdo[0] + "GENESIS" + server_nonce[0])
```

**Proteção contra backdating (GAP-C04):** o `server_nonce` é gerado pelo servidor no momento da inserção — um cliente malicioso não pode submeter timestamps retroativos porque não conhece o nonce que o servidor gerará para aquela entrada.

**Irretratabilidade externa (GAP-C03):** o Merkle root do ledger é ancorado periodicamente via `POST /ledger/timestamp` em três calendários OpenTimestamps independentes. Isso impede que o operador do servidor reescreva toda a cadeia — a âncora externa prova quando o Merkle root existia.

**Propriedade:** qualquer adulteração retroativa em qualquer registro quebra a cadeia subsequente (detectável localmente) e contradiz o Merkle root ancorado externamente (detectável por terceiros).

#### 2.3.7 UI Binding — Proteção contra Agente AI (GAP-A04)

Em cenários onde um agente AI constrói o request LICET, existe risco de manipulação do `action descriptor`: o agente apresenta ao humano "transferência de R$100" mas assina "transferência de R$100.000".

Implementado em 09/07/2026: commitment scheme criptográfico comprometido **antes** do início da captura biométrica:

```
ui_binding_commitment = SHA256(action | agent_id | target | nonce)
```

O commitment é gerado pelo componente sob controle humano (app do usuário) a partir do que é exibido na interface. O servidor verifica que o intent_hash é consistente com o commitment antes de processar a autorização.

**Resposta:** `ui_binding_status` presente em toda resposta de autorização:
- `VERIFIED` — commitment verificado; o que o humano viu é o que foi assinado
- `ABSENT` — nenhum commitment submetido (integrador não implementou UI binding)
- `FAILED` — commitment não corresponde ao intent_hash (possível manipulação detectada)

#### 2.3.8 Equidade em PPG — Fitzpatrick V-VI (GAP-B09)

Sensores PPG de LED verde/vermelho têm absorção aumentada por melanina em peles de tons escuros (Fitzpatrick types V-VI), resultando em erro de medição de HRV de até 30-40% versus ECG de referência (Bent et al., NPJ Digit Med 2020; Mannheimer et al., J Clin Monit Comput 2021).

Sem correção, usuários com peles escuras teriam baselines sistematicamente incorretos, resultando em taxas de falso positivo de negação desproporcionalmente altas — potencial discriminação por característica protegida.

Implementado em 09/07/2026:
- Campo `skin_tone_fitzpatrick` (1-6, opcional) no `BiometricPushRequest`
- `threshold_multiplier = 1.4` aplicado automaticamente para Fitzpatrick V-VI com sensor PPG
- `ppg_equity_warning` incluído na resposta quando o multiplicador está ativo
- Recomendação: sensores ECG de canal único para deployments de alta consequência com populações de pele escura

#### 2.3.9 Minimização de Dados Biométricos e GDPR (GAP-A05)

Dados fisiológicos brutos (ECG waveform, RR intervals) transitando pelo servidor constituem risco de acumulação de dataset biométrico por operador desonesto ou servidor comprometido.

Implementado em 09/07/2026:
- Quando `privacy_mode=True`: `ecg_waveform` e `rr_intervals` zerados após extração de features, antes de qualquer persistência
- O servidor armazena apenas features derivadas (RMSSD, cosine similarity), não sinais brutos

**Endpoints de direitos do titular (LGPD Art. 17-18 / GDPR Art. 15/17):**
```
GET    /gdpr/data/{user_id}     — Art. 15 GDPR: direito de acesso; retorna todos os dados armazenados
DELETE /gdpr/erasure/{user_id}  — Art. 17 GDPR / LGPD Art. 18 VI: direito ao esquecimento
```

---

## 3. Resistência Farmacológica

### 3.1 O problema das drogas de coerção

Ataques sofisticados podem tentar mascarar o estado de coerção usando agentes farmacológicos que suprimem respostas fisiológicas individuais. A arquitetura de três camadas do LICET foi projetada especificamente para tornar esses ataques autoderrotantes.

### 3.2 Três padrões de ataque farmacológico

**Padrão 1 — Betabloqueador (propranolol):**
- Efeito: suprime tremor (z_TREMOR < −2,0) + eleva FC vs. baseline (bloqueio do reflexo barorreceptor)
- Importante: betabloqueadores NÃO suprimem RMSSD — o mecanismo vagal/parassimpático é independente do receptor beta-adrenérgico
- Assinatura LICET: tremor suprimido + FC elevada + RMSSD preservado = dissociação anômala detectada por S⁻¹ na distância de Mahalanobis
- Resultado: D_M elevada, mesmo que FC e RMSSD individualmente pareçam normais

**Padrão 2 — Anticolinérgico (atropina, escopolamina):**
- Efeito: bloqueia receptores muscarínicos — EDA completamente plana + HRV paradoxalmente elevado (bloqueio vagal reverso sobre nódulo SA) + pele quente e seca
- Assinatura LICET: EDA-SCL ≈ 0, EDA-SCR ≈ 0, RMSSD elevado, ΔTemp positivo = toxidrome invertida
- A combinação EDA plana + HRV elevado é fisiologicamente incoerente com estado calmo e detectável pelo modelo de covariância
- Resultado: RECUSA por check farmacológico antes de alcançar Camada 3

**Padrão 3 — Opioide (fentanil, morfina):**
- Efeito: depressão respiratória → queda de SpO2 → bradicardia reflexa + pele quente (vasodilatação μ-opioide) + supressão de tremor
- Assinatura LICET: FC baixa + SpO2 baixo + ΔTemp positivo + tremor suprimido = padrão opioide
- Resultado: RECUSA por check farmacológico

### 3.3 Por que ataques combinados são autoderrotantes

A coerção por drogas exige manipular **simultaneamente** cinco canais fisiológicos independentes com mecanismos neurológicos distintos:

| Canal | Mecanismo | Bloqueio alvo |
|---|---|---|
| RMSSD | Vagal / parassimpático | Atropina (mas ela destrói EDA) |
| EDA-SCL / SCR | Simpático colinérgico | Nenhum agente isolado — exigiria anticolinérgico |
| ECG morfologia | Anatomia cardíaca | Cirurgia — não farmacológico |
| ΔTemp cutânea | Simpático adrenérgico + vasodilatação opioide | Múltiplos mecanismos opostos |
| Tremor 8-12 Hz | Beta-adrenérgico | Propranolol (mas eleva FC) |

Um bloqueador de um canal tipicamente ativa ou destrói outro. O objetivo do LICET não é detecção binária perfeita — é **elevar o custo de coerção** até o ponto em que o ataque requer expertise farmacológica especializada, múltiplos agentes de ação simultânea, e deixa assinaturas detectáveis em canais que o adversário não consegue controlar ao mesmo tempo.

---

## 4. Hierarquia de Confiança Biométrica L0-L3

O LICET v2.0 define quatro níveis de confiança de atestação, alinhados ao RFC 9334 (IETF RATS — Remote Attestation Procedures):

| Nível | Nome | Hardware | Mecanismo de atestação | Uso |
|---|---|---|---|---|
| **L0** | Sem atestação | Simulador / ambiente de desenvolvimento | Nenhum | Desenvolvimento, QA, demos |
| **L1** | Atestação de plataforma | Wearable BLE de consumo + HealthKit / Health Connect | Assinatura de app store, canal TLS | Uso clínico geral, finanças |
| **L2** | Atestação de hardware | Pixel Watch 2 + Titan M2 + Android Key Attestation | Chave vinculada a hardware — Android Key Attestation (X.509) | Infraestrutura crítica, saúde de alto risco |
| **L3** | Sensor-para-TEE direto | Especificação futura | Canal seguro sensor → TEE sem passar por SO principal | Alvo de especificação futura |

**Mapeamento RFC 9334:**
- Wearable = Sub-Attester (coleta e assina dados do sensor)
- Smartphone = Lead Attester (agrega evidências do Sub-Attester + atestação de plataforma)
- Servidor LICET = Verifier (valida a cadeia de evidências conforme RFC 9334 §3.1.4 Composite Attester)

**Efeito prático:** cada autorização LICET carrega no ledger o nível L0-L3 da atestação, permitindo que integradores definam requisitos mínimos por tipo de ação (ex: autorização de cirurgia requer L2; autorização de relatório requer L1).

---

## 5. Protocolo de Baseline Individual

### 5.1 Necessidade do baseline personalizado

Limiares universais (ex: "FC > 130 = coerção") são clinicamente inválidos. Um atleta de elite tem FC de repouso de 45 bpm e HRV de 80 ms; um paciente cardíaco tem FC de repouso de 90 bpm e HRV de 15 ms. O mesmo limiar absoluto produz falsos positivos em um e falsos negativos em outro.

O LICET v2.0 implementa um protocolo de baseline **individual e longitudinal**:

### 5.2 Requisitos de baseline

- **Mínimo:** ≥ 5 sessões de calibração × ≥ 3 minutos cada (15 minutos totais de dados calmos)
- **Validade:** 30 dias — após isso, o baseline expira e nova calibração é necessária
- **Condição:** sessões de calibração devem ocorrer em estado de repouso documentado (sem exercício recente, sem medicação de efeito agudo)
- **Armazenamento:** μ_calm (vetor de médias), S (matriz de covariância 5×5), data de expiração, maturity_score

### 5.3 Detecção pré-medicação

Durante a calibração, o sistema detecta anomalias que sugerem que o próprio baseline está sendo coletado sob influência farmacológica:

```python
# Sinais de alerta durante calibração
if eda_scl < limiar_minimo_EDA:
    flag("POSSÍVEL_ANTICOLINÉRGICO_NA_CALIBRAÇÃO")
if tremor_8_12hz < percentil_5_populacional:
    flag("POSSÍVEL_BETABLOQUEADOR_NA_CALIBRAÇÃO")
if rmssd > percentil_95_individual_histórico:
    flag("HRV_PARADOXALMENTE_ELEVADO — verificar anticolinérgico")
```

Um baseline coletado sob drogas produz um μ_calm distorcido que reduziria D_M para ataques farmacológicos subsequentes. O sistema rejeita sessões de calibração que apresentam esses padrões.

### 5.4 Renovação e continuidade

O baseline não é descartado abruptamente: uma janela deslizante de 30 dias com peso maior para sessões recentes permite adaptação a mudanças fisiológicas legítimas (nova medicação prescrita, mudança de condicionamento físico) sem tornar o sistema facilmente manipulável.

---

## 6. API — Protocolo de Comunicação

O LICET expõe uma API REST disponível em **https://licet.dev**

### Endpoints

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/v1/health` | Status do protocolo |
| POST | `/v1/authorize` | Autorização biométrica completa (três camadas) |
| POST | `/v1/biometric/push` | Recebe dados do wearable via app |
| POST | `/v1/authorize/from-push` | Autoriza usando dados do push |
| POST | `/v1/verify` | Verifica prova ZK (auditores) |
| GET | `/v1/ledger/integrity` | Verifica integridade do ledger |
| GET | `/v1/ledger/history` | Histórico de autorizações |
| GET | `/v1/hardware/scan` | Escaneia wearables BLE próximos |
| POST | `/v1/baseline/session` | Registra sessão de calibração de baseline |
| GET | `/v1/baseline/status` | Status do baseline do usuário (maturity, expiração) |
| GET | `/v1/signing-key` | Chave pública Ed25519 para auditores (GAP-C02) |
| POST | `/v1/ledger/timestamp` | Ancora Merkle root no OpenTimestamps (GAP-C03) |
| POST | `/v1/admin/key/split` | Shamir split da chave mestre — n=5, threshold=3 (GAP-O02) |
| POST | `/v1/admin/key/combine` | Reconstrução Shamir — somente em recuperação controlada (GAP-O02) |
| POST | `/v1/admin/revoke/{ledger_id}` | Revogação aditiva de entrada do ledger (GAP-O03/H03) |
| GET | `/v1/gdpr/data/{user_id}` | GDPR Art. 15 — direito de acesso (GAP-A05) |
| DELETE | `/v1/gdpr/erasure/{user_id}` | GDPR Art. 17 / LGPD Art. 18 VI — direito ao esquecimento (GAP-A05) |

### Exemplo de autorização v2.0

**Requisição:**
```json
POST /v1/authorize
{
  "action": "prescrever_insulina_50ui",
  "agent_id": "agente_medico_v1",
  "target": "paciente_joao_silva",
  "capture_seconds": 60,
  "trust_level_required": "L1"
}
```

**Resposta (autorizado):**
```json
{
  "authorized": true,
  "intent_hash": "a3f8b2c1d4e5...",
  "biometric_signature": "9f7e6d5c4b3a...",
  "trust_level": "L1",
  "layers": {
    "ecg_cosine_similarity": 0.94,
    "eda_scl": 2.1,
    "eda_scr_count": 3,
    "mahalanobis_distance": 1.47,
    "pharmacological_check": "CLEAR"
  },
  "coercion_risk": "LOW",
  "baseline_maturity": 0.87,
  "denial_reason": "",
  "zkp_proof": {
    "commitment": {"x": "...", "y": "..."},
    "challenge": "0x...",
    "response": "0x...",
    "public_key": {"x": "...", "y": "..."}
  },
  "ledger_id": 42,
  "timestamp": 1782576000.0,
  "hardware_source": "apple_watch_healthkit"
}
```

---

## 7. Modelo de Segurança

### 7.1 O que o LICET protege

| Ameaça | Proteção |
|---|---|
| Agente de IA agindo sem autorização | Intent Hash vincula ação à autorização biométrica |
| Agente AI manipulando action descriptor | UI Binding commitment antes da captura; ui_binding_status na resposta (GAP-A04) |
| Replay attack (reutilizar autorização antiga) | Timestamp na assinatura — cada autorização é única |
| Coerção física do autorizante | Camada 3 (D_M) — estado fisiológico incompatível com autorização detectado |
| Estado cognitivo comprometido | ECG morfologia (Camada 1) + EDA (Camada 2) |
| Spoofing farmacológico | Check de toxidrome + dissociação de correlações via S⁻¹ |
| Medicamentos legítimos causando discriminação | medication_accommodation flag — BETA_BLOCKER_ACCOMMODATED (GAP-L05) |
| Adulteração retroativa do ledger | Hash-chain + server_nonce + âncora OpenTimestamps (GAP-C03/C04) |
| Reescrita completa da cadeia pelo servidor | Merkle root em 3 calendários OpenTimestamps independentes (GAP-C03) |
| Backdating de entradas | server_nonce gerado pelo servidor por entrada (GAP-C04) |
| Exposição de dados biométricos em auditoria | ZKP com witness HKDF(k_m) não exposto no ledger (GAP-C01) |
| Auditoria por terceiros impossível | Ed25519 assimétrico; GET /signing-key (GAP-C02) |
| Comprometimento da chave mestre | Shamir (5,3) — sem HSM, threshold múltiplo de custodiantes (GAP-O02) |
| Perda da chave mestre | Shamir reconstituição com POST /admin/key/combine (GAP-O02) |
| Dispositivo comprometido ou roubado | Revogação aditiva POST /admin/revoke/{ledger_id} (GAP-O03/H03) |
| Baseline poisoned no enrollment | 5-check assessment em build_baseline() (GAP-B08) |
| Viés em peles escuras — PPG | threshold_multiplier ×1.4 para Fitzpatrick V-VI; ppg_equity_warning (GAP-B09) |
| Acumulação de dataset biométrico no servidor | Zeragem pós-extração; endpoints GDPR erasure (GAP-A05) |
| Hardware não confiável | Hierarquia de atestação L0-L3 (RFC 9334) |

### 7.2 Limitações reconhecidas (v2.0)

- A distância de Mahalanobis requer baseline de qualidade; usuários sem baseline válido operam em modo degradado
- Hardware de consumo (wearables) não tem certificação médica formal; L1 é adequado para maioria dos casos, L2 requer hardware específico
- A atestação L3 (sensor-para-TEE direto) é trabalho futuro — não há hardware de consumo disponível que implemente esse modelo hoje
- O custo de coerção farmacológica é elevado mas não infinito — adversários com recursos de nível estatal e expertise farmacológica especializada permanecem fora do modelo de ameaça desta versão
- App iOS e Android com suporte completo à Camada 2 (EDA) requer integração com WHOOP API (não pública para todos os desenvolvedores)

### 7.3 Roadmap de segurança

- v2.1: Validação clínica da Camada 3 com parceiro universitário
- v2.2: App iOS com Camada 1 (ECG) via HealthKit completo
- v3.0: Especificação L3 (sensor-para-TEE) — aguarda hardware disponível
- Ongoing: Estudo de validação com universidade parceira (USP/UNICAMP)

---

## 8. Alinhamento com IETF RATS

O LICET v2.0 foi submetido ao IETF como Internet-Draft `draft-pereira-licet-human-intent-01` (02/07/2026) e está alinhado com a arquitetura RFC 9334 (Remote Attestation Procedures).

### 8.1 Topologia Composite Attester

RFC 9334 §3.1.4 define o modelo de Composite Attester, onde múltiplos sub-attesters contribuem para uma evidência unificada verificada por um Verifier. O LICET mapeia diretamente sobre essa topologia:

```
┌──────────────────────────────────────────────────────┐
│  COMPOSITE ATTESTER (RFC 9334 §3.1.4)               │
│                                                      │
│  ┌─────────────────┐    ┌──────────────────────┐    │
│  │  Sub-Attester   │    │  Sub-Attester        │    │
│  │  Wearable       │    │  Wearable EDA        │    │
│  │  (ECG / Apple   │    │  (WHOOP 5 /          │    │
│  │  Watch 4+)      │    │  Samsung GW7)        │    │
│  └────────┬────────┘    └──────────┬───────────┘    │
│           └──────────┬─────────────┘                │
│                      ↓                              │
│         ┌────────────────────────┐                  │
│         │   Lead Attester        │                  │
│         │   Smartphone           │                  │
│         │   (iOS / Android)      │                  │
│         │   Agrega evidências +  │                  │
│         │   atestação de         │                  │
│         │   plataforma           │                  │
│         └──────────┬─────────────┘                  │
└────────────────────┼─────────────────────────────────┘
                     ↓
         ┌────────────────────────┐
         │   Verifier             │
         │   Servidor LICET       │
         │   Valida evidências    │
         │   RFC 9334 §3.2        │
         └────────────────────────┘
```

### 8.2 Evidência e Claims

No vocabulário RATS:
- **Evidence:** dados biométricos assinados pelo Lead Attester (app no smartphone)
- **Endorsements:** certificados de fabricante do wearable (Apple, Samsung, WHOOP)
- **Attestation Result:** o registro no ledger LICET + prova ZKP
- **Relying Party:** o agente de IA que solicitou a autorização

### 8.3 Níveis de garantia RATS e LICET L0-L3

| LICET Trust Level | RATS Terminology | Garantia |
|---|---|---|
| L0 | No Attestation | Apenas para desenvolvimento |
| L1 | Platform Attestation | App store integrity + canal TLS |
| L2 | Hardware Attestation | Android Key Attestation / Secure Enclave |
| L3 | (future) | Sensor-to-TEE direct channel |

---

## 9. Casos de Uso

### 9.1 Saúde (uso primário)

Agentes de IA médicos que precisam de autorização humana verificável para:
- Prescrição de medicamentos controlados (requer L1 mínimo)
- Ajuste de protocolos de tratamento
- Acesso a prontuários sensíveis
- Execução de procedimentos remotos (requer L2)

### 9.2 Finanças

- Autorização de transferências acima de limites definidos
- Aprovação de operações de crédito por agentes de IA
- Execução de trades por sistemas autônomos

### 9.3 Infraestrutura crítica

- Modificações em sistemas de energia, água, telecomunicações (requer L2)
- Operações de manutenção executadas por agentes autônomos
- Controle de acesso físico mediado por IA

### 9.4 Jurídico e compliance

- Assinatura de documentos por agentes com delegação legal
- Autorização de processos automatizados regulados
- Auditoria de decisões de IA com evidência de supervisão humana

---

## 10. Conformidade Regulatória

### LGPD (Lei Geral de Proteção de Dados — Brasil)

- Dados biométricos brutos nunca são armazenados no ledger
- A ZKP garante que a prova de autorização não expõe dados pessoais sensíveis
- O titular dos dados é o único capaz de gerar uma assinatura válida
- O baseline individual é armazenado criptografado e com data de expiração (30 dias)

### EU AI Act (Regulação Europeia de IA — 2024)

O LICET implementa diretamente os seguintes requisitos para sistemas de IA de alto risco:

- **Art. 9 (Gestão de riscos):** o protocolo de baseline individual e a hierarquia L0-L3 constituem sistema de gestão de riscos de autorização biométrica
- **Art. 12 (Manutenção de registros):** o ledger hash-chained fornece log técnico imutável de cada autorização, com Intent Hash, timestamp e prova ZKP — auditável sem exposição de dados biométricos
- **Art. 26(5) (Obrigações do operador):** o LICET fornece ao operador/deployer evidência criptográfica de que supervisão humana foi exercida, endereçando diretamente as obrigações de oversight do deployer

*Nota técnica: o Art. 14 (capacidade de supervisão humana do sistema de IA) trata da arquitetura interna do sistema de IA para permitir supervisão humana. O LICET não é o sistema de IA — é o mecanismo de attestation do supervisor humano. A conformidade relevante é Art. 26(5), não Art. 14.*

### CFM (Conselho Federal de Medicina — Brasil)

Complementa os requisitos de responsabilidade médica em contextos onde agentes de IA auxiliam ou executam procedimentos clínicos.

---

## 11. Propriedade Intelectual e Anterioridade

| Item | Detalhe |
|---|---|
| **Autor/Titular** | Christian Rodrigues Pereira |
| **Anterioridade blockchain** | 25/02/2026 — OpenTimestamps (Bitcoin) |
| **Domínio** | licet.dev — registrado 25/06/2026 |
| **Deploy de produção** | 26/06/2026 |
| **SSRN Preprint** | Abstract ID 7018458 — v1 publicado 29/06/2026, v2 atualizado 02/07/2026 |
| **GitHub** | github.com/christianrp45/licet-protocol — Apache 2.0 — publicado 29/06/2026 |
| **IETF Internet-Draft -00** | draft-pereira-licet-human-intent-00 — submetido 29/06/2026 |
| **IETF Internet-Draft -01** | draft-pereira-licet-human-intent-01 — submetido 02/07/2026 |
| **Paper LaTeX v2** | docs/arxiv/licet_protocol.tex — três camadas, Mahalanobis, L0-L3, farmacológico |
| **PR #97 LF Decentralized Trust** | proof-of-effort (LF-Decentralized-Trust-labs) — submetido 02/07/2026 |
| **Colaboração CPoE** | David Condrey (Linux Foundation / IETF RATS WG) — caminho de co-autoria aberto via draft-condrey-cpoe-protocol |
| **Registro de marca** | Pendente — INPI Classe 42 |
| **Organização** | NeuroTrust |

---

## 12. Conclusão

O LICET endereça um problema estrutural que se tornará crítico à medida que agentes de IA ganham autonomia real em domínios de alto impacto. A versão 2.0 avança substancialmente sobre a fundação da v1.0: substitui limiares binários por análise multivariada personalizada, adiciona morfologia ECG anatomicamente determinada e atividade eletrodérmica imune a betabloqueadores, formaliza a hierarquia de confiança de atestação e mapeia o protocolo sobre a arquitetura RATS do IETF.

O resultado é um protocolo onde o custo de coerção não é apenas "elevado" em termos abstratos — é operacionalmente quantificado. Um adversário que deseja suprimir os cinco canais biométricos simultaneamente precisa orquestrar agentes farmacológicos com mecanismos de ação opostos, deixando assinaturas detectáveis nos canais que não consegue controlar. Esse é o objetivo de design: não detectar coerção com certeza absoluta, mas tornar a coerção dispendiosa o suficiente para ser inviável na prática.

O protocolo está disponível publicamente em **https://licet.dev**, sua especificação técnica é aberta (Apache 2.0), o Internet-Draft está em processo de padronização no IETF, e o preprint está disponível no SSRN (Abstract ID 7018458).

---

*LICET — "É permitido" (latim) — porque a permissão humana consciente deve ser o fundamento de qualquer ação de IA com consequências reais.*
