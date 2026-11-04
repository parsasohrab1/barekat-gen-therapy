# Technology readiness (TRL) of the article component

**Level: TRL 4** for the component in `research/lnp_shift`: conformal coverage under random versus chemical-series splits (component validated in a laboratory setting).

| Evidence | Where |
|---|---|
| Code with unit tests (synthetic data generated in the tests and labelled as such, never reported as results) | `research/lnp_shift/tests` |
| Continuous integration | `.github/workflows/research-ci.yml` |
| Real-data validation | Not included in this branch: the public LANTERN/AGILE data were not available in the build environment; manuscript numbers are the author's own earlier run and have not been reproduced here. |

Not claimed: TRL 5 (relevant environment) for the whole product. This component is separate from the product's claimed functions; no claimed function is implemented or disclosed here. A patent attorney must review before any publication.

## Update 2026-11-04: cis/trans component (`research/lnp_cistrans`)

Real-data analysis on the LANTERN table supplied by the data-request task (SHA-256 `2aebccac...e4ff826`, 11,545 rows). 21 cis/trans pairs, all from the UnDen library (IGROV1, mRNA). Trans higher in 14 pairs, cis in 6, one tie; mean difference (cis minus trans) -0.357 (bootstrap 95% interval -0.697 to -0.029); sign test p = 0.115, Wilcoxon p = 0.062. Leave-one-pair-out order accuracy: 0.50 (fingerprint without chirality, ties by construction), 0.667 (chirality), 0.762 (Z/E counts); the constant rule "trans is higher" gives 0.69. Exploratory, one library, one cell line. 8 unit tests (toy molecules) in CI. Level stays TRL 4 for the component. Details: `docs/ARTICLE.md`.
