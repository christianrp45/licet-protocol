# LICET — Guia Completo de Aprendizado
## Para Christian Rodrigues Pereira | eColabs | Julho 2026

> **Como usar este guia:**
> Este documento foi escrito inteiramente em português para que você possa estudar o LICET
> sem barreira de idioma. Cada termo técnico aparece em inglês (porque é assim que o mundo
> técnico o conhece) seguido da tradução e explicação em português.
> Leia com calma. Volte sempre que precisar. Este é o seu mapa.

---

# PARTE 1 — O QUE É O LICET (A IDEIA CENTRAL)

## 1.1 O Problema que o LICET Resolve

Imagine que você tem um assistente de inteligência artificial (IA) que pode fazer compras,
assinar contratos, mover dinheiro ou tomar decisões em seu nome.

A pergunta mais importante do mundo é: **"Quem autorizou isso?"**

Era você? Era um hacker que invadiu sua conta? Era alguém te ameaçando com uma arma?
Era você sob efeito de drogas? Era você dormindo e com a digital colocada à força?

Os sistemas atuais — senha, impressão digital, reconhecimento facial — confirmam **identidade**,
mas não confirmam **intenção livre e consciente**. Alguém pode te forçar a desbloquear o
celular com seu próprio dedo.

## 1.2 A Solução LICET

**LICET** é a sigla de **"Liveness, Intent, Consent, and Ethical Trust"**
(em português: **Vivacidade, Intenção, Consentimento e Confiança Ética**).

O LICET é um **protocolo** — uma série de regras e verificações — que usa seus sinais
biométricos (batimento cardíaco, nível de estresse fisiológico, padrões elétricos da pele)
para provar que:

1. Você está **vivo e consciente** (não é uma gravação, uma máscara ou um corpo desmaiado)
2. Você está em **estado de calma voluntária** (não está sendo ameaçado, drogado ou coagido)
3. Você **realmente quis** autorizar aquela ação específica
4. Esta prova pode ser **verificada criptograficamente** por qualquer terceiro

Em uma frase: **o LICET prova que foi você, consciente e livre, quem disse "sim".**

## 1.3 Onde o LICET Pode Ser Usado

| Setor | Aplicação |
|-------|-----------|
| **Inteligência Artificial** | Agentes de IA precisam de autorização humana real antes de agir |
| **Serviços Financeiros** | Transações bancárias de alto valor comprovadamente intencionais |
| **Saúde** | Consentimento informado para cirurgias ou procedimentos |
| **Jurídico** | Assinatura de contratos com prova de livre vontade |
| **Governo / Votação** | Votação digital com prova de intenção não coagida |
| **Segurança Corporativa** | Acesso a sistemas críticos com atestação de estado mental |

---

# PARTE 2 — GLOSSÁRIO TÉCNICO COMPLETO

> Formato de cada entrada:
> **TERMO em inglês** | *Tradução em português* | Explicação clara

---

## 2.1 Termos Fundamentais do Protocolo

---

**LICET Protocol** | *Protocolo LICET*

O conjunto completo de regras que define como coletar sinais biométricos, analisá-los,
gerar provas criptográficas e registrar a autorização de forma imutável. É como uma
"constituição" que todos os componentes do sistema seguem.

---

**Protocol** | *Protocolo*

Um conjunto de regras acordadas que define como dois ou mais sistemas se comunicam.
Como as regras de trânsito: todos seguem as mesmas para que o sistema funcione.
Exemplos famosos: HTTP (internet), HTTPS (internet segura), TCP/IP (base da internet).
O LICET é um protocolo para autorização de intenção humana.

---

**Human Intent** | *Intenção Humana*

O conceito central do LICET. Não basta saber *quem* fez algo — é preciso saber se aquela
pessoa *quis* fazer de forma livre, consciente e sem pressão. O LICET tenta medir isso
através dos sinais fisiológicos do corpo.

---

**Authorization** | *Autorização*

Permissão concedida para realizar uma ação específica. No LICET, autorização só é concedida
quando os sinais biométricos confirmam estado de calma voluntária. Diferente de
**Authentication** (autenticação), que apenas confirma *quem você é*.
- **Authentication** = Quem é você? (identidade)
- **Authorization** = Você pode fazer isso? (permissão)

---

**Biometric** | *Biométrico*

Qualquer medição do corpo humano usada para identificação ou verificação de estado.
Exemplos: impressão digital, reconhecimento facial, batimento cardíaco, padrão elétrico
da pele. O LICET usa biometria de *estado fisiológico* (como você está), não apenas
de *identidade* (quem você é).

---

**Coercion** | *Coerção*

Forçar alguém a fazer algo contra sua vontade — através de ameaça física, chantagem,
drogas, pressão psicológica ou qualquer forma de pressão. O LICET é projetado para
detectar sinais fisiológicos de coerção e negar autorização quando detectados.

---

**Liveness** | *Vivacidade / Prova de Vida*

Prova de que existe um ser humano vivo e consciente presente. Sistemas biométricos simples
podem ser enganados com foto, vídeo ou até dedo cortado. O LICET verifica liveness
através de múltiplos sinais que só um humano vivo e consciente pode produzir
simultaneamente.

---

**Consent** | *Consentimento*

Acordo livre e informado para que algo seja feito. O LICET diferencia entre um "sim"
sob ameaça (não é consentimento válido) e um "sim" em estado de calma voluntária
(consentimento genuíno).

---

**Trust Level** | *Nível de Confiança*

Escala de L0 a L3 que indica o quanto a autorização LICET pode ser confiada:
- **L0** — Simulação / sem hardware real (desenvolvimento, testes)
- **L1** — Wearable com atestação de software (Apple Watch, Samsung Watch)
- **L2** — Hardware com atestação de chave criptográfica (Pixel Watch 2)
- **L3** — Sensor conectado diretamente ao chip seguro (trabalho futuro)

---

**Intent Hash** | *Hash de Intenção*

Uma "impressão digital matemática" única da ação que está sendo autorizada. Se alguém
tentar alterar a ação depois da autorização, o hash vai mudar e a fraude será detectada.
Calculado com SHA-256 (veja abaixo).

---

**Pipeline** | *Fluxo de Processamento / Cadeia de Verificação*

Sequência de etapas onde cada saída alimenta a próxima entrada. O LICET tem um pipeline
de autorização: Sinal Biométrico → Camada 1 (ECG) → Camada 2 (EDA) → Verificação
Farmacológica → Camada 3 (Mahalanobis) → ZKP → Ledger.

---

## 2.2 Termos de Cardiologia e HRV

---

**Heart Rate (HR)** | *Frequência Cardíaca (FC)*

Número de batimentos do coração por minuto (BPM — Beats Per Minute). Em repouso,
um adulto saudável tem entre 60 e 80 BPM. O LICET usa a FC como um dos sinais
de estado fisiológico: coerção tipicamente eleva a FC (taquicardia).

---

**SpO2** | *Saturação de Oxigênio no Sangue*

Porcentagem do sangue que está transportando oxigênio. Normal: 95-100%. Abaixo de 90%
indica comprometimento cognitivo (hipóxia). O LICET verifica SpO2 para garantir que
o usuário está cognitivamente capaz de tomar decisões.

---

**HRV (Heart Rate Variability)** | *VFC — Variabilidade da Frequência Cardíaca*

O coração saudável não bate em intervalos perfeitamente iguais. Ele acelera ligeiramente
ao inspirar e desacelera ao expirar. Essa variação é a VFC. Alta VFC = sistema nervoso
autônomo saudável e em equilíbrio. Baixa VFC = estresse, doença, coerção.
**O LICET usa a VFC como o principal indicador de estado emocional e autonômico.**

---

**RMSSD** | *Raiz Quadrada da Média dos Quadrados das Diferenças Sucessivas*

O jeito mais preciso de medir a VFC. Calcula a variação entre batimentos consecutivos.
Valores típicos em repouso: 30-60 ms (milissegundos). Coerção reduz o RMSSD. Drogas
anticolinérgicas (como escopolamina) abolem o RMSSD completamente.
**É o sinal mais importante no pipeline do LICET.**

---

**RR Interval** | *Intervalo RR*

O tempo (em milissegundos) entre dois batimentos cardíacos consecutivos. Se o coração
bate 60 vezes por minuto, o intervalo RR médio é 1000 ms. Esses intervalos são a
"matéria-prima" para calcular RMSSD e análise espectral. O LICET coleta ≥60 intervalos
RR (≈60 segundos) para análise espectral confiável.

---

**ECG (Electrocardiogram)** | *ECG — Eletrocardiograma*

Registro gráfico da atividade elétrica do coração. Cada batimento produz uma forma de
onda característica (complexo QRS). O padrão QRS de cada pessoa é único — como uma
impressão digital cardíaca. O LICET usa o ECG na Camada 1 para verificar identidade
(morfologia QRS) e vivacidade.

---

**QRS Complex** | *Complexo QRS*

A parte principal da onda do ECG — representa a contração dos ventrículos do coração.
A forma do complexo QRS é individualmente específica: altura, largura, simetria.
O LICET compara o QRS atual com o template do usuário usando similaridade cosseno.

---

**Cosine Similarity** | *Similaridade Cosseno*

Medida matemática de quanto duas formas são parecidas (0 = completamente diferentes,
1 = idênticas). Usada na Camada 1 para comparar o QRS atual com o template do baseline.
Limiar no LICET: ≥0.85 (85% de similaridade mínima para passar).

---

**RSA (Respiratory Sinus Arrhythmia)** | *ASR — Arritmia Sinusal Respiratória*

Fenômeno fisiológico normal: o coração acelera ao inspirar e desacelera ao expirar.
Isso cria uma oscilação rítmica no HRV sincronizada com a respiração. O LICET detecta
quando essa oscilação é suspeitamente regular (possível respiração ressonante treinada)
através do Índice de Periodicidade.

---

**Paced Breathing** | *Respiração Ressonante / Respiração Cadenciada*

Técnica de controle respiratório onde a pessoa respira a aproximadamente 6 ciclos por
minuto (~0.1 Hz) para maximizar a VFC e produzir um estado de calma fisiológica. É o
**principal ataque não mitigado contra o LICET**: um adversário treinado pode produzir
um vetor de calma genuíno sem nenhuma anomalia farmacológica.

