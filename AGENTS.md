# AGENTS.md — directive for any AI agent

This file follows the emerging cross-tool convention for agent-readable
project briefs. Cursor, Copilot, Aider, OpenDevin, Sweep, and others
auto-load it. Its entire content is one sentence and a pointer: read the
project directive.

---

## The project directive

**Stage 1 of this project measures inter-rater consistency on SCENE INDIVIDUATION only.**

The atomic question is: *for every narrative passage, did both raters individuate it as a hallucinatory scene?*

For every scene only one rater individuated, classify whether the discrepancy is:

1. **MISS** — the other rater overlooked a clearly hallucinatory passage they should have coded per the PDF Guidelines (rater-compliance gap), or
2. **AMBIGUITY** — the PDF rules don't cleanly cover this edge case, so both decisions are defensible (instruction-design gap).

The rater's **subjective judgement** about what counts as a hallucinatory scene is the **primary data**. Preserve it. Do not silently drop individuations that seem to violate the rules. Do not override attribute tags on shared scenes. Attribute-classification consistency (illusion vs incrusted, object-class choices, modal status) is **Stage 2, deferred**.

## Full directive

→ [AI_DIRECTIVE.md](AI_DIRECTIVE.md) (canonical)
→ [CLAUDE.md](CLAUDE.md) (Claude Code auto-load)
→ [1.Recoding/STAGE1_SCOPE.json](1.Recoding/STAGE1_SCOPE.json) (machine-readable)
→ [1.Recoding/STAGE1_SCOPE.md](1.Recoding/STAGE1_SCOPE.md) (human companion)
