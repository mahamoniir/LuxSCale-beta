# Lumen method: maintenance factor and average illuminance

## 1. Purpose

The **lumen method** provides a **single number** for **average illuminance** on the work plane without tracing every ray. It is used to:

- Estimate **minimum number of fixtures** before the IES grid runs.
- **Filter** candidates (**over-lighting cap**).

It does **not** by itself enforce **uniformity** — that comes from the **IES grid** (next docs).

---

## 2. Rated luminous flux per fixture

For each candidate **(luminaire, power W, efficacy)**:

\[
\Phi_\text{rated} = P \times \eta
\]

- \(P\) = power (W)
- \(\eta\) = efficacy (lm/W) from **`led_efficacy`**: interior single value (**110**), exterior list **(145, 160, 200)** in **`constants.py`**

If **IES** parses successfully and lumens > 0, the row may show **IES lumens** in output, but the **sweep** still uses **\(\Phi_\text{rated}\)** for the **lumen-method average** unless code path explicitly uses IES for min-fixtures (see **`calculate.py`** — it uses **`lumens = power * efficacy`** for the average lux line).

---

## 3. Maintenance factor \(MF\)

**`maintenance_factor = 0.63`** in **`constants.py`**.

Interpretation: **effective** lumens after **dirt, depreciation, lamp lumen depreciation** (single lumped factor).

\[
\Phi_\text{eff} = \Phi_\text{rated} \times MF
\]

---

## 4. Average illuminance (spatial mean, lumen method)

For **\(N\)** identical fixtures over floor area **\(A\)** (m²):

\[
E_\text{avg,lm} = \frac{N \cdot \Phi_\text{rated} \cdot MF}{A}
\]

Implementation: **`avg_lux = (num_fixtures * lumens * maintenance_factor) / area`** with **`lumens = power * efficacy`**.

**Units:** lm/m² = lx when **A** is in m².

---

## 5. Minimum fixture count (starting search)

Required lumens on the working plane **before** losses are already embedded in \(MF\):

\[
\Phi_\text{required} = \frac{E_m \cdot A}{MF}
\]

where \(E_m\) = **required_lux** (**Em,r**).

\[
N_\text{min} = \left\lfloor \frac{\Phi_\text{required}}{\Phi_\text{rated}} \right\rfloor + 1
\]

Code: **`min_fixtures = int(total_lumens_needed / lumens) + 1`** with **`total_lumens_needed = (required_lux * area) / maintenance_factor`**.

---

## 6. Over-lighting cap (search filter)

To avoid listing layouts that are **far too bright** on average:

\[
E_\text{avg,lm} \le 1.35 \times E_m
\]

**`max_avg_lux = required_lux * 1.35`** — loop **breaks** when exceeded for increasing \(N\) (exact behavior in **`calculate.py`** inner loop).

---

## 7. Relation to IES grid average

The **IES grid** produces **\(E_\text{avg,grid}\)** (mean of sample points). Compliance uses:

- **Lumen method** \(E_\text{avg,lm}\) vs **Em,r** for the **Lux gap**.
- **U₀** uses **\(U_0\)** from ratios of **grid** values (not the lumen-method number).

If IES header lumens disagree with rated lm/W, **grid absolute lx** can follow **IES scale** via **`flux_scale`** in **`compute_uniformity_metrics`** — see [05-ies-photometry-and-inverse-square.md](./05-ies-photometry-and-inverse-square.md).

---

Next: [04-spacing-layout-and-fixture-count.md](./04-spacing-layout-and-fixture-count.md)
