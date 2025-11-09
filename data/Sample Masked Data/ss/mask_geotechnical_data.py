#!/usr/bin/env python3
"""
Geotechnical Data Masking Script
Anonymizes project-specific geotechnical data for demonstration purposes
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class GeotechnicalDataMasker:
    def __init__(self):
        """Initialize the data masker with transformation mappings"""
        
        # Geological origin mappings
        self.geology_mapping = {
            'RS_XW': 'ROCK_A',
            'Dcf': 'SOIL_A',
            'ALLUVIUM': 'ALLUVIUM_GEN',
            'Rin': 'ROCK_B',
            'Tos': 'ROCK_C',
            'Rjbw': 'ROCK_D',
            'FILL': 'FILL_GEN',
            'TOPSOIL': 'TOPSOIL_GEN',
            'Toc': 'ROCK_E',
            'ASPHALT': 'PAVEMENT'
        }
        
        # Consistency mappings
        self.consistency_mapping = {
            'VSt': 'Very Stiff',
            'St': 'Stiff',
            'F': 'Firm',
            'M': 'Medium',
            'S': 'Soft',
            'VS': 'Very Soft',
            'H': 'Hard',
            'VH': 'Very Hard',
            'MD': 'Medium Dense',
            'D': 'Dense',
            'VD': 'Very Dense',
            'L': 'Loose',
            'VL': 'Very Loose',
            '1a': 'Grade I-a',
            '1b': 'Grade I-b',
            '2a': 'Grade II-a',
            '2b': 'Grade II-b',
            '3a': 'Grade III-a',
            '3b': 'Grade III-b',
            '4a': 'Grade IV-a',
            '4b': 'Grade IV-b',
            '5a': 'Grade V-a',
            '5b': 'Grade V-b',
            '6': 'Grade VI'
        }
        
        # Report name mappings
        self.report_mapping = {}
        self.report_counter = 1
        
        # Borehole ID mapping
        self.borehole_mapping = {}
        self.borehole_counter = 1
        
        # Location offsets
        self.easting_offset = 100000
        self.northing_offset = 50000
        self.chainage_offset = -20000
        self.rl_variation = 5  # ±5m random variation
        
    def create_borehole_mapping(self, hole_ids_list):
        """Create consistent borehole ID mapping across files"""
        unique_ids = []
        for hole_ids in hole_ids_list:
            unique_ids.extend(hole_ids)
        unique_ids = sorted(set(unique_ids))
        
        for hole_id in unique_ids:
            if hole_id not in self.borehole_mapping and pd.notna(hole_id):
                self.borehole_mapping[hole_id] = f"BH-{self.borehole_counter:03d}"
                self.borehole_counter += 1
        
        return self.borehole_mapping
    
    def mask_borehole_ids(self, df, id_column='Hole_ID'):
        """Apply borehole ID masking"""
        if id_column in df.columns:
            df[id_column] = df[id_column].map(lambda x: self.borehole_mapping.get(x, x) if pd.notna(x) else x)
        return df
    
    def mask_location_data(self, df):
        """Mask location-related data"""
        # Mask coordinates
        if 'Easting (m)' in df.columns:
            mask = df['Easting (m)'].notna()
            df.loc[mask, 'Easting (m)'] = df.loc[mask, 'Easting (m)'] + self.easting_offset
        
        if 'Northing (m)' in df.columns:
            mask = df['Northing (m)'].notna()
            df.loc[mask, 'Northing (m)'] = df.loc[mask, 'Northing (m)'] + self.northing_offset
        
        # Mask chainage
        if 'Chainage' in df.columns:
            mask = df['Chainage'].notna()
            df.loc[mask, 'Chainage'] = df.loc[mask, 'Chainage'] + self.chainage_offset
        
        # Mask surface RL with random variation
        rl_columns = ['Surface RL (m AHD)', 'Surface RL (mAHD)', 'From (m AHD)']
        for col in rl_columns:
            if col in df.columns:
                mask = df[col].notna()
                random_variation = np.random.uniform(-self.rl_variation, self.rl_variation, mask.sum())
                df.loc[mask, col] = df.loc[mask, col] + random_variation
        
        return df
    
    def mask_geological_classifications(self, df):
        """Mask geological classifications"""
        if 'Geology_Orgin' in df.columns:
            df['Geology_Orgin'] = df['Geology_Orgin'].map(lambda x: self.geology_mapping.get(x, x) if pd.notna(x) else x)
        
        if 'Consistency' in df.columns:
            df['Consistency'] = df['Consistency'].map(lambda x: self.consistency_mapping.get(x, x) if pd.notna(x) else x)
        
        return df
    
    def mask_report_names(self, df):
        """Mask report references"""
        if 'Report' in df.columns:
            unique_reports = df['Report'].dropna().unique()
            for report in unique_reports:
                if report not in self.report_mapping:
                    self.report_mapping[report] = f"Geotechnical Report {chr(64 + self.report_counter)}"
                    self.report_counter += 1
            
            df['Report'] = df['Report'].map(lambda x: self.report_mapping.get(x, x) if pd.notna(x) else x)
        
        return df
    
    def mask_spt_data(self, df):
        """Mask SPT N-values with realistic variation"""
        if 'SPT N Value' in df.columns:
            mask = df['SPT N Value'].notna()
            # Apply 0.8-1.2 random multiplier
            factors = np.random.uniform(0.8, 1.2, mask.sum())
            df.loc[mask, 'SPT N Value'] = np.round(df.loc[mask, 'SPT N Value'] * factors).astype(int)
            # Ensure minimum value of 0
            df.loc[mask, 'SPT N Value'] = df.loc[mask, 'SPT N Value'].clip(lower=0)
        
        if 'Interpreted Su (4.5)' in df.columns:
            mask = df['Interpreted Su (4.5)'].notna()
            factors = np.random.uniform(0.85, 1.15, mask.sum())
            df.loc[mask, 'Interpreted Su (4.5)'] = df.loc[mask, 'Interpreted Su (4.5)'] * factors
        
        return df
    
    def mask_atterberg_limits(self, df):
        """Mask Atterberg limits while maintaining relationships"""
        if 'LL (%)' in df.columns and 'PL (%)' in df.columns:
            # Mask Liquid Limit
            ll_mask = df['LL (%)'].notna()
            ll_variation = np.random.uniform(-5, 5, ll_mask.sum())
            df.loc[ll_mask, 'LL (%)'] = (df.loc[ll_mask, 'LL (%)'] + ll_variation).clip(lower=0)
            
            # Mask Plastic Limit proportionally
            pl_mask = df['PL (%)'].notna()
            pl_variation = np.random.uniform(-3, 3, pl_mask.sum())
            df.loc[pl_mask, 'PL (%)'] = (df.loc[pl_mask, 'PL (%)'] + pl_variation).clip(lower=0)
            
            # Recalculate PI to maintain relationship
            if 'PI (%)' in df.columns:
                pi_mask = df['LL (%)'].notna() & df['PL (%)'].notna()
                df.loc[pi_mask, 'PI (%)'] = df.loc[pi_mask, 'LL (%)'] - df.loc[pi_mask, 'PL (%)']
                df.loc[pi_mask, 'PI (%)'] = df.loc[pi_mask, 'PI (%)'].clip(lower=0)
        
        # Mask moisture content
        mc_columns = ['MC (%) - from Atterberg test', 'MC (%) - from CBR test', 'MC before Swell Test (%)']
        for col in mc_columns:
            if col in df.columns:
                mask = df[col].notna()
                variation = np.random.uniform(-2, 2, mask.sum())
                df.loc[mask, col] = (df.loc[mask, col] + variation).clip(lower=0)
        
        return df
    
    def mask_strength_parameters(self, df):
        """Mask strength parameters"""
        # UCS
        if 'UCS (MPa)' in df.columns:
            mask = df['UCS (MPa)'].notna()
            factors = np.random.uniform(0.85, 1.15, mask.sum())
            df.loc[mask, 'UCS (MPa)'] = (df.loc[mask, 'UCS (MPa)'] * factors).clip(lower=0.1)
        
        # Cohesion
        cohesion_columns = ['Cohesion (kPa)_multi_stage', 'Cohesion (kPa)_single_stage']
        for col in cohesion_columns:
            if col in df.columns:
                mask = df[col].notna()
                factors = np.random.uniform(0.9, 1.1, mask.sum())
                df.loc[mask, col] = (df.loc[mask, col] * factors).clip(lower=0)
        
        # Friction angle
        friction_columns = ['Friction angle_multi_stage', 'Friction angle_single_stage']
        for col in friction_columns:
            if col in df.columns:
                mask = df[col].notna()
                variation = np.random.uniform(-2, 2, mask.sum())
                df.loc[mask, col] = (df.loc[mask, col] + variation).clip(lower=0, upper=45)
        
        # Is50 values
        is50_columns = ['Is(50) Axial', 'Is(50) Diametral', 'Is50 combined', 'Is50d (MPa)', 'Is50a (MPa)']
        for col in is50_columns:
            if col in df.columns:
                mask = df[col].notna()
                factors = np.random.uniform(0.85, 1.15, mask.sum())
                df.loc[mask, col] = df.loc[mask, col] * factors
        
        return df
    
    def mask_compaction_data(self, df):
        """Mask compaction data"""
        if 'MDD (t/m3)' in df.columns:
            mask = df['MDD (t/m3)'].notna()
            variation = np.random.uniform(-0.05, 0.05, mask.sum())
            df.loc[mask, 'MDD (t/m3)'] = (df.loc[mask, 'MDD (t/m3)'] + variation).clip(lower=1.3, upper=2.6)
        
        if 'OMC (%)' in df.columns:
            mask = df['OMC (%)'].notna()
            variation = np.random.uniform(-2, 2, mask.sum())
            df.loc[mask, 'OMC (%)'] = (df.loc[mask, 'OMC (%)'] + variation).clip(lower=3, upper=40)
        
        return df
    
    def mask_cbr_data(self, df):
        """Mask CBR data"""
        if 'CBR (%) Soaked - 4 Days' in df.columns:
            mask = df['CBR (%) Soaked - 4 Days'].notna()
            factors = np.random.uniform(0.85, 1.15, mask.sum())
            df.loc[mask, 'CBR (%) Soaked - 4 Days'] = (df.loc[mask, 'CBR (%) Soaked - 4 Days'] * factors).clip(lower=1)
        
        if 'CBR Swell (%)' in df.columns:
            mask = df['CBR Swell (%)'].notna()
            factors = np.random.uniform(0.9, 1.1, mask.sum())
            df.loc[mask, 'CBR Swell (%)'] = (df.loc[mask, 'CBR Swell (%)'] * factors).clip(lower=0)
        
        return df
    
    def mask_chemical_properties(self, df):
        """Mask chemical properties"""
        if 'pH value' in df.columns:
            mask = df['pH value'].notna()
            variation = np.random.uniform(-0.3, 0.3, mask.sum())
            df.loc[mask, 'pH value'] = (df.loc[mask, 'pH value'] + variation).clip(lower=3, upper=10)
        
        chemical_columns = ['Sulphates (mg/kg)', 'Chlorides (mg/kg)', 'Conductivity (uS/cm)']
        for col in chemical_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    # Convert to numeric, handling any string values
                    df.loc[mask, col] = pd.to_numeric(df.loc[mask, col], errors='coerce')
                    mask = df[col].notna()  # Re-check after conversion
                    if mask.sum() > 0:
                        factors = np.random.uniform(0.8, 1.2, mask.sum())
                        df.loc[mask, col] = df.loc[mask, col] * factors
        
        return df
    
    def mask_particle_size_distribution(self, df):
        """Mask PSD data while maintaining curve shape"""
        # Find PSD columns (numeric column names representing sizes)
        psd_columns = []
        for col in df.columns:
            try:
                # Check if column name is a number (particle size)
                float(col)
                psd_columns.append(col)
            except:
                # Also check for columns with 'mm' in the name
                if 'mm' in str(col) and col not in ['0.075 mm']:
                    continue
                elif col == '0.075 mm' or (col.replace('.', '').replace(' ', '').isdigit()):
                    if col not in psd_columns:
                        psd_columns.append(col)
        
        if psd_columns:
            for idx in df.index:
                # Get all PSD values for this row
                psd_values = df.loc[idx, psd_columns]
                
                # Only process if we have valid data
                if psd_values.notna().sum() > 3:  # Need at least 3 points
                    # Apply smooth random variation
                    mask = psd_values.notna()
                    valid_cols = [col for col in psd_columns if mask[col]]
                    
                    if len(valid_cols) > 0:
                        variations = np.random.uniform(-5, 5, len(valid_cols))
                        
                        # Apply variations
                        for i, col in enumerate(valid_cols):
                            new_val = df.loc[idx, col] + variations[i]
                            df.loc[idx, col] = np.clip(new_val, 0, 100)
                        
                        # Normalize to maintain monotonic increase
                        values = df.loc[idx, valid_cols].values
                        values = np.sort(values)  # Ensure monotonic
                        df.loc[idx, valid_cols] = values
        
        return df
    
    def process_file(self, input_file, output_file, file_type='interp'):
        """Process a complete Excel file"""
        print(f"Processing {input_file}...")
        
        # Read the Excel file
        df = pd.read_excel(input_file)
        original_shape = df.shape
        
        # Apply transformations
        df = self.mask_borehole_ids(df)
        df = self.mask_location_data(df)
        df = self.mask_geological_classifications(df)
        df = self.mask_report_names(df)
        
        # Apply technical data masking for lab summary file
        if file_type == 'lab':
            df = self.mask_spt_data(df)
            df = self.mask_atterberg_limits(df)
            df = self.mask_strength_parameters(df)
            df = self.mask_compaction_data(df)
            df = self.mask_cbr_data(df)
            df = self.mask_chemical_properties(df)
            df = self.mask_particle_size_distribution(df)
        
        # Save the masked file
        df.to_excel(output_file, index=False)
        print(f"  Saved to {output_file}")
        print(f"  Shape: {original_shape} -> {df.shape}")
        
        return df
    
    def generate_report(self, output_file='Masking_Report.txt'):
        """Generate a report of all transformations applied"""
        with open(output_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("GEOTECHNICAL DATA MASKING REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("1. BOREHOLE ID MAPPINGS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total boreholes masked: {len(self.borehole_mapping)}\n")
            f.write("Sample mappings:\n")
            for i, (orig, new) in enumerate(list(self.borehole_mapping.items())[:10]):
                f.write(f"  {orig} -> {new}\n")
            f.write("\n")
            
            f.write("2. LOCATION DATA OFFSETS\n")
            f.write("-" * 30 + "\n")
            f.write(f"Easting offset: +{self.easting_offset:,} m\n")
            f.write(f"Northing offset: +{self.northing_offset:,} m\n")
            f.write(f"Chainage offset: {self.chainage_offset:,} m\n")
            f.write(f"Surface RL variation: ±{self.rl_variation} m\n\n")
            
            f.write("3. GEOLOGICAL CLASSIFICATIONS\n")
            f.write("-" * 30 + "\n")
            f.write("Geology mappings:\n")
            for orig, new in self.geology_mapping.items():
                f.write(f"  {orig} -> {new}\n")
            f.write("\n")
            
            f.write("4. REPORT REFERENCES\n")
            f.write("-" * 30 + "\n")
            f.write(f"Total reports masked: {len(self.report_mapping)}\n")
            for orig, new in self.report_mapping.items():
                f.write(f"  {orig} -> {new}\n")
            f.write("\n")
            
            f.write("5. TECHNICAL DATA VARIATIONS\n")
            f.write("-" * 30 + "\n")
            f.write("SPT N-values: 0.8-1.2x multiplier\n")
            f.write("Atterberg Limits: ±5% for LL, ±3% for PL\n")
            f.write("UCS: 0.85-1.15x multiplier\n")
            f.write("Cohesion: 0.9-1.1x multiplier\n")
            f.write("Friction angle: ±2 degrees\n")
            f.write("MDD: ±0.05 t/m³\n")
            f.write("OMC: ±2%\n")
            f.write("CBR: 0.85-1.15x multiplier\n")
            f.write("pH: ±0.3 units\n")
            f.write("Chemical properties: 0.8-1.2x multiplier\n")
            f.write("PSD: ±5% smooth variation\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")
        
        print(f"Report saved to {output_file}")


def main():
    """Main execution function"""
    print("=" * 60)
    print("GEOTECHNICAL DATA MASKING TOOL")
    print("=" * 60)
    
    # Initialize the masker
    masker = GeotechnicalDataMasker()
    
    # File paths
    file1_input = "BH_Interp - LGCFR.xlsx"
    file1_output = "BH_Interp_DEMO.xlsx"
    
    file2_input = "Lab_summary_final_with_SPT - LGCFR.xlsx"
    file2_output = "Lab_summary_final_with_SPT_DEMO.xlsx"
    
    # Read both files to create consistent borehole mapping
    print("\n1. Creating consistent borehole ID mappings...")
    df1_temp = pd.read_excel(file1_input)
    df2_temp = pd.read_excel(file2_input)
    
    masker.create_borehole_mapping([
        df1_temp['Hole_ID'].unique(),
        df2_temp['Hole_ID'].unique()
    ])
    print(f"   Created mappings for {len(masker.borehole_mapping)} unique boreholes")
    
    # Process both files
    print("\n2. Processing files...")
    df1 = masker.process_file(file1_input, file1_output, file_type='interp')
    df2 = masker.process_file(file2_input, file2_output, file_type='lab')
    
    # Generate report
    print("\n3. Generating transformation report...")
    masker.generate_report()
    
    # Verify data integrity
    print("\n4. Verifying data integrity...")
    
    # Check common boreholes are consistent
    df1_holes = set(df1['Hole_ID'].unique())
    df2_holes = set(df2['Hole_ID'].unique())
    common = df1_holes.intersection(df2_holes)
    print(f"   Common boreholes after masking: {len(common)}")
    
    # Check data ranges
    if 'SPT N Value' in df2.columns:
        print(f"   SPT range: {df2['SPT N Value'].min():.0f} - {df2['SPT N Value'].max():.0f}")
    if 'UCS (MPa)' in df2.columns:
        print(f"   UCS range: {df2['UCS (MPa)'].min():.1f} - {df2['UCS (MPa)'].max():.1f} MPa")
    
    print("\n" + "=" * 60)
    print("DATA MASKING COMPLETE!")
    print("Output files:")
    print(f"  - {file1_output}")
    print(f"  - {file2_output}")
    print(f"  - Masking_Report.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()