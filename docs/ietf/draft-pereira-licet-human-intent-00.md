---
title: "LICET: A Cryptographic Protocol for Physiological Human-Intent Verification in Autonomous AI Agent Authorization"
abbrev: "LICET Human Intent Protocol"
category: info

docname: draft-pereira-licet-human-intent-00
submissiontype: IETF
number:
date: 2026-06-29
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

--- abstract

Autonomous AI agents executing consequential actions in high-stakes
domains — medical prescribing, financial transactions, critical
infrastructure control — require authorization mechanisms that go
beyond classical identity verification. Existing mechanisms (passwords,
static biometrics, digital signatures) verify *who* authorized an
action but cannot verify *whether the authorizing human was genuinely
conscious, uncoerced, and cognitively capable* at the moment of
authorization.

This document specifies LICET (Latin: *it is permitted*), a
cryptographic middleware protocol that binds AI agent authorization
events to the real-time physiological state of the authorizing human.
LICET defines: (1) a biometric capture and coercion-detection
procedure using wearable sensor data; (2) per-event session-key
derivation using HKDF {{RFC5869}}; (3) a biometric temporal signature
using HMAC {{RFC2104}}; (4) a Schnorr zero-knowledge proof over the
BN128 elliptic curve enabling third-party audit without biometric data
exposure; and (5) a SHA-256 hash-chained ledger for tamper-evident
authorization records.

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

| Mechanism | Identity | Liveness | Coercion-free | Cognitively intact |
|---|:---:|:---:|:---:|:---:|
| Password | ~ | N | N | N |
| Static biometric | Y | Y | N | N |
| FIDO2 / passkey | Y | Y | N | N |
| Digital signature | Y | N | N | N |
| LICET | Y | Y | Y | Y |

This gap is the *intent gap* — the absence of a cryptographically
verifiable mechanism to attest that a human was genuinely capable of
and free to form the intent they expressed.

## Motivation

The EU AI Act {{EUAIACT}} mandates human oversight for high-risk AI
systems (Article 14) but specifies no technical standard for what
constitutes verifiable human oversight. LICET provides the technical
substrate for this regulatory requirement.

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

# Protocol Overview

The LICET authorization protocol proceeds as follows:

1. **Request.** Agent A submits an authorization request to LICET
   Server S specifying: action descriptor (a), agent identifier
   (id_A), target entity (tgt), and Unix timestamp (ts).

2. **Biometric Capture.** Server S instructs Wearable W to capture
   physiological data over a window t_c (default: 10 seconds):
   heart rate (f_HR), peripheral oxygen saturation (s_O2), and
   heart rate variability (v_HRV).

3. **Coercion Detection.** Server S evaluates the captured signals
   according to Section 4. If Coercion Risk is MEDIUM or HIGH, or
   cognitive impairment is detected, authorization MUST be denied.

4. **Intent Hash Generation.** Server S computes:

        h = SHA-256(a || id_A || tgt || ts)

5. **Session Key Derivation.** Server S derives a per-event session
   key using HKDF {{RFC5869}}:

        k_s = HKDF-SHA256(k_m, h)

   where k_m is the master key held by S.

6. **Biometric Signature.** Server S computes:

        σ = HMAC-SHA256(h || f_HR || s_O2 || v_HRV || ts, k_s)

7. **Zero-Knowledge Proof.** Server S generates a Schnorr proof π
   over BN128 as specified in Section 5.

8. **Ledger Append.** Server S appends an entry to the hash-chained
   ledger as specified in Section 6.

9. **Authorization Token.** Server S returns to Agent A: intent
   hash h, biometric signature σ, ZKP proof π, ledger record
   identifier, and timestamp.

# Biometric Capture and Coercion Detection {#coercion}

## Biometric Sources

LICET MUST accept biometric input from any of the following sources:

- BLE GATT Heart Rate Profile (IEEE 11073)
- Android Health Connect API
- Apple HealthKit
- Direct I2C sensor integration (e.g., MAX30102)
- Software simulation (development environments only)

## Captured Signals

Three signals MUST be captured over window t_c:

- **f_HR**: Heart rate in beats per minute (BPM)
- **s_O2**: Peripheral oxygen saturation in percent (%)
- **v_HRV**: Root mean square of successive differences (RMSSD)
  of inter-beat intervals in milliseconds (ms)

## Coercion Detection Function

The coercion detection function C maps physiological signals to a
risk level:

        C(f_HR, v_HRV) =
          HIGH    if f_HR > 130 AND v_HRV < 20
          MEDIUM  if f_HR > 100 AND v_HRV < 35
          LOW     otherwise

**Physiological basis.** Under acute psychological coercion, the
sympathetic branch of the autonomic nervous system simultaneously
elevates heart rate and suppresses HRV {{THAYER2012}}. This dual-axis
collapse distinguishes coercion from aerobic exercise, where HRV may
be maintained or recover rapidly.

## Cognitive Impairment Detection

        I(s_O2) =
          IMPAIRED  if s_O2 < 90
          NORMAL    otherwise

## Authorization Decision

Authorization MUST be denied if:

- C(f_HR, v_HRV) is MEDIUM or HIGH, OR
- I(s_O2) is IMPAIRED, OR
- Captured signals are outside valid sensor ranges, OR
- Capture window t_c produces insufficient data points

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
          "capture_seconds": integer (default: 10)
        }

## Authorization Response

        {
          "authorized":          boolean,
          "intent_hash":         hex string,
          "biometric_signature": hex string,
          "coercion_risk":       "LOW" | "MEDIUM" | "HIGH",
          "cognitive_state":     "NORMAL" | "IMPAIRED",
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

# Security Considerations {#security}

## Replay Attack Prevention

Each authorization event produces a unique intent hash h binding
the action, agent identifier, target, and timestamp. An authorization
token for action a at time ts is cryptographically invalid for any
other action or time. Implementations MUST reject authorization
requests with timestamps outside a configurable window
(RECOMMENDED: 60 seconds).

## Coercion Detection Limitations

The concurrent HR/HRV threshold described in Section 4 is a
statistical, not absolute, protection. Population-level thresholds
may produce false positives for individuals with baseline tachycardia
or false negatives for highly trained individuals. Future versions
of this protocol SHOULD define a personalized baseline calibration
procedure.

## Consumer Hardware Accuracy

Wrist-based photoplethysmography (PPG) provides HR and SpO2
estimates adequate for the detection thresholds defined in this
document. Clinical deployments SHOULD require medically certified
sensor hardware.

## Physiological Spoofing

An adversary with pharmacological knowledge could potentially
manipulate physiological signals to bypass coercion detection.
Multi-modal liveness verification (NFC document verification, facial
liveness detection) is RECOMMENDED for high-criticality deployments
and is designated for a future version of this protocol.

## Master Key Compromise

Compromise of the master key k_m exposes all session keys computable
from it. Implementations MUST protect k_m using hardware security
modules or equivalent mechanisms. Key rotation procedures MUST be
defined by the deployment.

## Biometric Privacy

Raw biometric values MUST NOT be stored in the ledger. The ZKP
mechanism defined in Section 5 ensures that auditors can verify
authorization validity without accessing biometric data, satisfying
the data minimization principle of privacy regulations including
{{LGPD}} and GDPR.

# IANA Considerations

This document has no IANA actions at this time.

Future versions of this protocol may request registration of:

- A media type for LICET authorization tokens
- An OAuth 2.0 token type for LICET tokens {{RFC7519}}
- A well-known URI for LICET discovery

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
blockchain-based audit trails.
