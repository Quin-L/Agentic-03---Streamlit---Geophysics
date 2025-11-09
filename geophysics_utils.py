import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go


def calculate_x(x, y):
    return math.sqrt(x**2 + y**2)


def compute_chainage(df):
    dx = np.diff(df.Easting)
    dy = np.diff(df.Northing)
    seg = np.sqrt(dx**2 + dy**2)
    chainage = np.concatenate([[0], np.cumsum(seg)])
    df['Chainage'] = chainage
    df["Spacing"] = np.r_[np.nan, seg] # note, in numpy, np.r_ is same as np.concatenate
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
    df = df[df['Velocity'] % velocity_interval == 0]
    df = df.sort_values(['Easting','Northing','Chainage','Elevation'], 
                        ascending=[True, True, True, False]).reset_index(drop=True)

    # shift within each coordinate group
    df['To_RL'] = df.groupby(['Easting','Northing','Chainage'])['Elevation'].shift(-1)
    df['From_RL'] = df['Elevation']

    # drop incomplete rows
    df = df.dropna(subset=['To_RL'])

    # build final dataframe
    df = df[['Easting','Northing','Chainage','From_RL','To_RL','Velocity']].copy()
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