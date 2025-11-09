# Streamlit Multi-Page App UX/UI Design Plan

## Overview

This document outlines the UX/UI architecture for transforming the Jupyter notebook geophysics analysis backend into an interactive Streamlit multi-page application.

## Analysis of Jupyter Notebook Backend

Your `Analysis.ipynb` implements a comprehensive geophysics-borehole correlation analysis workflow:

### Phase 1: Data Import & Setup
- Import multiple geophysics CSV files from a folder
- Import borehole interpretation data (BH_interp Excel file)
- Import lab test summary with UCS, SPT, and Atterberg results
- Configure analysis parameters (thresholds and ranges)

### Phase 2: Spatial Registration
- Match geophysics lines with nearby boreholes using coordinate proximity
- Create `geophysics_BH_register` mapping based on:
  - Tangential distance along geophysics line
  - Perpendicular offset from geophysics line
  - Configurable thresholds for matching

### Phase 3: Data Merging
- Merge geophysics velocity data with borehole consistency information
- Merge lab test results (UCS, SPT) with merged geophysics-BH data
- Create comprehensive `geophysics_bh_results_df` and `geophysics_bh_lab` dataframes

### Phase 4: Visualization
- Single geophysics line analysis with multiple overlay options
- Consistency mapping with customizable color schemes
- Lab results visualization (UCS, SPT, Atterberg)
- Background geophysics data for context

### Phase 5: Statistical Analysis
- Consistency vs Velocity correlations (scatter, box plots, bar charts)
- SPT vs Velocity trend analysis with OLS regression
- UCS vs Velocity relationship analysis
- Soil type categorization and grouping

---

## Page Structure Mapping

### **Page 1: Data Upload & Overview**
**Current File**: `pages/data.py`
**Purpose**: Data ingestion, quick overview, and interactive assistance

#### Features:
- **Geophysics File Upload** ✅
  - Multiple CSV file uploader in sidebar
  - Display uploaded files in dynamic multi-column grid
  - Show file preview (first 20 rows)
  - Clear all files button

- **New: Borehole Data Upload**
  - Upload BH_interp Excel file
  - Display sample data and column information
  - Validation: Check required columns exist

- **New: Lab Summary Upload**
  - Upload Lab_summary Excel file
  - Display sample data with test types
  - Validation: Check for UCS, SPT, Atterberg data

- **Quick Data Summary** (Calculated on upload)
  - Total geophysics files: count
  - Total boreholes loaded: count
  - Data coverage: chainage ranges, depth ranges
  - Status indicators: ready to process or missing data

- **AI Assistant Chatbot** ✅
  - ChatGPT-style interface with message bubbles
  - Short-term memory (last 5 messages)
  - Specialized for geophysics/geotechnical questions

#### UI Layout:
```
┌─────────────────────────────────────────────┐
│ 👏 Geophysics and its Engineering Friends  │
├─────────────────────────────────────────────┤
│ [Data Summary Cards]                        │
│ - Files Uploaded: X                         │
│ - Boreholes: Y                              │
│ - Ready to Process: [Yes/No]                │
│                                             │
│ Uploaded Files Grid                         │
│ [File 1] [File 2] [File 3]                 │
│ [File 4] [File 5] [File 6]                 │
│                                             │
│ ───────────────────────────────────────────│
│ 💬 AI Assistant                             │
│ [Chat History]                              │
│ [Chat Input]                                │
└─────────────────────────────────────────────┘
```

---

### **Page 2: Data Processing & Configuration**
**Current File**: `pages/data_processing.py`
**Purpose**: Configure parameters, run spatial registration, and merge data

#### Section 1: Parameter Configuration
- **TANGENT_THRESHOLD** (default: 5)
  - Slider: 0 to 20 m
  - Tooltip: "Maximum tangential distance (m) to match boreholes to geophysics line edges"

