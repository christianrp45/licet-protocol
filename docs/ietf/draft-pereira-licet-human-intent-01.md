---
title: "LICET: Multi-Modal Physiological Human-Intent Verification for Autonomous AI Agent Authorization"
abbrev: "LICET Human Intent Protocol"
category: info

docname: draft-pereira-licet-human-intent-01
submissiontype: IETF
number:
date: 2026-07-02
consensus: false
v: 3

area: Security
workgroup: Individual Submission

keyword:
 - AI safety
 - human oversight
 - biometric authorization
 - zero-knowledge proof
 - autonomous agents
 - coercion detection
 - heart rate variability
 - electrodermal activity
 - composite attester
 - RATS
 - coercion resistance

author:
 -
    fullname: Christian Rodrigues Pereira
    organization: eColabs Desenvolvimento de Pessoas e Organizações LTDA.
    country: Brazil
    email: contato@ecolabs.com.br
    uri: https://licet.dev

normative:
  RFC2119:
  RFC8174:
  RFC5869:
  RFC2104:

informative:
  RFC6962:
  RFC7519:
  RFC9334:
    title: "Remote ATtestation procedureS (RATS) Architecture"
    author:
      org: IETF
    date: 2023
  RFC8610:
    title: "Concise Data Definition Language (CDDL): A Notational Convention to Express Concise Binary Object Representation (CBOR) and JSON Data Structures"
    author:
      org: IETF
    date: 2019
  SSRN7018458:
    title: "LICET: A Biometric Intent Authorization Protocol for Autonomous AI Agents"
    author:
      name: Christian Rodrigues Pereira
    date: 2026-06-29
    target: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7018458
  EUAIACT:
    title: "Regulation (EU) 2024/1689 on Artificial Intelligence (EU AI Act)"
    author:
      org: European Parliament
    date: 2024
  LGPD:
    title: "Lei Geral de Proteção de Dados Pessoais (Lei 13.709/2018)"
    author:
      org: Brazil
    date: 2018
  FIAT1987:
    title: "How to Prove Yourself: Practical Solutions to Identification and Signature Problems"
    author:
      - name: Amos Fiat
      - name: Adi Shamir
    date: 1987
    seriesinfo:
      "CRYPTO '86": "LNCS vol. 263, pp. 186-194"
  THAYER2012:
    title: "A meta-analysis of heart rate variability and neuroimaging studies"
    author:
      - name: Julian F. Thayer
    date: 2012
    seriesinfo:
      "Neuroscience & Biobehavioral Reviews": "36(2):747-756"
  WESAD2018:
    title: "Introducing WESAD, a Multimodal Dataset for Wearable Stress and Affect Detection"
    author:
      - name: Philip Schmidt
    date: 2018
    seriesinfo:
      "ACM ICMI 2018": "Proceedings of the 20th ACM International Conference on Multimodal Interaction"
  FOWLES1986:
    title: "The eccrine system and electrodermal activity"
    author:
      - name: Don C. Fowles
    date: 1986
    seriesinfo:
      "Psychophysiology": "Handbook of Psychophysiology, pp. 51-96"
  BRANTIGAN1982:
    title: "Effect of beta blockade and beta stimulation on stage fright"
    author:
      - name: C. O. Brantigan
    date: 1982
    seriesinfo:
      "Am J Med": "72(1):88-94"
  LAKIE2019:
    title: "Physiological tremor"
    author:
      - name: Martin Lakie
    date: 1994
    seriesinfo:
      "J Neurol Neurosurg Psychiatry": "57(Suppl):56-60"

--- abstract

Autonomous AI agents executing consequential actions require authorization
mechanisms that verify not only identity but voluntary intent. Existing
mechanisms verify *who* authorized an action; they cannot verify *whether
the authorizing human was uncoerced and cognitively capable* at the moment
of authorization.

This document specifies LICET (Latin: *it is permitted*), a cryptographic
middleware protocol binding AI agent authorization to real-time multi-modal
physiological state via a three-layer architecture: (1) ECG waveform
morphology matching as a medication-resistant identity and liveness anchor;
(2) electrodermal activity (EDA) as a sympathetic cholinergic liveness signal
immune to beta-adrenergic blockade; and (3) personalized Mahalanobis distance
fusion over five physiological signals to elevate the cost of pharmacological
coercion attacks rather than claim binary detection.

