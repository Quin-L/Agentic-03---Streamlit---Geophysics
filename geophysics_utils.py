import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# For notebook
import plotly.express as px 
import statsmodels.api as sm
import scipy.stats as stats
from pathlib import Path
import pandas as pd
import numpy as np
import re
import plotly.io as pio
from IPython.display import display
pio.renderers.default = 'notebook'


# ============================================================================
# CONSTANTS
# ============================================================================

CONSISTENCY_ORDER = ['VS','S','F','St', 'VSt', 'H', 'VL','L','MD', 'D', 'VD', '5a', '5b','4a','4b','3a','3b','2a','2b','1a','1b']
HOVER_DATA = ['Geophysics_ID','Hole_ID', 'From_RL','Chainage', 'Velocity', 'Consistency', 'Geology_Orgin', 'perpendicular_offset']


# ============================================================================
# UTILITIES
# ============================================================================

def calculate_x(x, y):
    return math.sqrt(x**2 + y**2)


# ============================================================================
# DATA IMPORT & FILTERING
# ============================================================================

def data_processing_summary(total_files, processed_files, all_geophysics, skipped_files, EASTING_RANGE, NORTHING_RANGE):
    display("\n")
    print("="*60)
    print("DATA PROCESSING SUMMARY")
    print("="*60)
    print(f"Total CSV files found:        {total_files}")
    print(f"Files processed:              {processed_files}")
    print(f"Files skipped (out of range): {skipped_files}")
    print(f"\nStudy Area Range:")
    print(f"  Easting:  {EASTING_RANGE[0]:,.0f} - {EASTING_RANGE[1]:,.0f}")
    print(f"  Northing: {NORTHING_RANGE[0]:,.0f} - {NORTHING_RANGE[1]:,.0f}")
    print(f"\nProcessed Geophysics Lines:")
    for line_id in all_geophysics['geophysics_data'].keys():
        line_df = all_geophysics['geophysics_data'][line_id]
        print(f"  {line_id}: {len(line_df):,} data points")
    print("="*60)


def should_process_geophysics(df, easting_range, northing_range):
    """
    Check if geophysics line should be processed based on study area range.

    If ANY part of the line is within or intersects the range, return True
    and the entire line will be processed.

    Parameters:
    -----------
    df : DataFrame with 'Easting', 'Northing' columns
    easting_range : [min, max] - study area easting bounds
    northing_range : [min, max] - study area northing bounds

    Returns:
    --------
    bool : True if line intersects range (process entire line)
           False if completely outside range (skip entirely)
    """
    if df.empty:
        return False

    # Get bounding box of geophysics line
    geo_e_min = df['Easting'].min()
    geo_e_max = df['Easting'].max()
    geo_n_min = df['Northing'].min()
    geo_n_max = df['Northing'].max()

    # Check if completely outside range
    # Outside if: line_max < range_min OR line_min > range_max
    outside_easting = (geo_e_max < easting_range[0]) or (geo_e_min > easting_range[1])
    outside_northing = (geo_n_max < northing_range[0]) or (geo_n_min > northing_range[1])

    # If completely outside, don't process
    if outside_easting or outside_northing:
        return False

    # Otherwise (within or intersects), process the entire line
    return True


# ============================================================================
# GEOPHYSICS DATA PROCESSING
# ============================================================================

def compute_chainage(df):
    """
    Compute chainage for straight geophysics survey lines.

    Calculates distance from west endpoint (min Easting) and east endpoint (max Easting).
    Assumes survey line is a straight line.

    Returns:
    --------
    df : DataFrame with added 'Chainage_west_to_east' and 'Chainage_east_to_west' columns
    """
    df = df.copy()

    # Extract coordinates
    easting = df['Easting'].values
    northing = df['Northing'].values

    # Find endpoints
    west_idx = np.argmin(easting)
    east_idx = np.argmax(easting)

    # ============ West to East (distance from west endpoint) ============
    west_point = np.array([easting[west_idx], northing[west_idx]])
    dist_from_west = np.sqrt((easting - west_point[0])**2 +
                             (northing - west_point[1])**2)
    df['computed_Chainage_ascending'] = np.round(dist_from_west, 2)

    # ============ East to West (distance from east endpoint) ============
    east_point = np.array([easting[east_idx], northing[east_idx]])
    dist_from_east = np.sqrt((easting - east_point[0])**2 +
                             (northing - east_point[1])**2)
    df['computed_Chainage_descending'] = np.round(dist_from_east, 2)

    return df