---

**Resonance Frequency** | *Frequência de Ressonância*

A frequência de respiração (~0.1 Hz, ~6 respirações/min) que maximiza a oscilação do
HRV. Usado em biofeedback de redução de estresse. No contexto de segurança do LICET,
é a frequência usada em ataques de paced breathing.

---

## 2.3 Termos de Análise Espectral

---

**Spectral Analysis** | *Análise Espectral*

Técnica matemática para decompor um sinal em suas frequências componentes — como um
prisma que separa a luz em cores. Aplicada aos intervalos RR, revela padrões de
respiração e atividade autonômica que não são visíveis no sinal bruto.

---

**DFT (Discrete Fourier Transform)** | *TDF — Transformada Discreta de Fourier*

Algoritmo matemático que converte um sinal do domínio do tempo para o domínio da
frequência. O LICET implementa DFT puro em Python (sem bibliotecas externas) para
analisar os intervalos RR. Calcula a "potência" (energia) em cada frequência de 0.04
a 0.40 Hz.

---

**HF Band (High Frequency)** | *Banda HF (Alta Frequência)*

Faixa espectral de 0.15 a 0.40 Hz no HRV. Corresponde à modulação do nervo vago
sincronizada com a respiração (RSA). Alta potência HF = alta atividade parassimpática
= calma genuína. Paced breathing a 0.1 Hz *reduz* a potência HF porque move a
oscilação para a banda LF.

---

**LF Band (Low Frequency)** | *Banda LF (Baixa Frequência)*

Faixa espectral de 0.04 a 0.15 Hz no HRV. Reflete principalmente a modulação
barorreflexo (regulação da pressão arterial), não o tônus simpático como se pensava
antigamente. Beta-bloqueadores afetam esta banda.

---

**Periodicity Index (IP)** | *Índice de Periodicidade*

Métrica criada pelo LICET. Mede quanto da energia espectral do HRV está concentrada
em uma banda estreita ao redor do pico dominante. Fórmula:
`IP = potência na janela / potência total`
- IP > 0.80 = espectro suspeito (consistente com paced breathing)
- IP < 0.60 = espectro broadband (consistente com repouso genuíno)

---

**Broadband** | *Banda Larga (espectro distribuído)*

Quando a energia espectral está espalhada por muitas frequências — padrão do repouso
genuíno. Oposição: espectro estreito (narrow-band) com pico concentrado, típico de
paced breathing.

---

**RSA Amplitude** | *Amplitude RSA*

A variação pico-a-vale dos intervalos RR dentro de cada ciclo respiratório. Alta
amplitude com baixo coeficiente de variação (CV baixo) é suspeita: indica oscilação
regular como a produzida por paced breathing treinado.

---

**CV (Coefficient of Variation)** | *CV — Coeficiente de Variação*

Desvio padrão dividido pela média. Mede a irregularidade relativa. Para a amplitude
RSA no LICET:
- CV baixo (~0.03) = amplitude muito regular = possível paced breathing
- CV alto (~0.40) = amplitude variável = padrão de repouso genuíno

---

## 2.4 Termos de Fisiologia do Estresse

---

**ANS (Autonomic Nervous System)** | *SNA — Sistema Nervoso Autônomo*

A parte do sistema nervoso que controla funções automáticas (coração, respiração,
digestão, resposta ao estresse) sem necessidade de pensamento consciente. Tem dois
ramos principais:
- **Sympathetic** (*Simpático*): "Luta ou fuga" — acelera o coração, aumenta estresse
- **Parasympathetic** (*Parassimpático*): "Repouso e digestão" — desacelera, relaxa

---

**Vagal Tone** | *Tônus Vagal*

Nível de atividade do nervo vago — o principal nervo do sistema parassimpático. Alto
tônus vagal = RMSSD alto = calma. Baixo tônus vagal = RMSSD baixo = estresse, medo,
coerção. O LICET mede indiretamente o tônus vagal através do RMSSD.

---

**Sympathetic Activation** | *Ativação Simpática*

Resposta do sistema nervoso ao estresse ou perigo: aumento da FC, redução do HRV,
aumento da condutância da pele. Em coerção genuína, ocorre ativação simpática
intensa — o que o LICET tenta detectar.

---

**Vagal Withdrawal** | *Retirada Vagal*

Redução rápida da atividade parassimpática em resposta ao estresse ou ameaça. Resulta
em queda abrupta do RMSSD. É um dos indicadores que o LICET monitora para detectar coerção.

---

**Baroreflex** | *Barorreflexo*

Mecanismo de feedback do sistema cardiovascular para regular a pressão arterial. Quando
a pressão sobe, o barorreflexo desacelera o coração (mediado pelo nervo vago). Isso
gera a oscilação LF no HRV. Importante: LF não é simpático — é barorreflexo.

---

## 2.5 Termos de EDA (Atividade Eletrodérmica)

---

**EDA (Electrodermal Activity)** | *AED — Atividade Eletrodérmica*

Variação na condutância elétrica da pele causada pela atividade das glândulas sudoríparas.
Quando você fica estressado ou com medo, sua pele conduz mais eletricidade. É controlada
exclusivamente pelo sistema nervoso *simpático* colinérgico — por isso drogas
anticolinérgicas a suprimem completamente.

---

**SCL (Skin Conductance Level)** | *NCS — Nível de Condutância da Pele*

Componente tônico (lento) da EDA — o "nível base" de condutância da pele. Medido em
microsiemens (μS). Alta SCL = estado de alerta/estresse. Em repouso calmo: 1-5 μS típico.
Anticolinérgicos suprimem o SCL a valores próximos de zero.

---

**SCR (Skin Conductance Response)** | *RCS — Resposta de Condutância da Pele*

Componente fásico (rápido) da EDA — picos de condutância em resposta a estímulos
específicos (susto, ameaça, emoção). Medido em μS. Também chamado de "galvanic skin
response" (GSR). O LICET usa SCR < 0.01 μS como evidência de bloqueio colinérgico.

---

**Anticholinergic** | *Anticolinérgico*

Classe de drogas que bloqueiam a acetilcolina (neurotransmissor colinérgico). Efeitos:
EDA suprimida (glândulas sudoríparas paralisadas), RMSSD abolido, taquicardia (FC > 100).
Exemplos: escopolamina (usado em patches anti-enjoo), atropina. O LICET detecta a
tríade autoincriminante: EDA plana + RMSSD abolido + taquicardia.

---

**Self-Incriminating Triad** | *Tríade Autoincriminante*

Combinação de três sinais que, juntos, indicam bloqueio anticolinérgico com alta certeza:
1. EDA plana (SCR < 0.01 μS)
2. RMSSD abolido (muito abaixo do baseline)
3. Taquicardia (FC > 100 BPM ou muito acima do baseline)

Nenhum estado genuíno de calma produz esta tríade. O LICET nega automaticamente
com código `ANTICHOLINERGIC_SELF_INCRIMINATING_TRIAD`.

---

**Beta-blocker** | *Beta-bloqueador*

Classe de drogas que bloqueiam receptores beta-adrenérgicos. Efeitos: redução da FC,
aumento paradoxal do RMSSD (por redução da atividade simpática basal). Problema para
o LICET: o fingerprint de calma de um usuário em uso crônico de beta-bloqueador é
deslocado — RMSSD artificialmente elevado, FC artificialmente baixa. O LICET sinaliza
isso como `beta_blocker_confound_warning`.

---

## 2.6 Termos Matemáticos e Estatísticos

---

**Mahalanobis Distance** | *Distância de Mahalanobis*

Medida estatística que calcula o quão longe um ponto está do "centro" de um conjunto
de dados, **levando em conta a correlação entre as variáveis**. No LICET, mede o quão
diferente o estado biométrico atual é do baseline individual do usuário.
Fórmula: `D² = (x - μ)ᵀ Σ⁻¹ (x - μ)`
- `x` = vetor de sinais atuais
- `μ` = vetor médio do baseline
- `Σ⁻¹` = inversa da matriz de covariância

---

**Baseline** | *Linha de Base / Estado Basal*

O estado biométrico "normal" e individual de um usuário em repouso calmo. Calculado a
partir de ≥5 sessões de calibração de ≥3 minutos cada. O baseline é único para cada
pessoa — não compara com médias populacionais (exceto como fallback).

---

**Chi-squared (χ²)** | *Qui-quadrado*

Distribuição estatística usada como limiar no Mahalanobis. Se D² > χ²(df, p=0.05),
o desvio é estatisticamente significativo (só 5% de chance de ser aleatório).
Valores no LICET:
- 2 sinais: χ²(2) = 5.99
- 5 sinais: χ²(5) = 11.07
- 7 sinais: χ²(7) = 14.07

---

**Covariance Matrix (Σ)** | *Matriz de Covariância*

Matriz que descreve como os sinais biométricos variam juntos. Por exemplo: RMSSD e FC
têm covariância negativa (quando um sobe, o outro tende a descer). O LICET calcula Σ
a partir das sessões de baseline para personalizar o detector.

---

**Z-score** | *Z-escore / Escore Padrão*

Quantas vezes o desvio padrão um valor está acima ou abaixo da média do baseline.
Z = (valor - média) / desvio_padrão. No LICET, Z-scores > 2.0 ou < -2.0 ativam
verificações farmacológicas.

---

**Signal Vector** | *Vetor de Sinais*

Lista ordenada de valores de múltiplos sensores, tratada matematicamente como um único
ponto em espaço multidimensional. Exemplo: [RMSSD=52ms, SpO2=98%, SCL=3.5μS,
HF_power=45000ms²]. O Mahalanobis calcula a distância deste vetor ao baseline.

---

## 2.7 Termos Criptográficos

---

**Cryptography** | *Criptografia*

Ciência de proteger informações usando matemática. Transforma dados legíveis em dados
incompreensíveis para quem não tem a chave correta. O LICET usa criptografia para:
assinar autorizações, derivar chaves únicas por sessão e gerar provas verificáveis.

---

**HMAC (Hash-based Message Authentication Code)** | *Código de Autenticação de Mensagem baseado em Hash*