LICET defines a Biometric Trust Level hierarchy (L0-L3) aligned with the
IETF RATS architecture (RFC 9334), a baseline calibration protocol
establishing individual physiological profiles, per-event HKDF session-key
derivation, HMAC biometric temporal signatures, Schnorr zero-knowledge proofs
over BN128 enabling third-party audit without biometric exposure, and a
SHA-256 hash-chained tamper-evident ledger.

A reference implementation is publicly deployed at
https://licet.dev/v1/ and available as open source at
https://github.com/christianrp45/licet-protocol.

--- middle

# Introduction

Artificial intelligence agents are transitioning from passive tools to
autonomous actors capable of executing actions with real, irreversible
consequences. A medical AI agent may adjust medication dosages. A
financial AI may execute wire transfers. An infrastructure AI may
modify power-grid parameters. In each case, the assumed safeguard is
human authorization.

## The Intent Gap

Contemporary authorization primitives are designed to answer one
question: *is this person who they claim to be?* They are silent on a
second, equally critical question: *is this person currently in a
state that constitutes genuinely free, conscious, and cognitively
competent intent?*

The following table contrasts existing mechanisms against the
authorization properties required for high-stakes AI agent actions:

| Mechanism | Identity | Liveness | Coercion-free | Cognitively intact | Drug-resistant |
|---|:---:|:---:|:---:|:---:|:---:|
| Password | ~ | N | N | N | N |
| Static biometric | Y | Y | N | N | N |
| FIDO2 / passkey | Y | Y | N | N | N |
| Digital signature | Y | N | N | N | N |
| LICET | Y | Y | Y | Y | Y |

This gap is the *intent gap* — the absence of a cryptographically
verifiable mechanism to attest that a human was genuinely capable of
and free to form the intent they expressed.

## Motivation

The EU AI Act {{EUAIACT}} mandates human oversight capability for high-risk
AI systems (Articles 9, 12, and 26(5)). Article 9 requires risk management
systems. Article 12 requires logging sufficient to assess compliance.
Article 26(5) requires deployers to ensure human oversight capability.
LICET provides the technical substrate for these operational requirements.

## Relationship to RATS Architecture

LICET maps onto the IETF RATS architecture (RFC 9334 {{RFC9334}}). In LICET
deployments, the wearable device acts as a Sub-Attester, the mobile
application acts as Lead Attester, and the LICET Server acts as Verifier.
This Composite Attester topology (RFC 9334 Section 3.1.4) is not fully
specified in this document; a separate specification defining the wearable
Sub-Attester role and its chain of trust is designated as a future work
item (see Section 10).

## Conventions and Definitions

{::boilerplate bcp14-tagged}

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT",
"SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and
"OPTIONAL" in this document are to be interpreted as described in
BCP 14 {{RFC2119}} {{RFC8174}}.

**Authorizer (H):** The human whose physiological state and intent
are being verified.

**Agent (A):** An autonomous AI system requesting authorization to
perform an action.

**LICET Server (S):** The server that holds the master secret key and
executes the protocol logic.

**Auditor (V):** Any third party who may later verify that a valid
authorization occurred, without accessing biometric data.

**Wearable (W):** A biometric sensing device worn by the Authorizer.

**Intent Hash (h):** A cryptographic binding of an action request to
a specific moment in time.

**Biometric Signature (σ):** An HMAC commitment of biometric state
to the intent hash.

**Coercion Risk:** A categorical assessment (LOW, MEDIUM, HIGH) of
the probability that the Authorizer is under duress.

# Three-Layer Architecture {#layers}

LICET authorization requires evidence from three independent physiological
layers. Each layer addresses a distinct attack surface.

## Layer 1: ECG Identity and Liveness Anchor {#layer1}

Electrocardiogram (ECG) waveform morphology — specifically QRS complex shape
and PR/QT interval ratios — is anatomically determined by cardiac geometry
and conduction pathway structure. These features are stable across sessions
for the same individual and distinct across individuals.