- **PERPENDICULAR_THRESHOLD** (default: 25)
  - Slider: 0 to 100 m
  - Tooltip: "Maximum perpendicular offset (m) to consider borehole near geophysics line"

- **CHAINAGE_RANGE** (default: 0.5)
  - Slider: 0 to 5 m
  - Tooltip: "Range (m) around BH chainage to extract geophysics data"

- **Consistency Order** (for plotting)
  - Multi-select: VS, S, F, St, VSt, H, VL, L, MD, D, VD, 5a-1b
  - Reorder using drag-and-drop (optional enhancement)

#### Section 2: Run Registration
- **Status Indicator**: Ready/Processing/Complete/Error
- **Execute Button**: "Run Geophysics-BH Registration"
  - Disabled until data is uploaded
  - Shows progress bar during processing

- **Results Display**:
  - Summary statistics
    - Total geophysics-BH matches: count
    - Matches within line: count
    - Matches before line: count
    - Matches after line: count

  - Interactive data table: `geophysics_BH_register`
    - Sortable columns: Geophysics_ID, Hole_ID, Chainage, Offset
    - Filterable by Geophysics_ID
    - Export as CSV button

#### Section 3: Data Merging
- **Merge Borehole Consistency**
  - Button: "Merge BH Consistency Data"
  - Shows: Number of records created
  - Display: Preview of `geophysics_bh_results_df`

- **Merge Lab Results**
  - Button: "Merge Lab Test Results"
  - Shows: Number of lab records matched, unmatched records
  - Display: Preview of `geophysics_bh_lab`
  - Warning if many records unmatched

- **Data Quality Checks**
  - Validation message for missing data
  - Suggestions for parameter adjustment if few matches found

#### UI Layout:
```
┌─────────────────────────────────────────────┐
│ 🛠️ Data Processing & Configuration         │
├─────────────────────────────────────────────┤
│ ⚙️ Parameter Settings                       │
│ TANGENT_THRESHOLD: ─────●────── (5)        │
│ PERPENDICULAR_THRESHOLD: ─────●─── (25)    │
│ CHAINAGE_RANGE: ──────●────── (0.5)        │
│                                             │
│ Consistency Order: [Select Multiple]        │
│ [VS] [S] [F] [St] ...                      │
│                                             │
│ ─────────────────────────────────────────  │
│ 📊 Registration Results                     │
│ [Run Registration Button]                   │
│                                             │
│ Total Matches: 25                           │
│ [Table: geophysics_BH_register]             │
│                                             │
│ ─────────────────────────────────────────  │
│ 🔗 Data Merging                             │
│ [Merge Consistency] [Merge Lab Results]    │
│                                             │
│ [Preview Tables]                            │
└─────────────────────────────────────────────┘
```

---

### **Page 3: Single Geophysics Line Analysis**
**Current File**: `pages/single_demo.py`
**Purpose**: Detailed analysis of one selected geophysics line with multiple visualization options

#### Section 1: Line Selection
- **Dropdown**: Select geophysics line
  - Auto-populate from uploaded files
  - Show basic stats (chainage length, velocity range, BH matches)

#### Section 2: Raw Geophysics Data
- **Plot**: Scatter plot (Chainage vs Elevation)
  - Color by: Velocity
  - Hover data: Chainage, Elevation, Velocity
  - Range indicators on axes
  - Title: "Raw Geophysics Data - [Line Name]"

#### Section 3: Borehole Consistency Visualization
- **Tabs**:
  - Tab 1: Consistency Colors
    - Scatter plot colored by consistency category
    - Predefined color scheme matching soil type
    - Hover: Hole_ID, Consistency, Geology

  - Tab 2: Velocity Overlay
    - Scatter plot colored by velocity (jet colorscale)
    - Continuous color bar with S-velocity (m/s)

  - Tab 3: Combined Overlay
    - Background geophysics plot (low opacity)
    - Foreground borehole points colored by consistency
    - Interactive legend

