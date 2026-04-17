# R Example

Use this file to implement the Becker, Boll, and Voth (2026) workflow in R.

`spuR` handles the tests, transformations, and half-life step. `scpcR` handles inference.

The main R functions are:

- `spurtest_i0()`
- `spurtest_i1()`
- `spurtransform()`
- `scpc()`

Use `spurhalflife()` only if persistence itself is part of the question.

## Install

If you want to run this example, install the packages first.

```r
install.packages("remotes")
install.packages("geodist")

remotes::install_github("DGoettlich/spuR")
remotes::install_github("pdavidboll/scpcR")
```

`geodist` is needed here because this example uses longitude and latitude coordinates.

## Setup

```r
library(spuR)
library(scpcR)

data(spur_example)

analysis_formula <- am ~ gini + fracblack
```

## Step 1: Test The Dependent Variable

```r
i0_y <- spurtest_i0(
  am ~ 1,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  nrep = 100000,
  seed = 42
)

i1_y <- spurtest_i1(
  am ~ 1,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  nrep = 100000,
  seed = 42
)

i0_y
i1_y
```

Use the decision rule from `SKILL.md` to decide which branch to follow next.

## Step 2A: Levels Branch

Use this branch only if the decision rule in `SKILL.md` tells you to stay in levels.

```r
fit_levels <- lm(
  analysis_formula,
  data = spur_example
)

scpc_levels <- scpc(
  model = fit_levels,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  cvs = TRUE
)

summary(scpc_levels)
confint(scpc_levels)
```

## Step 2B: Transformed Branch

Use this branch if the decision rule in `SKILL.md` tells you to transform the regression.

```r
transformed <- spurtransform(
  analysis_formula,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  transformation = "lbmgls"
)

head(transformed[, c("h_am", "h_gini", "h_fracblack")])

fit_transformed <- lm(
  h_am ~ h_gini + h_fracblack,
  data = transformed
)

scpc_transformed <- scpc(
  model = fit_transformed,
  data = transformed,
  lon = "lon",
  lat = "lat",
  cvs = TRUE
)

summary(scpc_transformed)
confint(scpc_transformed)
```

## Optional: Half-Life

Use this only when persistence itself is part of the question.

```r
hl <- spurhalflife(
  am ~ 1,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  nrep = 100000,
  seed = 42
)

hl
```

## Practical Notes

- This example uses `lon` and `lat`. If you work with Euclidean coordinates instead, use `coords_euclidean` in `spuR` and `coord_euclidean` in `scpcR`.
- The example uses `nrep = 100000`, which matches the package default and is a good choice for real analysis.
- `spurtransform()` can take the original regression formula directly, which is the easiest way to transform all variables together.
- `scpc()` takes a fitted model plus the data frame that still contains the coordinates.