LICET uses ECG morphology as a medication-resistant identity anchor. The
cosine similarity between the session ECG feature vector and the enrolled
baseline is computed:

        rho_ECG = cosine_similarity(f(ecg_session), f(ecg_enrolled))

where f() denotes the ECG feature extraction function producing a normalized
vector of QRS morphological features.

Authorization requires rho_ECG >= theta_ECG (RECOMMENDED: 0.85).

**Drug resistance:** Beta-blockers lengthen PR interval but do not alter
QRS morphology. No common medication class changes ECG morphology
sufficiently to defeat morphology-based matching at this threshold.

**Platform support:** Apple Watch Series 4+ via HealthKit HKElectrocardiogram
(512 Hz sampling). Other ECG-capable wearables MAY be used if equivalent
sampling rate and feature extraction are demonstrated.

## Layer 2: EDA Liveness Signal {#layer2}

Electrodermal activity (EDA) — comprising skin conductance level (SCL) and
skin conductance responses (SCR) — is mediated by sympathetic cholinergic
innervation of eccrine sweat glands. Because the efferent pathway is
cholinergic (not adrenergic), EDA is immune to beta-adrenergic blockade
{{FOWLES1986}}.

EDA serves as the liveness signal in LICET: the presence of EDA activity
confirms a biological subject is present and physiologically active.

Authorization requires:

        z_EDA_SCL = (SCL_session - mu_SCL) / sigma_SCL > theta_EDA

where mu_SCL and sigma_SCL are derived from the individual's baseline
(Section 9).

**Platform support:** WHOOP 5 (continuous EDA); Samsung Galaxy Watch 7
(spot-check mode). EDA is not available on Apple Watch or most consumer
wearables. Deployments without EDA-capable hardware operate at reduced
liveness assurance (see Section 8).

## Layer 3: Mahalanobis Fusion {#layer3}

Layer 3 replaces population-level threshold comparison with a personalized
multivariate distance measure. The Mahalanobis distance computes how many
standard deviations the current session's signal vector lies from the
individual's enrolled calm-state baseline:

        D_M = sqrt((z - mu_calm)^T * S^{-1} * (z - mu_calm))

where z is the vector of per-signal z-scores:

        z_i = (x_i - mu_i^B) / sigma_i^B

with mu_i^B and sigma_i^B derived from the individual's baseline (Section 9),
and S is the covariance matrix of baseline z-scores.

The five-signal fusion vector is:

        z = [z_RMSSD, z_EDA_SCL, z_EDA_SCR, z_TEMP, z_TREMOR]

where:

- z_RMSSD: RMSSD heart rate variability z-score
- z_EDA_SCL: skin conductance level z-score
- z_EDA_SCR: skin conductance response rate z-score
- z_TEMP: skin temperature delta from resting baseline z-score
- z_TREMOR: 8-12 Hz physiological tremor power z-score {{LAKIE2019}}

Authorization requires D_M <= theta_DM (RECOMMENDED: 2.5).

**Note on coercion cost elevation:** Layer 3 does not claim to detect
coercion with certainty. It elevates the cost of pharmacological attacks
by requiring that an adversary simultaneously manipulate five independent
physiological signals to remain within the individual's personal baseline
distribution. Each additional signal exponentially increases the required
pharmacological complexity.

## Pharmacological Attack Detection {#pharma}

Three pharmacological attack patterns produce detectable signal combinations
in the fused space:

Beta-blocker attack (propranolol, metoprolol):

        DETECTED if: z_TREMOR < -2.0 AND delta_HR_baseline > 15%

Note: beta-blockers do NOT suppress RMSSD. Propranolol blocks sympathetic
(adrenergic) innervation; RMSSD reflects parasympathetic (vagal) withdrawal
under acute stress, which persists under beta-blockade {{BRANTIGAN1982}}.
The tremor suppression signal (z_TREMOR < -2.0) combined with elevated
baseline-relative HR is the detection indicator.

Anticholinergic attack (atropine, scopolamine):

        DETECTED if: z_EDA_SCL < -1.5 AND z_RMSSD > +1.0 AND delta_TEMP > 0

This pattern (EDA flat, HRV paradoxically elevated, skin warm) is the
pharmacological inverse of the coercion signature and is detectable as
a distinct toxidrome.

