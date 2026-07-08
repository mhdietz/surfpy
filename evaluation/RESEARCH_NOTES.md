# Research Notes: Surf Forecasting Science & "Good Enough"

Living document. Purpose: ground this project's engineering (comparison harness, correction
models) in the actual physics and forecasting science, and keep a running answer to the
project's real question — **can publicly available data and models provide surf data that's
good enough for surfers, without Surfline's proprietary pipeline?**

This is not a one-time deliverable. Update it as understanding develops, the same way
`README (1).md` treats its own findings as living, not a snapshot.

---

## 1. Physical fundamentals

**Wave generation.** Wind blowing over open water generates waves through a feedback process
(wind shear + wave-induced pressure perturbations growing the wave field). Wave energy at a
given point depends on three things: wind speed, **fetch** (the distance wind blows over open
water) and **duration** (how long it's blown). A storm's fetch/duration determines the wave
field's height and period — longer fetch/duration and higher wind speed produce taller, longer-period
waves. This is why groundswell (built far away, long fetch/duration, arrives as long-period,
clean, organized swell) reads so differently from local windswell (short fetch, short period,
choppy) even at the same height.

**Dispersion.** Waves of different periods travel at different speeds (deep-water group velocity
scales with period) — this is why swell "cleans up" as it travels: a storm generates a broad mix
of periods, but the longer-period waves outrun the shorter ones, arriving first and progressively
giving way to shorter-period energy from the same storm over the following days.

**Directional spectra.** The ocean surface at any point isn't really "primary/secondary/tertiary
swell" — that's a simplification. The actual sea state is a continuous 2D spectrum: wave energy
distributed across a range of frequencies (periods) and directions simultaneously. Both Surfline's
and NDBC's "primary/secondary swell" fields are both derived by peak-picking from that underlying
spectrum — they're each choosing where to place discrete labels on a continuous surface, and they
don't always agree on where the "peaks" are (this is the documented "swell slot ordering" mismatch
in the README: Surfline orders by break-specific impact, NDBC by spectral peak energy). Any
comparison harness scoring "primary vs primary" is implicitly comparing two different peak-picking
algorithms, not two measurements of the same physical quantity — worth remembering when a big
period/direction spike shows up and it's tempting to call it a data error.

**Nearshore transformation.** As waves move from deep water toward shore, several physical
effects change what a nearshore observer/surfer actually experiences, none of which an offshore
buoy reading captures on its own:
- **Shoaling**: as depth decreases, wave height increases and wavelength decreases (energy flux
  conservation) — Green's Law is the classical formula for this. This is a big part of why an
  offshore buoy systematically underreads a nearshore break's actual size.
- **Refraction**: waves bend as they slow down over shallower water, rotating their direction of
  travel toward alignment with the seafloor contours — why a buoy's reported direction and a
  spot's actual, refracted approach angle diverge, and why the divergence is spot-specific
  (depends on the local bathymetry between buoy and break).
- **Depth-limited breaking**: waves break when their height reaches roughly 0.6-0.8x local water
  depth (varies with beach slope/bathymetry) — this is the actual physical cap on breaking wave
  height at a given spot regardless of what the offshore swell height is, and it's genuinely
  spot-specific (a steep reef break and a gentle beach break transform the same offshore swell
  very differently).
- **Bathymetric focusing/defocusing**: submarine canyons and other seafloor features can focus
  wave energy (amplifying height at specific spots) or spread it out (attenuating it). This is the
  documented explanation for Steamer Lane's large negative height bias (Monterey Canyon waveguiding)
  and is the plausible mechanism behind Ocean Beach's bias/period-mismatch pattern too.

**Takeaway for this project**: the two "problem spots" (Steamer Lane, Ocean Beach) aren't buoy
noise or a matching bug — they're real, physically-caused, spot-specific transformation effects
between the offshore buoy and the nearshore break. That's *why* a single global correction factor
won't work and a per-spot correction (Model 1) is the right shape of fix, and why nearshore
buoys (CDIP) — which have already felt these transformation effects — are structurally better
positioned to close the gap than another offshore buoy would be.

---

## 2. How forecasting models actually work

