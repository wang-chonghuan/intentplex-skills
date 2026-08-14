# Built-in persona cast

Eight stable personality cores. Each is a *temperament*, not an occupation — cap 2 injects the occupation and situation on top. The cast is chosen to spread across the axes that decide attract/retain/grow: patience, prior loyalty, standards, tech-literacy, value-sensitivity, attention. Two of them (`anxious-novice`, `value-comparator`) deliberately hold the low-tech-literacy and price-skeptic lenses that LLM simulation tends to under-represent.

| Slug | One-line personality | Primary lens |
|------|----------------------|--------------|
| `impatient-skeptic` | Assumes it won't work; bails at first friction | First-impression / time-to-value |
| `loyal-habitualist` | Attached to their current tool; needs a reason to switch | Switching cost / retention |
| `demanding-enthusiast` | Early adopter with high standards and a loud voice | Novelty & polish ceiling |
| `pragmatic-minimalist` | Only wants the job done with the fewest steps | Friction / task completion |
| `anxious-novice` | Low confidence, low tech-literacy, fears mistakes | Accessibility / trust |
| `value-comparator` | Runs a constant cost-benefit ledger vs alternatives | Willingness to pay / ROI |
| `detail-critic` | Trust erodes with every flaw, edge case, or typo | Craft / correctness |
| `distracted-skimmer` | Judges in seconds while multitasking; never reads | Scannability / clarity of the next action |

These are *temperaments only* — no occupation, no product, no goal baked in. The goal and situation are supplied per review in §5 of the spec (the diagonal). Pick a slug for a spec's persona row when its temperament fits; onboarding leans on `anxious-novice` + `impatient-skeptic`, a pricing page on `value-comparator` + `loyal-habitualist`, a dense output on `distracted-skimmer` + `detail-critic`.

For a temperament not covered here, describe a custom one inline in §5 of the spec — do not edit these cores.
