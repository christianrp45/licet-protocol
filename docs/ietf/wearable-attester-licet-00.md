[//]: # (SPDX-License-Identifier: Apache-2.0)

# LICET Wearable Attester — Topology and Trust Hierarchy

**Document:** wearable-attester-licet-00
**Status:** Skeleton / in progress — awaiting topology review by David Condrey
**Authors:** Christian Pereira (NeuroTrust)
**Date:** 2026-07-10
**Related:** draft-pereira-licet-human-intent-01, LF-Decentralized-Trust-labs/proof-of-effort PR #97

---

## Abstract

This document defines the Attester topology and trust hierarchy for LICET (Layered Intent Corroboration via Embedded Trust) wearable devices operating as composite Attesters under IETF RFC 9334. It establishes L0–L3 as a graduated trust hierarchy in which evidential weight follows attestation level, and defers encoding to a later section once the conceptual framing is settled.

**The claim throughout is corroboration, not proof.** Physiological signals narrow the inference space; they do not establish intent with certainty. Sections 2 and 3 bound this claim explicitly before any architecture is presented.

---

## 1. Scope

This document addresses:

- The role of a LICET wearable as a composite Attester under RFC 9334 §3.3
- The L0–L3 trust hierarchy and how evidential weight is assigned per level
- Hard bounds on claims: what the ZKP proves, what it does not
- Appraisal logic for evidence packets
- Evidence encoding (deferred — Section 8, pending topology stabilization)

---

## 2. Primary Limitations

> **These limitations appear here, not in an appendix.** A reviewer who reaches the architecture without understanding the hard bounds will misread the system's claims. The two bounds below are load-bearing constraints on the entire design.

### 2.1 Paced Breathing — Hard Bound on Mahalanobis Claims

**This is the limitation that genuinely breaks the Mahalanobis design.**

A coerced subject trained in resonance-frequency breathing at ~0.1 Hz (6 cycles per minute) produces a physiologically authentic calm vector — elevated RMSSD and HF power, low EDA, low HR — that is internally consistent and matches the calm fingerprint. This is not a forgery of the baseline; it *is* the baseline, volitionally manufactured [Laborde et al., Psychophysiology 2022, DOI: 10.1111/psyp.13952].

The Mahalanobis design measures distance from the calm fingerprint. Paced breathing moves the subject to that fingerprint. The distance collapses to zero without producing any anomalous signal. The system cannot distinguish:

- (a) Genuine calm under no coercion
- (b) Volitional calm via paced breathing under coercion

**Consequence:** No claim derived from Mahalanobis distance alone survives this scenario. The Mahalanobis layer provides corroborating evidence under adversarial assumptions that exclude trained volitional vagal control. This assumption must be stated explicitly wherever the layer's output is interpreted.

**Current mitigation:** Respiratory periodicity index (RSA CV) can detect trained paced breathing by its characteristic regularity signature. Paced breathing at resonance frequency produces highly regular inter-breath intervals (RSA CV in the order of 0.03), whereas genuine resting HRV exhibits substantially higher inter-breath variability (RSA CV in the order of 0.40); these are illustrative values derived from the slow-paced breathing literature (Laborde et al., Psychophysiology 2022) and implementation measurements, not normative thresholds. This narrows the attack surface but does not close it. Respiratory periodicity is a discriminant, not a proof.

**Encoding note:** The `respiratory_periodicity_warning` flag in the evidence packet is a detector output, not a falsification of the Mahalanobis claim. Both are surfaced; interpretation is left to the Relying Party.

### 2.2 T2 Self-Report Gap

Layer T2 in the LICET model relies on user-reported behavioral signals (e.g., TypingDNA, gaze entropy, touchscreen dynamics). These signals are produced by the subject asserting intent and cannot be independently verified by the wearable Attester. The T2 attestation level reflects behavioral entropy, not physiological measurement.

**Consequence:** T2 evidence does not carry evidential weight independent of a concurrently valid T3 or T4 physiological layer. A Relying Party policy that grants authorization on T2 alone accepts self-report as its primary evidence. This must be explicit in policy.

---

## 3. The Claim: Corroboration, Not Proof

LICET produces an **intent corroboration score**, not a proof of intent.

The ZKP (zero-knowledge proof) in the LICET authorization bundle proves:

- That a measurement was taken at a claimed time
- That the measurement's Mahalanobis distance from the subject's baseline falls within a claimed range
- That the cryptographic chain from sensor to proof is intact

**The ZKP does not prove:**

- That the physiological state reflects genuine uncoerced calm
- That the subject was not performing volitional vagal enhancement (Section 2.1)
- That the self-report layer (T2) reflects actual behavioral state

Spell this out clearly to every Relying Party that inspects the proof: **ZKP ≠ proof-of-measurement-of-intent**. The proof validates the measurement chain. The inference from measurement to intent is a probabilistic claim bounded by the limitations in Section 2.

---

## 4. Attester Role Under RFC 9334

### 4.1 Composite Device Model (§3.3)

A LICET wearable operates as a **Composite Attester** as defined in RFC 9334 §3.3. The composite device consists of:

| Sub-attester | Environment | Produces |
|---|---|---|
| Sensor layer | TEE or hardware secure element (where available) | Raw biometric measurements |
| Processing layer | Application environment | Derived features (RMSSD, HF power, Mahalanobis distance) |
| Crypto layer | Secure enclave / ZKP prover | Authorization bundle + proof |
| Identity layer | Attester credentials | Attestation cert chain (L2+) |

Each sub-attester produces Claims. The Composite Attester aggregates them into a single Evidence message. The trust level of the composite is bounded by the weakest sub-attester in the chain.

### 4.2 Roles (RFC 9334 §4.1)

| Role | Entity | Notes |
|---|---|---|
| **Attester** | LICET wearable device | Produces Evidence about physiological state |
| **Verifier** | LICET Verifier service | Appraises Evidence against Endorsements and Reference Values |
| **Relying Party** | Authorization endpoint (app, door, transaction system) | Consumes Attestation Result; applies authorization policy |
| **Endorser** | Device manufacturer / NeuroTrust | Provides Endorsements (device cert, baseline parameters) |

### 4.3 Attestation Models

The LICET wearable supports both models defined in RFC 9334:

- **Passport Model (§5.1):** Verifier appraises Evidence and produces an Attestation Result token that the Relying Party consumes without re-verifying raw Evidence. Suitable for low-latency authorization flows.
- **Background-Check Model (§5.2):** Relying Party forwards Evidence to the Verifier at authorization time. Suitable for high-assurance flows where the Relying Party maintains its own appraisal policy.

---

## 5. Trust Hierarchy: L0–L3

Evidential weight follows attestation level. Higher levels require stronger attestation of the measurement environment and the credential chain.

### L0 — Uncertified Sensor

**What it is:** A consumer wearable with no hardware attestation, no secure element, no cert chain. The device reports measurements; there is no attestation of measurement integrity.

**Evidential weight:** Dimensionality. L0 contributes to the feature vector roughly what an inertial signal contributes — it adds a dimension that would cost an adversary something to match, but it does not resist a software-layer attack on the measurement chain.

**Claim supported:** "A device reported a measurement consistent with the claimed physiological state at the claimed time." The inference chain from measurement to intent is entirely dependent on the Relying Party's trust in the device model.

**ZKP scope:** None, or software-only hash chain. The proof does not attest to the measurement environment.

### L1 — Software Attestation

**What it is:** The measurement software runs in an attested execution environment (e.g., Android StrongBox, iOS Secure Enclave application). The device produces a Platform Attestation Result that covers the measurement software.

**Evidential weight:** The measurement software is covered by a hardware root of trust, but the sensors themselves are not attested. A hardware attack on the sensor output is not detected.

**Claim supported:** "Attested software on an attested platform reported a measurement consistent with the claimed physiological state." Software-layer forgery is detected; hardware-layer forgery is not.

### L2 — Certified Device with Attestation Chain

**What it is:** A device with a manufacturer cert chain that someone can actually verify. The Attester credential includes an x.509 cert chain rooted at an Endorser trusted by the Verifier. Evidence messages are signed with the Attester's private key; the chain is verifiable at appraisal time.

**Evidential weight:** This is where it starts carrying its own weight. A Verifier can confirm:
- Device identity (manufacturer-issued cert, not self-signed)
- Platform integrity (Platform Attestation Result over firmware)
- Key provenance (Attester key generated in and bound to secure element)

**Claim supported:** "A certified device with a verifiable attestation chain reported a measurement consistent with the claimed physiological state." An adversary that cannot compromise the secure element cannot forge the Evidence message.

**ZKP scope:** The ZKP is generated over measurements produced by an attested device. The proof validates the measurement chain up to the secure element boundary.

### L3 — Hardware-Attested Sensor

**What it is:** Sensor-level hardware attestation. The sensor output itself is signed or bound to the secure element at the hardware layer, not just the software layer. This requires device designs that bring the analog-to-digital conversion within the hardware trust boundary.

**Evidential weight:** The full chain — from analog biometric signal to ZKP — is covered by hardware attestation. This is the regime where LICET makes its strongest claim.

**Claim supported:** "A hardware-attested sensor on a certified device produced a measurement consistent with the claimed physiological state, with the measurement chain attested to the silicon boundary."

**Note:** No commercially available consumer wearable currently meets L3 as defined here. L3 is the target architecture for NeuroTrust's hardware program. Current deployments operate at L0 (simulation) or L1 (platform attestation via mobile OS).

---

## 6. Appraisal Logic

### 6.1 Evidence Appraisal by Level

The Verifier appraises Evidence packets according to the trust level of the Attester that produced them. Appraisal policy must be explicit about the minimum acceptable level:

```
if attester_level < L2:
    attestation_result.trust_tier = "corroborating"
    attestation_result.weight = "low"
else:
    attestation_result.trust_tier = "evidential"
    attestation_result.weight = "standard"
```

Relying Party policy translates trust tier into authorization decisions. A high-assurance Relying Party (e.g., medical consent, high-value transaction) SHOULD require L2 minimum.

### 6.2 Limitation Flags in Attestation Results

The following limitation flags MUST be surfaced in the Attestation Result when present:

| Flag | Source | Meaning |
|---|---|---|
| `respiratory_periodicity_warning` | Respiratory periodicity layer | Detected paced breathing pattern; Mahalanobis distance may not reflect genuine calm |
| `t2_self_report_only` | Attestation level check | T2 evidence present without corroborating T3/T4; weight is self-report only |
| `baseline_immature` | Baseline maturity check | Baseline built from < minimum session count; Mahalanobis reference is provisional |
| `sensor_uncertified` | Attester level check | L0 or L1 device; measurement chain is not hardware-attested |

### 6.3 ZKP Scope Statement

Every Evidence message that includes a ZKP MUST include a `zkp-scope` claim that states explicitly what the proof covers:

```
zkp-scope: {
  proves: ["measurement_chain_integrity", "mahalanobis_range", "timestamp"],
  does_not_prove: ["intent", "absence_of_coercion", "absence_of_volitional_vagal_enhancement"]
}
```

This is not optional. A Relying Party that receives a ZKP without a `zkp-scope` claim MUST treat the proof as covering measurement chain integrity only and MUST NOT infer absence of coercion.

---

## 7. Trust Hierarchy Summary

| Level | Sensor attestation | Device cert chain | ZKP scope | Evidential weight |
|---|---|---|---|---|
| L0 | None | None | None / software hash | Dimensionality only |
| L1 | Software | Self-signed or none | Platform-attested software | Software-layer forgery resistance |
| L2 | Software | Verifiable chain (x.509) | Attested device + software | Independent evidential weight |
| L3 | Hardware | Verifiable chain | Silicon-boundary attestation | Strongest available claim |

### 7.1 Relationship to CPoE T1–T4 Tiers

The CPoE evidence-packet schema defines a T1–T4 signal-type hierarchy. LICET L0–L3 is an orthogonal attestation-quality hierarchy: L0–L3 describes the trustworthiness of the measurement chain; T1–T4 describes the type of signal being measured. Both hierarchies appear in the same Evidence packet and MUST NOT be conflated.

Approximate correspondence:

| LICET level | Signal type (CPoE tier) | Basis |
|---|---|---|
| L0 | T1 / T2 | Uncertified sensor; dimensionality comparable to behavioral (T1) or inertial (T2) |
| L1 | T2 / T3 | Platform-attested software; physiological signal with software-layer guarantee |
| L2 | T3 | Certified device; physiological signal with verifiable hardware-backed chain |
| L3 | T3 / T4 | Hardware-attested sensor; physiological signal attested to silicon boundary |

The lower of (attestation level, signal type tier) governs the Attestation Result.

---

## 8. Evidence Encoding (Deferred)

Evidence encoding will be defined in a subsequent revision once the topology and appraisal logic in Sections 4–7 have been reviewed and stabilized.

The encoding will use the CBOR evidence-packet schema (CBOR tag 1129336645) defined in the proof-of-effort CPoE specification. No new schema will be defined here; LICET Evidence messages will conform to the existing evidence-packet structure with LICET-specific claim keys registered as extensions.

The rationale for deferral: fixing the encoding before the L0–L3 chain is stable risks recutting CDDL each time the trust model shifts. Topology and appraisal logic are established first; encoding follows.

---

## 9. Open Questions for Review

These items are flagged for David Condrey's review of the topology and appraisal logic:

1. **L2 cert chain:** Should the Endorser role be filled by NeuroTrust alone, or should the spec support a multi-endorser model (manufacturer + NeuroTrust + Relying Party)?
2. **Composite Attester boundary:** Is the current sub-attester breakdown in §4.1 the right granularity, or should the sensor layer and processing layer be a single sub-attester?
3. **Limitation flags in Attestation Results:** Are the four flags in §6.2 the right set, or are there additional flags the appraisal logic should surface?
4. **ZKP scope claim:** Is the `zkp-scope` structure in §6.3 the right format for the evidence-packet schema, or should it map to existing CPoE claim keys?
5. **L3 definition:** Is "analog-to-digital conversion within the hardware trust boundary" the right criterion for L3, or should L3 be defined differently in the context of RFC 9334?

---

## References

- RFC 9334 — RATS Architecture: https://datatracker.ietf.org/doc/rfc9334/
- RFC 9711 — Entity Attestation Token (EAT): https://datatracker.ietf.org/doc/rfc9711/
- draft-richardson-rats-composite-attesters: https://datatracker.ietf.org/doc/draft-richardson-rats-composite-attesters/
- draft-pereira-licet-human-intent-01: https://datatracker.ietf.org/doc/draft-pereira-licet-human-intent/
- LF-Decentralized-Trust-labs/proof-of-effort: https://github.com/LF-Decentralized-Trust-labs/proof-of-effort
- Laborde, S. et al. (2022). Psychophysiological effects of slow-paced breathing. Psychophysiology. DOI: 10.1111/psyp.13952
- Moak, J.P. et al. (2007). Supine LF power reflects baroreflex function. Heart Rhythm. PMC2204059
