# Core equations: lumen method, grid illuminance, uniformity

## 1. Floor area (quadrilateral sides)

Sides \(a,b,c,d\) (m) in order. **Brahmagupta** formula for a cyclic quadrilateral:

\[
s = \frac{a+b+c+d}{2}, \qquad
A = \sqrt{(s-a)(s-b)(s-c)(s-d)}.
\]

**Length / width** used for rectangular layouts:

\[
L = \max(a,c), \quad W = \max(b,d).
\]

---

## 2. Rated flux and lumen-method average illuminance

Rated flux per fixture (design intent):

\[
\Phi_\mathrm{rated} = P \cdot \eta .
\]

Effective flux (maintenance):

\[
\Phi_\mathrm{eff} = \Phi_\mathrm{rated} \cdot \mathrm{MF}.
\]

**Spatial average** (lumen method — used for search sizing and as fallback compliance average):

\[
E_\mathrm{avg,lm} = \frac{N \cdot \Phi_\mathrm{rated} \cdot \mathrm{MF}}{A}.
\]

**Minimum fixture count** before search refinement:

\[
\Phi_\mathrm{needed} = \frac{E_{m,r} \cdot A}{\mathrm{MF}}, \qquad
N_\mathrm{min} = \left\lfloor \frac{\Phi_\mathrm{needed}}{\Phi_\mathrm{rated}} \right\rfloor + 1.
\]

**Over-lighting stop** (main sweep): if \(E_\mathrm{avg,lm} > 1.35\, E_{m,r}\), the loop **breaks** (no higher \(N\) for that line).

---

## 3. Spacing (rectangular grid)

For integers \(n_x, n_y\) with \(n_x n_y = N\) chosen to balance centre-to-centre spacing:

\[
s_x = \frac{L}{n_x}, \quad s_y = \frac{W}{n_y}.
\]

**Minimum spacing constraint** (implementation): candidate pairs must satisfy \(\min(s_x, s_y) \ge 0.8\ \mathrm{m}\); fixture counts with no valid pairs are skipped.

---

## 4. Inverse-square horizontal illuminance (IES path)

For one fixture contribution at a horizontal work-plane point:

\[
E = \frac{I(\theta_h, \theta_v)}{R^2} \cdot \cos i,
\]

where:

- \(R\) — 3D distance (m) from luminaire point to sample \((x,y,h_\mathrm{wp})\);
- \(I\) — candela in direction \((\theta_h,\theta_v)\) from the **Type C** table, scaled to match design lumens (see [05](./05-ies-lm63-fields-beam-angle-and-flux.md));
- \(\cos i = (H - h_\mathrm{wp}) / R\) — oblique incidence on the **horizontal** plane (downward light).

**Superposition:** total \(E\) at a point = **sum** over all fixtures.

---

## 5. Uniformity metrics on the \(G\times G\) work-plane grid

Let samples \(k=1\ldots G^2\) have illuminances \(E_k\) from the IES calculation.

\[
E_\mathrm{min} = \min_k E_k,\quad
E_\mathrm{max} = \max_k E_k,\quad
E_\mathrm{avg,grid} = \frac{1}{G^2}\sum_{k=1}^{G^2} E_k.
\]

\[
U_0 = \begin{cases}
E_\mathrm{min} / E_\mathrm{avg,grid}, & E_\mathrm{avg,grid} > 0,\\
0, & \text{otherwise.}
\end{cases}
\qquad
U_1 = \begin{cases}
E_\mathrm{min} / E_\mathrm{max}, & E_\mathrm{max} > 0,\\
0, & \text{otherwise.}
\end{cases}
\]

**Note:** Compliance uses **\(U_0\)** vs \(U_{0,\mathrm{req}}\). **\(U_1\)** is reported but not the primary pass/fail gate in `calculate.py`.

---

## 6. Relation between \(E_\mathrm{avg,lm}\) and \(E_\mathrm{avg,grid}\)

They need **not** be equal:

- **\(E_\mathrm{avg,lm}\)** uses **area** and **total installed effective lumens** (no angular distribution).
- **\(E_\mathrm{avg,grid}\)** integrates **real photometry** and layout; scaling uses IES header lumens vs design lumens per slot.

Both appear in result rows (**Average Lux** vs **E_avg_grid_lx**). For lux compliance, implementation prefers **`E_avg_grid_lx`** when available.

---

Next: [03-compliance-inequalities-and-row-properties.md](./03-compliance-inequalities-and-row-properties.md)