Two different classes of model matter here, and understanding which one solves which problem
clarifies what this project is (and isn't) trying to approximate:

- **Deep-water spectral wave models** (WaveWatch III / WW3, ECMWF-WAM, NOAA's GFS-Wave): solve
  the spectral wave action balance equation over a large-scale grid — given a wind field, predict
  how wave energy is generated, propagates, and dissipates across an ocean basin. Output is a
  directional spectrum (or summary height/period/direction) at each grid point, days into the
  future. This is genuinely a forecast, not a real-time reading — its accuracy depends heavily on
  the accuracy of the *wind forcing* fed into it (errors in the wind field tend to dominate model
  error at this scale, more so than the wave physics itself).
- **Nearshore phase-averaged models** (SWAN is the standard here): take a deep-water spectral
  forecast as a boundary condition and propagate it through a high-resolution nearshore grid,
  explicitly modeling shoaling/refraction/breaking over real bathymetry. This is the physics-based
  version of "correct the offshore forecast for what a specific spot's seafloor does to it" — i.e.
  the same problem Model 1's empirical correction is trying to solve statistically instead of
  physically. A real production forecasting pipeline (this project's long-horizon SWAN item in the
  README) chains WW3/GFS-Wave → SWAN to get an actual nearshore forecast; what we're doing instead
  is trying to skip the physics and learn the transformation empirically from matched buoy/Surfline
  pairs. Worth being honest that this is a shortcut, not a replacement — SWAN is likely the "real"
  answer eventually, empirical correction is the fast/cheap first pass.

**Open question, not yet answered here**: how does Surfline's LOTUS model actually work — is it a
WW3-class spectral model, a SWAN-class nearshore model, a statistical/ML layer on top of one or
both, or something else? This matters for calibrating expectations (are we trying to match a pure
physics model, or a model that's *also* statistically calibrated against something we don't have
access to — see next section). Not yet researched in depth; flagged as an open item.

---

## 3. Competitive landscape — what's publicly knowable about Surfline

**Not yet researched in depth — this section needs a real pass.** One specific, important
hypothesis worth chasing down before assuming a pure physics/data gap explains all of the
measured bias: **Surfline operates a large network of surf cameras at many of its forecast
spots.** If (and this needs verification, not assumption) that camera network is used to visually
calibrate or correct their nearshore model output, that would be a structural advantage a
public-data-only approach cannot replicate — no amount of buoy/model data substitutes for an
actual visual ground-truth feed at the spot itself. If true, this reframes the project's goal:
not "match Surfline's number" (which may be calibrated against something we don't have), but "get
close enough, with a known and quantified gap, that the gap doesn't change a surfer's decision."

To research further: Surfline engineering blog posts (if any), any patents describing their
forecast pipeline, job postings describing their data/ML stack, and any public statements about
how LOTUS is built or validated.

---

## 4. Where the field is heading

**Not yet researched in depth — placeholder for a real literature pass.** Areas worth tracking:
- Higher-resolution public model runs (NOAA has been increasing GFS-Wave/WW3 resolution over time)
- Published research on ML-based correction of buoy-to-nearshore transformation (this is
  academically a well-studied downscaling problem — worth finding actual technique names before
  Model 1 reinvents something ad hoc)
- Satellite altimetry-derived wave height products (an entirely different public data source not
  yet considered anywhere in this project's roadmap)
- General movement toward ML-based weather/ocean models (GraphCast-style approaches) and whether
  anything comparable exists yet for wave forecasting specifically

---

## 5. Defining "good enough" — the actual target metric

This is the most important open gap right now: **the harness reports MAE/bias/R², but none of
those numbers say whether a surfer's actual decision would change.** "Good enough" needs a real
definition before Model 1 (or any model) can be judged as done.

Starting questions to work through (not yet answered):
- Does absolute error matter the same way at all sizes, or does 0.5ft matter enormously at 2ft
  (wading vs. surfable) but not at all at 15ft (still huge either way)? This suggests a
  **relative/percentage error target**, not a flat MAE-in-feet target, may be more decision-relevant.
- Is period accuracy more decision-relevant than height accuracy, given wave power scales with the
  square of height but linearly(ish) with period — meaning a period miss can imply a much larger
  power/energy miss than the same-magnitude height miss?
- Is direction accuracy only relevant relative to a specific break's exposure window (i.e., "is
  this swell direction inside the window this spot can receive at all") rather than exact-degree
  accuracy? A 10° miss might be irrelevant for a wide-open beach break and decisive for a
  narrow-window point break.
- What existing standard does surf forecasting itself use for "good enough" (if any) — e.g. does
  the industry talk in terms of categorical accuracy (flat/small/fun-size/overhead) rather than
  continuous height error?

**Status: unresolved.** This section should get a real pass before Model 1 is judged as a success
or failure — right now "the number went down" isn't actually a validated definition of "good enough."

---

## Open items / next research passes

- [ ] Research Surfline's actual technical approach (camera calibration hypothesis, LOTUS architecture)
- [ ] Survey published literature on ML-based nearshore wave downscaling
- [ ] Define a concrete, decision-relevant "good enough" target metric (Section 5)
- [ ] Look into satellite altimetry as an additional public data source
- [ ] Understand SWAN in enough depth to judge whether it's a near-term or long-horizon option
