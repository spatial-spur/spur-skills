# Stata Example

Use this file to implement the Becker, Boll, and Voth (2026) workflow in Stata.

The `spur` package provides the full OLS pipeline wrapper plus the individual
SPUR diagnostics, transformations, and half-life commands. The `scpc` package
handles inference.

For the `spur` API, see:

- <https://spatial-spur.github.io/spur-stata/>

`scpc` is **not** our package. It is the Mueller-Watson Stata package from the
external `SCPC` repository:

- <https://github.com/ukmueller/SCPC>

## Install

These install snippets point to the latest released `spur` version. The command
syntax below follows the current package API on `main`.

```stata
ssc install moremata, replace
net install spur, replace from(https://raw.githubusercontent.com/spatial-spur/spur-stata/v0.1.1/)

cap ado uninstall scpc
net install scpc, from("https://raw.githubusercontent.com/ukmueller/SCPC/master/src")
```

`moremata` is required by the `spur` package.

## Worked Example: `am gini fracblack`

Use the `spur` wrapper when you want the full OLS workflow in one command. Use
the individual commands when you want only selected tests, transformations, or
the final inference step (scpc).

Also note that IV and absorbed fixed effects enter only at the `scpc` stage in
Stata. The `spur` wrapper is OLS-only.

This example assumes your data already contain:

- `am` as the outcome
- `gini` and `fracblack` as regressors
- `lat` and `lon` as coordinates

Both `spur` and `scpc` expect the coordinate variables to be named `s_1` and
`s_2`. With `latlong`, `s_1` is latitude and `s_2` is longitude.

```stata
rename lat s_1
rename lon s_2

set seed 42
```

### Example with pipeline wrapper

```stata
spur am gini fracblack, q(15) nrep(100000) latlong replace
```

The wrapper runs the four SPUR diagnostics, estimates the levels regression,
runs `scpc`, transforms the dependent and independent variables with the
default `lbmgls` transformation, estimates the transformed regression, and runs
`scpc` again. It currently applies lbmgls transformation; if the user wants
something else, he would need to orchestrate this from the individual test
commands instead of the pipeline wrapper.

### Example with individual test functions

#### Step 1: test the dependent variable

```stata
spurtest i0 am, q(15) nrep(100000) latlong
spurtest i1 am, q(15) nrep(100000) latlong
```

Use the practitioner-guide decision rule to choose whether to stay in levels or
transform the regression.

#### Step 2A: levels branch

```stata
reg am gini fracblack, robust
scpc, latlong
```

#### Step 2B: transformed branch

```stata
spurtransform am gini fracblack, prefix(h_) transformation(lbmgls) latlong replace

reg h_am h_gini h_fracblack, robust
scpc, latlong
```

## SCPC-only: IV / FE example

If your final regression is IV or uses fixed effects, handle that at the
estimation plus `scpc` step. In Stata, a common pattern is to include fixed
effects as dummies in `ivregress` and then run `scpc` immediately afterward.

```stata
clear
set obs 100
set seed 42

gen fe = ceil(_n / 5)
gen s_1 = rnormal()
gen s_2 = rnormal()
gen z = rnormal()
gen w = rnormal()
gen u = rnormal()
gen x_endog = 0.8 * z + 0.3 * u + rnormal() * 0.5

bysort fe: gen fe_effect = rnormal() if _n == 1
bysort fe: replace fe_effect = fe_effect[1]

gen y = 1 + 0.5 * w + 1.2 * x_endog + fe_effect + u

ivregress 2sls y w i.fe (x_endog = z), robust
scpc
```

If the SPUR decision rule tells you to transform the specification first, run
`spurtransform` on the variables you need for the regression and instrument set,
then estimate the IV model on the transformed variables before calling `scpc`.

## Optional: Half-Life

Use this only when persistence itself is part of the question.

```stata
spurhalflife am, q(15) nrep(100000) level(95) latlong
```

## Practical Notes

- If your coordinates are already named `s_1` and `s_2`, you do not need to
  rename them.
- If you work with Euclidean coordinates instead of latitude and longitude,
  keep the `s_*` naming but drop the `latlong` option.
- `scpc` is a postestimation command, so run it immediately after the
  regression you want inference for.
- `spurtransform` defaults to `lbmgls`; it is written out here so the
  transformation step is explicit.
- `replace` makes it easier to rerun the code by overwriting existing `h_*`
  variables.
- In Stata, IV and fixed effects are currently handled only through the
  estimation command plus `scpc`, not through a top-level `spur` wrapper.

## Option Reference

This is a compact guide to the options used above. For the full command syntax,
see the docs linked at the top and the external `SCPC` help file.

- `q(#)`: the number of low-frequency weighted averages used in the SPUR tests.
  Larger values let the diagnostics probe richer low-frequency dependence, but
  increase computation.
- `nrep(#)`: the number of Monte Carlo draws used in SPUR tests and half-life
  intervals. Larger values reduce simulation noise.
- `latlong`: tells `spur` and `scpc` to interpret `s_1` and `s_2` as latitude
  and longitude rather than Euclidean coordinates.
- `prefix(h_)`: the prefix used for transformed variables created by `spur` or
  `spurtransform`, such as `h_am` and `h_gini`.
- `transformation(lbmgls)`: the spatial transformation applied by `spur` or
  `spurtransform`. `lbmgls` is the default empirical branch shown here.
- `replace`: lets `spurtransform` overwrite existing transformed variables so
  the example can be rerun cleanly.
- `robust`: estimates the regression with robust standard errors before running
  `scpc` as a postestimation command.
- `cluster(...)`: estimates the regression with cluster-robust standard errors
  before `scpc`; SCPC then treats the cluster as the unit of spatial inference.
- `avc(#)`: the upper bound on average pairwise correlation assumed by SCPC.
  Smaller values impose a stricter dependence bound and can make inference more
  conservative and computation harder.
- `uncond`: request unconditional SCPC inference. By default, `scpc` uses
  conditional critical values after supported linear models; `uncond` switches
  to inference that does not condition on the realized regressors.
- `cvs`: requests extra SCPC critical values in addition to the default 95%
  interval output.
- `spur`: the full OLS pipeline wrapper. It runs diagnostics, levels inference,
  the `lbmgls` transformation, and transformed inference. IV and fixed effects
  are still handled through direct estimation plus `scpc`.