def classify_soil(cons):
    cohesive = {'VS','S','F','St','VSt','H'}
    granular = {'VL','L','MD','D','VD'}
    rocklike = {'5a','5b','4a','4b','3a','3b','2a','2b','1a','1b'}
    if pd.isna(cons):
        return ''
    consistency = str(cons)
    if consistency in cohesive:
        return 'Cohesive'
    if consistency in granular:
        return 'Granular'
    if consistency in rocklike or (len(consistency) and consistency[0].isdigit()):
        return 'Rock'
    return 'Other'


def process_individual_geophysics(df, velocity_interval=5):
    
    # filter and sort
    df = df.drop_duplicates()
    df = df.dropna(subset=['Velocity'])

    # compute chainage from coordinates (straight line assumption)
    df = compute_chainage(df)
    df = df[df['Velocity'] % velocity_interval == 0]
    df = df.sort_values(['Easting','Northing','Chainage','Elevation'],
                        ascending=[True, True, True, False]).reset_index(drop=True)

    # shift within each coordinate group
    df['To_RL'] = df.groupby(['Easting','Northing','Chainage'])['Elevation'].shift(-1)
    df['From_RL'] = df['Elevation']

    # drop incomplete rows
    df = df.dropna(subset=['To_RL'])

    # build final dataframe - include computed chainage columns at the end
    df = df[['Easting','Northing','Chainage','From_RL','To_RL','Velocity',
             'computed_Chainage_ascending','computed_Chainage_descending']].copy()
    df['Layer_center'] = (df['From_RL'] + df['To_RL']) / 2
    df = df[df['To_RL'] != df['From_RL']]
    # df = df.sort_values(['Easting','Northing','Chainage','From_RL'],
    #                 ascending=[True, True, True, False]).reset_index(drop=True)

    return df


def resample_data(df, step=1):
    new_chainage = np.arange(df.Chainage.min(),df.Chainage.max(), step)

    Easting = np.interp(new_chainage, df.Chainage, df.Easting)
    Northing = np.interp(new_chainage, df.Chainage, df.Northing)
    Elevation = np.interp(new_chainage, df.Chainage, df.Elevation)
    Velocity = np.interp(new_chainage, df.Chainage, df.Velocity)

    new_df = pd.DataFrame({"Chainage":new_chainage,
                           "Easting": Easting,
                           "Northing": Northing,
                           "Elevation": Elevation,
                           "Velocity": Velocity,
                          })
    return new_df


# ============================================================================
# SPATIAL ANALYSIS
# ============================================================================

