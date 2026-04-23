# Solver: option order, fast mode, fallback

## 1. Outer loops

**`calculate_lighting`** iterates:

1. **`determine_luminaire(height)`** — list of **(family name, [powers])** filtered by **interior vs exterior** threshold.
2. For each **power**, resolve **IES** (optional).
3. For each **efficacy** (interior: single **lm/W**; exterior: list **145, 160, 200**).
4. **Fixture count** from **`min_fixtures`** to **`max_fixtures`** step **`fixture_step`** (**2** if **`fast`**, else **1**).

---

## 2. Starting fixture count

\[
N_\text{min} = \left\lfloor \frac{E_m \cdot A}{\text{MF} \cdot \Phi_\text{rated}} \right\rfloor + 1
\]

**Search span** adapts with **`min_fixtures`** (caps for very large counts). **`max_fixtures = min_fixtures + search_span`**.

---

## 3. Stopping when “enough” compliant options

**Admin** **`get_max_solutions_total()`** caps how many **compliant** rows are collected (**default 80** if settings missing). Search sets **`stop_search`** when **`len(results) >= max_solutions_cap`**.

**`fast=True`**: **`max_solutions_cap = min(3, cap)`**, coarser fixture stepping, reduced uniformity logging and fallback budgets.

---

## 4. First compliant wins per (luminaire, power, efficacy)

Inside the fixture loop, the first **(lux_ok and u0_ok)** hits **`break`** — **least fixture count** that passes both checks in search order (**`Selection: least_fixture_count_compliant`**).

---

## 5. Uniformity report chunks

When a compliant row is appended, a **uniformity text chunk** is often appended immediately. If counts drift (e.g. fallback), **`_sync_uniformity_report_chunks`** rebuilds sections per final **`results`** order.

---

## 6. No compliant options

1. Collect **closest non-compliant** rows per combo.
2. If **results** still empty, run **`_uniformity_fallback_sweep_rows`** from those seeds.
3. If still empty, user sees **no compliant** options; **`meta.no_compliant_options`** reflects that.

Fallback sweep specifics (current implementation):

- Relaxes average-lux cap to about **`1.65 × required_lux`**
- Uses call budgets (lower in `fast` mode; may increase for stricter U₀ targets)
- Can skip narrow-beam seeds for high-uniformity targets
- Ranks fallback candidates by `(U0 gap, Lux gap, -U0_calculated, total power, fixtures)`
- Marks accepted fallback rows as `Selection: uniformity_fixture_sweep_fallback`

---

## 7. Meta returned with results

**`calculate_lighting`** returns **`(results, length, width, meta)`** including **`calc_mode`**, **`fixture_count_step`**, **`capped_at_max`**, **`used_uniformity_sweep_fallback`**, **`no_compliant_options`**, **`interior_height_threshold_m`**, etc.

---

Next: [11-concepts-not-full-engine.md](./11-concepts-not-full-engine.md)
