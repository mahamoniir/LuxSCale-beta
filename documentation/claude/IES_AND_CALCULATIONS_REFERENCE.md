# IES Files, Fixed Parameters, Beam Angle, and the Full Calculation Pipeline

## Overview

LuxScaleAI uses two sources of photometric data for each fixture:

1. **IES files** — real measured light distribution data (manufacturer or lab-measured)
2. **Fixed catalog parameters** — simplified constants (efficacy, nominal beam angle) used when IES data is unavailable or as a starting estimate

Understanding the difference between these two, and how beam angle flows through the entire calculation, is essential to interpreting any result from the tool.

---

## Part 1 — Fixed Catalog Parameters

### What they are

Fixed parameters are the simplified constants stored in `luxscale/lighting_calc/constants.py` and the fixture catalog JSON files. They describe a fixture in broad strokes:

| Parameter | Example value | Where it lives |
|-----------|--------------|----------------|
| Efficacy (lm/W) | Interior: 110, Exterior: 145 / 160 / 200 | `constants.py → led_efficacy` |
| Nominal beam angle | 120° | `constants.py → beam_angle` |
| Power options (W) | `[9, 10]` for SC downlight | `constants.py → interior_luminaires` |
| Shape / size | Circle 0.464 m diameter | `constants.py → luminaire_shapes` |

### How fixed parameters are used in calculation

**Step 1 — Rated flux per fixture:**

```
Φ_rated = Power (W) × Efficacy (lm/W)
```

Example: 100 W × 145 lm/W = 14,500 lm

**Step 2 — Effective flux after maintenance:**

```
Φ_eff = Φ_rated × Maintenance Factor (MF)
```

Default MF = 0.63 (accounts for dirt, lamp depreciation, aging)

**Step 3 — Lumen method average illuminance:**

```
E_avg = (N × Φ_rated × MF) / Area
```

Where N = number of fixtures, Area = floor area in m²

**Step 4 — Minimum fixture count:**

```
N_min = floor((E_required × Area / MF) / Φ_rated) + 1
```

This gives the starting point for the search loop.

### Limitations of fixed parameters alone

When only fixed parameters are used (no IES file available):

- The calculation only produces **average lux** — no uniformity (U₀ or U₁)
- Beam angle is the nominal catalog value (120° default), not the real distribution
- No hot spots, wall illuminance, or work-plane grid are computed
- The result row will show `"Lux compliance basis": "lumen method (no IES grid)"`

---

## Part 2 — IES Files (LM-63 Format)

### What an IES file contains

An IES file (Illuminating Engineering Society format, LM-63 standard) stores the **measured luminous intensity distribution** of a real fixture in 3D space. The key data inside:

```
TILT=NONE
1  14500  1.0  37  1  1  1  -0.464  -0.464  0
...
0  5  10  15  20  25  30  ...  (vertical angles)
0  45  90  135  180  225  270  315  (horizontal angles)
14200  14100  13800  13200  12400  11500  10400  ...  (candela values)
```

| Field | Meaning |
|-------|---------|
| Lumens per lamp | Total luminous flux from the fixture header |
| Multiplier | Scale factor (usually 1.0) |
| Vertical angles | Angles from nadir (0°) to horizontal (90°) or zenith (180°) |
| Horizontal angles | Azimuth planes around the fixture (0°–360°) |
| Candela values | Luminous intensity in each direction (candela) |

### How LuxScaleAI reads IES files

The tool uses `ies-render/module/ies_parser.py` (loaded dynamically via `importlib`) to parse LM-63 files. For performance, parsed data is cached via `lru_cache` — the same IES file is only parsed once per session.

A fast path also exists via `photometry_ies_adapter.py` which loads pre-processed JSON blobs from the catalog index, avoiding repeated file parsing.

### What IES files enable that fixed parameters cannot

| Capability | Fixed params only | With IES file |
|------------|------------------|---------------|
| Average lux | ✓ (lumen method) | ✓ (grid-calibrated) |
| Uniformity U₀ | ✗ | ✓ (point-by-point grid) |
| Uniformity U₁ | ✗ | ✓ |
| Real beam angle | ✗ (nominal 120°) | ✓ (half-power calculation) |
| Min/max grid lux | ✗ | ✓ |
| Asymmetric distribution | ✗ | ✓ |
| Wall and ceiling illuminance | ✗ | ✓ (future) |
| Fixture-specific comparison | ✗ | ✓ (each product different) |

---

## Part 3 — Beam Angle: Definition, Calculation, and Effect on Results

### Definition

The **beam angle** (also called full beam angle) is the cone angle within which the luminaire emits at least 50% of its peak intensity. It is the angle between the two points on the intensity distribution where intensity drops to half the peak value (half-power points), measured as the full included angle.

