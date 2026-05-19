# 03_decision_log.md

# Purpose

This document records intentional wording and behavioral decisions used in the operational calling script.

It exists to:

- preserve reasoning behind accepted phrasing,
- document rejected alternatives,
- reduce future wording regression,
- support reviewer and governance traceability,
- maintain conversational consistency across revisions.

---

# Scope

This log covers:

- conversational phrasing decisions,
- escalation/de-escalation wording,
- operational commitment boundaries,
- personalization logic,
- documented fallback handling decisions explicitly present in the script,
- customer autonomy preservation,
- risk-sensitive wording.

This document does NOT redefine the script itself.

---

# Decision Log Entries

---

## DL-001 — “Calling and informing” framing

### Accepted Wording

> “That’s why calling and informing.”

### Rejected Alternatives

Examples intentionally avoided:

- “We are reminding you”
- “You need to renew immediately”
- “Mandatory renewal notice”
- “Final warning”

### Reasoning

The accepted wording maintains an informational tone rather than an enforcement tone.

The script consistently positions the interaction as a reminder/information call instead of a compliance threat or aggressive sales conversion attempt.

---

## DL-002 — Avoiding operational overcommitment

### Accepted Wording

> “Okay, we’ll send on WhatsApp.”

### Rejected Alternatives

Examples intentionally avoided:

- “Sending now”
- “You’ll receive immediately”
- “We have already sent”
- “You will get it shortly”

### Reasoning

The script explicitly separates conversational acknowledgement from operational completion.

Operational execution is deferred into post-call follow-up tasks rather than implied as completed during the live conversation.

This aligns with the operational principle section.

---

## DL-003 — Controlled explanation for data source questions

### Scope Tags

- Fallback Handling
- Risk-Sensitive Wording

### Accepted Wording

Primary:

> “Registered number only, from earlier emission test entry.”

Fallback:

> “From the test registration records only.”

### Rejected Alternatives

Examples intentionally avoided:

- detailed database explanations,
- references to third-party sharing,
- references to government integrations,
- technical CRM explanations.

### Reasoning

The script intentionally limits explanation depth when customers ask how their number was obtained.

The wording provides minimal operational clarification while avoiding over-explanation.

### Related Entries

- DL-004 — Non-threatening handling of suspicion
- DL-007 — Reliability-gated personalization

---

## DL-004 — Non-threatening handling of suspicion

### Scope Tags

- Risk-Sensitive Wording
- Escalation / De-escalation

### Accepted Wording

> “No online payment or anything… just informing before expiry.”

### Rejected Alternatives

Examples intentionally avoided:

- “This is not spam”
- “Trust us”
- “This is official enforcement”
- “You must act immediately”

### Reasoning

The script reduces perceived scam risk without becoming defensive or confrontational.

The wording reassures the customer while preserving conversational calmness.

### Related Entries

- DL-003 — Controlled explanation for data source questions
- DL-005 — Soft consequence framing
- DL-009 — FC expiry escalation separation

---

## DL-005 — Soft consequence framing

### Scope Tags

- Escalation / De-escalation
- Risk-Sensitive Wording

### Accepted Wording

Examples:

> “Later insurance renewal issue can come.”

> “Claim or renewal side issue can come.”

### Rejected Alternatives

Examples intentionally avoided:

- “Insurance becomes invalid immediately”
- “Claims will definitely be rejected”
- “Vehicle becomes illegal”
- “Heavy penalty will happen”

### Reasoning

The script avoids absolute legal or insurance claims.

The wording consistently uses probabilistic phrasing such as:

- “can come”
- “later issue”
- “better not to keep pending”

This reduces risk of overstatement.

### Related Entries

- DL-004 — Non-threatening handling of suspicion
- DL-009 — FC expiry escalation separation

---

## DL-006 — Customer autonomy preservation

### Accepted Wording

Examples:

> “You can come whenever free.”

> “You can check once and decide.”

> “If possible.”

### Rejected Alternatives

Examples intentionally avoided:

- “You must come today”
- “Mandatory visit”
- “Immediate action required”
- pressure-based closing language.

### Reasoning

The script repeatedly preserves customer decision-making autonomy.

The conversational style encourages action without coercive pressure.

---

## DL-007 — Reliability-gated personalization

### Scope Tags

- Personalization Logic
- Fallback Handling

### Accepted Behavior

Use personalization only when variables are reliable.

When personalization variables are unavailable or unreliable, the script falls back to neutral conversational phrasing instead of attempting forced personalization.

Examples:

- honorific suppression when gender unavailable,
- name suppression when confidence low,
- branch/location suppression when unavailable,
- neutral greeting usage when customer identity confidence is low.

### Rejected Alternatives

Examples intentionally avoided:

- forced sir/madam usage,
- guessing customer identity,
- assuming branch familiarity,
- mandatory personalization.

### Reasoning

The script prioritizes correctness and conversational safety over aggressive personalization.

Unverified personalization is intentionally avoided.

---

## DL-008 — Minimalistic identity disclosure

### Accepted Wording

Examples:

> “Emission center side only.”

> “{branch_name} only.”

### Rejected Alternatives

Examples intentionally avoided:

- long organization introductions,
- corporate disclaimers,
- scripted legal identity paragraphs,
- excessive operational detail.

### Reasoning

The script intentionally maintains lightweight conversational identity disclosure suitable for short operational reminder calls.

---

## DL-009 — FC expiry escalation separated from standard expiry flow

### Scope Tags

- Escalation / De-escalation
- Risk-Sensitive Wording

### Accepted Behavior

FC-related risk escalation is conditionally introduced only when:

`{fc_expiry_status} = expired`

### Rejected Alternatives

Examples intentionally avoided:

- discussing FC risk for all customers,
- unconditional insurance-risk escalation,
- generic compliance fear escalation.

### Reasoning

The script conditionally escalates seriousness only when the FC-expired condition exists.

This prevents unnecessary escalation for standard renewal reminders.

### Related Entries

- DL-005 — Soft consequence framing
- DL-004 — Non-threatening handling of suspicion

---

## DL-010 — Explicit operational/task separation

### Accepted Design

Operational actions become:

- post-call follow-up tasks,
- CRM actions,
- suppression decisions,
- retry decisions.

### Rejected Alternatives

Examples intentionally avoided:

- embedding operational assumptions directly inside conversation flow,
- assuming task completion during calls,
- conversationally implying backend completion.

### Reasoning

The script intentionally separates:

- live customer interaction,
- operational execution,
- CRM workflow handling.

This improves operational traceability and reduces false commitments.

---

# Known Non-Documented Areas

The following areas are NOT explicitly defined in the current script and therefore are intentionally not assumed in this decision log:

- retry attempt policy,
- call frequency limits,
- suppression duration logic,
- multilingual handling rules,
- escalation ownership,
- CRM status taxonomy beyond listed outcomes,
- legal/compliance review status,
- WhatsApp template policy,
- consent handling rules,
- call recording disclosure rules,
- regional language adaptation rules,
- hostile customer termination policy,
- exact definition of “reliable” variable confidence.

These areas require separate documentation if needed.
