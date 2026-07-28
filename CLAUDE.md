# CLAUDE.md — LICET Protocol / NeuroTrust

Instruções obrigatórias para toda sessão neste repositório.
Estas instruções têm prioridade sobre comportamentos padrão.

---

## Skills por Tipo de Trabalho

### Criptografia e Segurança

**Quando:** qualquer edição em `core/crypto.py`, `core/key_management.py`, `zkp/proof.py`,
ou quando o trabalho envolve HMAC, Ed25519, HKDF, ZKP, Mahalanobis, threshold, baseline,
análise de vulnerabilidades, threat modeling, ou revisão de segurança do protocolo.

**Skill obrigatória:** `/cryptoaudit`

- Carregar e aplicar a skill antes de qualquer modificação ou análise
- Usar os 6 domínios da skill como checklist
- Todo finding deve ter: severidade, vetor de ataque concreto, mitigação específica

### API / Backend Python

**Quando:** qualquer edição em `api/routes.py`, `main.py`, `core/baseline.py`,
`core/pharmacological_check.py`, `core/respiratory_periodicity.py`, ou qualquer endpoint.

**Skills relevantes:**

- `fastapi-patterns` — padrões de estrutura, response models, dependency injection
- `python-patterns` — qualidade de código Python
- `api-design` — design de contratos e versionamento de API
- `security-review` — revisão de segurança de endpoints (rate limiting, auth, input validation)

**Padrões obrigatórios neste projeto:**

- Usar `hmac.compare_digest()` — nunca `==` para comparar segredos
- Usar `secrets.token_hex()` — nunca `random` para valores criptográficos
- Float encoding em HMAC: sempre `:.1f` para determinismo
- Validação de entrada em todos os endpoints antes de processamento
- Response models explícitos (sem retornar dicts crus)

### Android / Kotlin

**Quando:** qualquer trabalho em `licet-android/` ou integração Watch/Health Connect.

**Skills relevantes:**

- `android-clean-architecture` — arquitetura de camadas
- `kotlin-patterns` — idiomas Kotlin, coroutines, flows
- `kotlin-testing` — testes unitários e de integração

**Arquitetura atual:** Opção B (phone-only via Health Connect). Opção A (Wear OS app nativo)
está planejada mas não implementada ainda.

### Exploração de Codebase

**Quando:** perguntas sobre arquitetura, rastreamento de dependências, análise de impacto,
ou qualquer questão aberta sobre "como X funciona" no repositório.

**Skill:** `/graphify` — se `graphify-out/graph.json` já existe, usar query direto.

### Documentação e Publicações

**Quando:** trabalho em `docs/`, papers, submissões arXiv/MDPI, IETF drafts.

**Skills relevantes:**

- `article-writing` — estrutura de paper científico
- `literature-review` — revisão e citação de literatura relevante

---

## Padrões Gerais (aplicar sempre)

### Segurança

- Nunca expor chaves, tokens ou segredos em respostas de API (ver CA-02)
- Todo endpoint administrativo (`/admin/*`) requer autenticação (ver CA-01)
- Rate limiting é obrigatório em todos os endpoints expostos (ver CA-05)
- Campos que influenciam decisão de autorização devem estar cobertos pelo HMAC (ver CA-04)

### Qualidade de Código

- Não adicionar abstração para uso único — manter complexidade no nível necessário
- Não adicionar tratamento de erro para cenários impossíveis
- Não criar docstrings/comentários em código não modificado
- Preferir editar arquivo existente a criar novo
- Comentar apenas onde a lógica não é autoevidente

### Git e Commits

- Commits em português ou inglês (seguir estilo do histórico recente)
- Não commitar sem solicitação explícita do usuário
- Verificar `git diff` antes de qualquer commit

---

## PROIBIDO — Nunca Fazer

### 1. Git — O que jamais vai para o repositório

**Credenciais e chaves:**

- Arquivos `.env` ou qualquer variável com valor real de produção
- Chaves Ed25519 privadas (`private_key`, `signing_key`, `sk_bytes`, qualquer `_private`)
- `LICET_ADMIN_TOKEN` ou qualquer token de autenticação com valor real
- Chaves do Google Cloud (`service_account.json`, `credentials.json`, `keyfile.json`)
- Strings de conexão de banco de dados com senha (`postgresql://user:senha@...`)
- API keys de terceiros (Samsung SDK, qualquer serviço externo)

**Dados de usuários e testes reais:**

- Arquivos `.db` com dados biométricos reais (`licet_ledger.db`, `test_gdpr.db` — não commitar versões atualizadas sem verificar)
- Logs com RR intervals, EDA, HR de sessões reais
- Qualquer payload biométrico identificável (viola LGPD Art. 11)

**Propriedade intelectual sensível:**

