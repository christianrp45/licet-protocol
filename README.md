# LICET — Human Intent Protocol

> *"No AI acts without you."*

**LICET** (Latin: *it is permitted*) is an open authorization middleware protocol that cryptographically binds autonomous AI agent actions to the real-time physiological state of the authorizing human.

Unlike passwords, biometric templates, or digital signatures — which verify *who you are* — LICET verifies *that you are conscious, uncoerced, and cognitively capable* at the exact moment of authorization.

**Live API:** [licet.dev/v1/](https://licet.dev/v1/)  
**Preprint:** [SSRN 7018458](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7018458) (v2 updated July 2026)  
**IETF Internet-Draft:** [draft-pereira-licet-human-intent-01](https://datatracker.ietf.org/doc/draft-pereira-licet-human-intent/) (submitted July 2, 2026)  
**Protocol timestamp:** Bitcoin blockchain via OpenTimestamps — February 25, 2026  

---

## The Problem

AI agents are executing consequential actions — prescribing medications, executing financial transfers, modifying critical infrastructure. Existing authorization mechanisms answer *"who authorized?"* but not *"was that person genuinely free, conscious, and capable at that moment?"*

| Mechanism | Identity | Liveness | Coercion-free | Cognitively intact | Drug-resistant |
| --- | --- | --- | --- | --- | --- |
| Password | ~ | ✗ | ✗ | ✗ | ✗ |
| Static biometric | ✓ | ✓ | ✗ | ✗ | ✗ |
| Digital signature | ✓ | ✗ | ✗ | ✗ | ✗ |
| Single-signal HRV | ✓ | ✓ | ~ | ~ | ✗ |
| **LICET v2** | ✓ | ✓ | ✓ | ✓ | **Y** |

---

## How It Works

LICET v2 uses a three-layer biometric pipeline. All three layers must pass before an authorization is issued.

```text
AI Agent requests action
        ↓
┌─────────────────────────────────────────────────────────┐
│  LAYER 1 — ECG Waveform Morphology (QRS shape)          │
│  Platform: Apple Watch Series 4+ (HealthKit, 512 Hz)    │
│  Purpose:  medication-resistant identity + liveness      │
│  Window:   60 seconds minimum                           │
│  Fail:     QRS morphology mismatch → DENIED             │
└─────────────────────────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────────────────────────┐
│  LAYER 2 — EDA (Electrodermal Activity)                  │
│  Platform: WHOOP 5 (continuous) / Samsung GW7 (spot)    │
│  Signals:  SCL (skin conductance level — tonic)         │
│            SCR (skin conductance response — phasic)     │
│  Purpose:  sympathetic cholinergic liveness             │
│            immune to beta-blockers                      │
│  Fail:     EDA flat (anticholinergic profile) → DENIED  │
└─────────────────────────────────────────────────────────┘
        ↓ (pass)
┌─────────────────────────────────────────────────────────┐
│  LAYER 3 — Mahalanobis Distance Fusion                  │
│  Signals:  RMSSD, EDA-SCL, EDA-SCR, skin temp,         │
│            tremor 8–12 Hz                               │
│  Baseline: personalized (NOT population thresholds)     │
│  Purpose:  detect pharmacological deviation from        │
│            the individual's own baseline                │
│  Fail:     D² > threshold for user baseline → DENIED   │
└─────────────────────────────────────────────────────────┘
        ↓ (all layers pass)
Intent Hash  = SHA256(action ‖ agent_id ‖ target ‖ timestamp)
Session key  = HKDF(master_key, intent_hash)
Bio signature = HMAC(intent_hash ‖ biometrics, session_key)
ZKP (Schnorr/BN128) — proves valid biometrics without revealing them
Ledger append = SHA256(entry ‖ prev_hash)   — tamper-evident chain
        ↓
AUTHORIZED ✓  — returns intent_hash + zkp_proof + ledger_id + trust_level
```

### Biometric Trust Levels (aligned with IETF RATS RFC 9334)

| Level | Name | Hardware | Attestation |
| --- | --- | --- | --- |
| L0 | No attestation | Simulator | Software only — development use |
| L1 | Platform attestation | Consumer BLE + HealthKit / Health Connect | OS-level platform attestation |
| L2 | Hardware attestation | Pixel Watch 2 + Titan M2 + Android Key Attestation | Hardware-backed key in secure enclave |
| L3 | Sensor-to-TEE direct | Future — not yet available | Direct sensor path into TEE |

In the RATS composite attester model (RFC 9334 §3.1.4): the wearable is the **Sub-Attester**, the mobile app is the **Lead Attester**, and the LICET server is the **Verifier**.

---

## API — Live Reference

The LICET protocol is live at [licet.dev/v1/](https://licet.dev/v1/).

| Method | Endpoint | Description |
| --- | --- | --- |
| GET | `/v1/health` | Protocol status and trust level |
| POST | `/v1/authorize` | Full three-layer biometric authorization |
| POST | `/v1/biometric/push` | Receive wearable data from mobile app |
| POST | `/v1/authorize/from-push` | Authorize using pushed biometrics |
| POST | `/v1/verify` | ZKP verification (for auditors) |
| GET | `/v1/ledger/integrity` | Verify full ledger hash chain |
| GET | `/v1/ledger/history` | Authorization event history |

**Authorization response shape:**

```json
{
  "authorized": true,
  "intent_hash": "a3f8b2c1...",
  "coercion_cost_elevation": "NOMINAL",
  "cognitive_state": "NORMAL",
  "trust_level": "L1",
  "layer1_ecg": "PASS",
  "layer2_eda": "PASS",
  "layer3_mahalanobis_d2": 1.43,
  "zkp_proof": { "commitment": {...}, "challenge": "0x...", "response": "0x..." },
  "ledger_id": 42,
  "timestamp": 1782490000.0
}
```

---

## Hardware Support

| Source | Signals | Protocol | Trust Level | Status |
| --- | --- | --- | --- | --- |
| Apple Watch Series 4+ | ECG (512 Hz), HR, HRV | HealthKit (iOS) | L1 | Spec ready |
| WHOOP 5 | EDA-SCL, EDA-SCR, skin temp, HR | WHOOP API (continuous) | L1 | In development |
| Samsung Galaxy Watch 7 | EDA (spot-check), HR, HRV | Health Connect (Android) | L1 | In development |
| Pixel Watch 2 | HR, HRV | Android Key Attestation + Titan M2 | L2 | Spec ready |
| Any BLE wearable | HR | GATT Heart Rate Profile | L1 | Supported |
| MAX30102 sensor | HR, SpO₂ | I²C / Raspberry Pi | L1 | Supported |

---

## Regulatory Alignment

- **EU AI Act (2024) Art. 9** — risk management system: three-layer biometric pipeline satisfies systematic risk controls for high-risk AI
- **EU AI Act (2024) Art. 12** — record-keeping: tamper-evident hash-chained ledger with ZKP-verified authorization records
- **EU AI Act (2024) Art. 26(5)** — deployer obligations for human oversight: LICET provides cryptographic evidence that a human in a verifiable physiological state authorized each consequential action
- **Brazil LGPD** — biometric data never stored in ledger; ZKP ensures privacy by design
- **NIST AI RMF** — tamper-evident authorization records satisfy GOVERN/MEASURE functions
- **IETF RATS RFC 9334** — biometric trust level hierarchy (L0–L3) maps to composite attester architecture

---

## Security Properties

| Threat | Protection |
| --- | --- |
| Replay attack | Timestamp-bound intent hash — each authorization is unique |
| Coercion cost elevation | Three-layer resistance — ECG identity + EDA liveness + Mahalanobis personalized state |
| Cognitive impairment | Mahalanobis deviation from personal baseline — not population average |
| Pharmacological attack | Beta-blocker: tremor signal z_TREMOR < −2.0 detected. Anticholinergic (atropine/scopolamine): EDA flat + HRV elevated + warm skin — inverted toxidrome detected. Opioid: respiratory depression signal detected. |
| Attestation chain gap | L0–L3 trust levels declared explicitly — L3 (sensor-to-TEE) is future work, acknowledged |
| Ledger tampering | Hash chain — mathematically detectable |
| Biometric exposure in audit | ZKP — proves validity without revealing raw data |
| Session key compromise | HKDF per-event derivation — isolated per authorization |

---

## Specification Documents

| Document | Location |
| --- | --- |
| Academic paper (LaTeX source + PDF) | [`docs/arxiv/`](docs/arxiv/) |
| IETF Internet-Draft -01 | [`docs/ietf/draft-pereira-licet-human-intent-01.txt`](docs/ietf/draft-pereira-licet-human-intent-01.txt) |
| IETF Internet-Draft -01 (Markdown source) | [`docs/ietf/draft-pereira-licet-human-intent-01.md`](docs/ietf/draft-pereira-licet-human-intent-01.md) |
| Full technical whitepaper | [`WHITEPAPER.md`](WHITEPAPER.md) |

---

## Citation

If you use LICET in your research:

```text
Pereira, C. R. (2026). LICET: A Biometric Intent Authorization Protocol
for Autonomous AI Agents (v2). eColabs. SSRN 7018458.
https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7018458

IETF Internet-Draft: draft-pereira-licet-human-intent-01 (July 2, 2026)
https://datatracker.ietf.org/doc/draft-pereira-licet-human-intent/
```

---

## License

This protocol specification is released under the **Apache 2.0 License**.

You are free to use, modify, and distribute LICET in commercial and non-commercial projects.  
Attribution required. Patent rights reserved by eColabs Desenvolvimento de Pessoas e Organizações LTDA.

---

## Author

**Christian Rodrigues Pereira**  
eColabs Desenvolvimento de Pessoas e Organizações LTDA.  
[contato@ecolabs.com.br](mailto:contato@ecolabs.com.br)  
[licet.dev](https://licet.dev)

Protocol timestamp registered on Bitcoin blockchain via OpenTimestamps — February 25, 2026.