```
Full beam angle = 2 × (angle from nadir to half-peak point)
```

### How LuxScaleAI calculates beam angle from IES data

The calculation is done in `ies_fixture_params.py → approx_beam_angle_deg_for_horizontal()`:

1. Read the candela values for one horizontal plane slice
2. Find the peak candela value
3. Find where the candela drops to 50% of peak (half-power threshold = 0.5)
4. Linear interpolation between adjacent angle samples to find the crossing point
5. Multiply the half-angle by 2 to get the full beam angle

For asymmetric fixtures (e.g., asymmetric flood lights), this is done across all horizontal planes and the **narrowest** beam angle is reported as the primary value. This is conservative — it represents the tightest dimension of the beam.

```python
# Simplified from ies_fixture_params.py
peak = max(candela_values)
cutoff = 0.5 * peak
# Find crossing point between consecutive angles
# Return 2 × half_angle as full beam angle
```

### IES angle sign convention

IES LM-63 vertical angles follow a signed convention where angles can extend past 90° (toward the ceiling for up-light components). Some fixtures produce negative signed angles in the half-power calculation. LuxScaleAI always takes the absolute value for display:

```python
def _non_negative_beam_angle_deg(v):
    return abs(float(v))
```

The result row includes a note when this correction was applied: `"Beam angle note": "IES vertical angles follow a signed convention..."`

### How beam angle affects the calculation

**1. Fixture filtering during the search**

In `_uniformity_fallback_sweep_rows()`, narrow-beam fixtures are filtered out when high uniformity is required:

```python
if beam_deg is not None and required_uniformity >= 0.62 and beam_deg < 34.0:
    continue  # Skip narrow-beam fixtures for high-uniformity spaces
```

Narrow beams create concentrated hot spots rather than even coverage. A 20° spot cannot produce U₀ ≥ 0.62 in a normal room without extreme fixture density.

**2. Work-plane grid illuminance (inverse-square law)**

For each fixture, at each grid point, the illuminance contribution is:

```
E = I(θ_h, θ_v) × cos(i) / R²
```

Where:
- `I(θ_h, θ_v)` = candela from IES at the angle toward the sample point
- `cos(i) = (ceiling_height - work_plane_height) / R` — oblique incidence factor
- `R` = 3D distance from fixture to sample point (meters)

The candela value `I` comes directly from the IES angle table. A fixture with a narrow 30° beam has very high candela in the central cone but near-zero candela at wide angles. This produces:
- Very high illuminance directly below each fixture
- Very low illuminance between fixtures
- Low U₀ (high ratio of E_max to E_min)

A fixture with a wide 120° beam distributes light more evenly, increasing overlap between fixtures and raising the minimum illuminance relative to the average.

**3. Flux scaling between IES and design lumens**

```
I_used = I_file × (Φ_design_per_slot / Φ_IES)
```

If the IES header lumens differ from the design lumens (power × efficacy), candela is scaled proportionally. The ratio is capped between 0.25 and 4.0 to prevent meaningless results from bad IES headers:

```python
ies_lumen_to_design_ratio_min = 0.25
ies_lumen_to_design_ratio_max = 4.0
```

**4. Compliance decision**

After the IES grid runs, compliance uses the grid average (E_avg_grid_lx) rather than the lumen-method average when available:

```python
def _avg_lux_for_compliance(row):
    eg = row.get("E_avg_grid_lx")
    if eg is not None and float(eg) >= 0:
        return float(eg)
    return float(row.get("Average Lux") or 0.0)
```

The grid average is more accurate because it accounts for the actual photometric distribution, not just total lumens divided by area.

---

## Part 4 — Full Calculation Pipeline Step by Step

### Step 0 — Input parsing

```
sides=[L1, W1, L2, W2], height, place or standard_ref_no
```

- Room area computed via Brahmagupta formula (supports non-rectangular quadrilaterals)
- Length = max(side1, side3), Width = max(side2, side4)
- Zone determined: interior (height < threshold, default 5m) or exterior

### Step 1 — Luminaire options

Based on zone, `determine_luminaire(height)` returns available fixture families from the merged IES catalog. Interior: downlight, triproof, backlight. Exterior: highbay, flood, street.

For compact rooms (area ≤ 400 m² or min dimension ≤ 14 m), triproof is prioritized first.

### Step 2 — For each (luminaire, power, efficacy) combination

**2a — Lumen method minimum:**
```
Φ = power × efficacy
N_min = ceil((E_required × area / MF) / Φ)
```

**2b — IES file resolution:**
`resolve_ies_path(luminaire_name, power_w)` looks up the IES file from the fixture map JSON. If found, `ies_params_for_file()` extracts beam angle, lumens from header, and stores the path for grid use.