- Implementação detalhada de `compute_mahalanobis_distance` em documentação pública
- Parâmetros específicos de threshold calibrados internamente
- Detalhes do `pharmacological_check` que revelem os vetores de ataque que o protocolo detecta

### 2. Código — Vulnerabilidades que nunca introduzir

**Injeção e input não sanitizado:**

- Nunca passar input do usuário para `eval()`, `exec()`, `os.system()`, `subprocess` com `shell=True`
- Nunca usar f-strings com dados do usuário em queries SQL — usar parâmetros SQLAlchemy
- Nunca deserializar `pickle` de dado recebido via API
- Nunca usar `yaml.load()` — sempre `yaml.safe_load()`

**Exposição de estado interno:**

- Nunca retornar stack traces completos em respostas de produção (`detail=str(e)` em FastAPI é proibido em prod)
- Nunca logar chaves, tokens, HMAC calculado, ou dados biométricos brutos
- Nunca incluir `key_hex`, `private_key`, ou derivação de chave em qualquer response JSON
- Nunca expor parâmetros internos do Mahalanobis (covariância, mean) via API sem autenticação

**Timing e comparação insegura:**

- Nunca usar `==` para comparar HMACs, tokens, ou qualquer segredo — sempre `hmac.compare_digest()`
- Nunca retornar erro diferenciado entre "usuário não existe" e "HMAC inválido" (vaza informação)
- Nunca usar `time.sleep()` como rate limiting (substituível por timing attack)

**Configuração insegura:**

- Nunca deixar `debug=True` no FastAPI em produção
- Nunca usar `allow_origins=["*"]` sem verificar que o endpoint não expõe dados sensíveis
- Nunca desabilitar verificação de certificado TLS (`verify=False` em requests)
- Nunca hardcodar IPs, URLs de produção, ou portas em código-fonte

### 3. Protocolo — Simplificações que quebram o LICET

**Nunca enfraquecer as verificações de segurança:**

- Nunca adicionar bypass ou fallback que pule a verificação HMAC (mesmo "para testes")
- Nunca aceitar `source="simulation"` como produção sem flag explícita isolada
- Nunca remover a verificação de `rr_intervals` para `source != "simulation"`
- Nunca aceitar autorização sem validação do baseline de maturidade

**Nunca expor o oracle biométrico:**

- Nunca retornar o valor exato de `D²` (distância de Mahalanobis) em respostas públicas — facilita membership inference
- Nunca retornar o valor exato do `IP` (Periodicity Index) — facilita calibração de ataque de respiração paced
- Retornar apenas `authorized: true/false` e `trust_level` categórico para clientes não autenticados

**Nunca modificar o ledger retroativamente:**

- O hash chain é imutável por design — nunca adicionar endpoint de edição/deleção de registros
- Nunca permitir que um registro seja reescrito, mesmo para "corrigir erro"

**Nunca implementar roadmap criptográfico sem alinhamento:**

- ZKP Schnorr → ZK-SERIES/Groth16: mudança de protocolo, requer alinhamento com Christian antes
- Ed25519 → ML-DSA-44: migração com período híbrido, não implementar unilateralmente
- OPRF para anti-clone V4: arquitetura nova, não é uma "melhoria" simples

---

## Contexto do Projeto

**O que é o LICET:** protocolo de autorização baseado em evidências biométricas fisiológicas
(HRV, EDA, temperatura, tremor) com assinatura Ed25519, Mahalanobis distance, ZKP Schnorr,
e ledger com hash chain. Publicado no IACR ePrint 2026/110546.

**Stack:**

- Backend: Python / FastAPI — `api/routes.py`, `core/`, `zkp/`
- Android: Kotlin / Health Connect / Samsung Sensor SDK — `licet-android/`
- Deploy: Google Cloud Run + Cloud SQL (em migração do SQLite efêmero)

**Arquivos críticos:**

- `api/routes.py` — todos os endpoints REST
- `core/crypto.py` — lógica HMAC, derivação de chaves, autorização
- `core/mahalanobis.py` — distância de Mahalanobis para detecção de anomalia
- `zkp/proof.py` — implementação ZKP Schnorr
- `core/baseline.py` — enrollment e maturidade do baseline biométrico

**Bugs conhecidos em produção (não resolver sem reportar primeiro):**

- V2 bug: tríade anticolinérgica (`EDA_SCL=0.2µS + HR=102bpm`) retorna `CLEAN(HIGH)` incorretamente
- SQLite efêmero em Cloud Run — baseline perdido a cada deploy

**Roadmap criptográfico (não implementar antes de alinhar):**

- Ed25519 → ML-DSA-44 (FIPS 204) — híbrido em 2026, completo em 2028
- ZKP Schnorr → ZK-SERIES (arXiv:2506.19393) → Groth16+Pedersen (BioZero) longo prazo
- Anti-clone (V4): OPRF via BFRB (IACR 2025/1211)