- **Settings Panel** (collapsible):
  - Plot range controls
    - xmin, xmax (chainage range)
    - ymin, ymax (elevation range)
    - Auto-scale button
  - Marker size slider (2-15 px)
  - Opacity slider for background geophysics (0-100%)

#### Section 4: Lab Results Visualization
- **Radio Button**: Select lab parameter
  - Options: SPT N-value, UCS (MPa), Liquid Limit (%)

- **Plot**:
  - Scatter plot with selected lab parameter
  - Points colored by category (discrete colors)
  - Background geophysics as reference
  - Hover: Hole_ID, Lab Result, Depth

- **Alternative**: Box plot of lab results grouped by consistency

#### UI Layout:
```
┌──────────────────────────────────────────────────┐
│ 🧪 Single Geophysics Line Analysis              │
├──────────────────────────────────────────────────┤
│ Select Line: [Dropdown: AU-GP163-01]             │
│ Stats: 250m, Vel: 50-950 m/s, 8 BH matches     │
│                                                  │
│ ┌──────────────┬────────────────────────────┐  │
│ │ Raw Data     │ [Plot: Chainage vs Elev]   │  │
│ ├──────────────┼────────────────────────────┤  │
│ │ BH Analysis: │                            │  │
│ │ • Consistency│ [Plot: Colored by Consist] │  │
│ │ • Velocity   │                            │  │
│ │ • Overlay    │ [Settings: Range, Size]    │  │
│ ├──────────────┼────────────────────────────┤  │
│ │ Lab Results: │                            │  │
│ │ • SPT        │ [Plot: Lab Results]        │  │
│ │ • UCS        │                            │  │
│ │ • Atterberg  │                            │  │
│ └──────────────┴────────────────────────────┘  │
└──────────────────────────────────────────────────┘
```

---

### **Page 4: Multiple Lines Analysis & Statistics**
**Current File**: `pages/multiple_analysis.py`
**Purpose**: Compare multiple geophysics lines and perform statistical analysis

#### Section 1: Multi-Line Comparison
- **Multi-select Dropdown**: Choose geophysics lines
  - Default: All lines
  - Show preview statistics for selected lines

- **Comparison Mode** (Radio buttons):
  - Side-by-side: Multiple columns, one row
  - Stacked: Single column, multiple rows
  - Overlay: All on same plot with different colors

- **Plot Type** (Radio buttons):
  - Consistency view (colored by consistency)
  - Velocity view (colored by velocity)
  - Lab results view (colored by selected lab parameter)

#### Section 2: Statistical Analysis
- **Tab 1: Consistency vs Velocity**
  - Plot Type Options:
    - Scatter plot with soil type coloring
    - Box plot: Consistency on Y-axis, Velocity on X-axis
    - Bar chart: Mean velocity ± std by consistency

  - Display:
    - Statistical summary table
    - Correlation statistics (if applicable)
    - Export data button

- **Tab 2: SPT vs Velocity**
  - Scatter plot with OLS trendline
  - Faceted by soil type
  - Display:
    - Equation and R² for each soil type
    - Confidence interval band
    - Summary statistics table

- **Tab 3: UCS vs Velocity**
  - Scatter plot with OLS trendline
  - Overall and by soil type
  - Display:
    - Equation and R²
    - Confidence interval
    - Data point count and quality metrics

- **Tab 4: Custom Analysis**
  - Select X-axis variable (dropdown)
  - Select Y-axis variable (dropdown)
  - Select color variable (dropdown)
  - Auto-generate scatter plot with basic statistics

#### Section 3: Export & Download
- **Data Export**:
  - Button: Download `geophysics_bh_results_df` (CSV/Excel)
  - Button: Download `geophysics_bh_lab` (CSV/Excel)
  - Button: Download `geophysics_BH_register` (CSV/Excel)

- **Plot Export**:
  - Button: Download current plot (PNG/HTML)
  - Export all statistical plots as PDF report