Mecanismo simétrico para verificar integridade — quem gera também pode forjar. O LICET
usava HMAC-SHA256 como Biometric Signature nas versões anteriores, mas migrou para
Ed25519 (veja abaixo) porque HMAC não permite auditoria por terceiros sem revelar a
chave secreta (GAP-C02, corrigido em 09/07/2026).

---

**Ed25519** | *Assinatura Digital de Curva Elíptica*

Algoritmo de assinatura assimétrica baseado na curva Edwards25519. Usa par de chaves:
a chave privada (só o servidor conhece) produz a assinatura; a chave pública (disponível
em `GET /signing-key`) permite que qualquer auditor verifique a assinatura sem acesso
ao servidor. O LICET migrou de HMAC-SHA256 para Ed25519 em 09/07/2026 (GAP-C02).
**Propriedade fundamental:** não-repúdio — o servidor não pode negar ter produzido uma
assinatura válida com sua chave privada.

---

**SHA-256** | *Algoritmo de Hash Seguro 256 bits*

Função matemática que transforma qualquer dado em uma string de 64 caracteres fixos.
Propriedade fundamental: uma mínima mudança na entrada gera uma saída completamente
diferente. Irreversível: não dá para recuperar o original a partir do hash.
Usado no LICET para criar o Intent Hash e na cadeia de hashes do ledger.

---

**HKDF (HMAC-based Key Derivation Function)** | *Função de Derivação de Chave baseada em HMAC*

Algoritmo para derivar chaves criptográficas únicas a partir de uma chave mestra.
O LICET usa HKDF-SHA256 para criar uma chave de sessão diferente para cada autorização —
assim, mesmo que uma sessão seja comprometida, as outras permanecem seguras.

---

**ZKP (Zero-Knowledge Proof)** | *Prova de Conhecimento Zero*

Método criptográfico que permite provar que você sabe algo (ou que um fato é verdadeiro)
**sem revelar a informação em si**. No LICET: prova que os sinais biométricos passaram
em todas as verificações, sem expor os dados brutos do usuário.
Analogia: provar que você sabe a senha de um cofre sem dizer a senha.

---

**Schnorr Proof** | *Prova de Schnorr*

Tipo específico de ZKP baseado em criptografia de curva elíptica. É eficiente e bem
compreendido pela comunidade criptográfica. O LICET usa Schnorr sobre a curva BN128.

---

**BN128** | *Curva Elíptica BN128*

Curva matemática específica usada em criptografia. BN128 (também chamada de alt_bn128)
é amplamente usada em contratos inteligentes Ethereum e sistemas ZKP. Permite
computações criptográficas eficientes.

---

**Hash Chain** | *Cadeia de Hashes*

Estrutura onde cada registro contém o hash do registro anterior. Isso torna adulteração
retroativa matematicamente detectável: mudar um registro invalida todos os subsequentes.
O Bitcoin usa o mesmo princípio. O LICET aplica isso ao ledger de autorizações.

---

**Ledger** | *Ledger / Livro-Razão*

Registro histórico imutável de todas as autorizações. No LICET, cada entrada contém:
dados da autorização + hash do estado fisiológico + link para o registro anterior
(chain hash). Pode ser verificado por qualquer terceiro para detectar adulteração.

---

**Biometric Signature** | *Assinatura Biométrica*

Código único produzido pelo LICET que vincula matematicamente: a ação autorizada +
o estado fisiológico do usuário + a chave privada do servidor. A partir de 09/07/2026,
usa Ed25519 (assimétrico) em vez de HMAC-SHA256 (simétrico), tornando a assinatura
verificável por qualquer auditor com acesso à chave pública em `GET /signing-key`.

---

**Shamir Secret Sharing** | *Compartilhamento de Segredo de Shamir*

Técnica criptográfica que divide um segredo (como a chave mestre `k_m`) em `n` partes
(*shares*), de forma que qualquer `t` partes (threshold) são suficientes para reconstruir
o segredo, mas `t-1` partes revelam zero informação. O LICET usa configuração (n=5, t=3)
sobre GF(2^256+297): qualquer 3 dos 5 custodiantes reconstroem `k_m`; perder até 2 shares
não compromete a recuperação (GAP-O02, implementado em 09/07/2026).

---

**Secret Key** | *Chave Secreta*

Dado criptográfico secreto que não pode ser descoberto por terceiros. O LICET usa
`LICET_SECRET_KEY` (64 caracteres hexadecimais) como chave mestra. Nunca armazenada
em código — apenas em variáveis de ambiente seguras.

---

**Session Key** | *Chave de Sessão*

Chave temporária única derivada da chave mestra para cada autorização. Mesmo que
alguém capture a chave de uma sessão, não consegue forjar sessões futuras.

---

## 2.8 Termos de Hardware e Wearables

---

**Wearable** | *Dispositivo Wearável / Vestível*

Dispositivo eletrônico usado no corpo. Exemplos: smartwatch (Apple Watch, Samsung Galaxy
Watch), anel inteligente (Oura Ring), bandas (WHOOP). O LICET suporta qualquer wearable
que exponha dados de FC, HRV, EDA e SpO2.

---

**BLE (Bluetooth Low Energy)** | *Bluetooth de Baixo Consumo*

Protocolo de comunicação sem fio de curto alcance e baixo consumo de bateria. Usado
pela maioria dos wearables para transmitir dados para smartphones. O LICET pode
receber dados via BLE diretamente de sensores compatíveis.

---

**NFC (Near Field Communication)** | *Comunicação de Campo Próximo*

Tecnologia de comunicação sem fio de curtíssimo alcance (< 4 cm). Usada em pagamentos
por aproximação (Google Pay, Apple Pay). O app Android do LICET planeja integrar NFC
para fluxos de autorização de alta segurança.

---

**MAX30102** | *Sensor Óptico MAX30102*

Chip sensor de FC e SpO2 por fotopletismografia (PPG — luz LED que detecta variação
no volume de sangue sob a pele). É o sensor de referência do LICET para hardware
embarcado (Raspberry Pi / Arduino).

---

**PPG (Photoplethysmography)** | *FPO — Fotopletismografia*

Técnica de medição de FC e SpO2 usando luz. Um LED ilumina a pele e um fotodetector
mede a luz refletida/transmitida — a variação rítmica corresponde ao pulso cardíaco.
A maioria dos smartwatches usa PPG.

---

**TEE (Trusted Execution Environment)** | *AEC — Ambiente de Execução Confiável*

Área isolada e segura dentro de um processador onde código crítico pode rodar sem
ser acessado por software malicioso. Exemplos: Secure Enclave (Apple), Titan M2
(Google Pixel), TrustZone (ARM). Nível L3 do LICET requer dados do sensor direto
no TEE.

---

**Hardware Attestation** | *Atestação de Hardware*

Prova criptográfica de que um dado foi produzido por um hardware específico e não foi
alterado. Exemplo: Android Key Attestation prova que uma chave criptográfica foi
criada dentro do chip Titan M2. Habilita nível L2 no LICET.

---

**HealthKit** | *HealthKit (Apple)*

Framework da Apple para iOS que centraliza dados de saúde do iPhone e Apple Watch.
Permite que apps (como o LICET) leiam FC, HRV, SpO2 com privacidade controlada pelo
usuário. Equivalente da Samsung: Health Connect.

---

**Health Connect** | *Health Connect (Samsung / Android)*

Plataforma do Android (Google + Samsung) para dados de saúde. O app Android do LICET
usa Health Connect para ler dados do Galaxy Watch (incluindo EDA no Watch 5+).

---

## 2.9 Termos de Software e Arquitetura

---

**API (Application Programming Interface)** | *Interface de Programação de Aplicativos*

Conjunto de regras que define como dois programas se comunicam entre si. O LICET
expõe uma API REST que qualquer sistema pode usar para solicitar autorização biométrica.
Como um menu de restaurante: define o que pode ser pedido e como pedir.

---

**REST API** | *API REST*

Estilo de API baseado em HTTP (o protocolo da internet). Usa verbos HTTP:
- `GET` = buscar dados
- `POST` = enviar/criar dados
O LICET tem endpoints REST em `https://licet.dev/v1/`

---

**Endpoint** | *Endpoint / Ponto de Acesso*

URL específica da API que realiza uma função. Exemplos do LICET:
- `POST /v1/authorize` — solicita autorização biométrica
- `GET /v1/health` — verifica se o servidor está online
- `POST /v1/baseline/start` — inicia calibração de baseline

---

**FastAPI** | *FastAPI*

Framework Python para criar APIs REST de alta performance. É o framework que o LICET
usa para construir todos os seus endpoints. Documentação automática em `/docs`.

---

**Cloud Run** | *Cloud Run (Google Cloud)*

Serviço do Google Cloud que executa contêineres de forma serverless — você não gerencia
servidores, só o código. Escala automaticamente (de 0 a milhares de instâncias). O LICET
está em produção no Cloud Run, região `us-central1`.

---

**Container / Docker** | *Contêiner / Docker*

Tecnologia de empacotamento de software com todas suas dependências. Garante que o código
funciona identicamente em qualquer ambiente (desenvolvimento, produção, cloud).
O LICET usa Dockerfile para construir o contêiner enviado ao Cloud Run.

---

**SQLite** | *SQLite*

Banco de dados leve que armazena dados em um único arquivo. Usado pelo LICET em
desenvolvimento e no Cloud Run para o ledger de autorizações e baselines.

---

**SQLAlchemy** | *SQLAlchemy*

Biblioteca Python que facilita a interação com bancos de dados. Permite escrever código
Python ao invés de SQL puro. O LICET usa SQLAlchemy para todas as operações no banco.

---

**Dataclass** | *Dataclass (Python)*

Forma de definir estruturas de dados em Python de forma limpa. O LICET usa dataclasses
para definir `BiometricReading`, `UserBaseline`, `AuthorizationBundle`, etc.

---

**Pydantic** | *Pydantic*

Biblioteca Python para validação de dados. Garante que os dados enviados à API têm o
tipo e formato corretos antes de serem processados. Integrado ao FastAPI.

---

**HMAC validation** | *Validação HMAC do App Móvel*

Verificação de que os dados enviados pelo app iOS/Android vieram de um aplicativo
legítimo (não de alguém tentando forjar dados). O app assina os dados com
`LICET_MOBILE_APP_SECRET` antes de enviar.

