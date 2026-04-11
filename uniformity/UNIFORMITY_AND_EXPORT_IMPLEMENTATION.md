# Uniformity Calculation and Export Features - Implementation Summary

## 📋 Overview

This document summarizes the implementation of:
1. **Point-by-point uniformity calculation** using IES candela data
2. **Beam angle extraction** from IES files
3. **Full standard reference data** in recommendations
4. **Comprehensive fixture data display** (beam angles, lumens, uniformity)
5. **PDF export** for all options
6. **CSV export** for individual options (POQ format)

---

## 🧮 Uniformity Calculation Method

### Implementation Based on `pick helper.md`

The uniformity calculation follows the methodology from `pick helper.md`:

1. **Point-by-Point Illuminance Calculation**
   - Creates a 10×10 grid on the work plane
   - For each point, calculates illuminance from all fixtures using IES candela data
   - Uses inverse-square law: `E = I(θ) × cos(θ) / d²`
   - Sums contributions from all fixtures

2. **Uniformity Metrics**
   - **E_min**: Minimum illuminance across all grid points
   - **E_avg**: Average illuminance across all grid points
   - **E_max**: Maximum illuminance across all grid points
   - **U0**: Uniformity ratio = E_min / E_avg
   - **U1**: Uniformity ratio = E_min / E_max

### Files Created/Modified

- **`collected_project/src/uniformity_calculator.py`** (NEW)
  - `calc_point_illuminance()`: Calculates illuminance at a single point
  - `calc_uniformity()`: Calculates uniformity metrics on a grid
  - `get_beam_angles()`: Extracts beam angles from IES files
  - `interp_intensity()`: Linear interpolation of candela values

- **`collected_project/src/fixture_recommender.py`** (MODIFIED)
  - `_calculate_uniformity_for_offer()`: Calculates uniformity for each recommendation
  - `_get_beam_angles_for_offer()`: Extracts beam angles for each recommendation
  - Updated `get_recommendations()` to include uniformity and beam angles

---

## 📊 Beam Angle Extraction

### Implementation

- Extracts **FWHM (Full Width Half Maximum)** beam angles from IES files
- Horizontal and vertical beam angles are calculated from candela matrix
- Falls back to estimated values if IES parsing fails

### Display

Beam angles are displayed in the frontend for each recommendation:
- Horizontal Beam Angle (FWHM)
- Vertical Beam Angle (FWHM)

---

## 📋 Standard Reference Data

### Implementation

- Full standard data from `standards_filtered.json` is included in recommendations
- All standard parameters are displayed:
  - Reference Number (ref_no)
  - Category
  - Task/Activity
  - Required Illuminance (Em,r)
  - Maintained Illuminance (Em,u)
  - Uniformity (Uo)
  - Color Rendering (Ra)
  - UGR Limit
  - Cylindrical Illuminance (Ez)
  - Specific Requirements

### Files Modified

- **`collected_project/src/api_server.py`**
  - Updated `/get-fixture-recommendations` endpoint to include standard reference

- **`collected_project/static/index.html`**
  - Added comprehensive standard data display section

---

## 🎨 Frontend Display Enhancements

### New Data Displayed

For each fixture recommendation:
1. **Basic Information**
   - Name, Manufacturer, Model, Category
   - Wattage, Lumens per Fixture, Total Lumens
   - Lamp Type, Number of Fixtures, Total Power
   - Efficacy (lm/W)

2. **Beam Angles**
   - Horizontal Beam Angle (FWHM)
   - Vertical Beam Angle (FWHM)

3. **Uniformity Analysis**
   - E_min (Minimum Illuminance)
   - E_avg (Average Illuminance)
   - E_max (Maximum Illuminance)
   - U0 (E_min/E_avg)
   - U1 (E_min/E_max)

4. **Standard Reference**
   - All standard parameters as recommendations

---

## 📄 PDF Export

### Features

- **Export All Options**: Single button to export all recommendations to PDF
- **Comprehensive Report** includes:
  - Standard Reference (all parameters)
  - Room Analysis
  - Each Option with:
    - Fixture Details
    - Uniformity Analysis
    - Fixture Layout (X, Y coordinates)
  - Professional formatting with red/grey/black color scheme
  - Page numbers and footer

### File: `collected_project/static/index.html`
- Function: `exportAllOptionsToPDF()`
- Uses jsPDF and jspdf-autotable libraries

---

## 📊 CSV Export (POQ Format)

### Features

- **Export Individual Option**: Each recommendation has its own CSV export button
- **Naming Format**: `poq-[YYYYMMDD].csv` (e.g., `poq-20251203.csv`)
- **Comprehensive Data** includes:
  - Standard Reference
  - Room Analysis
  - Fixture Details
  - Beam Angles
  - Uniformity Analysis
  - Fixture Layout (X, Y coordinates)

### File: `collected_project/static/index.html`
- Function: `exportOptionToCSV(optionIndex)`
- Generates CSV with all relevant data for price quotation

---

## 🔧 Technical Details

### IES File Path Resolution

The system handles IES file paths in multiple ways:
1. Absolute paths (from `ies_path` in database)
2. Relative paths (from `ies_file` in database)
3. Automatic path resolution to `LuxSCale interface/IES/` folder

### Error Handling

- Graceful fallback if IES file not found
- Uniformity calculation returns `calculated: false` if unable to calculate
- Beam angles return `null` if unable to extract

---

## 📝 Usage

### For Users

1. **Get Recommendations**: Enter room dimensions and room type
2. **View Data**: All fixture data, beam angles, and uniformity are displayed
3. **Export PDF**: Click "📄 Export All to PDF" to export all options
4. **Export CSV**: Click "📊 Export CSV" on any option to export that option as POQ

### For Developers

1. **Uniformity Calculation**: Uses `uniformity_calculator.py` module
2. **Beam Angles**: Extracted using `get_beam_angles()` function
3. **Standard Data**: Retrieved from `standards_lookup.py` and included in API response
4. **Export Functions**: JavaScript functions in `index.html` handle PDF/CSV generation

---

## ✅ Testing Checklist

- [x] Uniformity calculation works with IES files
- [x] Beam angles extracted correctly
- [x] Standard reference data displayed
- [x] PDF export generates complete report
- [x] CSV export generates POQ format with correct naming
- [x] IES file path resolution handles both absolute and relative paths
- [x] Error handling for missing IES files
- [x] Frontend displays all data correctly

---

## 🚀 Next Steps (Optional Enhancements)

1. **Increase Grid Resolution**: Change from 10×10 to 20×20 for more accurate uniformity
2. **3D Visualization**: Add 3D illuminance distribution plots
3. **Interactive Layout**: Allow users to adjust fixture positions and recalculate uniformity
4. **Comparison Mode**: Compare uniformity across different options
5. **Export Formats**: Add Excel export option

---

## 📚 References

- **pick helper.md**: Methodology for point-by-point illuminance calculation
- **IES File Format**: Standard photometric data format
- **EN 12464-1**: Lighting standards reference

---

**Implementation Date**: December 3, 2025  
**Status**: ✅ Complete and Ready for Testing