Opioid attack (fentanyl, morphine):

        DETECTED if: z_RESP < -2.0 AND delta_TEMP > 0 AND z_RMSSD < 0

Detection of any pharmacological attack pattern MUST result in
authorization denial with reason code PHARMACOLOGICAL_ANOMALY.

# Protocol Overview

The LICET authorization protocol proceeds as follows:

1. **Request.** Agent A submits an authorization request to LICET
   Server S specifying: action descriptor (a), agent identifier
   (id_A), target entity (tgt), and Unix timestamp (ts).

2. **Biometric Capture.** Server S instructs Wearable W to capture
   physiological data over a minimum window t_c of 60 seconds. RMSSD
   computation requires a minimum of 60 seconds of inter-beat interval
   data to achieve acceptable statistical reliability.

3. **Three-Layer Evaluation.** Server S evaluates the captured signals
   according to Sections 3 and 5. If any layer fails, or cognitive
   impairment is detected, authorization MUST be denied with the
   appropriate reason code.

4. **Intent Hash Generation.** Server S computes:

        h = SHA-256(a || id_A || tgt || ts)

5. **Session Key Derivation.** Server S derives a per-event session
   key using HKDF {{RFC5869}}:

        k_s = HKDF-SHA256(k_m, h)

   where k_m is the master key held by S.

6. **Biometric Signature.** Server S computes:

        σ = HMAC-SHA256(h || f_HR || s_O2 || v_RMSSD || ts, k_s)

7. **Zero-Knowledge Proof.** Server S generates a Schnorr proof π
   over BN128 as specified in Section 6.

8. **Ledger Append.** Server S appends an entry to the hash-chained
   ledger as specified in Section 7.

9. **Authorization Token.** Server S returns to Agent A: intent
   hash h, biometric signature σ, ZKP proof π, ledger record
   identifier, and timestamp.

# Biometric Capture {#biometric}

## Biometric Sources

LICET MUST accept biometric input from hardware meeting the trust level
requirements defined in Section 8. The minimum capture window is 60 seconds.

Supported source types:

- ECG: Apple Watch Series 4+ (HealthKit HKElectrocardiogram, 512 Hz)
- EDA: WHOOP 5 (continuous); Samsung Galaxy Watch 7 (spot-check)
- HR/HRV: Any BLE GATT Heart Rate Profile device (IEEE 11073)
- HR/HRV: Android Health Connect API; Apple HealthKit
- Direct I2C sensor integration (e.g., MAX30102 for HR/SpO2)
- Software simulation (development environments only; trust level L0)

## Captured Signals

The following signals MUST be captured where hardware supports them:

- **f_HR**: Heart rate (BPM) — required
- **v_RMSSD**: RMSSD of RR intervals (ms) — required; minimum 60s window
- **s_O2**: Peripheral oxygen saturation (%) — required
- **v_EDA_SCL**: Skin conductance level (microsiemens) — required for L2+
- **v_EDA_SCR**: Skin conductance response rate (events/min) — required for L2+
- **v_TEMP**: Skin temperature delta from resting baseline (°C) — RECOMMENDED
- **v_TREMOR**: 8-12 Hz accelerometer power (m/s²) — RECOMMENDED
- **v_RESP**: Respiratory rate (breaths/min) — RECOMMENDED

## Layer Execution

The three layers defined in Section 3 MUST be executed in order:

1. Layer 1 (ECG identity): if rho_ECG < theta_ECG, DENY with IDENTITY_MISMATCH
2. Layer 2 (EDA liveness): if z_EDA_SCL <= theta_EDA, DENY with LIVENESS_FAILED
   (if EDA hardware unavailable, log LIVENESS_UNVERIFIED and continue at reduced assurance)
3. Pharmacological pattern check (Section 3.4): if any pattern detected, DENY with PHARMACOLOGICAL_ANOMALY
4. Layer 3 (Mahalanobis fusion): if D_M > theta_DM, DENY with STATE_ANOMALY

## SpO2 Cognitive Impairment Check

        I(s_O2) = IMPAIRED if s_O2 < 90%, NORMAL otherwise

Authorization MUST be denied if I(s_O2) = IMPAIRED with reason COGNITIVE_IMPAIRMENT.

