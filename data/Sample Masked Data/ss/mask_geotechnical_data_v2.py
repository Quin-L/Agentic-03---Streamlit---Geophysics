#!/usr/bin/env python3
"""
Geotechnical Data Masking Script V2
- Limits to 100 boreholes with spatial distribution
- Applies proper coordinate transformation within UTM Zone 56
"""

import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Set random seed for reproducibility
np.random.seed(42)

class GeotechnicalDataMaskerV2:
    def __init__(self, max_boreholes=100):
        """Initialize the data masker with transformation mappings"""
        
        self.max_boreholes = max_boreholes
        self.selected_boreholes = []
        
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
        
        # Coordinate transformation parameters
        self.coord_transform = {
            'rotation_angle': np.random.uniform(15, 45),  # Degrees
            'translation_e': np.random.uniform(-30000, 30000),  # Within Zone 56
            'translation_n': np.random.uniform(-20000, 20000),
            'scatter_radius': 500  # Random scatter up to 500m
        }
        
        # Store original coordinates for selected boreholes
        self.original_coords = {}
        self.transformed_coords = {}
        
    def select_boreholes_spatially(self, df_lab, df_interp):
        """Select 100 boreholes with good spatial distribution"""
        print(f"\nSelecting {self.max_boreholes} boreholes with spatial distribution...")
        
        # Get boreholes that have coordinates
        df_with_coords = df_lab[df_lab['Easting (m)'].notna() & df_lab['Northing (m)'].notna()]
        unique_bh_coords = df_with_coords.groupby('Hole_ID').first()[['Easting (m)', 'Northing (m)']].reset_index()
        
        if len(unique_bh_coords) <= self.max_boreholes:
            # If we have fewer than requested, take all
            selected_bh = unique_bh_coords['Hole_ID'].tolist()
        else:
            # Use spatial sampling to get well-distributed points
            coords = unique_bh_coords[['Easting (m)', 'Northing (m)']].values
            
            try:
                # K-means clustering approach to ensure spatial distribution
                from sklearn.cluster import KMeans
                kmeans = KMeans(n_clusters=min(self.max_boreholes, len(unique_bh_coords)), 
                              random_state=42, n_init=10)
                kmeans.fit(coords)
                
                # Select one borehole closest to each cluster center
                selected_indices = []
                for center in kmeans.cluster_centers_:
                    distances = np.sqrt(((coords - center) ** 2).sum(axis=1))
                    closest_idx = np.argmin(distances)
                    if closest_idx not in selected_indices:
                        selected_indices.append(closest_idx)
                
                # If we need more, add random selections
                while len(selected_indices) < self.max_boreholes and len(selected_indices) < len(unique_bh_coords):
                    idx = np.random.randint(0, len(unique_bh_coords))
                    if idx not in selected_indices:
                        selected_indices.append(idx)
            except ImportError:
                # Alternative: Grid-based selection for spatial distribution
                e_min, e_max = coords[:, 0].min(), coords[:, 0].max()
                n_min, n_max = coords[:, 1].min(), coords[:, 1].max()
                
                # Create a grid
                grid_size = int(np.sqrt(self.max_boreholes))
                e_bins = np.linspace(e_min, e_max, grid_size + 1)
                n_bins = np.linspace(n_min, n_max, grid_size + 1)
                
                selected_indices = []
                for i in range(grid_size):
                    for j in range(grid_size):
                        # Find points in this grid cell
                        mask = ((coords[:, 0] >= e_bins[i]) & (coords[:, 0] < e_bins[i+1]) &
                               (coords[:, 1] >= n_bins[j]) & (coords[:, 1] < n_bins[j+1]))
                        cell_indices = np.where(mask)[0]
                        
                        if len(cell_indices) > 0:
                            # Select one random point from this cell
                            selected_idx = np.random.choice(cell_indices)
                            selected_indices.append(selected_idx)
                            
                            if len(selected_indices) >= self.max_boreholes:
                                break
                    if len(selected_indices) >= self.max_boreholes:
                        break
                
                # If we need more, add random selections
                while len(selected_indices) < self.max_boreholes and len(selected_indices) < len(unique_bh_coords):
                    idx = np.random.randint(0, len(unique_bh_coords))
                    if idx not in selected_indices:
                        selected_indices.append(idx)
            
            selected_bh = unique_bh_coords.iloc[selected_indices]['Hole_ID'].tolist()
        
        # Also include boreholes that are in BH_Interp but not in Lab_summary
        all_interp_bh = df_interp['Hole_ID'].unique()
        additional_bh = [bh for bh in all_interp_bh if bh not in df_lab['Hole_ID'].unique()]
        
        # Add some of these if we have room
        remaining_slots = self.max_boreholes - len(selected_bh)
        if remaining_slots > 0 and additional_bh:
            selected_bh.extend(additional_bh[:remaining_slots])
        
        self.selected_boreholes = selected_bh[:self.max_boreholes]
        print(f"  Selected {len(self.selected_boreholes)} boreholes")
        
        # Store original coordinates for transformation
        for bh in self.selected_boreholes:
            bh_data = df_with_coords[df_with_coords['Hole_ID'] == bh]
            if not bh_data.empty:
                self.original_coords[bh] = {
                    'easting': bh_data.iloc[0]['Easting (m)'],
                    'northing': bh_data.iloc[0]['Northing (m)']
                }
        
        return self.selected_boreholes
    
    def transform_coordinates(self, easting, northing, borehole_id=None):
        """Apply rotation, translation, and random scatter to coordinates"""
        if pd.isna(easting) or pd.isna(northing):
            return easting, northing
        
        # Get center of original coordinates for rotation
        if self.original_coords:
            center_e = np.mean([c['easting'] for c in self.original_coords.values() if not pd.isna(c['easting'])])
            center_n = np.mean([c['northing'] for c in self.original_coords.values() if not pd.isna(c['northing'])])
        else:
            center_e = 513283  # Approximate center from analysis
            center_n = 6940374
        
        # Translate to origin
        e_centered = easting - center_e
        n_centered = northing - center_n
        
        # Apply rotation
        angle_rad = np.radians(self.coord_transform['rotation_angle'])
        e_rotated = e_centered * np.cos(angle_rad) - n_centered * np.sin(angle_rad)
        n_rotated = e_centered * np.sin(angle_rad) + n_centered * np.cos(angle_rad)
        
        # Translate back and apply overall translation
        e_transformed = e_rotated + center_e + self.coord_transform['translation_e']
        n_transformed = n_rotated + center_n + self.coord_transform['translation_n']
        
        # Add random scatter (consistent for same borehole)
        if borehole_id:
            if borehole_id not in self.transformed_coords:
                # Generate random scatter for this borehole
                scatter_angle = np.random.uniform(0, 2 * np.pi)
                scatter_dist = np.random.uniform(0, self.coord_transform['scatter_radius'])
                scatter_e = scatter_dist * np.cos(scatter_angle)
                scatter_n = scatter_dist * np.sin(scatter_angle)
                self.transformed_coords[borehole_id] = {'scatter_e': scatter_e, 'scatter_n': scatter_n}
            else:
                scatter_e = self.transformed_coords[borehole_id]['scatter_e']
                scatter_n = self.transformed_coords[borehole_id]['scatter_n']
            
            e_transformed += scatter_e
            n_transformed += scatter_n
        
        # Ensure we stay within reasonable UTM Zone 56 bounds
        e_transformed = np.clip(e_transformed, 300000, 700000)
        n_transformed = np.clip(n_transformed, 6800000, 7100000)
        
        return e_transformed, n_transformed
    
    def create_borehole_mapping(self):
        """Create borehole ID mapping for selected boreholes only"""
        for hole_id in self.selected_boreholes:
            if pd.notna(hole_id):
                self.borehole_mapping[hole_id] = f"BH-{self.borehole_counter:03d}"
                self.borehole_counter += 1
        
        return self.borehole_mapping
    
    def filter_and_mask_boreholes(self, df, id_column='Hole_ID'):
        """Filter to selected boreholes and apply ID masking"""
        # Filter to selected boreholes
        df_filtered = df[df[id_column].isin(self.selected_boreholes)].copy()
        
        # Apply ID masking
        if id_column in df_filtered.columns:
            df_filtered[id_column] = df_filtered[id_column].map(
                lambda x: self.borehole_mapping.get(x, x) if pd.notna(x) else x
            )
        
        return df_filtered
    
    def mask_location_data(self, df):
        """Mask location-related data with proper coordinate transformation"""
        # Apply coordinate transformation
        if 'Easting (m)' in df.columns and 'Northing (m)' in df.columns:
            # Get borehole ID for consistent scatter
            for idx in df.index:
                bh_id = df.loc[idx, 'Hole_ID'] if 'Hole_ID' in df.columns else None
                e_orig = df.loc[idx, 'Easting (m)']
                n_orig = df.loc[idx, 'Northing (m)']
                
                if pd.notna(e_orig) and pd.notna(n_orig):
                    e_new, n_new = self.transform_coordinates(e_orig, n_orig, bh_id)
                    df.loc[idx, 'Easting (m)'] = e_new
                    df.loc[idx, 'Northing (m)'] = n_new
        
        # Transform chainage with smaller variation
        if 'Chainage' in df.columns:
            mask = df['Chainage'].notna()
            # Add random variation between -5000 and +5000
            variation = np.random.uniform(-5000, 5000)
            df.loc[mask, 'Chainage'] = df.loc[mask, 'Chainage'] + variation
        
        # Mask surface RL with random variation
        rl_columns = ['Surface RL (m AHD)', 'Surface RL (mAHD)', 'From (m AHD)']
        for col in rl_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    random_variation = np.random.uniform(-10, 10, mask.sum())
                    df.loc[mask, col] = df.loc[mask, col] + random_variation
        
        return df
    
    def mask_geological_classifications(self, df):
        """Mask geological classifications"""
        if 'Geology_Orgin' in df.columns:
            df['Geology_Orgin'] = df['Geology_Orgin'].map(
                lambda x: self.geology_mapping.get(x, x) if pd.notna(x) else x
            )
        
        if 'Consistency' in df.columns:
            df['Consistency'] = df['Consistency'].map(
                lambda x: self.consistency_mapping.get(x, x) if pd.notna(x) else x
            )
        
        return df
    
    def mask_report_names(self, df):
        """Mask report references"""
        if 'Report' in df.columns:
            unique_reports = df['Report'].dropna().unique()
            for report in unique_reports:
                if report not in self.report_mapping:
                    self.report_mapping[report] = f"Geotechnical Report {chr(64 + self.report_counter)}"
                    self.report_counter += 1
            
            df['Report'] = df['Report'].map(
                lambda x: self.report_mapping.get(x, x) if pd.notna(x) else x
            )
        
        return df
    
    # Include all the technical data masking methods from the original script
    def mask_spt_data(self, df):
        """Mask SPT N-values with realistic variation"""
        if 'SPT N Value' in df.columns:
            mask = df['SPT N Value'].notna()
            if mask.sum() > 0:
                factors = np.random.uniform(0.8, 1.2, mask.sum())
                df.loc[mask, 'SPT N Value'] = np.round(df.loc[mask, 'SPT N Value'] * factors).astype(int)
                df.loc[mask, 'SPT N Value'] = df.loc[mask, 'SPT N Value'].clip(lower=0)
        
        if 'Interpreted Su (4.5)' in df.columns:
            mask = df['Interpreted Su (4.5)'].notna()
            if mask.sum() > 0:
                factors = np.random.uniform(0.85, 1.15, mask.sum())
                df.loc[mask, 'Interpreted Su (4.5)'] = df.loc[mask, 'Interpreted Su (4.5)'] * factors
        
        return df
    
    def mask_atterberg_limits(self, df):
        """Mask Atterberg limits while maintaining relationships"""
        if 'LL (%)' in df.columns and 'PL (%)' in df.columns:
            ll_mask = df['LL (%)'].notna()
            if ll_mask.sum() > 0:
                ll_variation = np.random.uniform(-5, 5, ll_mask.sum())
                df.loc[ll_mask, 'LL (%)'] = (df.loc[ll_mask, 'LL (%)'] + ll_variation).clip(lower=0)
            
            pl_mask = df['PL (%)'].notna()
            if pl_mask.sum() > 0:
                pl_variation = np.random.uniform(-3, 3, pl_mask.sum())
                df.loc[pl_mask, 'PL (%)'] = (df.loc[pl_mask, 'PL (%)'] + pl_variation).clip(lower=0)
            
            if 'PI (%)' in df.columns:
                pi_mask = df['LL (%)'].notna() & df['PL (%)'].notna()
                df.loc[pi_mask, 'PI (%)'] = df.loc[pi_mask, 'LL (%)'] - df.loc[pi_mask, 'PL (%)']
                df.loc[pi_mask, 'PI (%)'] = df.loc[pi_mask, 'PI (%)'].clip(lower=0)
        
        mc_columns = ['MC (%) - from Atterberg test', 'MC (%) - from CBR test', 'MC before Swell Test (%)']
        for col in mc_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    variation = np.random.uniform(-2, 2, mask.sum())
                    df.loc[mask, col] = (df.loc[mask, col] + variation).clip(lower=0)
        
        return df
    
    def mask_strength_parameters(self, df):
        """Mask strength parameters"""
        if 'UCS (MPa)' in df.columns:
            mask = df['UCS (MPa)'].notna()
            if mask.sum() > 0:
                factors = np.random.uniform(0.85, 1.15, mask.sum())
                df.loc[mask, 'UCS (MPa)'] = (df.loc[mask, 'UCS (MPa)'] * factors).clip(lower=0.1)
        
        cohesion_columns = ['Cohesion (kPa)_multi_stage', 'Cohesion (kPa)_single_stage']
        for col in cohesion_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    factors = np.random.uniform(0.9, 1.1, mask.sum())
                    df.loc[mask, col] = (df.loc[mask, col] * factors).clip(lower=0)
        
        friction_columns = ['Friction angle_multi_stage', 'Friction angle_single_stage']
        for col in friction_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    variation = np.random.uniform(-2, 2, mask.sum())
                    df.loc[mask, col] = (df.loc[mask, col] + variation).clip(lower=0, upper=45)
        
        is50_columns = ['Is(50) Axial', 'Is(50) Diametral', 'Is50 combined', 'Is50d (MPa)', 'Is50a (MPa)']
        for col in is50_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    factors = np.random.uniform(0.85, 1.15, mask.sum())
                    df.loc[mask, col] = df.loc[mask, col] * factors
        
        return df
    
    def mask_compaction_data(self, df):
        """Mask compaction data"""
        if 'MDD (t/m3)' in df.columns:
            mask = df['MDD (t/m3)'].notna()
            if mask.sum() > 0:
                variation = np.random.uniform(-0.05, 0.05, mask.sum())
                df.loc[mask, 'MDD (t/m3)'] = (df.loc[mask, 'MDD (t/m3)'] + variation).clip(lower=1.3, upper=2.6)
        
        if 'OMC (%)' in df.columns:
            mask = df['OMC (%)'].notna()
            if mask.sum() > 0:
                variation = np.random.uniform(-2, 2, mask.sum())
                df.loc[mask, 'OMC (%)'] = (df.loc[mask, 'OMC (%)'] + variation).clip(lower=3, upper=40)
        
        return df
    
    def mask_cbr_data(self, df):
        """Mask CBR data"""
        if 'CBR (%) Soaked - 4 Days' in df.columns:
            mask = df['CBR (%) Soaked - 4 Days'].notna()
            if mask.sum() > 0:
                factors = np.random.uniform(0.85, 1.15, mask.sum())
                df.loc[mask, 'CBR (%) Soaked - 4 Days'] = (df.loc[mask, 'CBR (%) Soaked - 4 Days'] * factors).clip(lower=1)
        
        if 'CBR Swell (%)' in df.columns:
            mask = df['CBR Swell (%)'].notna()
            if mask.sum() > 0:
                factors = np.random.uniform(0.9, 1.1, mask.sum())
                df.loc[mask, 'CBR Swell (%)'] = (df.loc[mask, 'CBR Swell (%)'] * factors).clip(lower=0)
        
        return df
    
    def mask_chemical_properties(self, df):
        """Mask chemical properties"""
        if 'pH value' in df.columns:
            mask = df['pH value'].notna()
            if mask.sum() > 0:
                variation = np.random.uniform(-0.3, 0.3, mask.sum())
                df.loc[mask, 'pH value'] = (df.loc[mask, 'pH value'] + variation).clip(lower=3, upper=10)
        
        chemical_columns = ['Sulphates (mg/kg)', 'Chlorides (mg/kg)', 'Conductivity (uS/cm)']
        for col in chemical_columns:
            if col in df.columns:
                mask = df[col].notna()
                if mask.sum() > 0:
                    df.loc[mask, col] = pd.to_numeric(df.loc[mask, col], errors='coerce')
                    mask = df[col].notna()
                    if mask.sum() > 0:
                        factors = np.random.uniform(0.8, 1.2, mask.sum())
                        df.loc[mask, col] = df.loc[mask, col] * factors
        
        return df
    
    def process_files(self, file1_input, file1_output, file2_input, file2_output):
        """Process both Excel files with coordinated transformations"""
        print("\n" + "=" * 60)
        print("PROCESSING FILES")
        print("=" * 60)
        
        # Read original files
        print("\n1. Reading original files...")
        df1_orig = pd.read_excel(file1_input)
        df2_orig = pd.read_excel(file2_input)
        print(f"   BH_Interp: {df1_orig.shape}")
        print(f"   Lab_summary: {df2_orig.shape}")
        
        # Select boreholes spatially
        selected = self.select_boreholes_spatially(df2_orig, df1_orig)
        
        # Create borehole mapping
        print("\n2. Creating borehole ID mappings...")
        self.create_borehole_mapping()
        print(f"   Created mappings for {len(self.borehole_mapping)} boreholes")
        
        # Process BH_Interp file
        print("\n3. Processing BH_Interp file...")
        df1 = self.filter_and_mask_boreholes(df1_orig, 'Hole_ID')
        df1 = self.mask_location_data(df1)
        df1 = self.mask_geological_classifications(df1)
        df1 = self.mask_report_names(df1)
        
        # Process Lab_summary file
        print("\n4. Processing Lab_summary file...")
        df2 = self.filter_and_mask_boreholes(df2_orig, 'Hole_ID')
        df2 = self.mask_location_data(df2)
        df2 = self.mask_geological_classifications(df2)
        df2 = self.mask_report_names(df2)
        df2 = self.mask_spt_data(df2)
        df2 = self.mask_atterberg_limits(df2)
        df2 = self.mask_strength_parameters(df2)
        df2 = self.mask_compaction_data(df2)
        df2 = self.mask_cbr_data(df2)
        df2 = self.mask_chemical_properties(df2)
        
        # Save files
        print("\n5. Saving masked files...")
        df1.to_excel(file1_output, index=False)
        print(f"   Saved {file1_output}: {df1.shape}")
        
        df2.to_excel(file2_output, index=False)
        print(f"   Saved {file2_output}: {df2.shape}")
        
        return df1, df2
    
    def generate_report(self, output_file='Masking_Report_V2.txt'):
        """Generate a report of all transformations applied"""
        with open(output_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("GEOTECHNICAL DATA MASKING REPORT V2\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write("1. BOREHOLE SELECTION AND MAPPING\n")
            f.write("-" * 30 + "\n")
            f.write(f"Boreholes selected: {len(self.borehole_mapping)} (from original 345)\n")
            f.write("Selection method: Spatial clustering for distribution\n")
            f.write("Sample mappings:\n")
            for i, (orig, new) in enumerate(list(self.borehole_mapping.items())[:10]):
                f.write(f"  {orig} -> {new}\n")
            f.write("\n")
            
            f.write("2. COORDINATE TRANSFORMATION (UTM Zone 56)\n")
            f.write("-" * 30 + "\n")
            f.write(f"Rotation angle: {self.coord_transform['rotation_angle']:.1f} degrees\n")
            f.write(f"Translation E: {self.coord_transform['translation_e']:.0f} m\n")
            f.write(f"Translation N: {self.coord_transform['translation_n']:.0f} m\n")
            f.write(f"Random scatter: up to {self.coord_transform['scatter_radius']} m radius\n")
            f.write("Bounds maintained: E 300,000-700,000, N 6,800,000-7,100,000\n\n")
            
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
            f.write("Chemical properties: 0.8-1.2x multiplier\n\n")
            
            f.write("=" * 60 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 60 + "\n")
        
        print(f"\nReport saved to {output_file}")


def main():
    """Main execution function"""
    # Import KMeans at module level or use alternative
    global KMeans
    try:
        from sklearn.cluster import KMeans
        use_kmeans = True
    except ImportError:
        print("Note: scikit-learn not available, using alternative spatial selection method")
        use_kmeans = False
    
    print("=" * 60)
    print("GEOTECHNICAL DATA MASKING TOOL V2")
    print("Limited to 100 boreholes with proper UTM Zone 56 transformation")
    print("=" * 60)
    
    # Initialize the masker
    masker = GeotechnicalDataMaskerV2(max_boreholes=100)
    
    # File paths
    file1_input = "BH_Interp - LGCFR.xlsx"
    file1_output = "BH_Interp_DEMO_100.xlsx"
    
    file2_input = "Lab_summary_final_with_SPT - LGCFR.xlsx"
    file2_output = "Lab_summary_final_with_SPT_DEMO_100.xlsx"
    
    # Process both files
    df1, df2 = masker.process_files(file1_input, file1_output, file2_input, file2_output)
    
    # Generate report
    masker.generate_report()
    
    # Verify data integrity
    print("\n" + "=" * 60)
    print("VERIFICATION")
    print("=" * 60)
    
    # Check coordinate ranges
    if 'Easting (m)' in df2.columns:
        e_min, e_max = df2['Easting (m)'].min(), df2['Easting (m)'].max()
        n_min, n_max = df2['Northing (m)'].min(), df2['Northing (m)'].max()
        print(f"\nNew coordinate ranges (UTM Zone 56):")
        print(f"  Easting: {e_min:.0f} to {e_max:.0f}")
        print(f"  Northing: {n_min:.0f} to {n_max:.0f}")
        print(f"  Within Zone 56: {'YES' if 300000 <= e_min and e_max <= 700000 else 'NO'}")
    
    # Check common boreholes
    df1_holes = set(df1['Hole_ID'].unique())
    df2_holes = set(df2['Hole_ID'].unique())
    common = df1_holes.intersection(df2_holes)
    print(f"\nBorehole counts:")
    print(f"  BH_Interp: {len(df1_holes)} unique boreholes")
    print(f"  Lab_summary: {len(df2_holes)} unique boreholes")
    print(f"  Common: {len(common)} boreholes")
    
    # Check data ranges
    if 'SPT N Value' in df2.columns:
        print(f"\nTechnical data ranges:")
        print(f"  SPT: {df2['SPT N Value'].min():.0f} - {df2['SPT N Value'].max():.0f}")
    if 'UCS (MPa)' in df2.columns:
        print(f"  UCS: {df2['UCS (MPa)'].min():.1f} - {df2['UCS (MPa)'].max():.1f} MPa")
    
    print("\n" + "=" * 60)
    print("DATA MASKING COMPLETE!")
    print(f"Limited to {len(masker.borehole_mapping)} boreholes")
    print("Coordinates properly transformed within UTM Zone 56")
    print("Output files:")
    print(f"  - {file1_output}")
    print(f"  - {file2_output}")
    print(f"  - Masking_Report_V2.txt")
    print("=" * 60)


if __name__ == "__main__":
    main()