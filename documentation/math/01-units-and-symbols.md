# Units and symbols

## 1. Base units (SI)

| Symbol | Meaning | Unit |
|--------|---------|------|
| \(L, W\) | Room length and width (derived from sides) | m |
| \(A\) | Floor area | m² |
| \(H\) | Ceiling height (luminaire plane) | m |
| \(h_\mathrm{wp}\) | Work plane height above floor | m (default **0.75**) |
| \(\Phi\) | Luminous flux | lm |
| \(E\) | Illuminance on the work plane | lx (= lm/m²) |
| \(I\) | Luminous intensity | cd |
| \(r\) | Distance (fixture centre to sample point) | m |

## 2. Subscripts and names

| Symbol | Meaning |
|--------|---------|
| \(E_{m,r}\) | Required **maintained average** illuminance from standard row (**`Em_r_lx`**) |
| \(U_{0,\mathrm{req}}\) | Required uniformity ratio from standard row (**`Uo`**, e.g. 0.4) |
| \(\mathrm{MF}\) | Maintenance factor (runtime from `app_settings`, default **0.8**) |
| \(\eta\) | LED efficacy (**lm/W**) |
| \(P\) | Lamp / luminaire electrical power (**W**) |
| \(N\) | Number of fixtures (integer) |
| \(U_0\) | Computed **\(E_\mathrm{min}/E_\mathrm{avg}\)** on the sample grid |
| \(U_1\) | Computed **\(E_\mathrm{min}/E_\mathrm{max}\)** on the sample grid |

## 3. Non-dimensional ratios

- **Uniformity ratios** \(U_0, U_1 \in [0,1]\) in ideal cases; implementation clamps behaviour via denominators.
- **Gaps** (Lux gap, U₀ gap) are **non-negative** by definition in the API row (see [03](./03-compliance-inequalities-and-row-properties.md)).

---

Next: [02-core-equations-lumen-grid-uniformity.md](./02-core-equations-lumen-grid-uniformity.md)