def offset_bh_geophysics_line(geophysics, BH_coordinates):
    """
    this function 
    """

    Geophysics_Easting  = geophysics.Easting.to_numpy()
    Geophysics_Northing = geophysics.Northing.to_numpy()
    
    # --- Compute chainage along the line with numpy ---
    dX = np.diff(Geophysics_Easting)
    dY = np.diff(Geophysics_Northing)
    seg_lengths   = np.hypot(dX, dY)                  # segment lengths
    chainage_vals = np.r_[0, np.cumsum(seg_lengths)]  # chainage at each vertex
    L = chainage_vals[-1]                             # total length
    
    best = {"dist": np.inf, "chainage": None, "i": None, "t_raw": None}
    
    # --- Loop over each segment to find best projection ---
    for i in range(len(Geophysics_Easting)-1):
        A = np.array([Geophysics_Easting[i],   Geophysics_Northing[i]])
        B = np.array([Geophysics_Easting[i+1], Geophysics_Northing[i+1]])
        AB = B - A
        denom = np.dot(AB, AB)
        if denom == 0:  # skip zero-length segments
            continue
    
        numerator = np.dot((BH_coordinates - A), AB)
        t_raw  = numerator / denom
        t_clip = np.clip(t_raw, 0, 1)
        Q = A + t_clip * AB
    
        distance = np.linalg.norm(BH_coordinates - Q)
    
        if distance < best['dist']:
            best = {
                'dist'    : distance,
                'chainage': chainage_vals[i] + t_raw * seg_lengths[i],  # use raw t
                'i'       : i,
                't_raw'   : t_raw,
                't_clip'  : t_clip,
                'Q'       : Q,
                'AB'      : AB,
            }
    
    # --- Classification based on projection ---
    chainage_projection = best['chainage']
    
    # Start tangent
    # --- Start tangent: use GLOBAL direction S0 -> final end (not first unique point)
    S0 = np.array([Geophysics_Easting[0], Geophysics_Northing[0]])
    S_end = np.array([Geophysics_Easting[-1], Geophysics_Northing[-1]])
    t0 = S_end - S0
    t0 = t0 / (np.linalg.norm(t0) + 1e-12)
    n0 = np.array([-t0[1], t0[0]])
    
    # End tangent
    SN   = np.array([Geophysics_Easting[-1], Geophysics_Northing[-1]])
    for j in range(len(Geophysics_Easting)-2, -1, -1):
        if (Geophysics_Easting[j] != Geophysics_Easting[-1]) or (Geophysics_Northing[j] != Geophysics_Northing[-1]):
            SNm1 = np.array([Geophysics_Easting[j], Geophysics_Northing[j]])
            break
    else:
        SNm1 = SN - np.array([1.0, 0.0])
    t1 = t0.copy()
    n1 = np.array([-t1[1], t1[0]])
    
    # Vectors from start/end to BH
    v0 = BH_coordinates - S0
    v1 = BH_coordinates - SN
    
    # --- Offsets ---
    if chainage_projection < -1e-9:
        tangential_offset    = (BH_coordinates - S0) @ t0
        perpendicular_offset = abs((BH_coordinates - S0) @ n0)
    
    elif chainage_projection > L + 1e-9:
        tangential_offset    = L + (BH_coordinates - SN) @ t1
        perpendicular_offset = abs((BH_coordinates - SN) @ n1)
    
    else:
        tangential_offset    = chainage_projection
        perpendicular_offset = best["dist"]

    return tangential_offset, perpendicular_offset


# ============================================================================
# DATA MERGING
# ============================================================================

def merge_geophysics_bh_consistency(geophysics_bh_results, geophysics_id, geophysics_df, hole_id, bh_interp_df):
    
    for _, geo_row in geophysics_df.iterrows():
        geo_top = max(geo_row['From_RL'], geo_row['To_RL'])
        geo_bot = min(geo_row['From_RL'], geo_row['To_RL'])

        for _, litho_row in bh_interp_df.iterrows():
            litho_top = max(litho_row['From_RL'], litho_row['To_RL'])
            litho_bot = min(litho_row['From_RL'], litho_row['To_RL'])

            # Overlap interval
            overlap_top = min(geo_top, litho_top)
            overlap_bot = max(geo_bot, litho_bot)
            overlap_len = overlap_top - overlap_bot

            if overlap_len > 0:
                geophysics_bh_results.append({
                    'Geophysics_ID': geophysics_id,
                    'Hole_ID':hole_id,
                    'From_RL': overlap_top,
                    'To_RL': overlap_bot,
                    'Chainage': geo_row.Chainage,
                    'Velocity': geo_row['Velocity'],
                    'Consistency': litho_row['Consistency'],
                    'Geology_Orgin': litho_row['Geology_Orgin']
                })

    return geophysics_bh_results


