# Compliance inequalities and result row properties

## 1. Targets from the standard row

From **`standards_cleaned.json`** (or legacy **`define_places`**):

- **Required average illuminance:** \(E_{m,r} =\) **`Em_r_lx`** (lx).
- **Required uniformity:** \(U_{0,\mathrm{req}} =\) **`Uo`** (dimensionless, e.g. 0.4).

---

## 2. Lux gap (work-plane average when IES ran)

Let \(\bar{E}_\mathrm{grid}\) = **`E_avg_grid_lx`** (IES work-plane spatial mean) and \(\bar{E}_\mathrm{lm}\) = **Average Lux** (lumen method).

The implementation uses **`_avg_lux_for_compliance`**: \(\bar{E} = \bar{E}_\mathrm{grid}\) when the grid ran, else \(\bar{E}_\mathrm{lm}\). This avoids approving layouts where the lumen average exceeds \(E_{m,r}\) but photometry yields a much lower work-plane mean (common for panels / asymmetric distributions).

\[
\text{Lux gap} = \max\bigl(0,\; E_{m,r} - \bar{E}\bigr).
\]

**Pass condition:** \(\text{Lux gap} = 0\) (within \(\varepsilon \approx 10^{-9}\)), i.e. \(\bar{E} \ge E_{m,r}\).

**Relation:** Lux gap is **one-sided** — over-lighting is limited separately by the **1.35** cap on the **lumen-method** sweep (search logic); grid-based lux is the compliance gate when IES data exists.

---

## 3. U₀ gap (grid check)

Let \(U_0^\*\) = **`U0_calculated`** from the grid (may be absent if IES failed).

\[
\text{U0 gap} = \begin{cases}
\max\bigl(0,\; U_{0,\mathrm{req}} - U_0^\*\bigr), & U_0^\* \text{ defined,}\\
U_{0,\mathrm{req}}, & \text{undefined.}
\end{cases}
\]

**Pass:** \(\text{U0 gap} = 0\) \(\Leftrightarrow\) \(U_0^\* \ge U_{0,\mathrm{req}}\).

---

## 4. Boolean compliance

\[
\texttt{is\_compliant} \equiv (\text{Lux gap} \le \varepsilon) \land (\text{U0 gap} \le \varepsilon).
\]

Both illuminance (grid-preferred average) and uniformity (IES grid) must pass.

---

## 5. Standard margin percentages (informational)

**Lux margin (%):**

\[
\frac{E_{m,r} - \bar{E}}{E_{m,r}} \times 100\%
\]

(can be **negative** if \(\bar{E} > E_{m,r}\)).

**U₀ margin (%):**

\[
\frac{U_{0,\mathrm{req}} - U_0^\*}{U_{0,\mathrm{req}}} \times 100\%
\]

(negative when \(U_0^\*\) exceeds the requirement).

These **do not** replace gaps for pass/fail; they aid **comparison** in the UI/PDF.

---

## 6. Logical relations between quantities

| If … | Then … |
|------|--------|
| \(\bar{E} \uparrow\) (more fixtures or higher \(\eta\)) | Lux gap \(\downarrow\) toward 0 (until over-light cap stops search) |
| Tighter spacing / more overlap | Often \(E_\mathrm{min} \uparrow\) and \(U_0 \uparrow\) (not guaranteed globally) |
| Higher ceiling \(H\) | Usually **lower** grid illuminances (larger \(R\)) unless compensated by \(N\) |
| Wider IES beam | Different \(E_\mathrm{min}/E_\mathrm{avg}\) — must use IES, not beam angle alone |

---

## 7. Closest non-compliant ranking (when no pass)

When no compliant layout exists for a **(luminaire, power, efficacy)** line, the solver keeps the row minimizing **(U₀ gap, Lux gap, -U₀_calculated, total power, fixture count)** — used to **seed** the fallback sweep.

---

Next: [04-pipeline-from-request-to-results-and-export.md](./04-pipeline-from-request-to-results-and-export.md)