# Intent Hash and Cryptographic Binding {#crypto}

## Intent Hash

The intent hash uniquely identifies the requested action:

        h = SHA-256(a || id_A || tgt || ts)

where || denotes concatenation, a is the UTF-8 encoded action
descriptor, id_A is the UTF-8 encoded agent identifier, tgt is the
UTF-8 encoded target entity, and ts is the Unix timestamp encoded
as a 64-bit big-endian integer.

The intent hash is the cryptographic anchor binding the biometric
authorization to a specific action at a specific time.

## Session Key Derivation

A per-event session key SHALL be derived using HKDF {{RFC5869}}:

        k_s = HKDF(hash=SHA-256, IKM=k_m, info=h, L=32)

where k_m is the server master key (minimum 256 bits, generated
using a cryptographically secure random number generator) and h
is the intent hash.

HKDF's extract step MAY use a salt; if omitted, HKDF uses a
zero-length salt as defined in {{RFC5869}} Section 2.2.

Session key isolation ensures that compromise of k_s for event i
does not expose k_s for any other event j, nor the master key k_m.

## Biometric Temporal Signature

        σ = HMAC-SHA256(h || f_HR || s_O2 || v_HRV || ts, k_s)

The biometric values f_HR, s_O2, v_HRV MUST be encoded as IEEE 754
double-precision (64-bit) big-endian floating-point values.

Properties:

- **Event-unique:** ts ensures no replay across distinct events.
- **Action-bound:** h is embedded; σ is cryptographically invalid
  for any action other than the one specified in h.
- **Non-invertible:** biometric values cannot be recovered from σ
  without k_s.

# Zero-Knowledge Proof {#zkp}

LICET uses a non-interactive Schnorr proof over the BN128 elliptic
curve with the Fiat-Shamir heuristic {{FIAT1987}}.

Let G be the BN128 generator point and q the group order.

## Proof Generation

1. Compute witness:

        w = SHA-256(σ || h) mod q

2. Compute public key:

        PK = w · G

3. Sample random nonce:

        r ← Z_q

4. Compute commitment:

        R = r · G

5. Compute challenge (Fiat-Shamir):

        c = SHA-256(R || PK || h) mod q

6. Compute response:

        s = (r - c · w) mod q

The proof is π = (R, c, s, PK).

## Proof Verification

Given π = (R, c, s, PK) and intent hash h, a verifier V computes:

        s · G + c · PK =?= R

AND verifies:

        c =?= SHA-256(R || PK || h) mod q

If both equalities hold, V is convinced that the prover possessed
knowledge of w — and therefore that a valid biometric signature
existed for this intent hash — without learning σ, f_HR, s_O2,
or v_HRV.

# Tamper-Evident Ledger {#ledger}

## Structure

Every authorization event MUST be appended to a hash-chained
ledger. Each entry contains:

- Sequential record identifier
- Intent hash h
- Authorization result (authorized: true/false)
- Coercion risk level
- Cognitive state
- ZKP proof π
- Unix timestamp

## Chaining

        L_0 = SHA-256(entry_0 || "LICET-GENESIS")
        L_n = SHA-256(entry_n || L_{n-1}),  n >= 1

Any retroactive modification to entry i invalidates L_i, L_{i+1},
..., L_n, making tampering mathematically detectable by any party
recomputing the chain.

## Integrity Verification

Implementations MUST provide a mechanism to verify the full hash
chain and return a boolean integrity result. This mechanism MUST
be publicly accessible without authentication.

# API Specification

Implementations SHOULD expose the following HTTP endpoints:

| Method | Path | Description |
|---|---|---|
| GET | /v1/health | Protocol liveness and mode |
| POST | /v1/authorize | Full biometric authorization |
| POST | /v1/biometric/push | Receive wearable data |
| POST | /v1/authorize/from-push | Authorize from push data |
| POST | /v1/verify | ZKP verification |
| GET | /v1/ledger/integrity | Chain integrity check |
| GET | /v1/ledger/history | Authorization history |

## Authorization Request

        POST /v1/authorize
        Content-Type: application/json

        {
          "action":          string,
          "agent_id":        string,
          "target":          string,
          "capture_seconds": integer (minimum: 60)
        }

