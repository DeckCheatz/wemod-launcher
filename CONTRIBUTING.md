# Contribution Policy

Thanks for considering contributing to the Wand Launcher. This document describes what this project strives for and what a good PR looks like. It's short on purpose.

## What This Project Strives For

- **Clear architecture.** Code is grouped by responsibility (settings, logging, UI, steps) with clean internal APIs and a single source of truth: e.g. `SettingsManager` owns flags, paths, and config.
- **Platform-correct.** Consistent Wine/Proton prefix handling and tiered config (`CLI args → env vars → config file → defaults`).
- **Predictable and debuggable.** Structured, contextual logging with standard log levels.
- **Quality over speed.** Reviewed, maintainable code beats quick-and-dirty fixes.

## What a Good PR Looks Like

- **Small and focused.** One logical change per PR. A big refactor gets split into reviewable pieces.
- **Explains why.** Describe the problem and your approach, not just what changed. Reference the relevant issue where possible.
- **Follows the architecture.** Match the structure in `src/`; don't bolt on a parallel mechanism when an existing one should be extended.
- **Meets the tooling bar.** `ruff` format (line length 78, as enforced by CI). Use the conventional-commit format for messages (`fix:`, `feat:`, `docs:`, `chore:`, ...).
- **Updates the docs.** If behavior changes, update the affected docs (`README.md` or the wiki). Stale docs are a bug.
- **Tests where it makes sense.** There's no test suite yet, but logic-heavy changes (path conversion, config merging, prefix matching) should come with tests.
- **Ready to review.** No merge conflicts, no unrelated whitespace churn, no WIP-in-disguise.

## AI-Assisted Contributions

We treat AI as just another tool, and clearly a useful one.
We judge your contribution on technical merit, not on how it was written.

That said, AI is not a free pass to skip work:

- **You own your contribution.** If AI wrote it, you are responsible for it. Review the code, make sure it works, and stand behind it exactly as if you wrote it by hand.
- **Disclose it.** If you used AI assistance in a meaningful way, say so in the PR description.
- **No AI slop.** Low-quality generated code, duplicate issues, and noise that just wastes maintainers' time will be rejected. Quality and thoroughness beat volume.
- **Maintainers decide.** AI-assisted or not, every change is reviewed on its own merits and can be rejected if it doesn't meet the bar.