---

**TTL (Time To Live)** | *Tempo de Vida*

Duração máxima de validade de um dado antes de expirar. No LICET:
- Push biométrico expira em 60 segundos
- Token de sessão de baseline expira em 10 minutos
- Baseline completo expira em 30 dias

---

## 2.10 Termos de Padrões e Normas Internacionais

---

**IETF (Internet Engineering Task Force)** | *Força-Tarefa de Engenharia de Internet*

Organização internacional que desenvolve padrões técnicos para a internet (chamados
de RFCs). O LICET tem um draft de Internet-Draft no IETF:
`draft-pereira-licet-human-intent`. Ter um draft no IETF confere credibilidade técnica
internacional ao protocolo.

---

**RFC (Request for Comments)** | *Solicitação de Comentários*

Documento formal do IETF que define padrões técnicos da internet. Exemplos famosos:
RFC 2616 (HTTP), RFC 5246 (TLS), RFC 9334 (RATS). O LICET referencia o RFC 9334.

---

**RFC 9334 — RATS** | *RFC 9334 — Arquitetura RATS*

Standard do IETF de 2023 que define como dispositivos provam remotamente que são
confiáveis (Remote ATtestation procedureS). O LICET se alinha com a arquitetura RATS,
posicionando-o no ecossistema global de confiança zero.

---

**Attester** | *Atestador*

No vocabulário RATS/IETF: entidade que produz evidências de seu próprio estado. No
contexto do LICET + David Condrey (CPoE): o wearable seria o Attester, produzindo
evidências biométricas que o servidor LICET verifica.

---

**CPoE (Composite Proof of Effort)** | *Prova Composta de Esforço*

Protocolo desenvolvido por David Condrey (Linux Foundation) para provar trabalho humano
em sistemas descentralizados. Complementar ao LICET — CPoE foca em padrão de especificação
(IETF draft + CDDL), LICET foca em implementação de referência em produção.

---

**CDDL (Concise Data Definition Language)** | *Linguagem de Definição de Dados Concisa*

Linguagem formal para definir a estrutura de dados de protocolos IETF. Usada para
especificar exatamente quais campos e tipos um pacote de dados deve ter. Próxima tarefa
LICET: criar `cddl/licet.cddl` para formalizar o evidence-packet.

---

**GDPR (General Data Protection Regulation)** | *RGPD — Regulamento Geral de Proteção de Dados*

Lei europeia de proteção de dados pessoais (2018). Define direitos dos cidadãos sobre
seus dados e obrigações das empresas. O LICET foi projetado para ser compatível com
GDPR: dados biométricos nunca são armazenados em texto claro — apenas hashes e assinaturas.

---

**LGPD** | *Lei Geral de Proteção de Dados (Brasil)*

Equivalente brasileiro do GDPR. Entrou em vigor em 2020. A eColabs já notificou a
ANPD (Autoridade Nacional de Proteção de Dados) sobre o protocolo LICET.

---

**ANPD** | *Autoridade Nacional de Proteção de Dados (Brasil)*

Órgão regulador brasileiro responsável por fiscalizar o cumprimento da LGPD. Equivalente
brasileiro do ICO (Reino Unido) ou CNIL (França). Contato da eColabs: ouvidoria@anpd.gov.br.

---

**AI Act (EU AI Act)** | *Lei de IA da União Europeia*

Regulamento europeu de 2024 que classifica sistemas de IA por nível de risco e define
requisitos obrigatórios. Sistemas de IA de alto risco (como agentes autônomos em
contexto financeiro ou médico) precisarão de supervisão humana auditável —
exatamente o que o LICET provê.

---

**SSRN** | *Social Science Research Network*

Repositório de preprints (artigos científicos antes da revisão por pares). O LICET tem
preprint publicado: Abstract ID 7018458. Importante para estabelecer anterioridade.

---

**arXiv** | *arXiv*

Repositório de preprints científicos amplamente usado em física, matemática, ciência da
computação e engenharia. O LICET foi submetido em 13/07/2026 com ID 7765569 (cs.CR +
cs.AI + cs.HC, licença CC BY) — endossado por David Condrey (IETF RATS WG).

---

**INPI** | *Instituto Nacional da Propriedade Industrial (Brasil)*

Órgão brasileiro responsável por registros de marcas e patentes. A eColabs está
registrando LICET na Classe 42 (serviços tecnológicos).

---

## 2.11 Termos do Projeto Específico

---

**eColabs** | *eColabs*

A empresa fundada por Christian Rodrigues Pereira para desenvolver e comercializar o
protocolo LICET. Razão social: eColabs Desenvolvimento de Pessoas e Organizações LTDA.

---

**Layer 1 — ECG Morphology** | *Camada 1 — Morfologia ECG*

Primeira camada de verificação do LICET. Compara a forma do complexo QRS atual com o
template do baseline do usuário via similaridade cosseno. Verifica: identidade e vivacidade
resistente a medicamentos (a forma do QRS não muda com drogas comuns).

---

**Layer 2 — EDA** | *Camada 2 — Atividade Eletrodérmica*

Segunda camada. Verifica se o sistema nervoso autônomo simpático está funcionando
normalmente (EDA não suprimida). EDA plana = possível bloqueio anticolinérgico → negação.

---

**Layer 3 — Mahalanobis** | *Camada 3 — Mahalanobis*

Terceira camada. Calcula a distância entre o estado biométrico atual e o baseline
individual. Se o estado atual é estatisticamente inconsistente com o estado calmo
normal do usuário → negação.

---

**Pharmacological Check** | *Verificação Farmacológica*

Módulo que detecta padrões de interferência de drogas nos sinais biométricos.
Detecta: beta-bloqueadores, anticolinérgicos, opioides. Resultado: CLEAN, BETA_BLOCKER,
ANTICHOLINERGIC, OPIOID.

---

**Layer Forgery Cost** | *Custo de Falsificação por Camada*

Estimativa qualitativa de quão difícil é para um adversário forjar cada camada:
- VERY_HIGH = exige hardware especializado + conhecimento profundo
- HIGH = difícil sem equipamento especial
- MEDIUM = possível com treinamento ou droga acessível
- LOW = acessível a adversário motivado
- NONE = camada não avaliada nesta sessão

---

**Design Limitation** | *Limitação de Design*

Campo sempre presente na resposta de autorização do LICET, informando ao integrador
sobre a limitação primária não mitigada: paced breathing treinado (~0.1 Hz) pode
produzir um vetor de calma genuíno que o LICET não consegue distinguir de repouso real.
Transparência é princípio fundamental do protocolo.

---

**CryptoAudit** | *Auditoria Criptográfica*

Processo formal de revisão das primitivas criptográficas e da implementação do protocolo
contra ataques conhecidos. O LICET passou por CryptoAudit em 26/07/2026 com 9 achados
(CA-01 a CA-09). Dois críticos afetam produção: CA-01 (admin sem autenticação) e CA-02
(chave mestra em plaintext HTTP). O processo é realizado com a skill `/cryptoaudit` que
usa framework de 6 domínios: primitivas, cobertura HMAC, ZKP, STRIDE, biometria, side-channels.

---

**HMAC v2** | *Assinatura de Mensagem com Hash — versão 2*

A versão atual do HMAC usado pelo app Android para autenticar dados enviados ao servidor.
A assinatura cobre: `source:heart_rate:spo2:hrv:timestamp:sha256(rr_intervals)`. A versão
anterior (v1) não cobria os intervalos RR — criando o bypass CA-03. Para dados reais de
wearable, `rr_intervals` deve ser sempre obrigatório.

---

**ML-DSA-44** | *Module Lattice Digital Signature Algorithm*

O sucessor pós-quântico do Ed25519, padronizado pelo NIST como FIPS 204 (2024). Resistente
ao algoritmo de Shor em computadores quânticos. Benchmark: 0.507 ms de verificação em ARM
Cortex-M0+ (hardware equivalente ao Galaxy Watch 6, que é muito mais rápido). A migração
do LICET para ML-DSA-44 está planejada em modo híbrido: ambas as assinaturas (Ed25519 +
ML-DSA-44) coexistem no bundle durante a transição 2026–2030.

---

**Groth16 / ZK-SERIES** | *Sistemas ZKP de próxima geração*

Alternativas ao ZKP Schnorr atual do LICET para dados biométricos contínuos:
- **ZK-SERIES** (arXiv:2506.19393, 2025): ZKP temporal para séries de intervalos RR; roda em 1.3s em smartphone; permite provar que HRV está dentro de um intervalo sem revelar o valor exato.
- **Groth16 + Pedersen** (BioZero, arXiv:2409.17509): prova sucinta de 200 bytes, mais expressiva que Schnorr para dados biométricos complexos.
Ambos são candidatos ao upgrade do ZKP do LICET em 2026.

---

**OPRF** | *Oblivious Pseudo-Random Function (Função Pseudo-Aleatória Oblivívia)*

Protocolo criptográfico onde o servidor e o cliente colaboram para calcular uma função sem
que o servidor veja a entrada do cliente nem o cliente veja a chave do servidor. Aplicação
no LICET: BFRB (IACR 2025/1211) usa OPRF para transformar templates biométricos em valores
que não podem ser atacados por força bruta offline — mesmo que o adversário capture o banco
de dados do servidor, os templates são inúteis sem o servidor. Mitigação para o clone
perfeito (V4).

---

# PARTE 3 — ARQUITETURA DO LICET EXPLICADA

## 3.1 Os Componentes do Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         MUNDO EXTERNO                           │
│   App Android (Kotlin)    |    Wearable (Samsung/Apple)         │
│   App iOS (futuro)        |    Sensor MAX30102 (hardware)       │
└─────────────────┬───────────────────────────┬───────────────────┘
                  │ HTTPS                     │ BLE / HealthKit