## Authorization Response

        {
          "authorized":          boolean,
          "intent_hash":         hex string,
          "biometric_signature": hex string,
          "coercion_risk":       "LOW" | "MEDIUM" | "HIGH",
          "cognitive_state":     "NORMAL" | "IMPAIRED",
          "trust_level":         "L0" | "L1" | "L2" | "L3",
          "denial_reason":       string | null,
          "zkp_proof": {
            "commitment": { "x": string, "y": string },
            "challenge":  hex string,
            "response":   hex string,
            "public_key": { "x": string, "y": string }
          },
          "ledger_id":   integer,
          "timestamp":   number
        }

# Biometric Trust Levels {#trustlevels}

LICET defines four trust levels for wearable evidence, aligned with the
IETF RATS architecture (RFC 9334 {{RFC9334}}):

| Level | Name | Description | Example Hardware |
|---|---|---|---|
| L0 | No attestation | Software simulation; no hardware binding | Development only |
| L1 | Platform attestation | App-level attestation; OS-signed evidence | Consumer BLE + HealthKit/Health Connect |
| L2 | Hardware attestation | Device-rooted attestation key; third-party verifiable CA | Pixel Watch 2 + Titan M2 + Android Key Attestation |
| L3 | Sensor-to-TEE direct | Sensor measurement attested directly within TEE | Not yet available in consumer hardware |

Deployments MUST declare their trust level in the authorization response.
Verifiers and Relying Parties MUST NOT treat L0 or L1 physiological
evidence as proof of genuine measurement — these levels provide
dimensionality and raise attack complexity but do not constitute
hardware-rooted attestation.

L3 is specified as a future target. A separate specification defining the
wearable Sub-Attester role, its signing key establishment procedure, and
the chain-of-trust from sensor to Verifier is required before L3 can be
normatively specified.

## RATS Composite Attester Mapping

In LICET deployments following the RATS Composite Attester topology
(RFC 9334 Section 3.1.4):

- **Sub-Attester**: Wearable device (physiological signal source)
- **Lead Attester**: Mobile application (Evidence aggregator)
- **Verifier**: LICET Server
- **Endorser**: Hardware manufacturer (for L2: device attestation CA)
- **Relying Party**: AI agent or authorization system

This topology is informative only. Normative specification of the
Composite Attester profile for physiological wearable Attesters is
future work.

# Baseline Capture Protocol {#baseline}

The Mahalanobis distance computation (Section 3.3) requires an individual
physiological baseline. Implementations MUST collect baseline data before
enabling Layer 3 authorization.

## Baseline Requirements

- Minimum 5 sessions
- Minimum 3 minutes per session
- Sessions collected in calm resting state (no acute stress, no exercise
  within 30 minutes, no stimulant intake within 2 hours)
- Sessions distributed across at least 3 calendar days

## Baseline Data

For each session, compute and store:

- Per-signal mean (mu_i^B) and standard deviation (sigma_i^B) for all
  captured signals
- Covariance matrix S of z-scores across sessions
- Session timestamp and declared collection conditions

## Baseline Validity

Baselines expire after 30 days. Implementations MUST require re-calibration
after expiry.

Pre-medication anomaly detection: if resting HR deviates more than 15%
from baseline mean, or EDA SCL is below 50% of baseline mean, the
implementation SHOULD flag BASELINE_ANOMALY and require manual confirmation
before accepting the authorization.

## Baseline Security

Baseline data MUST be stored with integrity protection (e.g., HMAC under
a key separate from k_m). Baseline tampering MUST be treated as a security
event. The baseline is self-asserted by the Authorizer and MUST NOT be
treated as a trusted Reference Value in the RATS sense — it is
corroborative, not authoritative.

# Security Considerations {#security}

## Replay Attack Prevention

Each authorization event produces a unique intent hash h binding
the action, agent identifier, target, and timestamp. An authorization
token for action a at time ts is cryptographically invalid for any
other action or time. Implementations MUST reject authorization
requests with timestamps outside a configurable window
(RECOMMENDED: 60 seconds).

## Pharmacological Attack Resistance

LICET employs three mechanisms to raise the cost of pharmacological attacks:

