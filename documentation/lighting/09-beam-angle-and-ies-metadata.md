# Beam angle and IES metadata

## 1. Nominal fallback

**`luxscale/lighting_calc/constants.py`** defines **`beam_angle = 120`** (degrees). This **nominal** value is stored on each result row as **`Beam Angle nominal (°)`** and used when **IES** does not yield a beam estimate.

---

## 2. IES-derived beam (**half-power** style)

**`approx_beam_angle_deg(ies_data, threshold=0.5)`** in **`ies_fixture_params.py`**:

- Takes the **first horizontal** candela slice ( **`horizontal_angles[0]`** ).
- Finds **global peak** candela on that vertical profile.
- Walks **increasing vertical angle** until candela **crosses** **`0.5 × peak`** (50 % of peak — half-power style).
- **Linearly interpolates** the crossing angle → **half-angle**; returns **twice** that → **full beam width** (symmetric-about-nadir convention, matching **`ies-render`** viewer).

**`threshold=0.1`** would give a wider “field” angle; the **solver and results** use **0.5** for **`beam_angle_deg`** in **`ies_params_for_file`**.

---

## 3. What beam angle changes in outputs

| Aspect | Effect |
|--------|--------|
| **Result columns** | **`Beam Angle (°)`** shows IES estimate when available, else **120°**; **`Beam source`** = **`IES half-power estimate`** or **`nominal catalog value`**. |
| **ASCII-safe keys** | **`beam_angle_deg`**, **`Beam Angle (deg)`** duplicated for JSON layers that strip Unicode (**`_add_ascii_safe_result_keys`**). |
| **Photometry / U₀** | **Not** fed back as a simplified cone — **actual** **U₀** comes from the **full candela** grid. Beam angle is **metadata** for spec sheets and UI, not a separate geometric substitute for IES. |

Narrower beams (smaller **FWHM**) tend to produce **higher peak / lower min** for the same spacing → often **lower U₀** unless spacing or count compensates; the tool captures that through **IES**, not through an analytic beam formula.

---

## 4. Other IES fields exposed

**`ies_params_for_file`** also returns **`lumens_per_lamp`**, **`num_lamps`**, **`max_candela`**, **`shape`**, luminaire opening dimensions from the file, etc. **`calculate.py`** attaches **`IES file`** basename and **`IES lumens (lm)`** when parsing succeeds.

---

Next: [10-solver-option-picking-fast-fallback.md](./10-solver-option-picking-fast-fallback.md)