#### UI Layout:
```
┌──────────────────────────────────────────────────┐
│ 📊 Multiple Lines Analysis & Statistics         │
├──────────────────────────────────────────────────┤
│ Select Lines: [Multi-select dropdown]            │
│ View Mode: ○ Side-by-side ○ Stacked ○ Overlay  │
│ Plot Type: ○ Consistency ○ Velocity ○ Lab Res   │
│                                                  │
│ ┌──────────────────────────────────────────────┐ │
│ │ [Comparison Plots]                           │ │
│ │ [Multiple geophysics lines visualization]   │ │
│ └──────────────────────────────────────────────┘ │
│                                                  │
│ ┌─ Statistical Analysis ──────────────────────┐ │
│ │ • Consistency vs Velocity                    │ │
│ │   [Box Plot/Bar Chart]                       │ │
│ │                                              │ │
│ │ • SPT vs Velocity                            │ │
│ │   [Scatter with Trendline]                   │ │
│ │                                              │ │
│ │ • UCS vs Velocity                            │ │
│ │   [Scatter with Trendline]                   │ │
│ │                                              │ │
│ │ • Custom Analysis                            │ │
│ │   [Axis selectors] [Dynamic plot]            │ │
│ └──────────────────────────────────────────────┘ │
│                                                  │
│ [Download Data] [Download Plots] [Export PDF]   │
└──────────────────────────────────────────────────┘
```

---

## Key UX/UI Enhancements

