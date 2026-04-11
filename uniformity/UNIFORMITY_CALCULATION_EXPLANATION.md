# Uniformity Calculation Methods - Explanation

## 📐 What is Uniformity (Uo)?

**Uniformity (Uo)** is the ratio of minimum illuminance to average illuminance on the work plane:

```
Uo = E_min / E_avg
```

Where:
- **E_min** = Minimum illuminance (lowest point on work plane) in lux
- **E_avg** = Average illuminance (mean across work plane) in lux

**Standard Requirements:**
- Most standards require Uo ≥ 0.6 (minimum 60% of average)
- Some applications require Uo ≥ 0.7 or higher
- Higher uniformity = more even light distribution

---

## 🧮 Calculation Methods

### Method 1: Simplified Lumen Method (Fast, Approximate)

**Formula:**
```
E_avg = (Φ × n × UF × MF) / A
```

Where:
- **Φ** = Luminous flux per fixture (lumens)
- **n** = Number of fixtures
- **UF** = Utilization Factor (typically 0.4-0.7, depends on room index and fixture type)
- **MF** = Maintenance Factor (typically 0.7-0.8, accounts for aging and dirt)
- **A** = Room area (m²)

**For Uniformity:**
```
E_min ≈ E_avg × Uniformity_Factor
```

Where Uniformity_Factor depends on:
- **Fixture spacing ratio** (spacing / mounting height)
- **Beam angle** (wider beams = better uniformity)
- **Fixture distribution pattern**

**Typical Uniformity_Factor values:**
- Spacing ratio < 1.0: Uniformity_Factor ≈ 0.7-0.8
- Spacing ratio 1.0-1.5: Uniformity_Factor ≈ 0.6-0.7
- Spacing ratio > 1.5: Uniformity_Factor ≈ 0.4-0.6

**Pros:**
- ✅ Fast calculation
- ✅ Good for initial estimates
- ✅ Works with basic fixture data

**Cons:**
- ❌ Less accurate
- ❌ Doesn't account for actual light distribution
- ❌ Assumes uniform fixture distribution

---

### Method 2: Point-by-Point with IES Candela Data (Accurate, Slower)

**Process:**
1. Create a grid of calculation points on the work plane (e.g., 0.5m spacing)
2. For each point, calculate illuminance from all fixtures using IES candela data
3. Use inverse-square law: `E = I(θ) / h² × cos(θ)`
4. Sum contributions from all fixtures
5. Find E_min and E_avg across all points
6. Calculate: `Uo = E_min / E_avg`

**Formula for each point:**
```
E_point = Σ [I(θ_i) / h_i² × cos(θ_i)]
```

Where:
- **I(θ_i)** = Candela value at angle θ_i from fixture i (from IES file)
- **h_i** = Distance from fixture i to calculation point
- **θ_i** = Angle from fixture vertical axis to calculation point

**Pros:**
- ✅ Most accurate method
- ✅ Uses actual fixture photometric data
- ✅ Accounts for real light distribution patterns

**Cons:**
- ❌ Slower calculation (many points × many fixtures)
- ❌ Requires IES candela matrix data
- ❌ More complex implementation

---

### Method 3: Hybrid Method (Balanced)

**Process:**
1. Calculate E_avg using Lumen Method
2. Estimate E_min based on:
   - Fixture spacing ratio
   - Beam angle (from IES or estimated)
   - Room geometry
3. Use simplified formula: `E_min = E_avg × f(spacing, beam_angle)`

**Uniformity Factor Formula:**
```
Uniformity_Factor = f(spacing_ratio, beam_angle)

Where:
spacing_ratio = max(spacing_x, spacing_y) / mounting_height
beam_angle_factor = min(beam_angle / 90, 1.0)  # Normalize to 90°

Uniformity_Factor ≈ 0.4 + 0.4 × beam_angle_factor - 0.2 × spacing_ratio
```

**Pros:**
- ✅ Faster than point-by-point
- ✅ More accurate than pure lumen method
- ✅ Uses available fixture data (beam angle, spacing)

**Cons:**
- ❌ Still an approximation
- ❌ Requires beam angle data

---

## 🎯 Recommended Approach for Our System

### Phase 1: Hybrid Method (Recommended for Now)

**Why:**
- We have fixture spacing from layout recommendations
- We can extract beam angles from IES files (or estimate)
- Good balance of accuracy and speed
- Works with current database structure

**Implementation Steps:**
1. Calculate E_avg using Lumen Method with utilization factor
2. Get fixture spacing from layout (spacing_x, spacing_y)
3. Get beam angle from IES metadata or estimate from fixture type
4. Calculate spacing ratio: `spacing_ratio = max(spacing_x, spacing_y) / mounting_height`
5. Calculate uniformity factor based on spacing ratio and beam angle
6. Calculate E_min: `E_min = E_avg × uniformity_factor`
7. Calculate Uo: `Uo = E_min / E_avg = uniformity_factor`

**Formula:**
```python
# Utilization factor (simplified, based on room index)
UF = 0.4 + 0.3 * min(room_index / 5.0, 1.0)  # Typical range: 0.4-0.7
MF = 0.8  # Maintenance factor

# Average illuminance
E_avg = (total_lumens * UF * MF) / room_area

# Spacing ratio
spacing_ratio = max(spacing_x, spacing_y) / mounting_height

# Beam angle factor (normalize to 90°)
beam_angle_factor = min(beam_angle / 90.0, 1.0)

# Uniformity factor
uniformity_factor = 0.4 + 0.4 * beam_angle_factor - 0.2 * min(spacing_ratio, 2.0)
uniformity_factor = max(0.3, min(0.9, uniformity_factor))  # Clamp to reasonable range

# Minimum illuminance
E_min = E_avg * uniformity_factor

# Uniformity
Uo = E_min / E_avg = uniformity_factor
```

---

## 📊 Additional Fixture Data to Display

Based on your request, we should also display:

1. **Beam Angle** (from IES file or metadata)
   - Horizontal beam angle (FWHM)
   - Vertical beam angle (FWHM)
   - Or single beam angle if symmetric

2. **Total Lumens**
   - Per fixture: `lumens_per_fixture`
   - Total installation: `total_lumens = lumens_per_fixture × number_of_fixtures`

3. **Other Useful Data:**
   - Manufacturer
   - Model number
   - Lamp type
   - Color temperature (if available)
   - CRI/Ra (if available)

---

## ✅ Summary

**Recommended Method:** Hybrid approach using:
- Lumen Method for E_avg
- Spacing ratio and beam angle for uniformity estimation
- Simple, fast, reasonably accurate

**Next Steps:**
1. Extract beam angles from IES files (or estimate from fixture type)
2. Calculate uniformity using hybrid method
3. Display all fixture data (beam angle, lumens, uniformity) in recommendations

---

**Questions for You:**
1. Do you want the **Hybrid Method** (recommended) or **Point-by-Point** (more accurate but slower)?
2. Should we extract beam angles from IES files, or estimate based on fixture category?
3. What other fixture data should we display in the recommendations?





