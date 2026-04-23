# Python Example

Use this file to implement the Becker, Boll, and Voth (2026) workflow in Python.

`spur-python` handles the SPUR diagnostics, transformations, half-life step, and
the full `spur()` pipeline. `scpc-python` handles SCPC inference on fitted
models.

This reference shows both entry paths:

- a pipeline wrapper when you want the full workflow in one call
- individual functions when you want only selected diagnostics,
  transformations, or the final inference step

For the full API, see:

- <https://spatial-spur.github.io/spur-python/>
- <https://spatial-spur.github.io/scpc-python/>

## Install

These install snippets point to the latest released versions on PyPI. The
example code below follows the current package API on `main`.

```bash
uv venv --python 3.11
uv pip install spur-python
```

## Worked Example: `am ~ gini + fracblack`

This example uses the packaged Chetty data from `spur-python`.

```python
import spur

df = spur.load_chetty_data()

df = df[~df["state"].isin(["AK", "HI"])][
    ["am", "gini", "fracblack", "lat", "lon"]
].copy()

df = df.dropna(subset=["am", "gini", "fracblack", "lat", "lon"])
```

### Example with pipeline wrapper

If you do not want to run each test and branch by hand, use the top-level
`spur()` wrapper.

```python
import spur

pipeline = spur(
    "am ~ gini + fracblack",
    df,
    lon="lon",
    lat="lat",
    q=15,
    nrep=100000,
    seed=42,
    avc=0.03,
)

print(pipeline.summary())
print(pipeline.tests.i0.summary())
print(pipeline.fits.levels.scpc)
print(pipeline.fits.transformed.scpc)
```

`pipeline.tests` contains the four SPUR diagnostics, and `pipeline.fits`
contains both the levels and transformed regression branches together with their
SCPC results. This wrapper fits OLS internally. If your final specification is
IV or uses absorbed fixed effects, use the manual path and call `scpc()` on the
fitted IV/FE model yourself.

### Example with individual test functions

Use the individual functions below if you want only selected parts of the
workflow.

#### Step 1: test the dependent variable

```python
import spur

i0_y = spur.spurtest(
    "am",
    df,
    test="i0",
    lon="lon",
    lat="lat",
    q=15,
    nrep=100000,
    seed=42,
)

i1_y = spur.spurtest(
    "am",
    df,
    test="i1",
    lon="lon",
    lat="lat",
    q=15,
    nrep=100000,
    seed=42,
)

print(i0_y.summary())
print(i1_y.summary())
```

Use the practitioner-guide decision rule to choose whether to stay in levels or
transform the regression.

#### Step 2A: levels branch

```python
import statsmodels.formula.api as smf
import scpc

fit_levels = smf.ols("am ~ gini + fracblack", data=df).fit()

scpc_levels = scpc(
    fit_levels,
    data=df,
    lon="lon",
    lat="lat",
    cvs=True,
)

print(scpc_levels)
```

#### Step 2B: transformed branch

```python
import statsmodels.formula.api as smf
import scpc
import spur

transformed = spur.spurtransform(
    "am ~ gini + fracblack",
    df,
    lon="lon",
    lat="lat",
    transformation="lbmgls",
    prefix="h_",
)

fit_transformed = smf.ols(
    "h_am ~ h_gini + h_fracblack",
    data=transformed,
).fit()

scpc_transformed = scpc(
    fit_transformed,
    data=transformed,
    lon="lon",
    lat="lat",
    cvs=True,
)

print(scpc_transformed)
```

## SCPC-only: IV / FE example

`spur()` currently fits OLS internally. If your final regression is IV or uses
absorbed fixed effects, run the SPUR diagnostics and any transformation
manually, then fit the IV/FE model yourself and pass that fitted model to
`scpc()`.

```python
import numpy as np
import pandas as pd
import pyfixest as pf
import scpc

rng = np.random.default_rng(42)
n_fe = 20
t_per_fe = 5
n = n_fe * t_per_fe

fe = np.repeat(np.arange(n_fe), t_per_fe)
s_1 = rng.normal(size=n)
s_2 = rng.normal(size=n)
z = rng.normal(size=n)
w = rng.normal(size=n)
u = rng.normal(size=n)
x = 0.8 * z + 0.3 * u + rng.normal(scale=0.5, size=n)
fe_effect = rng.normal(size=n_fe)[fe]
y = 1.0 + 0.5 * w + 1.2 * x + fe_effect + u

iv_df = pd.DataFrame(
    {
        "y": y,
        "x": x,
        "z": z,
        "w": w,
        "fe": fe,
        "s_1": s_1,
        "s_2": s_2,
    }
)

fit_iv = pf.feols("y ~ w | fe | x ~ z", data=iv_df)

out_iv = scpc(
    fit_iv,
    data=iv_df,
    coords_euclidean=["s_1", "s_2"],
    cvs=True,
)

print(out_iv) # from >=v0.1.2
```

If the SPUR decision rule tells you to transform the specification first,
transform the outcome, regressors, and instrument together and then fit the IV
model on those transformed variables before calling `scpc()`.

From `scpc-python>=0.1.2`, `scpc()` results also provide R-like helpers for
named access: `coef()`, `confint()`, and `summary()`. Raw arrays remain
available as `scpcstats` and `scpccvs` when lower-level access is needed.

## Optional: Half-Life

Use this only when persistence itself is part of the question.

```python
import spur

hl = spur.spurhalflife(
    "am",
    df,
    lon="lon",
    lat="lat",
    q=15,
    nrep=100000,
    seed=42,
)

print(hl.summary())
```

## Practical Notes

- Use `lon` and `lat` for geographic coordinates. Use `coords_euclidean` only
  for planar coordinates.
- `spurtransform()` defaults to `transformation="lbmgls"` and `prefix="h_"` in
  the full `spur()` pipeline. The manual example writes both out explicitly.
- `scpc-python` now supports fitted `statsmodels` models and `pyfixest` models,
  including IV. This example keeps the regression step on the simple
  `statsmodels` path.
- IV and absorbed-FE estimation are currently SCPC-only concerns in Python. The
  `spur()` wrapper itself still fits OLS internally.
- Do not substitute ordinary regression standard errors for SCPC inference.

## Parameter Reference

This is a compact guide to the arguments used above. For full signatures and
return objects, see the package docs linked at the top.

- `formula`: the model specification. Use a two-sided formula such as
  `"am ~ gini + fracblack"` when regressors matter for the SPUR residual tests,
  transformation step, or final regression.
- `data`: the DataFrame containing both the model variables and the coordinate
  columns used by SPUR and SCPC.
- `lon`, `lat`: use these when your coordinates are geographic and distances
  should be treated as great-circle distances on the earth.
- `coords_euclidean`: use this instead of `lon` / `lat` when coordinates live
  in a planar system such as projected meters or x/y grid coordinates.
- `q`: the number of low-frequency spatial averages used in the SPUR tests.
  Larger values let the diagnostics look at richer low-frequency dependence, but
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
  fits OLS internally for the final SCPC step. If your final regression is IV
  or uses absorbed fixed effects, call `scpc()` directly on the fitted model
  instead.
