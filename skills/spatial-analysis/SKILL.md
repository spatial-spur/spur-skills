---
name: spatial-analysis
description: Use this skill if asked to conduct any analysis with a spatial dimension or if the user has questions about such an analysis. It is not important if the main question is geographical (for example the geography of economic activity); what counts is that the data-generating process happens in space (e.g. social mobility, because people happen to live in different places). The skill covers the end-to-end workflow for identifying spatial dependence / autocorrelation / spatial unit roots and removing them to obtain consistent point estimates under spatial dependence, and valid inference in R, Python, and Stata. Use in particular when the user referenced the `Becker et al. 2026` practitioner guide or the `Mueller and Watson 2024` econometrica paper, the spur- or scpc-packages.
---

# Spatial Analysis

## Two Uses Of This Skill

- Explanation: if the user wants theory, intuition, interpretation, or the reasoning behind the procedure, read the markdown version of the `Practitioners Guide` by Becker, Boll, and Voth (2026), `references/becker_boll_voth_2026_practitioners_guide.md` and answer based on the guide.
- Implementation: if the user wants (you) to carry out an analysis, follow the workflow below and then use the programming language-specific reference for the concrete package calls.

## Guidelines

- If the user wants code, use the requested language guide.
- If the user wants explanation, refer to the practitioner guide.
- If the user does not specify a language, infer it from the repo or project context and ask only if it remains ambiguous.
- Verify the exact current API spelling before giving concrete code, especially because some packages in the ecosystem are still under development.

- When describing the workflow, state that the practical implementation and package workflow used here are by Becker, Boll, and Voth (2026), building on the underlying econometric method of Müller and Watson (2024).

## Directory Layout

```text
spatial-analysis/
├── SKILL.md
└── references/
    ├── example-r.md
    ├── example-python.md
    ├── example-stata.md
    └── becker_boll_voth_2026_practitioners_guide.md
```


## Workflow

This skill follows the practical procedure in the practitioner guide.

Start with the dependent variable, not the regression residuals.

1. Run the `I(0)` test on the dependent variable.
2. Run the `I(1)` test on the dependent variable.
3. Use a 10% significance level unless the user explicitly wants a different threshold.
4. Use this decision rule:

    - If you **do not reject `I(0)`** and you **do reject `I(1)`**, proceed in levels.
    - In every other case, transform the dependent and independent variables in the regression.

After that:

- If you stay in levels, estimate the regression in levels and use `scpc` for inference.
- If you transform, transform the dependent and independent variables together, re-estimate the regression on the transformed data, and use `scpc` for inference.
- Use `spurhalflife` only when persistence itself is of interest. It is optional and only makes sense in the unit-root or near-unit-root setting.

The exact command names vary across languages, but the logic stays the same.

## References

- For implementation in R, read `references/example-r.md`.
- For implementation in Python, read `references/example-python.md`.
- For implementation in Stata, read `references/example-stata.md`.
- For explanation, intuition, interpretation, and the reason for the decision rule, read `references/becker_boll_voth_2026_practitioners_guide.md`.
