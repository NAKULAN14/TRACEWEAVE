# TRACEWEAVE Phase 9E.4 — Recovery Capability Matrix

## Objective

Map parser-failed malformed ICS artifacts to the recovery capability
required to reconstruct and validate the artifact.

| Case | Failure Class | Required Capability | Current Status | Priority |
|---|---|---|---|---|
| TW-ICS-003 | Property/folding corruption | Recover malformed content-line folding and property boundaries | PARTIAL | HIGH |
| TW-ICS-004 | Missing VCALENDAR BEGIN | Reconstruct missing outer VCALENDAR boundary | MISSING/PARTIAL | HIGH |
| TW-ICS-009 | Severe structural/encoding corruption | Recover encoding and structural boundaries from raw bytes | MISSING | HIGH |
| TW-ICS-015 | Truncated artifact | Reconstruct missing closing component/calendar boundaries when safe | MISSING/PARTIAL | HIGH |
| TW-ICS-016 | Severe truncation + corrupted component declaration | Detect/reconstruct damaged component boundary when sufficient evidence exists | MISSING | MEDIUM |

---

## Capability A — Property/Folding Recovery

Target:
TW-ICS-003

Requirements:

1. Preserve leading whitespace during raw inspection.
2. Detect continuation/folding lines.
3. Detect broken property boundaries.
4. Reconstruct logically continuous property values.
5. Preserve the original artifact.
6. Record every transformation.
7. Validate the reconstructed artifact with the standard parser.

Expected result:

Corrupted ICS
→ structural analysis
→ property/folding reconstruction
→ recovered ICS
→ standard parser SUCCESS

---

## Capability B — Container Boundary Recovery

Target:
TW-ICS-004

Requirements:

1. Detect missing BEGIN:VCALENDAR.
2. Confirm END:VCALENDAR exists.
3. Determine whether the remaining structure is consistent with
   a VCALENDAR.
4. Add the missing boundary only when evidence supports it.
5. Record the transformation.
6. Validate using the standard parser.

Expected transformation:

VERSION:2.0
...
END:VCALENDAR

→

BEGIN:VCALENDAR
VERSION:2.0
...
END:VCALENDAR

---

## Capability C — Severe Structural/Encoding Recovery

Target:
TW-ICS-009

Requirements:

1. Inspect raw bytes before decoding.
2. Detect encoding anomalies.
3. Preserve undecodable bytes.
4. Identify possible BEGIN/END markers.
5. Reconstruct structural boundaries only when confidence is sufficient.
6. Never silently discard bytes.
7. Record the original hash and recovered hash.
8. Record all transformations.
9. Validate the recovered artifact.

Expected result:

Raw bytes
→ encoding analysis
→ structural reconstruction
→ recovered artifact
→ parser validation

---

## Capability D — Truncation Recovery

Target:
TW-ICS-015

Requirements:

1. Detect incomplete artifact.
2. Identify the last complete component.
3. Determine missing END:VEVENT / END:VCALENDAR boundaries.
4. Reconstruct only boundaries supported by evidence.
5. Mark the recovery as inferred.
6. Record confidence.
7. Validate the recovered artifact.

Important:

A truncated artifact must not be treated as fully recovered merely
because artificial closing tags allow a parser to accept it.

---

## Capability E — Severe Truncation / Component Boundary Recovery

Target:
TW-ICS-016

Requirements:

1. Detect incomplete component declaration.
2. Determine whether the corrupted declaration can be reconstructed
   with sufficient evidence.
3. If evidence is insufficient, preserve the failure rather than
   inventing structure.
4. Record the reason for failure.
5. Return an explicit confidence/status value.

Expected behaviour:

Recoverable:
→ reconstruct
→ validate
→ SUCCESS

Not safely recoverable:
→ preserve original
→ RECOVERY_FAILED
→ explain why