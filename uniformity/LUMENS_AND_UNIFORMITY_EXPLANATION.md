# Lumens and Uniformity Explanation

## Understanding Lumens per Fixture

### What "Lumens per Fixture" Means

In IES files, the **"lumens per fixture"** value represents the **total luminous output of the entire luminaire** (all lamps combined).

### How IES Files Store Lumens

IES files contain:
- `lamp_count`: Number of lamps in the fixture (e.g., 2)
- `lumens_per_lamp`: Lumens output of each individual lamp (e.g., 13,250 lm)
- `total_lumens`: Total output = `lamp_count × lumens_per_lamp` (e.g., 26,500 lm)

### Example: Highbay 150W

If you see:
- **Lumens per Fixture: 26,500 lm**

This means:
- The fixture has **2 lamps** at **13,250 lm each**
- Total fixture output: **2 × 13,250 = 26,500 lm**
- This is the **correct value** for "lumens per fixture"

### Why This Value is Used

When calculating how many fixtures you need:
- You need **total lumens** from each fixture
- Formula: `Number of fixtures = Total lumens required / Lumens per fixture`
- So we use the **total output** (26,500 lm), not per-lamp (13,250 lm)

### Display in Recommendations

The system now shows:
- **Lumens per Fixture**: 26,500 lm (2 × 13,250 lm/lamp) - when lamp count > 1
- **Lumens per Fixture**: 13,250 lm - when lamp count = 1

This makes it clear that the value is the total output, and shows the breakdown if multiple lamps are present.

---

## Uniformity Calculation

### How Uniformity is Calculated

The system uses **point-by-point illuminance calculation** based on IES candela data:

1. **Grid Creation**: Creates a 10×10 grid on the work plane (avoiding walls by 0.5m margin)

2. **Point-by-Point Calculation**: For each grid point:
   - Calculates distance and angle to each fixture
   - Interpolates candela value from IES data at that angle
   - Applies inverse-square law: `E = I(θ) × cos(θ) / d²`
   - Sums contributions from all fixtures

3. **Uniformity Metrics**:
   - **E_min**: Minimum illuminance on grid
   - **E_avg**: Average illuminance on grid
   - **E_max**: Maximum illuminance on grid
   - **U0**: `E_min / E_avg` (minimum to average ratio)
   - **U1**: `E_min / E_max` (minimum to maximum ratio)

### Why Uniformity Might Show Zeros

If uniformity shows all zeros, it could be because:

1. **IES File Path Not Found**: The system couldn't locate the IES file
   - Check console logs for path resolution errors
   - Ensure IES files are in the correct location

2. **Missing Candela Data**: The IES file doesn't contain candela matrix
   - Some IES files may be incomplete
   - Check IES file validity

3. **Calculation Error**: An error occurred during calculation
   - Check console for error messages
   - The error will be logged with details

### Fixes Applied

1. **Improved Path Resolution**: 
   - Now tries multiple possible IES file locations
   - Handles both absolute and relative paths
   - Better error messages when file not found

2. **Better Error Handling**:
   - Added detailed logging for debugging
   - Shows which paths were tried
   - Provides clear error messages

3. **Variable Name Fix**:
   - Fixed variable name conflict (`fixtures` vs `fixture_positions`)
   - Ensures IES path is correctly retrieved from offer data

### Next Steps

If uniformity still shows zeros:

1. **Check Console Logs**: Look for messages like:
   - `📊 Calculating uniformity for...`
   - `⚠️  IES file not found...`
   - `❌ Error calculating uniformity...`

2. **Verify IES Files**: Ensure IES files exist in:
   - `LuxSCale interface/IES/[Category Folder]/[file].ies`

3. **Rebuild Database**: If IES files were moved, rebuild the database:
   ```bash
   cd "LuxSCale interface/IES"
   python ies_database_builder.py
   ```

4. **Check Database**: Verify `ies_path` is stored correctly in `fixtures_database.json`

---

## Summary

- **Lumens per Fixture**: Total output of fixture (lamp_count × lumens_per_lamp) ✅ Correct
- **Uniformity Calculation**: Point-by-point using IES candela data ✅ Fixed
- **Display**: Now shows lamp breakdown when multiple lamps present ✅ Improved