┌─────────────────▼───────────────────────────▼───────────────────┐
│                    LICET API (FastAPI + Cloud Run)               │
│                    https://licet.dev/v1/                         │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                 PIPELINE DE AUTORIZAÇÃO                  │   │
│  │                                                          │   │
│  │  Leitura Biométrica                                      │   │
│  │       ↓                                                  │   │
│  │  Análise Espectral RR (Periodicidade Respiratória)       │   │
│  │       ↓                                                  │   │
│  │  CAMADA 1: ECG Morfologia QRS ───── Baseline ECG         │   │
│  │       ↓ (se passar)                                      │   │
│  │  CAMADA 2: EDA (SCL + SCR)                               │   │
│  │       ↓ (se passar)                                      │   │
│  │  CHECK FARMACOLÓGICO                                     │   │
│  │       ↓ (se limpo)                                       │   │
│  │  CAMADA 3: Mahalanobis D² ──── Baseline Individual       │   │
│  │       ↓ (se dentro do envelope)                          │   │
│  │  GERAÇÃO DE ZKP (Schnorr / BN128)                        │   │
│  │       ↓                                                  │   │
│  │  REGISTRO NO LEDGER (Hash Chain)                         │   │
│  │       ↓                                                  │   │
│  │  AuthorizationResponse (JSON)                            │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐ │
│  │  Ledger DB   │  │  Baseline DB  │  │  ZKP Module          │ │
│  │  (SQLite +   │  │  (SQLite)     │  │  (py_ecc BN128)      │ │
│  │  Hash Chain) │  │               │  │                      │ │
│  └──────────────┘  └───────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 O Que Cada Arquivo do Projeto Faz

| Arquivo | O que é | O que faz |
|---------|---------|-----------|
| `api/routes.py` | Controlador da API | Define todos os endpoints REST, valida requests, chama o pipeline |
| `core/crypto.py` | Motor central | Orquestra o pipeline completo de autorização, gera assinatura biométrica |
| `core/mahalanobis.py` | Detector de desvio | Calcula se o estado biométrico atual desviou do baseline individual |
| `core/baseline.py` | Gestor de baseline | Cria, salva e carrega o perfil biométrico individual de cada usuário |
| `core/ecg_layer.py` | Camada 1 | Verifica morfologia ECG (identidade + vivacidade) |
| `core/eda_layer.py` | Camada 2 | Verifica atividade eletrodérmica (tônus simpático colinérgico) |
| `core/pharmacological_check.py` | Detector farmacológico | Identifica assinaturas de drogas (beta-bloqueador, anticolinérgico, opioide) |
| `core/respiratory_periodicity.py` | Detector de paced breathing | Análise espectral dos intervalos RR para detectar respiração ressonante treinada |
| `hardware/sensor_interface.py` | Interface de hardware | Abstrai o hardware real (MAX30102) e o simulador — mesmo código, diferente modo |
| `hardware/wearable_manager.py` | Gerenciador de wearables | Conecta e lê dados de smartwatches via BLE |
| `ledger/db.py` | Banco de dados | Define e gerencia as tabelas SQLite, mantém a cadeia de hashes |
| `zkp/proof.py` | Prova ZKP | Gera e verifica provas de conhecimento zero (Schnorr/BN128) |
| `docs/arxiv/licet_protocol.tex` | Artigo científico | Especificação formal do protocolo em formato IEEE para publicação |

## 3.3 O Fluxo de uma Autorização (Passo a Passo)

**Cenário:** Um agente de IA quer mover R$50.000 da conta do usuário.

```
1. O agente envia POST /v1/authorize:
   {"action": "wire_transfer", "agent_id": "agent-001",
    "target": "conta-destino", "user_id": "christian"}

2. LICET captura sinais biométricos do smartwatch:
   FC=68 BPM, SpO2=98%, RMSSD=55ms, SCL=3.2μS, SCR=0.28μS

3. Gera Intent Hash:
   SHA256("wire_transfer:agent-001:conta-destino:1783462000") = "a3f7b2..."
   [Qualquer alteração na ação mudaria este hash completamente]

4. Análise Espectral dos RR Intervals:
   IP=0.22 (broadband) → sem suspeita de paced breathing

5. CAMADA 1 — ECG:
   Cosine Similarity = 0.94 (> 0.85 mínimo) → PASS

6. CAMADA 2 — EDA:
   SCL=3.2μS (normal), SCR=0.28μS (normal) → PASS

7. CHECK FARMACOLÓGICO:
   Z_HRV = (55-52)/8 = 0.37 (normal)
   Z_HR = (68-70)/5 = -0.4 (normal) → CLEAN

8. CAMADA 3 — MAHALANOBIS:
   D² = 2.1 < χ²(7)=14.07 → PASS
   [Estado atual dentro do envelope individual]

9. Verifica UI Binding (GAP-A04):
   Confere se SHA256(action|agent_id|target|nonce) corresponde ao intent_hash
   ui_binding_status: "VERIFIED"

10. Gera Biometric Signature (Ed25519 — GAP-C02):
    Ed25519.sign("a3f7b2..." ‖ {FC:68, SpO2:98, HRV:55, ...}, chave_privada_servidor)
    [Verificável por qualquer auditor com GET /signing-key]

11. Gera ZKP (Schnorr):
    witness = HKDF(k_m, intent_hash)  — nunca entra no ledger (GAP-C01)
    Prova que os sinais passaram sem revelar valores brutos

12. Registra no Ledger com server_nonce (GAP-C04):
    server_nonce = secrets.token_hex(16)
    {intent_hash, bio_signature, D²=2.1, layer1=PASS, ..., server_nonce, chain_hash}

13. Retorna AuthorizationResponse:
    {authorized: true, trust_level: "L1", layer_forgery_cost: {overall: "MEDIUM"},
     ui_binding_status: "VERIFIED", ppg_equity_warning: null,
     biometric_signature: "<Ed25519 base64>",
     design_limitation: "PRIMARY UNMITIGATED LIMITATION: paced breathing..."}
```

---

# PARTE 4 — AS TRÊS CAMADAS DE SEGURANÇA EM DETALHE

## 4.1 Por Que Três Camadas?

O LICET usa três camadas independentes porque nenhuma delas, sozinha, é suficiente:

| Camada | O que verifica | Ponto fraco |
|--------|---------------|-------------|
| ECG | Identidade + forma única do coração | Não detecta coerção diretamente |
| EDA | Atividade simpática (estresse/calma) | Pode ser suprimida com anticolinérgicos |
| Mahalanobis | Desvio do estado normal pessoal | Vulnerável a paced breathing treinado |

Juntas, as três criam redundância defensiva. Um adversário precisa superar **as três
simultaneamente**, o que aumenta exponencialmente a dificuldade.

## 4.2 O Que Cada Camada Detecta

**Camada 1 — ECG:**
- ✅ Detecta: impersonação (outra pessoa), replay de sinal gravado, morfologia anormal
- ❌ Não detecta: coerção em pessoa viva com ECG normal

**Camada 2 — EDA:**
- ✅ Detecta: bloqueio anticolinérgico (droga usada para suprimir EDA), EDA artificialmente plana
- ❌ Não detecta: paced breathing (que não afeta EDA), beta-bloqueadores

**Camada 3 — Mahalanobis:**
- ✅ Detecta: desvio do baseline individual (estresse agudo, coerção física)
- ❌ Não detecta: paced breathing treinado (produz calma genuína, não forjada)

**Análise Espectral (não é camada, é aviso):**
- ⚠️ Sinaliza: concentração espectral suspeita ao redor de 0.1 Hz (IP > 0.80)
- ❌ Não é bloqueante: limitação primária documentada sem mitigação

## 4.3 Status dos Gaps de Segurança (27/07/2026)

A tabela abaixo mostra os 11 gaps mitigados em código nas sessões de 07–09/07/2026.
Para a análise completa de todos os **52 gaps** (incluindo 9 novos do CryptoAudit de 26/07/2026),
veja `docs/research/security-gaps.md` (v1.1).

| Gap | Dimensão | Mitigação implementada |
|---|---|---|
| C01 | Criptografia | Witness ZKP = `HKDF(k_m, intent_hash)` — não reproductível do ledger |
| C02 | Criptografia | Ed25519 assimétrico; chave pública em `GET /signing-key` |
| C03 | Criptografia | Merkle root + OpenTimestamps (3 calendários); `POST /ledger/timestamp` |
| C04 | Criptografia | `server_nonce` gerado pelo servidor por entrada — impede backdating |
| O02 | Operacional | Shamir (5,3) para k_m; `POST /admin/key/split` e `/combine` |
| O03/H03 | Operacional/Hardware | Revogação aditiva; `POST /admin/revoke/{ledger_id}` |
| A04 | IA | Commitment UI antes da captura; `ui_binding_status` na resposta |
| L05 | Legal | `medication_accommodation`; BETA_BLOCKER_ACCOMMODATED |
| B08 | Biometria | 5 checks anti-envenenamento em `build_baseline()` |
| B09 | Biometria/Equidade | Multiplicador ×1.4 para Fitzpatrick V-VI; `ppg_equity_warning` |
| A05 | IA/Privacidade | Zeragem pós-extração; endpoints GDPR/LGPD Art. 17 |
| B01 | Biometria | IP ≥ 0.80 bloqueia automaticamente paced breathing — **bypassável via CA-03** |

**Achados do CryptoAudit de 26/07/2026 (CA-01 a CA-07) — pendentes:**

| Gap | Severidade | Status | Descrição resumida |
|---|---|---|---|
| CA-01 | 🔴 CRÍTICO | ABERTO | `/admin/key/split` e `/combine` sem autenticação — qualquer um acessa |
| CA-02 | 🔴 CRÍTICO | ABERTO | `k_m` (chave mestra) retornado em plaintext HTTP no `/admin/key/combine` |
| CA-03 | 🟠 ALTO | ABERTO | Bypass do IP check: omitir `rr_intervals` força HMAC v1 sem análise espectral |
| CA-04 | 🟠 ALTO | ABERTO | `user_id`, `eda_scl`, `eda_scr`, `skin_temp`, `tremor` fora da cobertura do HMAC |
| CA-05 | 🟠 ALTO | ABERTO | Sem rate limiting em nenhum endpoint — flooding, oracle Mahalanobis, OOM |
| CA-06 | 🟡 MÉDIO | ABERTO | HKDF com `salt=None` — reduz entropia da derivação de k_session |
| CA-07 | 🟡 MÉDIO | ABERTO | Float sem normalização no HMAC — divergência Android/Python (ex: 33.9 vs 33.900001) |

> **O que fazer com CA-01 e CA-02:** são os únicos que afetam produção imediatamente.
> Antes de dar acesso a qualquer cliente real, corrigir os dois (`api/routes.py` linhas 932–998).

