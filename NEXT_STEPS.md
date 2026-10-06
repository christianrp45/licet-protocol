---
updatedAt: 2026-09-28
---

# LICET — Próximos Passos

Este arquivo é a fonte única de "o que fazer agora", lido tanto por sessões
futuras do Claude quanto pela rotina diária de lembrete (ver seção final).
Mantido atualizado — se algo aqui está resolvido, mover pra "Concluído" em vez
de deixar como pendente.

## 🔴 URGENTE — sequência de correções em andamento (27/09/2026)

Auditoria encontrou 5 sinais de segurança calculados pelo Android que nunca
chegam a influenciar a decisão do servidor. Christian aprovou resolver em
sequência, por gravidade. Status:

1. ~~**GAP-CA-10 — alerta de emergência**~~ ✅ **CORRIGIDO** (SMS+GPS real,
   local, testado por compilação+testes unitários — falta testar em
   dispositivo físico). Ver `security-gaps.md`.
2. ~~**GAP-CA-09 — liveness/coerção/nível ignorados pelo servidor**~~ ✅
   **CORRIGIDO (versão intermediária)** — sig_data v4 (HMAC cobre os 3
   campos), persistido no ledger, sem verificação criptográfica independente
   (limitação aceita, documentada). 3 bugs reais pegos e corrigidos durante a
   verificação (nome de campo, capitalização de bool, interação com
   device_signature/GAP-CA-08). Ver `security-gaps.md`.
3. ~~**GAP-CA-11 — baseline poisoning computado, nunca persistido**~~ ✅
   **CORRIGIDO (28/09/2026)** — persistido em `user_baselines`, exposto em
   `/admin/dashboard` e `/gdpr/data/{user_id}`. Sem consequência automática
   pra risco HIGH (decisão consciente do Christian — só informativo por
   ora). Migração testada contra schema real de produção (ALTER TABLE +
   linha pré-existente sobrevive). Ver `security-gaps.md`.
4. ~~**GAP-CA-12 — medication_accommodation sem como o app acionar**~~ ✅
   **CORRIGIDO (28/09/2026)** — toggle em Configurações + HMAC cobrindo o
   campo (v2-bb) + mensagem de erro do endpoint inexistente corrigida. Ver
   `security-gaps.md`.
5. **GAP-CA-13 — action_commitment nunca enviado pelo app** — PRÓXIMO (último
   da sequência).

Detalhes completos: `docs/research/security-gaps.md` GAP-CA-08 a CA-13.

## 🔴 Caminho crítico — nessa ordem

1. **Escrever a prosa das Seções 3, 4 e 5 do paper VLP** (Threat Model,
   Protocol Spec, Security Analysis) — rascunho crescendo em
   `docs/research/paper_vlp_draft.md`. **Seção 3 (Threat Model) concluída em
   27/09/2026** — modelo de sistema, modelo de adversário formal (5
   capacidades), 5 classes de adversário, 4 não-objetivos explícitos
   (incluindo o achado do oracle leak como exemplo real de extração).
   Faltam Seções 4 e 5. Sem isso o paper não existe pra submeter em venue
   nenhuma.
2. **Aguardar resposta MDPI Cryptography** (waiver enviado 29/08/2026) — sem
   ação possível, só monitorar e-mail.
3. **Submeter IACR Communications in Cryptology** — checklist pronto em
   `docs/iacr_cic/README_cic.md`, falta executar (compilar `iacrcc.cls`,
   gerar versão anônima, submeter). Mecânico, não depende de ninguém.
4. **PR #103 (IETF draft) — aguardando David Condrey** revisar a correção de
   25/09 (DCO + 3 blockers). Já cutucamos educadamente. Sem ação possível até
   ele responder.
5. **Monitorar oposição INPI** (processo 944297536, RPI 2901) até
   ~10/10/2026 — sem oposição confirmada até 25/09.
6. **Auditoria externa de segurança** (Trail of Bits/NCC Group-style) — ainda
   não iniciada, é pré-requisito pra "pré-mercado", não urgente ainda mas
   entrar no radar.

## 🟡 Paralelo — não bloqueia o caminho crítico, mas soma valor real

- **App iOS** — 3 bugs de HMAC corrigidos (26/09), falta abrir no Xcode
  (precisa de Mac). Ver memória `project_ios_app_status`.
- **BLE GATT (Polar H10)** — código pronto dos dois lados, aguardando compra
  confirmada em 25/09.
- **Onboarding de colaboradores externos** (Garmin + Samsung Watch 8) —
  termos prontos (`docs/anpd/`), aguardando e-mails dos dois (segunda-feira).
