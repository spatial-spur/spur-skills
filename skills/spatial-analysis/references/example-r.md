# R Example

Use this file to implement the Becker, Boll, and Voth (2026) workflow in R.

`spuR` handles the SPUR diagnostics, transformations, half-life step, and the
full `spur()` pipeline. `scpcR` handles SCPC inference on fitted models.

This reference shows both entry paths:

- a pipeline wrapper when you want the full workflow in one call
- individual functions when you want only selected diagnostics,
  transformations, or the final inference step

For the full API, see:

- <https://spatial-spur.github.io/spuR/>
- <https://spatial-spur.github.io/scpcR/>

## Install

These install snippets point to the latest released versions. The example code
below follows the current package API on `main`.

```r
install.packages("remotes")
install.packages("geodist")

remotes::install_github("spatial-spur/scpcR@v0.1.3")
remotes::install_github("spatial-spur/spuR@v0.1.2")
```

`geodist` is needed here because the example uses longitude and latitude
coordinates. GitHub installation does not guarantee the declared `scpcR`
version is updated, so make sure both versions are up to date by installing
the *latest* tagged version of each package explicitly.

## Worked Example: `am ~ gini + fracblack`

```r
library(spuR)
library(scpcR)

data(spur_example)

analysis_formula <- am ~ gini + fracblack
```

### Example with pipeline wrapper

If you do not want to run the diagnostics and both branches by hand, use the
top-level `spur()` wrapper.

```r
pipeline <- spur(
  analysis_formula,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  q = 15L,
  nrep = 100000L,
  seed = 42L,
  avc = 0.03,
  uncond = FALSE,
  cvs = FALSE
)

summary(pipeline)
pipeline$tests$i0
pipeline$fits$levels$scpc$scpcstats
pipeline$fits$transformed$scpc$scpcstats
```

`pipeline$tests` contains the four SPUR diagnostics, and `pipeline$fits`
contains both regression branches together with their SCPC results. This
wrapper fits `lm()` internally. If your final specification is IV or uses
absorbed fixed effects, use the manual path and call `scpc()` on the fitted
IV/FE model yourself.

### Example with individual test functions

Use the individual functions below if you want only selected parts of the
workflow.

#### Step 1: test the dependent variable

```r
i0_y <- spurtest_i0(
  am ~ 1,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  q = 15L,
  nrep = 100000L,
  seed = 42L
)

i1_y <- spurtest_i1(
  am ~ 1,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  q = 15L,
  nrep = 100000L,
  seed = 42L
)

i0_y
i1_y
```

Use the practitioner-guide decision rule to choose whether to stay in levels or
transform the regression.

#### Step 2A: levels branch

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

#### Step 2B: transformed branch

```r
transformed <- spurtransform(
  analysis_formula,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  transformation = "lbmgls",
  prefix = "h_"
)

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

## SCPC-only: IV / FE example

`spur()` currently fits `lm()` internally. If your final regression is IV or
uses absorbed fixed effects, run the SPUR diagnostics and any transformation
manually, then fit the IV/FE model yourself and pass that fitted model to
`scpc()`.

```r
library(fixest)

set.seed(42)
n_fe <- 20L
t_per_fe <- 5L
n <- n_fe * t_per_fe

fe <- rep(seq_len(n_fe), each = t_per_fe)
s_1 <- rnorm(n)
s_2 <- rnorm(n)
z <- rnorm(n)
w <- rnorm(n)
u <- rnorm(n)
x <- 0.8 * z + 0.3 * u + rnorm(n, sd = 0.5)
fe_effect <- rnorm(n_fe)[fe]
y <- 1 + 0.5 * w + 1.2 * x + fe_effect + u

iv_df <- data.frame(
  y = y,
  x = x,
  z = z,
  w = w,
  fe = fe,
  s_1 = s_1,
  s_2 = s_2
)

fit_iv <- fixest::feols(y ~ w | fe | x ~ z, data = iv_df)

out_iv <- scpc(
  model = fit_iv,
  data = iv_df,
  coords_euclidean = c("s_1", "s_2"),
  cvs = TRUE
)

summary(out_iv)
confint(out_iv)
```

If the SPUR decision rule tells you to transform the specification first,
transform the outcome, regressors, and instrument together and then fit the IV
model on those transformed variables before calling `scpc()`.

## Optional: Half-Life

Use this only when persistence itself is part of the question.

```r
hl <- spurhalflife(
  am ~ 1,
  data = spur_example,
  lon = "lon",
  lat = "lat",
  q = 15L,
  nrep = 100000L,
  seed = 42L
)

hl
```

## Practical Notes

- Use `lon` and `lat` for geographic coordinates. Use `coords_euclidean` for
  planar coordinates.
- `spurtransform()` can take the full regression formula directly, which is the
  easiest way to transform the dependent and independent variables together.
- `scpcR::scpc()` currently supports `lm` and `fixest`, including IV. This
  example stays on the simple `lm` path.
- IV and absorbed-FE estimation are currently SCPC-only concerns in R. The
  `spur()` wrapper itself still fits `lm()` internally.
- `scpc()` takes a fitted model plus the data frame that still contains the
  coordinate columns.

## Parameter Reference

This is a compact guide to the arguments used above. For full signatures and
return objects, see the package docs linked at the top.

- `formula`: the model specification. Use a two-sided formula such as
  `am ~ gini + fracblack` when regressors matter for the SPUR residual tests,
  transformation step, or final regression.
- `data`: the data frame containing both the model variables and the coordinate
  columns used by SPUR and SCPC.
- `lon`, `lat`: use these when your coordinates are geographic and distances
  should be treated as great-circle distances on the earth.
- `coords_euclidean`: use this instead of `lon` / `lat` when coordinates live
  in a planar system such as projected meters or x/y grid coordinates.
- `q`: the number of low-frequency spatial averages used in the SPUR tests.
  Larger values let the diagnostics probe richer low-frequency dependence, but
  increase computation.
- `nrep`: the number of Monte Carlo draws used in SPUR tests and half-life
  intervals. Larger values reduce simulation noise.
- `seed`: the random seed for the simulation-based SPUR steps, so results can
  be reproduced.
- `transformation`: the spatial transformation applied by `spurtransform()`.
  `lbmgls` is the default empirical branch shown here.
- `prefix`: the prefix used for transformed variables created by
  `spurtransform()`, such as `h_am` and `h_gini`.
- `avc`: the upper bound on average pairwise correlation assumed by SCPC.
  Smaller values impose a stricter dependence bound and can make inference more
  conservative and computation harder.
- `uncond`: request unconditional SCPC inference. Conditional SCPC adjusts
  critical values using the realized regressors; unconditional SCPC does not,
  and is useful when the conditional adjustment is unavailable or when you want
  the unconditional procedure explicitly.
- `cvs`: store additional SCPC critical values beyond the default 95% interval
  output, which is useful when you want several confidence levels from one run.
- `spur()`: the convenience wrapper that runs the full SPUR workflow and then
  fits `lm()` internally for the final SCPC step. If your final regression is
  IV or uses absorbed fixed effects, call `scpc()` directly on the fitted model
  instead.