def merge_lab_into_results(geophysics_bh_results, UCS_SPT):
    lab_groups = UCS_SPT.groupby('Hole_ID')
    final_results = []
    
    for result in geophysics_bh_results:
        hole_id = result['Hole_ID']
        geo_top = max(result['From_RL'], result['To_RL'])
        geo_bot = min(result['From_RL'], result['To_RL'])
    
        best_row = None
        best_overlap = 0
    
        if hole_id in lab_groups.groups:
            lab_df = lab_groups.get_group(hole_id)
    
            for _, lab_row in lab_df.iterrows():
                lab_top = lab_row['From_RL']
                lab_bot = lab_row['To_RL']
    
                overlap = min(geo_top, lab_top) - max(geo_bot, lab_bot)
    
                if overlap > 0 and overlap > best_overlap:
                    best_overlap = overlap
                    best_row = lab_row
    
        merged_row = dict(result)
        if best_row is not None:
            merged_row.update({
                'Lab_From_RL': best_row['From_RL'],
                'Lab_To_RL': best_row['To_RL'],
                'UCS_MPa': best_row.get('UCS (MPa)', pd.NA),
                'SPT_N': best_row.get('SPT N Value', pd.NA),
                'LL (%)': best_row.get('LL (%)', pd.NA),
            })
    
        final_results.append(merged_row)
    
    geophysics_bh_lab = pd.DataFrame(final_results)
    return geophysics_bh_lab


def add_to_register(geophysics_BH_register, individual_geophysics_ID, BH_ID, chainage, perpendicular_offset):
    record = {
        "Geophysics_ID" : individual_geophysics_ID,
        "Hole_ID" : BH_ID,
        "geophysics_chainage" : chainage,
        "perpendicular_offset" : perpendicular_offset,
    }
    geophysics_BH_register.append(record)


# ============================================================================
# VISUALIZATION HELPERS (continued)
# ============================================================================

def plot_geophysics(df, x='Chainage', y='To_RL', color='Velocity', title=None, height=500, range_color=[50,1000]):
    fig = px.scatter(df, x, y,  color=color, title=title, height=height, color_continuous_scale="jet",range_color=range_color)
    fig.update_layout(
        coloraxis_colorbar=dict(
            title="S-Velocity (m/s)",
            tickmode="linear",
            tick0=50,
            dtick=100
        )
    )
    return fig


def add_background_geophysics(all_geophysics, Geophysics_ID, fig, transpareny=0.5, marker_size=3):
    full_line = all_geophysics['geophysics_data'][Geophysics_ID]
    fig.add_trace(
        go.Scattergl(
            x=full_line['Chainage'],
            y=full_line['From_RL'],
            mode='markers',
            marker=dict(
                size=marker_size,
                color=full_line['Velocity'],
                colorscale='Jet',
                cmin=50,
                cmax=950,
                opacity=transpareny,
                showscale=True,  # turn on this trace’s colorbar
                colorbar=dict(
                    title='S-Velocity (m/s)',
                    tickmode='linear',
                    tick0=50,
                    dtick=100,
                    x=1.15,
                    y=0.53,
                )
            ),
            # hoverinfo='skip',
            showlegend=False
        )
    )
    fig.data = (fig.data[-1],) + fig.data[:-1]


def add_label(fig, plot_df):
    label_df = plot_df.groupby(['Hole_ID'], as_index=False).agg({'Chainage': 'first', 'From_RL': 'max', 'perpendicular_offset': 'first'})

    label_df['label'] = (
            label_df['Hole_ID']
            + '<br>'
            + label_df['perpendicular_offset'].map(lambda v: f'{v:.2f} m')
        )
    
    fig.add_trace(
      go.Scatter(
            x=label_df['Chainage'],
            y=label_df['From_RL'] + 0.5,
            mode='text',
            text=label_df['label'],
            textposition='top center',
            textfont=dict(family='Arial', size=8, color='blue'),
            hoverinfo='skip',
            showlegend=False
      )
    )