- **Health Connect Changes API** — investigação não iniciada, alternativa
  mais barata que adotar infraestrutura externa pra resolver latência de
  sincronização (decidimos não adotar `open-wearables`, ver memória
  `research_repos_wearables_27092026`).

## 🔴 Incidente resolvido (28/09/2026) — leitura obrigatória antes de migrações futuras

Deploy do GAP-CA-09/CA-11 quebrou `/ledger/history` e `/biometric/push` em
produção com HTTP 500 (`UndefinedColumn`), mesmo com todos os testes locais
(SQLite) passando. Causa: `_migrate_columns()` (`ledger/db.py`) rodava todas
as migrações numa única transação compartilhada. No **PostgreSQL** (produção
usa Cloud SQL; testes locais usam SQLite), a primeira coluna "já existente"
que falha deixa a transação inteira abortada — todo ALTER seguinte falha
silenciosamente (capturado pelo mesmo `except` genérico), e as colunas novas
nunca são criadas de verdade. SQLite não tem esse comportamento, por isso
passou despercebido em todo teste local desta sessão.

**Corrigido:** cada migração agora roda na sua própria transação isolada.
Deploy da correção verificado ao vivo (`licet.dev/v1/ledger/history` voltou a
200, `/biometric/push` sem mais 500).

**Lição para toda migração futura:** testes locais com SQLite NÃO detectam
esse tipo de problema — sempre que uma migração desse tipo for adicionada,
considerar o comportamento de transação do PostgreSQL antes de assumir que
"passou no teste local" = "vai funcionar em produção".

## ✅ Concluído recentemente (28/09/2026)

- GAP-CA-08 a CA-12 corrigidos e testados (ver seção URGENTE acima) — CA-13 é
  o único aberto
- Incidente de migração PostgreSQL (transação abortada em cascata) encontrado
  e corrigido em produção no mesmo dia
- Paginação real (offset-based) em `/ledger/history` + numeração de página no
  Dashboard Android ("Últimas Autorizações" não é mais onepage crescendo)
- Botão de copiar `chain_hash` em cada card de autorização — permite
  verificação independente por quem receber o resultado
- Nova caixa "Verify an Authorization" em `licet.dev` (`GET /v1/ledger/verify`)
  — cola o hash copiado do app, confirma que está no ledger público
- Corrigido: `LedgerRecord` (Android) ainda esperava campos que o servidor
  parou de enviar no fix F-10/F-11 (oracle leak, 25/09) — nunca eram lidos
  na UI, mas o modelo estava desalinhado; alinhado com o schema real
- Corrigido: link de download quebrado em `licet.dev` (apontava pra
  `licet-android.apk`, o CI publica como `licet-phone.apk`)
- `firebase.json`/`.firebaserc` órfãos removidos (nunca commitados, sem uso)
- `docs/GUIA_COMPLETO_LICET.md`/`.pdf` atualizados (estava parado desde julho)

## ✅ Concluído recentemente (25-27/09/2026)

- Experimento WESAD rodado e analisado (15/15 sujeitos, GAP-B01 confirmado)
- Incidente de segurança do oracle D²/IP corrigido e deployado (licet-00066-xn2)
- Commit do material WESAD feito (`ddb80c0`), dataset 17GB excluído via `.gitignore`
- Pesquisa de concorrência: nenhum concorrente direto encontrado; monitor
  mensal automático configurado
- Decisão de não adotar `open-wearables` como camada de dados

## Segurança — histórico (não retestar sem motivo)

CA-01 a CA-09, V2 (tríade anticolinérgica), F-01 a F-09 (auditoria 07/09) e
F-10/F-11 (oracle D²/IP, 25/09) todos fechados. Único item aberto sem
esforço de implementação: F-06 (HMAC v1 legado, prioridade baixa).

## Como retomar

- `"vamos continuar"` ou `"o que temos pra fazer"` → este arquivo
- `"vamos pro CA-13"` → GAP-CA-13 (action_commitment nunca enviado pelo app real)
- `"escrever seção 3"` / `"4"` / `"5"` → retomar a redação do paper
- `"status PR #103"` → `gh pr view 103 --repo LF-Decentralized-Trust-labs/proof-of-effort`
- `"status ledger"` → `curl https://licet.dev/v1/ledger/history?limit=5`
- `"chegou o Polar H10"` → testar BLE GATT ponta a ponta
- `"vamos cadastrar os colaboradores"` → Firebase App Distribution + termos

Detalhes técnicos completos de cada item ficam na memória do Claude Code
(`C:\Users\chris\.claude\projects\d--NeuroTrust-licet\memory\`), não
duplicados aqui — este arquivo é o resumo executivo, versionado no repo.
