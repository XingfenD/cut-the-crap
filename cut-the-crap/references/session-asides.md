# Session asides and additions

Worked examples for the rule in SKILL.md: a clause, qualifier, or parenthetical
whose only reason to exist is the working session is residue even when it is
positive and true. The test is not the form — parentheses are fine — it is the
justification.

Two checks before keeping any aside:

- **Audience test** — would a reader with no session history find it puzzling,
  redundant, or self-referential?
- **Redundancy test** — does the surrounding text already state it?

If either check fails, restate the content as steady-state behavior or drop it.

## Patterns that are residue

1. Denial of a rejected alternative.

   - `(single-session parameter, no “last used”)` → `(single-session parameter)`
   - `(nothing is persisted across sessions)` → the positive model already says
     it: `(single-session parameter)`

2. Pre-emptive reassurance against a concern the session raised.

   - `(no re-authorization is triggered)` → `(reuses the existing capture stream)`
   - `(harmless no-op)` → `(no-op)`
   - `(capture is unaffected, but it is unnecessary)` → drop the clause; keep
     only the reason that stands on its own.

3. Announcement of the session's fix — positive and true, still residue.

   - `Relay page (system Chrome --app, dedicated profile; quality can now be
     switched while running)` → `Relay page (system Chrome --app, dedicated
     profile)`. If mid-session switching deserves documentation, describe the
     control where its audience uses it, not as a parenthetical appendage to an
     unrelated line.

4. Change-relative wording — records the session's trajectory, not the result.

   - `no longer uploads frames` → `accepts and ignores requests`
   - `no longer renegotiates the source` → `the source keeps its negotiated size`
   - `frames still flow` → `frames flow at full resolution`
   - `this round's logger` → `the logger`

## Boundary cases that stay

- **Negation that is the semantics.** `page=false does not open the window` is
  what the flag does; it is the API, not a comment on the session.
- **Hazard guards.** `without path=..., the stream resolves to the default
  source (the camera)` prevents a real regression; keep the warning and its
  reason.
- **Authorized decision records.** Specs, ADRs, and changelogs may explain why
  an alternative was rejected when the surface exists to record decisions.
- **Contracts and diagnostics.** `null when absent`, `no auth on loopback`,
  `probe failed; keeping full resolution` are facts the reader needs.

## Sweep

One residue instance found in review or after a repair triggers a class-wide
sweep of the whole bundle; fixing the spot leaves its siblings behind. For a
candidate list of asides, run `scripts/flag_asides.py` and adjudicate every hit
with the two checks above.