## 4.5 Testes Físicos — Samsung Galaxy Watch 6 (26/07/2026)

O protocolo foi testado com dados reais de um Samsung Galaxy Watch 6 (Christian, em repouso).

**Resultados medidos:**

| Dado | Valor real |
|---|---|
| RMSSD | 33.9 ms (repouso normal) |
| Frequência Cardíaca | 64 bpm |
| Amostras RR | 150 intervalos — processo Ornstein-Uhlenbeck com parâmetros do Watch 6 |
| Fluxo completo | POST /biometric/push → push_id → POST /authorize/from-push → AUTORIZADO ✓ |
| Limiar IP real | 20 ms de modulação a 0.1 Hz já gera IP=0.83 → BLOQUEADO ✓ |
| Replay attack | push_id consumido após uso — ineficaz ✓ |
| HMAC adulterado | 6 variantes testadas — todas rejeitadas com HTTP 401 ✓ |
| V2 bug confirmado | EDA_SCL=0.2µS + HR=102 bpm → sistema retorna CLEAN(HIGH) — **incorreto, aberto** |

**SDK obtido:**

- Samsung Health Sensor SDK v1.4.1 (conta Business eColabs Desenvolvimento de Pessoas e Organizações LTDA)
- APIs disponíveis: `IBI_LIST` (RR beat-to-beat em ms), `ECG_MV` (ECG raw 500 Hz), `SKIN_CONDUCTANCE` (EDA em µS)
- `SamsungSensorManager.kt` criado e compilando

---

## 4.4 Novos Endpoints da API (adicionados em 09/07/2026)

| Método | Endpoint | Função | Gap |
|---|---|---|---|
| GET | `/v1/signing-key` | Retorna chave pública Ed25519 para auditores verificarem biometric_signature | C02 |
| POST | `/v1/ledger/timestamp` | Ancora Merkle root no OpenTimestamps (3 calendários) | C03 |
| POST | `/v1/admin/key/split` | Divide k_m em 5 shares Shamir; qualquer 3 reconstroem | O02 |
| POST | `/v1/admin/key/combine` | Reconstrói k_m a partir de ≥3 shares (somente em recuperação) | O02 |
| POST | `/v1/admin/revoke/{ledger_id}` | Adiciona registro de revogação aditiva ao ledger | O03/H03 |
| GET | `/v1/gdpr/data/{user_id}` | GDPR Art. 15 / LGPD Art. 18 II — direito de acesso | A05 |
| DELETE | `/v1/gdpr/erasure/{user_id}` | GDPR Art. 17 / LGPD Art. 18 VI — direito ao esquecimento | A05 |

**Exemplo de resposta de autorização com novos campos:**

```json
{
  "authorized": true,
  "intent_hash": "a3f8b2c1d4e5...",
  "biometric_signature": "<Ed25519 base64>",
  "trust_level": "L1",
  "layer1_ecg": "PASS",
  "layer2_eda": "PASS",
  "layer3_mahalanobis_d2": 1.47,
  "pharmacological_check": "CLEAN",
  "ui_binding_status": "VERIFIED",
  "ui_binding_warning": null,
  "ppg_equity_warning": null,
  "coercion_cost_elevation": "NOMINAL",
  "zkp_proof": { "commitment": {...}, "challenge": "0x...", "response": "0x..." },
  "ledger_id": 42,
  "timestamp": 1782576000.0
}
```

**Novo campo no BiometricPushRequest:**

```json
{
  "skin_tone_fitzpatrick": 5
}
```
Valores 1–6 (escala de Fitzpatrick). Null = não declarado. Valores 5–6 com sensor PPG
ativam `threshold_multiplier = 1.4` e `ppg_equity_warning` na resposta.

---

## 4.5 Equidade e Acessibilidade — PPG em Peles Escuras (GAP-B09)

Sensores PPG (fotopletismografia) usam LED verde ou vermelho para medir o pulso através
da pele. A melanina absorve parte dessa luz, e em tons de pele mais escuros
(Fitzpatrick V e VI) esse efeito é substancial: estudos mostram erro de HRV de 30–40%
em comparação com ECG de referência (Bent et al., NPJ Digit Med 2020; Mannheimer et al.,
J Clin Monit Comput 2021).

**O problema de equidade:** sem correção, o LICET produzia baselines sistematicamente
imprecisos para usuários com pele mais escura, resultando em taxas de falso positivo de
negação desproporcionalmente altas — potencial discriminação por característica protegida.

**Mitigação implementada (09/07/2026):**

- O campo `skin_tone_fitzpatrick` (1–6) pode ser informado no `BiometricPushRequest`
- Para Fitzpatrick V–VI com sensor PPG, o limiar Mahalanobis recebe
  `threshold_multiplier = 1.4` — aumentando a tolerância para compensar a imprecisão do sensor
- A resposta inclui `ppg_equity_warning` sempre que o multiplicador está ativo, para
  que integradores saibam que a compensação está em uso
- **Recomendação para alta consequência:** usar ECG de canal único (Apple Watch 4+) em
  vez de PPG puro para deployments com populações de pele escura — ECG de luz infravermelha
  tem absorção muito menor por melanina

---

## 4.6 Privacidade por Design e GDPR — Minimização de Dados (GAP-A05)

O servidor LICET, por necessidade operacional, recebe sinais fisiológicos brutos
(`ecg_waveform`, `rr_intervals`) para extrair features. Esses dados brutos são
extremamente valiosos para treinar modelos de síntese biométrica e representam um
risco de acumulação de dataset por operador desonesto ou servidor comprometido.

**Mitigação implementada (09/07/2026):**

Quando `privacy_mode=True` (recomendado para produção):
- `ecg_waveform` e `rr_intervals` são zerados na memória imediatamente após a
  extração de features (RMSSD, cosine similarity)
- O servidor armazena apenas features derivadas — não os sinais brutos
- Nenhum dado biométrico bruto é persistido em banco de dados

**Endpoints de direitos do titular:**

| Endpoint | Direito | Base legal |
|---|---|---|
| `GET /gdpr/data/{user_id}` | Direito de acesso — ver todos os dados armazenados | GDPR Art. 15 / LGPD Art. 18 II |
| `DELETE /gdpr/erasure/{user_id}` | Direito ao esquecimento — apagar todos os dados | GDPR Art. 17 / LGPD Art. 18 VI |

---

## 4.7 UI Binding — Proteção contra Manipulação por Agente AI (GAP-A04)

**O problema:** em cenários de agente AI, o agente constrói o request LICET. Um agente
malicioso ou comprometido poderia apresentar ao humano "autorizar transferência de R$100"
na interface, mas enviar ao servidor "autorizar transferência de R$100.000" no payload.
O humano estaria em estado biométrico de calma (tendo visto a ação menor) enquanto
o protocolo assinaria a ação maior.

**Mitigação implementada (09/07/2026) — Commitment Scheme:**

1. Antes de iniciar a captura biométrica, o componente UI (sob controle humano) calcula:
   `ui_binding_commitment = SHA256(action | agent_id | target | nonce)`
2. Este commitment é submetido ao servidor ANTES de qualquer dado biométrico
3. O servidor verifica que o `intent_hash` é consistente com o commitment
4. Resultado em toda resposta: `ui_binding_status: VERIFIED | ABSENT | FAILED`

**Significado de cada status:**

| Status | Significado | Ação recomendada ao integrador |
|---|---|---|
| `VERIFIED` | Commitment conferido — o que o humano viu é o que foi assinado | Confiança plena |
| `ABSENT` | Nenhum commitment foi submetido | Alertar: UI binding não implementado |
| `FAILED` | Commitment não corresponde ao intent_hash | Rejeitar: possível manipulação detectada |

---

## 4.8 Proteção do Baseline contra Envenenamento (GAP-B08)

**O problema (Baseline Poisoning):** se um adversário controla as condições durante
o enrollment do usuário, pode calibrar o baseline para aceitar estados coagidos como
"normais". Aplicando coerção leve durante as sessões de calibração, o vetor μ captura
um estado moderadamente estressado como baseline de "calma".

**5 checks implementados em `build_baseline()` (09/07/2026):**

1. **Spread temporal:** as sessões devem cobrir pelo menos 3 dias de calendário distintos
   — impede que um adversário realize todas as sessões no mesmo dia sob condições controladas

2. **Plausibilidade fisiológica:** os valores de HR, RMSSD, EDA-SCL devem estar dentro
   de ranges biologicamente plausíveis para um humano em repouso real

3. **Coeficiente de Variação (CV):** o CV entre sessões deve ser compatível com variação
   biológica natural — CV muito baixo (sessões suspeitamente uniformes) é sinal de
   condições artificialmente controladas

4. **Detecção de outliers:** sessões com valores extremos (mais de 2.5σ da média das
   outras sessões) são identificadas e descartadas antes do cálculo de μ e S

5. **Análise de tendência:** detecta se os valores estão derivando monotonicamente ao
   longo das sessões (possível condicionamento gradual) — uma tendência linear forte
   nos valores de baseline aciona `BASELINE_TREND_WARNING`

---

## 4.9 Acomodação de Medicamentos — Sem Discriminação (GAP-L05)

**O problema legal:** um cardiologista que usa beta-bloqueadores (propranolol, metoprolol)
para fibrilação atrial seria sistematicamente negado pelo detector `BETA_BLOCKER` —
potencialmente discriminação por condição médica (ADA, EU Employment Equality Directive,
LGPD, Constituição Federal Art. 5°).

**Mitigação implementada (09/07/2026):**

- Campo `medication_accommodation: true` no perfil do usuário
- Quando ativo com declaração médica formal: resultado `BETA_BLOCKER` → `BETA_BLOCKER_ACCOMMODATED`
  (autorização não negada automaticamente; status registrado no ledger para auditoria)
- A declaração médica é assinada digitalmente pelo profissional responsável e armazenada
  no perfil — cria trilha de responsabilidade profissional, não um bypass anônimo

**Medicamentos afetados pelo accommodation:**
- Beta-bloqueadores (propranolol, metoprolol, atenolol, bisoprolol)
- Outros com indicação médica formal podem ser adicionados ao perfil

---