1. **ECG morphology anchor (Layer 1):** No common medication class alters
   ECG QRS morphology sufficiently to defeat morphology-based identity
   matching. This layer is medication-resistant by anatomical constraint.

2. **EDA liveness (Layer 2):** EDA is mediated by sympathetic cholinergic
   (not adrenergic) innervation. Beta-adrenergic blockers (propranolol,
   metoprolol, atenolol) do not suppress EDA {{FOWLES1986}}.

3. **Mahalanobis fusion (Layer 3):** Personalized distance over five signals
   requires simultaneous manipulation of five independent physiological
   dimensions. Beta-blockers suppress tremor (detectable as z_TREMOR < -2.0)
   but do not suppress RMSSD — parasympathetic vagal withdrawal under acute
   stress persists under beta-blockade {{BRANTIGAN1982}}. Anticholinergic
   agents suppress EDA but produce an inverted toxidrome (elevated HRV, warm
   skin) detectable as a distinct pattern. No currently known pharmacological
   combination simultaneously defeats all five signals while remaining
   hemodynamically compatible with cognitive function.

LICET does not claim to make coercion impossible. It elevates the cost and
complexity of coercion attacks to a level that raises the probability of
detection through other channels (behavioral anomaly, medical supervision,
witness observation).

## Consumer Hardware Accuracy

Wrist-based photoplethysmography (PPG) provides HR and SpO2
estimates adequate for the detection thresholds defined in this
document. Clinical deployments SHOULD require medically certified
sensor hardware.

## Master Key Compromise

Compromise of the master key k_m exposes all session keys computable
from it. Implementations MUST protect k_m using hardware security
modules or equivalent mechanisms. Key rotation procedures MUST be
defined by the deployment.

## Biometric Privacy

Raw biometric values MUST NOT be stored in the ledger. The ZKP
mechanism defined in Section 6 ensures that auditors can verify
authorization validity without accessing biometric data, satisfying
the data minimization principle of privacy regulations including
{{LGPD}} and GDPR.

# IANA Considerations

This document has no IANA actions at this time.

Future versions of this protocol may request registration of:

- A media type for LICET authorization tokens
- An OAuth 2.0 token type for LICET tokens {{RFC7519}}
- A well-known URI for LICET discovery

# Open Research Problems {#openproblems}

The following problems are identified for future specification:

1. **L3 wearable attestation:** Specification of a sensor-to-TEE direct
   attestation mechanism for consumer wearable devices. Requires hardware
   vendor cooperation for signing key establishment and CA infrastructure.

2. **RATS Composite Attester profile:** Normative definition of the
   wearable Sub-Attester role, Evidence format, and Endorser requirements
   for physiological Attesters in the RATS architecture (RFC 9334).

3. **ECG feature extraction standardization:** Standardization of the
   feature vector f(ecg) to enable interoperability across wearable
   platforms.

4. **Baseline federation:** Secure transfer of baseline profiles across
   devices and deployments while preserving the self-asserted (non-trusted)
   nature of baseline data.

5. **EDA hardware coverage:** Extension of Layer 2 to hardware platforms
   beyond WHOOP 5 and Samsung Galaxy Watch 7, or definition of an
   equivalent liveness signal achievable on PPG-only hardware.

--- back

# Protocol Timestamp

The LICET protocol was first documented and registered on the Bitcoin
blockchain via OpenTimestamps on February 25, 2026. The SHA-256 hash
of the original protocol document is publicly archived as a tamper-
evident timestamp predating this Internet-Draft.

# Reference Implementation

A reference implementation of this protocol is publicly available:

- **Live API:** https://licet.dev/v1/
- **Source code:** https://github.com/christianrp45/licet-protocol
- **Preprint:** https://papers.ssrn.com/sol3/papers.cfm?abstract_id=7018458

# Acknowledgments
{:numbered="false"}

The author thanks the open-source communities behind FastAPI, py_ecc,
and OpenTimestamps. Protocol design was informed by prior work on
coercion-resistant authentication, affective computing, and
blockchain-based audit trails. The author thanks David Condrey (Linux
Foundation) for technical review identifying the attestation chain gap
and the need for a separate wearable Attester specification.
