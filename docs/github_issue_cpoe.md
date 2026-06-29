### Context

The CPoE architecture defines four assurance tiers, with T2 described as "corroborated, cross-signal verification." The current evidence model collects behavioral signals (keystroke dynamics, pause patterns, editing trajectories) and cross-references them with accelerometer impulses via inertial coherence analysis.

This issue proposes a concrete T2 corroboration path: wearable-sourced physiological signals as an independent evidence class that behavioral data alone cannot provide — specifically, proof that the human author was uncoerced and cognitively intact at the time of attestation.

### The gap behavioral evidence cannot close

A person under physical duress can type, edit, and produce behavioral patterns within human baseline distributions. Keystroke entropy, cognitive load correlation, and biological cadence analysis do not detect coercion — they detect human-like behavior, which can coexist with duress.

The missing claim in the current evidence model: `coercion_risk` and `cognitive_state` — physiological dimensions that are independent of behavioral output.

### Proposed evidence signals

Three metrics captured over a 10-second window via wearable (BLE GATT Heart Rate Profile, Samsung Health Connect, or Apple HealthKit):

| Signal | Physiological basis | Coercion indicator |
|---|---|---|
| Heart Rate (HR, bpm) | Sympathetic activation under acute stress | Elevated |
| HRV — RMSSD (ms) | Parasympathetic suppression under acute stress | Collapsed |
| SpO₂ (%) | Peripheral oxygen saturation | Cognitive impairment below 90% |

The key insight from autonomic neuroscience: the concurrent collapse of both HR ↑ and HRV ↓ distinguishes coercion from aerobic exercise, where HRV recovers rapidly. This dual-axis signature is not reproducible by behavioral patterns alone.

### Coercion detection function

```
C(HR, HRV) = HIGH    if HR > 130 bpm AND HRV < 20ms  → block
C(HR, HRV) = MEDIUM  if HR > 100 bpm AND HRV < 35ms  → block
C(HR, HRV) = LOW     otherwise                        → pass

I(SpO₂)   = IMPAIRED if SpO₂ < 90%                   → block
```

### RATS architecture mapping

```
Wearable device   → Attester (physiological)
Biometric capture → Evidence Packet (new claim type)
ZKP output        → Attestation Result (coercion_risk, cognitive_state)
LICET server      → Verifier
```

The wearable is a new Attester type alongside the existing HW attestation (TPM/HSM). It produces a new Evidence Packet claim type that feeds into the existing Verifier → Relying Party flow.

### Privacy: ZKP for physiological evidence

Physiological values are sensitive personal data (GDPR Article 9, LGPD Article 5). A Schnorr ZKP over BN128 allows the Verifier to confirm that thresholds were met without learning the underlying HR, HRV, or SpO₂ values — the same zero-knowledge property CPoE applies to behavioral entropy.

The proof π = (R, c, s, PK) is stored in the Evidence Packet. Verification requires only the public key and the session identifier — fully offline, no registry lookup.

### CBOR encoding

Proposed new claim types for `evidence-packet` (tag 1129336645):

```cddl
physiological-evidence = {
  coercion_risk:    text,   ; "LOW" / "MEDIUM" / "HIGH"
  cognitive_state:  text,   ; "NORMAL" / "IMPAIRED"
  capture_window_s: uint,   ; default 10
  zkp_proof:        bstr,   ; Schnorr proof bytes
  wearable_type:    text,   ; "BLE_GATT" / "HealthConnect" / "HealthKit"
  timestamp_ms:     uint
}
```

### EU AI Act alignment

CPoE addresses Article 50 (AI-generated content disclosure). The LICET protocol addresses Article 14 (human oversight of high-risk AI systems). These are distinct requirements in the same regulation. A combined CPoE + physiological attestation layer would address both sides: proving human authorship and proving the human was capable of genuine oversight.

### Reference implementation

- **Live API:** https://licet.dev/v1/
- **IETF Internet-Draft:** draft-pereira-licet-human-intent-00
- **SSRN Preprint:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7018458
- **GitHub:** https://github.com/christianrp45/licet-protocol
- **Blockchain timestamp:** OpenTimestamps / Bitcoin, 2026-02-25

I can contribute a draft section for the CDDL schema extension and the RATS role mapping if the direction is useful to the group.

---
*Christian Rodrigues Pereira — eColabs Desenvolvimento de Pessoas e Organizações LTDA. — contato@ecolabs.com.br*
