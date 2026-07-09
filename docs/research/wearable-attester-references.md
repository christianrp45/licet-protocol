[//]: # (SPDX-License-Identifier: Apache-2.0)

# Wearable Attester — Research References

Atualizado: 2026-07-09 | Gerado: 2026-07-06 | Context: Contribution to proof-of-effort / CPoE wearable Attester draft

## Documentos relacionados

- [bio-sensors-matrix.md](bio-sensors-matrix.md) — Matriz completa de dispositivos com sensores biológicos para integração LICET
- [security-gaps.md](security-gaps.md) — 46 gaps de segurança catalogados com severidade e mitigação

---

## 1. Paced Breathing → Volitional Vagal Enhancement

**Vulnerabilidade crítica identificada por David:** Um sujeito coagido treinado em
respiração ressonante (~0.1 Hz) produz um vetor de calma fisiologicamente autêntico
— RMSSD elevado, HF elevado, EDA baixa, HR baixa — indistinguível de calma genuína.
O design Mahalanobis colapsa a distância a zero. Deve ser nomeado como limitação
primária no wearable Attester draft.

### Referência principal

- **Laborde, S. et al. (2022).** *Psychophysiological effects of slow-paced breathing
  at six cycles per minute with or without heart rate variability biofeedback.*
  Psychophysiology.
  DOI: [10.1111/psyp.13952](https://onlinelibrary.wiley.com/doi/10.1111/psyp.13952)
  — Confirma que SPB a 6 ciclos/min eleva RMSSD significativamente, com ou sem
  biofeedback. Mecanismo puramente comportamental, sem farmacologia.

### Suporte adicional

- Influência da frequência respiratória no HRV vagal-mediado:
  [PubMed 38063977](https://pubmed.ncbi.nlm.nih.gov/38063977/)
- Meta-análise sobre slow breathing e HRV:
  [ScienceDirect](https://www.sciencedirect.com/science/article/abs/pii/S0149763422002007)

---

## 2. Beta-Blockers (Propranolol/Metoprolol) — HRV e Reatividade ao Estresse

**Dois caveats identificados por David:**
1. "A literatura mostra que RMSSD ainda colapsa" superestima o que foi medido —
   o experimento específico beta-bloqueador + estresse mental agudo + RMSSD está
   ausente da literatura. É mecanisticamente esperado, não demonstrado.
2. Beta-bloqueadores crônicos elevam RMSSD basal e reduzem HR de repouso —
   o fingerprint de calma fica deslocado antes de qualquer estresse. Confound real
   para um detector de baseline personalizado.

### Referências principais

- **Steptoe, A. et al. (2018).** *The effect of beta-adrenergic blockade on
  inflammatory and cardiovascular responses to acute mental stress.*
  Brain, Behavior, and Immunity.
  PMC: [PMC5965252](https://pmc.ncbi.nlm.nih.gov/articles/PMC5965252/)
  — Achado crítico: HR e PA aumentaram marcadamente durante os tasks, **sem
  diferença de reatividade entre propranolol e placebo** — suporta que a reatividade
  ao estresse mental sobrevive ao bloqueio beta.

- **Lampert, R. et al. (2003).** *Effects of propranolol on recovery of heart rate
  variability following acute myocardial infarction and relation to outcome in the
  Beta-Blocker Heart Attack Trial.*
  American Journal of Cardiology.
  [ScienceDirect](https://ajconline.org/article/S0002-9149(02)03098-9/fulltext)
  — Beta-bloqueadores elevam RMSSD basal e reduzem HR de repouso.

---

## 3. LF não é marcador simpático limpo

**Correção de David:** Remover o framing de "ramo simpático" do LF. LF reflete
modulação barorreflexa do outflow autonômico, não tônus simpático cardíaco diretamente.

### Referência principal

- **Moak, J.P. et al. (2007).** *Supine low-frequency power of heart rate variability
  reflects baroreflex function, not cardiac sympathetic innervation.*
  Heart Rhythm.
  PMC: [PMC2204059](https://pmc.ncbi.nlm.nih.gov/articles/PMC2204059/) |
  PubMed: [17997358](https://pubmed.ncbi.nlm.nih.gov/17997358/)
  — LF power não correlaciona com inervação simpática cardíaca; correlaciona
  positivamente com slope barorreflex-cardiovagal.

### Consenso posterior

- **Goldstein, D.S. (2011).** *Low-frequency power of heart rate variability is not
  a measure of cardiac sympathetic tone but may be a measure of modulation of cardiac
  autonomic outflows by baroreflexes.*
  Experimental Physiology.
  [Wiley](https://physoc.onlinelibrary.wiley.com/doi/abs/10.1113/expphysiol.2010.056259)

- **Billman, G.E. (2013).** *The LF/HF ratio does not accurately measure cardiac
  sympatho-vagal balance.*
  Frontiers in Physiology.
  PMC: [PMC3576706](https://pmc.ncbi.nlm.nih.gov/articles/PMC3576706/)

---

## 4. EDA — Inervação Simpático-Colinérgica

**Ponto de David:** Anticolinérgicos (atropina, escopolamina) produzem assinatura
invertida autoincriminante: RMSSD abolido + EDA plana + HR elevada. Nenhum estado
genuíno de calma produz essa combinação.

### Fundamento fisiológico

- Glândulas écrinas têm inervação **simpática** mas neurotransmissor **colinérgico**
  (acetilcolina, não noradrenalina).
- EDA reflete exclusivamente atividade simpática — sem inervação parassimpática
  das glândulas sudoríparas écrinas.

### Fontes

- [Encyclopedia MDPI — Electrodermal Activity](https://encyclopedia.pub/entry/277)
- [Springer — Clinical use of EDA](https://link.springer.com/article/10.1007/s00249-026-01820-z)

---

## 5. RFC 9334 — RATS Architecture e Composite Attester

### Estrutura de seções relevantes (confirmada)

| Seção | Título |
|-------|--------|
| §3.1 | Two Types of Environments of an Attester |
| §3.3 | Composite Device |
| §4.1 | Roles |
| §8.1 | Passport Model |
| §8.2 | Background-Check Model |

### Correção crítica (David)

- `§3.1.4` **não existe** no RFC 9334
- O modelo Composite Device está em **§3.3**, não §3.1.4
- Roles (Attester, Verifier, Relying Party) definidos em **§4.1**, não §3.1

### Fontes

- RFC 9334: [datatracker.ietf.org/doc/rfc9334](https://datatracker.ietf.org/doc/rfc9334/)
- RFC 9711 (EAT): [datatracker.ietf.org/doc/rfc9711](https://datatracker.ietf.org/doc/rfc9711/)
- Draft Composite Attesters: [draft-richardson-rats-composite-attesters](https://datatracker.ietf.org/doc/draft-richardson-rats-composite-attesters/)

---

## 6. Resposta enviada ao David (2026-07-06)

> David,
>
> Thank you for the detailed and precise feedback — this is exactly the level of
> rigor the spec needs.
>
> **On beta-blockers:** both caveats taken. I'll revise the language from "the
> literature shows RMSSD still collapses" to "mechanistically expected but not
> directly demonstrated in the specific propranolol/metoprolol + acute mental
> stress + RMSSD-reactivity experimental design." Steptoe et al. (Brain Behav
> Immun 2018, PMC5965252) supports the mechanism by inference — HR reactivity
> survives propranolol — but the direct RMSSD measurement in that configuration
> is absent from the published record, and the spec will say so explicitly.
>
> The baseline-shift confound is a more serious problem than I initially framed
> it: chronic beta-blockade raises resting RMSSD and lowers resting HR (Lampert
> et al., Am J Cardiol 2003), which means a subject on chronic therapy presents
> an already-shifted calm fingerprint before any challenge is applied. For a
> personalized-baseline detector this is a genuine confound, not a peripheral
> note. I'll add it as such.
>
> **On LF framing:** agreed. I'll drop the "sympathetic branch" language. LF
> reflects baroreflex modulation of autonomic outflow, not cardiac sympathetic
> tone directly — Moak et al. (Heart Rhythm 2007, PMC2204059) and Goldstein
> (Exp Physiol 2011) make that unambiguous. The LF suppression observation
> stays; the interpretation gets corrected.
>
> **On anticholinergics:** the eccrine gland point stands — sympathetic-cholinergic
> innervation means atropine/scopolamine flatten EDA and abolish RMSSD
> simultaneously. The resulting combination (abolished RMSSD + flat EDA +
> elevated HR) is self-incriminating precisely because no genuine calm state
> produces it. Noted for the footnote.
>
> **On paced breathing:** this is the point I should have named first. A coerced
> subject trained in resonance-frequency breathing at ~0.1 Hz produces a
> physiologically authentic calm vector — elevated RMSSD and HF, low EDA, low
> HR, internally consistent — that is not a forgery of the baseline; it *is* the
> baseline, volitionally manufactured (Laborde et al., Psychophysiology 2022,
> DOI: 10.1111/psyp.13952). The Mahalanobis design measures distance from the
> calm fingerprint. Paced breathing moves the subject to that fingerprint. The
> distance collapses to zero without any anomalous signal. I don't have a
> mitigation for this in the current design, and it will be named as a primary
> limitation in the wearable Attester document from the first draft.
>
> **On architecture:** correcting PR #97 now — composite model is RFC 9334 §3.3,
> not §3.1.4. I'll open the wearable Attester draft as a separate document in
> this repo. Before I put a skeleton together: do you want the CDDL Evidence
> format as the opening section, or would you prefer the document to establish
> the attester topology and trust relationships first and defer the CDDL to a
> later section once the conceptual framing is settled?
>
> Ready to move when you are.
>
> Christian

---

## Próximos passos

- [ ] Aguardar resposta do David sobre estrutura do wearable Attester draft
- [ ] Abrir wearable Attester draft como documento separado no repo proof-of-effort
- [ ] Nomear paced breathing como limitação primária desde a primeira versão
- [ ] Incorporar correções de linguagem sobre beta-blockers e LF no LICET spec
- [ ] Integrar TypingDNA SDK como primeira implementação T1 (entropy-behavioral)
- [ ] Integrar Apple HealthKit como stack T2/T3 principal (HRV + EDA + ECG)
- [ ] Resolver GAP-C01 e GAP-C02 antes de qualquer auditoria de segurança externa
- [ ] Resolver GAP-O02 (HSM + Shamir Secret Sharing para k_m)
- [ ] Incorporar security-gaps.md na seção Security Considerations do IETF draft