# PARTE 5 — PLANO DE APRESENTAÇÃO PARA INVESTIDORES

## 5.1 Estrutura Geral da Apresentação (Pitch de 20 minutos)

```
SLIDE 1  — Capa + Impacto Emocional          (1 min)
SLIDE 2  — O Problema: A Crise de Intenção   (3 min)
SLIDE 3  — A Solução: LICET                  (2 min)
SLIDE 4  — Como Funciona (simplificado)      (3 min)
SLIDE 5  — Mercado Total Endereçável         (2 min)
SLIDE 6  — Diferenciação Competitiva         (2 min)
SLIDE 7  — Tração e Credenciais              (2 min)
SLIDE 8  — Modelo de Negócio                 (2 min)
SLIDE 9  — Roadmap                           (1 min)
SLIDE 10 — O Pedido (Ask)                    (2 min)
```

---

## 5.2 Roteiro Detalhado de Cada Slide

---

### SLIDE 1 — CAPA + IMPACTO EMOCIONAL

**Título:** "Quem autorizou isso?"

**Subtítulo:** LICET — O primeiro protocolo do mundo para provar intenção humana autêntica

**Visual sugerido:** Imagem de um agente de IA executando uma transferência bancária enorme,
com a pergunta "Quem REALMENTE autorizou isso?" em destaque.

**O que você fala:**
> "Antes de começar, quero fazer uma pergunta simples: quando um sistema de inteligência
> artificial age em seu nome — move dinheiro, assina um contrato, toma uma decisão crítica —
> como você prova que foi *você*, *consciente* e *livre*, quem disse sim?
> Hoje, não dá para provar. Nós criamos o LICET para mudar isso."

---

### SLIDE 2 — O PROBLEMA: A CRISE DE INTENÇÃO

**Título:** "Identidade não é suficiente"

**3 Pontos-chave:**

**Ponto 1 — O Gap de Consentimento:**
> "Sistemas atuais de autenticação — senha, biometria, certificado digital — provam
> *quem* você é. Mas não provam que você estava livre, consciente e sem pressão quando
> disse sim. A digital do seu polegar funciona igual se você está relaxado ou se há
> uma faca no seu pescoço."

**Ponto 2 — O Problema dos Agentes de IA:**
> "Em 2026, agentes de IA estão tomando decisões autônomas em nome de pessoas: comprando,
> vendendo, assinando, executando. A pergunta 'quem autorizou?' está se tornando a questão
> legal, regulatória e ética mais importante da era da IA. O EU AI Act exige supervisão
> humana auditável. Como você audita intenção?"

**Ponto 3 — A Escala do Problema:**
> "O mercado global de autenticação biométrica é de US$41 bilhões (2024). O mercado de
> agentes de IA autônomos está crescendo 37% ao ano. A interseção desses mercados —
> provar intenção humana para autorização de IA — não tem solução hoje."

**Visual sugerido:** Três colunas: "O que existe hoje" (senha, digital, face) vs
"O que falta" (prova de intenção livre) vs "O que o LICET faz" (prova fisiológica de calma voluntária)

---

### SLIDE 3 — A SOLUÇÃO: LICET

**Título:** "LICET: Liveness, Intent, Consent, and Ethical Trust"

**Frase central:**
> "O LICET usa seus sinais fisiológicos — batimento cardíaco, variabilidade cardíaca,
> condutância da pele — para provar que você estava *vivo, consciente e calmo* quando
> autorizou uma ação. Esta prova é criptograficamente verificável por qualquer terceiro,
> para sempre."

**3 Pilares:**

1. **Fisiológico** — Mede o que o corpo não consegue mentir: RMSSD abolido, EDA suprimida,
   desvio do baseline individual são sinais que drogas ou coerção produzem involuntariamente.

2. **Criptográfico** — Cada autorização gera uma assinatura biométrica + prova de
   conhecimento zero + registro em ledger hash-chained. Imutável e verificável.

3. **Aberto** — Protocolo open standard no IETF. Qualquer fabricante de wearable,
   qualquer sistema de IA, qualquer banco pode implementar. A eColabs mantém a
   implementação de referência e o ecossistema.

---

### SLIDE 4 — COMO FUNCIONA (simplificado)

**Título:** "Três camadas de verificação em menos de 3 segundos"

**Visual: Diagrama em 3 etapas simples:**

```
[WEARABLE]          [LICET SERVER]           [INTEGRADOR]
Smartwatch   →→→→   ECG: Quem é você?   →→→→
  |                 EDA: Você está normal?
  |                 Mahalanobis: Você está calmo?
  |                 ZKP: Gera prova             →→→→  authorized: true
  |                 Ledger: Registra imutável          trust_level: L1
                                                       forgery_cost: MEDIUM
```

**O que você fala:**
> "Em menos de 3 segundos, o smartwatch do usuário envia sinais biométricos para o
> servidor LICET. O servidor verifica três camadas independentes: se a morfologia
> do ECG corresponde ao usuário conhecido; se a atividade eletrodérmica mostra sistema
> nervoso funcionando normalmente; e se o estado biométrico está dentro do perfil
> calmo individual daquela pessoa.
>
> Se tudo passar, o LICET gera uma prova criptográfica verificável e registra no ledger.
> Se detectar coerção, droga ou anomalia, nega a autorização instantaneamente.
>
> E — isso é importante — o LICET é transparente: sempre informa suas limitações.
> É o único protocolo do mundo que documenta o que *não* consegue detectar."

---

### SLIDE 5 — MERCADO TOTAL ENDEREÇÁVEL

**Título:** "Um mercado de trilhões que ainda não tem solução"

**TAM / SAM / SOM:**

| Nível | Mercado | Tamanho |
|-------|---------|---------|
| **TAM** (Total Addressable Market) | Autenticação + IA Autônoma + Conformidade Regulatória | US$850B (2030 est.) |
| **SAM** (Serviceable Addressable Market) | Autorização biométrica de alta segurança | US$45B (2030 est.) |
| **SOM** (Serviceable Obtainable Market) | Segmento inicial: FinTech + IA Agentes | US$2.1B (2028 est.) |

**Catalisadores de mercado:**
- **EU AI Act (2024):** exige supervisão humana auditável para sistemas de IA de alto risco
- **Open Banking:** transações programáticas exigem consentimento verificável
- **Explosão de Agentes IA:** OpenAI, Google, Anthropic lançando agentes autônomos
- **LGPD / GDPR enforcement:** multas crescentes por uso não consentido de dados

---

### SLIDE 6 — DIFERENCIAÇÃO COMPETITIVA

**Título:** "Por que o LICET não tem concorrente direto"

**Matriz de diferenciação:**

| Solução | Prova Identidade | Prova Liveness | Prova Calma Voluntária | Open Standard | ZKP | Ledger |
|---------|:---:|:---:|:---:|:---:|:---:|:---:|
| Senha/PIN | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Biometria (Apple Face ID) | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| DocuSign / Assinatura digital | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| HSM / Hardware Security | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| **LICET** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Moat (barreira competitiva):**

1. **Anterioridade pública estabelecida** — SSRN, IETF draft, arXiv, blockchain timestamp (Bitcoin)
2. **Especificidade técnica** — Combinação única de HRV + EDA + Mahalanobis + ZKP não encontrada em nenhuma patente ou produto
3. **Network effects do standard aberto** — Quanto mais implementações, mais valioso o ecossistema
4. **Dados de baseline** — Cada usuário que calibra baseline cria dados proprietary que fortalecem o modelo
5. **Relações IETF/Linux Foundation** — Posicionamento no ecossistema técnico global

---

### SLIDE 7 — TRAÇÃO E CREDENCIAIS

**Título:** "Nós já saímos do papel"

**Evidências de tração:**

**Técnico:**
- ✅ Implementação de referência em produção (Cloud Run, 24/7)
- ✅ API pública funcional: `https://licet.dev/v1/`
- ✅ App Android funcional (Kotlin + Health Connect) instalado em hardware real
- ✅ Pipeline completo de três camadas com ZKP

**Propriedade Intelectual:**
- ✅ IETF Internet-Draft: `draft-pereira-licet-human-intent-01`
- ✅ Preprint SSRN: Abstract ID 7018458
- ✅ arXiv cs.CR: ID 7765569 — submetido 13/07/2026 (cs.CR + cs.AI + cs.HC, CC BY)
- ✅ Timestamp blockchain (Bitcoin, OpenTimestamps, 2026-02-25)
- ✅ Notificação ANPD
- 🔄 Registro INPI Classe 42 (em andamento)

**Reconhecimento técnico:**
- ✅ Revisão técnica por David Condrey (Linux Foundation / IETF RATS WG)
- ✅ Alinhamento com RFC 9334 (RATS Architecture)
- ✅ Discussão ativa no Working Group IETF CPoE

**Publicação científica:**
- ✅ Artigo técnico completo (22 páginas, IEEE format) com threat model, análise de segurança,
  estimated error rates, acknowledged limitations e referências bibliográficas

---

### SLIDE 8 — MODELO DE NEGÓCIO

**Título:** "Três fontes de receita convergentes"

**Receita 1 — API SaaS (Software as a Service):**
> Cobrança por autorização processada via API LICET.
> Target: empresas de FinTech, plataformas de IA, sistemas de saúde.
> Modelo: `US$0.05 – US$0.50 por autorização` (volume-based pricing)
> Análogo: Stripe cobra por transação, Twilio por mensagem.

**Receita 2 — SDK Licenciamento:**
> SDK para integração nativa em apps móveis e sistemas embarcados.
> Licença anual por empresa integradora.
> Modelo: `US$10.000 – US$100.000/ano` (enterprise licensing)

**Receita 3 — Certificação e Compliance:**
> Empresas que precisam demonstrar conformidade com EU AI Act e LGPD precisarão de
> autorização LICET-certified como evidência auditável.
> Modelo: Certificação + auditoria + relatórios de conformidade.

**Analogia de negócio:**
> "Pense no LICET como o HTTPS para intenção humana. Todo site precisa de HTTPS hoje —
> não por escolha, mas por regulação e confiança. Em 5 anos, todo sistema de IA autônomo
> vai precisar de prova de intenção humana — não por escolha, mas por lei."

---

### SLIDE 9 — ROADMAP