### 1. Progressive Workflow
- Guide users through logical steps: Upload → Process → Analyze
- Lock pages until prerequisites are met (e.g., can't analyze without processing data)
- Show completion badges/checkmarks for each step

### 2. Session State Management
- Persist all dataframes across page navigation
- Cache processed results to avoid recomputation
- Allow users to go back and modify parameters without losing other work
- Show last updated timestamp for each dataset

### 3. Interactive Visualizations
- Use Plotly for all plots (zoom, pan, hover tooltips)
- Custom hover templates showing relevant information
- Click-to-select features for drilling down into data
- Synchronized plots when viewing same data with different parameters

### 4. Feedback & Validation
- Progress bars for long-running operations
- Success/error messages with actionable solutions
- Data quality warnings (e.g., "Only 3 BH matches found, consider increasing thresholds")
- Validation checks before operations:
  - Required files uploaded
  - Columns exist and have expected data types
  - No critical missing data

### 5. Data Accessibility
- Quick stats cards showing data overview
- Searchable/filterable data tables
- Export functionality for all major datasets
- Ability to compare specific boreholes or lines

### 6. Visual Consistency
- Standardized color schemes:
  - Consistency categories: predefined colors
  - Velocity: jet colorscale (50-950 m/s)
  - Soil type: categorical colors
- Consistent plot styling and layouts
- Responsive design for different screen sizes

### 7. Help & Documentation
- Tooltips on parameters explaining their meaning and typical values
- Expandable sections with methodology explanations
- Links to parameter documentation
- Example workflows and use cases

---

## Implementation Priority & Phases

### Phase 1: Core Functionality (Foundation)
**Estimated Timeline**: 2-3 weeks

1. **Data Page Enhancement**
   - Add BH_interp Excel file uploader
   - Add Lab_summary Excel file uploader
   - Display quick data summary cards
   - Data validation and error handling

2. **Data Processing Page**
   - Implement parameter sliders
   - Create registration execution button
   - Display results table with sorting/filtering
   - Merge data buttons and results display

3. **Single Demo Page Enhancement**
   - Dropdown to select geophysics line
   - Raw geophysics plot
   - Borehole consistency plot
   - Tab-based visualization switching
   - Plot settings (range, opacity, marker size)

### Phase 2: Enhanced Analysis (Advanced Features)
**Estimated Timeline**: 2-3 weeks

4. **Multiple Analysis Page**
   - Multi-select dropdown for line selection
   - Side-by-side/stacked/overlay comparison modes
   - Statistical analysis tabs (Consistency vs Velocity, SPT vs Velocity, UCS vs Velocity)
   - OLS regression implementation with visualization
   - Statistical summary tables

5. **Export Functionality**
   - CSV/Excel export for dataframes
   - PNG/HTML export for plots
   - PDF report generation (optional)

### Phase 3: Polish & Optimization (User Experience)
**Estimated Timeline**: 1-2 weeks

6. **UI Refinement**
   - Improve visual hierarchy and layout
   - Add spinner/loading animations
   - Enhance color schemes and typography
   - Mobile responsiveness testing

7. **Performance Optimization**
   - Cache expensive computations
   - Implement lazy loading for large plots
   - Optimize data table rendering

8. **Documentation**
   - User guide/help sections
   - Parameter documentation
   - Workflow examples
   - Troubleshooting guide

### Phase 4: Advanced Features (Future Enhancements)
**Estimated Timeline**: Ongoing

9. **Machine Learning Integration**
   - Predictive models for velocity-consistency relationships
   - Anomaly detection in data
   - Automated parameter suggestions

10. **Advanced Visualizations**
    - 3D scatter plots
    - Cross-section views
    - Heatmaps for spatial analysis
    - Interactive geological interpretation tools

11. **Collaboration Features**
    - Save/load analysis configurations
    - Share results with team
    - Annotation and comment system
    - Version control for analyses

---

## Technical Architecture Considerations

### Data Pipeline
```
Upload → Validation → Session State → Processing → Display → Export
  ↓         ↓            ↓             ↓            ↓        ↓
Files   Checks      Streamlit      Functions   Plotly    CSV/Excel
        Format      State Dict     in Memory   Charts    PDF Reports
```

### Session State Structure
```python
st.session_state = {
    'uploaded_files': [list of geophysics CSV files],
    'all_geophysics': {
        'geophysics_data': {file_name: dataframe, ...},
        'geophysics_BH_register': dataframe,
        'geophysics_bh_results_df': dataframe,
        'geophysics_bh_lab': dataframe,
    },
    'parameters': {
        'tangent_threshold': 5,
        'perpendicular_threshold': 25,
        'chainage_range': 0.5,
    },
    'bh_data': dataframe,
    'lab_data': dataframe,
    'processing_status': 'complete' | 'processing' | 'pending',
}
```

### Key Functions to Implement/Import
- `process_individual_geophysics()` - Already in notebook
- `offset_bh_geophysics_line()` - Already in notebook
- `add_to_register()` - Already in notebook
- `merge_geophysics_bh_consistency()` - Already in notebook
- `classify_soil()` - Already in notebook
- `merge_lab_into_results()` - Already in notebook
- `plot_geophysics()` - Already in notebook
- `add_label()` - Already in notebook

---

## Success Metrics

1. **Functionality**
   - All notebook workflows reproducible in Streamlit
   - Data processing produces identical results
   - All visualizations match notebook outputs

2. **Usability**
   - Users can complete workflow in <5 minutes
   - Zero data loss when navigating between pages
   - Clear feedback on all operations

3. **Performance**
   - Plot rendering: <2 seconds
   - Data registration: <10 seconds for typical datasets
   - Page navigation: <1 second

4. **Data Quality**
   - Input validation catches 100% of critical issues
   - Error messages guide users to solutions
   - Export data matches source calculations

---

## Future Enhancement Ideas

1. **Real-time Collaboration**: Share live analysis sessions with team members
2. **Custom Reporting**: Generate professional PDF/Word reports with selections
3. **Predictive Analytics**: ML models to predict consistency/quality from velocity
4. **Database Integration**: Store processed results in database for historical analysis
5. **Mobile App**: Companion mobile app for field data collection and quick analysis
6. **API Endpoint**: REST API for programmatic access to analysis functions
7. **Version Control**: Track analysis versions and parameter changes over time
