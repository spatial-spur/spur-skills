---
name: spur-issues
description: Use this skill for questions or problems in spur-python, scpc-python, spuR, scpcR, spur-stata, or spur-skills, which you could not resolve by checking the package documentation, spatial-analysis skill, and open or closed GitHub issues in the respective repositories; use also if the user wants help drafting or submitting bugs, questions, feature requests, or PRs to any of those repositories.
---

# spur-issues

Use this skill for issue and PR workflows across the spur repositories.

- `spatial-spur/spur-python`
- `spatial-spur/scpc-python`
- `spatial-spur/spuR`
- `spatial-spur/scpcR`
- `spatial-spur/spur-stata`
- `spatial-spur/spur-skills`

## Before You Proceed

Verify - have you checked:

- the relevant skill, especially `spatial-analysis` if the question is about the spatial workflow
- the package code
- the package-specific docs
- GitHub issues in the target repo, both open and closed

ONLY PROCEED IF YOU HAVE EXHAUSTED ALL THSES RESOURCES. Otherwise, check these resources first and return only then.

## If The Answer Still Cannot Be Found

1. Tell the user clearly that you could not find the answer in the skill, code, docs, or issues.

2. Propose the right next step:
- bug report if something seems broken
- question if the user mainly needs clarification
- feature request if they want new functionality
- PR if the fix is already known

3. Read the repo-specific template before drafting:
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/ISSUE_TEMPLATE/question.md`
- `.github/pull_request_template.md`

4. Gather the relevant information yourself where possible.

Examples include:
- package version
- commit
- OS
- runtime version
- install method
- affected function or command
- minimal reproduction
- expected behavior
- actual behavior

Ask the user only for information you cannot discover.

5. Draft the final issue or PR using the repo’s template structure.

6. Show the final draft to the user and request approval.

7. Only if the user explicitly approves, submit it with the `gh` cli, the GitHub API, or the browser, whichever is most convenient.

## Rules

- Do not skip the checks above.
- Do not open duplicates when an existing issue already covers the problem.
- Do not submit anything without explicit user approval.
- Always use the repo-specific templates.