**Título:** "24 meses para liderança de mercado"

```
Q3 2026 ─── AGORA
 ✅ API em produção (Cloud Run)
 ✅ App Android funcional
 ✅ IETF draft-01

Q4 2026
 🔄 Versão 2.1 (CDDL schema, wearable Attester draft)
 🔄 iOS app (HealthKit integration)
 🔄 Primeiros clientes piloto (FinTech)
 ✅ arXiv cs.CR submetido — 13/07/2026 (antecipado de Q4 para Q3)

Q1 2027
 📋 SDK v1.0 para integradores
 📋 Integração Health Connect real (Galaxy Watch)
 📋 2-3 pilotos pagantes
 📋 IETF draft-02

Q2 2027
 📋 Integração NFC
 📋 Certificação L2 (Android Key Attestation)
 📋 10+ clientes
 📋 Expansão para HealthTech e LegalTech

2028
 📋 Standard ratificado no IETF
 📋 Parceria OEM com fabricante wearable
 📋 100+ clientes, MRR > US$500K
```

---

### SLIDE 10 — O PEDIDO (ASK)

**Título:** "Seed Round: US$500K — para liderar o mercado que criamos"

**Uso dos recursos:**

| Área | % | US$ | O que faz |
|------|---|-----|-----------|
| **Engenharia** | 40% | US$200K | 2 engenheiros sênior: iOS app, SDK, NFC, hardware L2 |
| **Go-to-Market** | 25% | US$125K | Primeiros 10 clientes, vendas enterprise, conferências IETF |
| **Propriedade Intelectual** | 15% | US$75K | INPI, patentes internacionais (PCT), trademark global |
| **Operacional** | 10% | US$50K | Cloud, infraestrutura, jurídico |
| **P&D / Pesquisa** | 10% | US$50K | Validação clínica (populações especiais), peer review científico |

**O que entregamos em 18 meses:**
- 3+ pilotos pagantes em FinTech ou HealthTech
- iOS app funcional com HealthKit
- SDK licenciável para integradores
- IETF draft-02 com comunidade técnica ativa
- MRR > US$30K
- Empresa valorada em US$5M+ para próxima rodada

---

## 5.3 Frases-Chave para Conversas Técnicas

Aqui estão frases que você pode usar em inglês (com pronúncia aproximada em português)
para quando precisar se comunicar com parceiros técnicos internacionais:

---

**Para apresentar o LICET:**
> *"LICET is a biometric authorization protocol that proves human intent using physiological
> signals — heart rate variability, electrodermal activity, and Mahalanobis distance from
> individual baseline — combined with zero-knowledge proofs and a hash-chained ledger."*
>
> **Pronúncia aproximada:** "LICET iz a bio-MÉ-tric au-tho-rai-ZÉI-shon PRÓ-to-col..."

---

**Para explicar o problema central:**
> *"Current authentication systems prove identity, but not voluntary intent. LICET bridges
> that gap by measuring the physiological state of the authorizing person."*
>
> **Pronúncia aproximada:** "CÁ-rrent ó-then-ti-KÉI-shon SIS-tems pruv ai-DÉN-ti-ti..."

---

**Para responder sobre segurança:**
> *"The primary unmitigated limitation is resonance-frequency breathing — a trained subject
> can produce a genuine calm vector without pharmacological intervention. We document this
> transparently in the spec."*

---

**Para falar sobre IETF:**
> *"LICET has an Internet-Draft at the IETF: draft-pereira-licet-human-intent-01.
> We're aligning with RFC 9334 RATS architecture."*

---

**Para falar com David Condrey:**
> *"Following your feedback, we updated the LF framing to baroreflex modulation per
> Moak 2007, and acknowledged paced breathing as the primary unmitigated limitation
> in Section Acknowledged Limitations."*

---

## 5.4 Perguntas Difíceis e Como Responder

**"Isso não pode ser hackeado?"**
> "Todo sistema de segurança pode ser atacado — a questão é o custo do ataque versus o valor
> protegido. O LICET documenta isso explicitamente com o campo layer_forgery_cost. A principal
> limitação conhecida — paced breathing treinado — requer meses de prática biofeedback.
> Para transações de alto valor, esse custo adversarial é aceitável. E somos o único
> protocolo do mundo que documenta publicamente o que não detecta."

**"Por que open source não te deixa sem produto?"**
> "O modelo LICET é como Linux / Red Hat ou Android / Google. O protocolo é aberto —
> a implementação de referência, o ecossistema, a certificação, o SDK e o suporte
> enterprise são proprietary. Quanto mais o standard cresce, mais vale ser a empresa
> que o criou e mantém."

**"Concorrentes maiores podem copiar?"**
> "A anterioridade pública está estabelecida desde fevereiro de 2026: blockchain timestamp,
> SSRN, IETF draft. Grandes empresas (Apple, Google) têm biometria de identidade mas não
> de intenção — e o custo de reputação de criar um concorrente ao nosso protocolo aberto
> seria enorme. Além disso, eles prefeririam implementar o LICET do que criar algo que
> fragmentaria o ecossistema."

**"Qual o prazo para regulação forçar adoção?"**
> "EU AI Act: aplicação completa em agosto 2026 para sistemas de alto risco. Brasil: LGPD
> enforcement crescendo. EUA: Executive Order on AI Safety + emergência de legislação estadual.
> Nossa estimativa: 18-36 meses para mandato regulatório em FinTech de alto valor na Europa."

---

# PARTE 6 — GUIA DE ESTUDO RÁPIDO

## 6.1 Os 12 Conceitos Mais Importantes do LICET

Se você precisar resumir o LICET em pontos para uma conversa rápida:

1. **O problema:** Sistemas de autenticação provam *quem você é*, não *se você quis livre e conscientemente*.

2. **A solução central:** Medir o estado fisiológico (calma x estresse x coerção) através de sinais que o corpo produz involuntariamente.

3. **O sinal mais importante:** RMSSD (variabilidade cardíaca) — é reduzido por coerção, abolido por drogas anticolinérgicas, elevado artificialmente por beta-bloqueadores. Valor real medido no Watch 6: 33.9 ms em repouso.

4. **A camada mais forte:** Mahalanobis — compara o estado atual com o *perfil individual* do usuário, não com médias populacionais. Cada pessoa tem seu próprio "fingerprint de calma".

5. **A limitação mais séria:** Paced breathing treinado — um adversário pode produzir calma fisiológica genuína e enganar o LICET sem drogas. Documentamos isso abertamente.

6. **A prova criptográfica:** Zero-Knowledge Proof (Schnorr/BN128 hoje; roadmap para ZK-SERIES temporal + Groth16 em 2026) — prova que os sinais passaram sem revelar os dados brutos.

7. **O registro imutável:** Hash-chained ledger — cada autorização referencia o hash da anterior. Adulteração retroativa é matematicamente detectável.

8. **O posicionamento:** IETF Internet-Draft — tornamos o LICET um padrão aberto internacional, não um produto fechado. Publicações: Zenodo (DOI 10.5281/zenodo.21345045), IACR ePrint 2026/110546, SSRN 7018458.

9. **O custo de ataque:** layer_forgery_cost — informamos ao integrador o quão difícil é forjar cada camada, para que use o LICET com consciência dos riscos.

10. **O modelo de negócio:** API SaaS + SDK enterprise + certificação de conformidade. Como Stripe para intenção humana.

11. **A auditoria contínua:** O protocolo passou por CryptoAudit formal (26/07/2026) com 9 achados documentados — 2 críticos em correção ativa. Ser o único protocolo que publica abertamente o que não funciona é posição de força, não de fraqueza.

12. **O roadmap pós-quântico:** Ed25519 é vulnerável a computadores quânticos. Migração planejada para ML-DSA-44 (FIPS 204) em modo híbrido 2026–2030. Benchmark confirmado: 0.507 ms em hardware wearable equivalente ao Galaxy Watch 6.

---

## 6.2 Sequência de Estudo Recomendada

1. **Semana 1:** Leia as Partes 1 e 2 deste guia. Foque nos termos de HRV (RMSSD, ECG) e nos termos fundamentais do protocolo.

2. **Semana 2:** Leia a Parte 3 (arquitetura). Tente desenhar o pipeline de memória.

3. **Semana 3:** Pratique o Slide 3 (solução) e Slide 4 (como funciona) do roteiro de pitch até conseguir explicar sem ler.

4. **Semana 4:** Leia o artigo científico (`docs/arxiv/licet_protocol.tex`) — especialmente as seções "Threat Model" e "Acknowledged Limitations". Esses são os pontos que investidores técnicos vão questionar.

5. **Em curso:** Sempre que aparecer uma pergunta sobre o LICET, consulte o Glossário (Parte 2) antes de responder.

---

## 6.3 Palavras em Inglês Mais Usadas em Conversas Técnicas do LICET

| Inglês | Português | Como usar |
|--------|-----------|-----------|
| intent | intenção | "LICET proves human **intent**" |
| coercion | coerção | "**Coercion** detection via HRV" |
| biometric | biométrico | "**biometric** authorization" |
| threshold | limiar | "D² above the **threshold** is denied" |
| baseline | linha de base | "individual **baseline** calibration" |
| pipeline | fluxo | "three-layer **pipeline**" |
| proof | prova | "zero-knowledge **proof**" |
| ledger | registro | "hash-chained **ledger**" |
| wearable | vestível | "consumer **wearable** integration" |
| endpoint | ponto de acesso | "REST **endpoint**" |
| deploy | implantação | "Cloud Run **deploy**" |
| open standard | padrão aberto | "**open standard** protocol" |
| draft | rascunho/proposta | "IETF Internet-**Draft**" |
| acknowledgment | reconhecimento | "**Acknowledgments** section" |
| limitation | limitação | "**acknowledged limitations**" |

---

*Este documento foi gerado pela IA Claude (Anthropic) para uso exclusivo de Christian Rodrigues Pereira / eColabs.*
*Última atualização: 27/07/2026 — v1.2 (CryptoAudit 9 achados, testes físicos Watch 6, Samsung SDK v1.4.1, 52 gaps, roadmap ZKP e PQC, 12 conceitos)*
*Versão LICET: 2.1.0 — 11 gaps de segurança mitigados em código (07–09/07/2026)*