**2c — Main search loop (N = N_min to N_max):**

For each fixture count N:
1. Check minimum spacing: `min(L/nx, W/ny) ≥ 0.8 m`
2. Compute lumen-method average: `E_avg_lm = N × Φ × MF / area`
3. Stop if `E_avg_lm > 1.35 × E_required` (over-lighting cap)
4. Skip if `E_avg_lm < E_required`
5. For each valid grid layout `(nx, ny)` where `nx × ny = N`:
   - Run IES point-by-point grid (`compute_uniformity_metrics`)
   - Compute U₀ = E_min / E_avg_grid
   - Compute compliance (lux gap, U₀ gap)
   - Keep best layout (minimum U₀ gap, then lux gap)

**2d — Uniformity grid calculation (`compute_uniformity_metrics`):**

Places a G×G sample grid on the work plane (default G determined by room size). For each of the `nx × ny` fixture positions, for each of the G² sample points:

```
1. Compute 3D distance R from fixture to sample point
2. Compute vertical angle θ_v = atan2(horizontal_dist, delta_z)
3. Compute horizontal angle θ_h = atan2(dy, dx)
4. Look up I(θ_h, θ_v) from IES candela table (nearest H, interpolated V)
5. Scale I by (design_lumens / IES_lumens)
6. E_contribution = I × cos(i) / R²
7. Add to total E at this sample point
```

Sum over all fixtures, then compute:
```
U₀ = E_min / E_avg_grid
U₁ = E_min / E_max
```

### Step 3 — Compliance sorting

Results are sorted by:
1. Fully compliant (lux ✓ AND U₀ ✓) before non-compliant
2. Among compliant: `least_fixture_count_compliant` selected as primary
3. Remaining compliant options sorted by power efficiency
4. Non-compliant closest options included if no compliant found

### Step 4 — Fallback sweep

If no standard layout meets both lux and U₀, `_uniformity_fallback_sweep_rows()` sweeps upward in fixture count with a relaxed lux cap (×1.65 instead of ×1.35), evaluating up to 300 IES grid calls to find layouts that improve U₀.

### Step 5 — Output assembly

Each result row contains:
- Lumen method: Average Lux, Fixtures, Spacing X/Y, Total Power, Efficacy
- IES grid: E_avg_grid_lx, E_min_grid_lx, E_max_grid_lx, U₀_calculated, U₁_calculated
- Beam data: beam_angle_deg (from IES), beam_angle_nominal_deg (120°), Beam source
- Compliance: Standard margin (lux %), Standard margin (U0 %), Lux gap, U0 gap
- Meta: IES file, IES lumens, Layout grid, Selection method, Maintenance factor

---

## Part 5 — Key Differences Summary Table

| Aspect | Fixed Parameters | IES File |
|--------|-----------------|----------|
| Data source | Catalog constants | Measured photometry file |
| Lux calculation | Lumen method average | Point-by-point inverse-square |
| Beam angle | Nominal (120° default) | Half-power measured from candela |
| Uniformity (U₀) | Not available | Calculated from grid |
| Fixture comparison | Same formula for all | Each product truly different |
| Asymmetric beams | Not captured | Fully represented |
| Compliance basis | `lumen method (no IES grid)` | `IES work plane E_avg` |
| Accuracy | Approximate | Accurate (within IES measurement tolerance) |
| Speed | Fast (no file I/O) | Slower (grid calculation per layout) |

---

## Appendix — Result Fields Reference

| Field | Source | Meaning |
|-------|--------|---------|
| `Average Lux` | Lumen method | `N × Φ × MF / area` |
| `E_avg_grid_lx` | IES grid | Mean of all sample point illuminances |
| `E_min_grid_lx` | IES grid | Lowest sample point illuminance |
| `E_max_grid_lx` | IES grid | Highest sample point illuminance |
| `U0_calculated` | IES grid | `E_min / E_avg_grid` |
| `U1_calculated` | IES grid | `E_min / E_max` |
| `beam_angle_deg` | IES half-power | Full cone angle at 50% peak intensity |
| `beam_angle_nominal_deg` | Catalog constant | Always 120° (legacy default) |
| `Beam source` | Logic flag | `"IES half-power estimate"` or `"nominal catalog value"` |
| `Standard margin (lux %)` | Compliance | `(E_required - E_avg_grid) / E_required × 100` |
| `Standard margin (U0 %)` | Compliance | `(U0_required - U0_calculated) / U0_required × 100` |
| `IES lumens (lm)` | IES header | Manufacturer-stated lumens (or rated if header invalid) |
| `Maintenance factor` | Settings | Applied MF value (default 0.63) |
| `Lux compliance basis` | Logic flag | Which average was used for pass/fail |
