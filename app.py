import os
import streamlit as st
import pandas as pd
import pydeck as pdk
from deta import Deta

st.set_page_config(layout="wide",
                   page_title="Delivery Code 5 Map",
                   page_icon="uk.png")

def color_map(val):
    if 0 > val >= -500:
        return [255, 215, 8, 255]
    elif -500 > val >= -1000:
        return [255, 159, 0, 255]
    elif -1000 > val >= -2500:
        return [254, 91, 0, 255]
    elif -2500 > val >= -5000:
        return [223, 13, 0, 255]
    elif -5000 > val:
        return [162, 4, 0, 255]
    elif 0 < val <= 500:
        return [216, 255, 20, 255]
    elif 500 < val <= 1000:
        return [75, 237, 21, 255]
    elif 1000 < val <= 2500:
        return [46, 200, 18, 255]
    elif 2500 < val <= 5000:
        return [37, 164, 14, 255]
    elif 5000 < val:
        return [28, 129, 10, 255]


def neg_map0(val):
    if val < 0:
        return "-"
    if val > 0:
        return "+"


def neg_map(val):
    if val < 0:
        return val * -1
    else:
        return val


def neg_map2(val):
    if val == "-":
        return -1
    else:
        return 1


def proc_file2(file):
    try:
        lats, longs, rdcs, fmiles, names, storesserved = make_dicts(ll_ff)

        x = pd.read_csv(file)
        x = x.groupby(['Store Number', 'Week Number'], as_index=False).agg({'Value': 'sum'})
        x.columns = ['no', 'week', 'value']

        x['name'] = x['no'].map(names)
        x['rdc'] = x['no'].map(rdcs)
        x['finalmile'] = x['no'].map(fmiles)
        x['lat'] = x['no'].map(lats)
        x['lng'] = x['no'].map(longs)

        ##########################################
        #   Need to get ROI store lats / longs ...
        ##########################################
        x = x[~x['rdc'].isna()]
        ##########################################

        x['colors'] = x['value'].map(color_map)
        x['neg'] = x['value'].map(neg_map0)
        x['value'] = x['value'].map(neg_map)
        x = x[x['value'] != 0]

        return x, list(x['week'].unique()), storesserved

    except Exception as e:
        print('proc_file2', e)


def make_deck(procd_data):
    try:
        column_layer = pdk.Layer(
            "ColumnLayer",
            data=procd_data,
            get_position=["lng", "lat"],
            get_elevation="value",
            elevation_scale=100,
            radius=1000,
            get_fill_color="colors",
            pickable=True,
            auto_highlight=True,
        )

        column_layer_depots = pdk.Layer(
            "ColumnLayer",
            data=df_depots,
            get_position=["lng", "lat"],
            get_elevation=1000,
            elevation_scale=100,
            radius=1000,
            get_fill_color=[255, 255, 255, 255],
            pickable=True,
            auto_highlight=True,
        )

        view_state = pdk.ViewState(
            longitude=-1.415,
            latitude=52.2323,
            # zoom=6,
            zoom=4,
            min_zoom=5,
            max_zoom=15,
            pitch=40.5,
            bearing=-27.36)

        tooltip = {
            "html": "<u><b>{no} {name}</b></u>"
                    "<br>"
                    "<br>Net Balance:   {neg}£{value}"
                    "<br>RDC:   {rdc}"
                    "<br>Final Mile:    {finalmile}",
            "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial',
                      "z-index": "10000"},
        }

        r = pdk.Deck(
            layers=[column_layer, column_layer_depots],
            initial_view_state=view_state,
            tooltip=tooltip,
            map_style=pdk.map_styles.DARK,
        )

        return r

    except Exception as e:
        print('make_deck', e)


def make_dicts(file):
    try:
        x = pd.read_csv(file)
        y = x.groupby(['finalmile']).size().reset_index(name='sserved')
        return dict(zip(x['no'], x['lat'])), \
               dict(zip(x['no'], x['lng'])), \
               dict(zip(x['no'], x['rdc'])), \
               dict(zip(x['no'], x['finalmile'])), \
               dict(zip(x['no'], x['name'])), \
               dict(zip(y['finalmile'], y['sserved'])), \

    except Exception as e:
        print('make_dict', e)


@st.cache_data
def get_data_from_deta():
    deta = Deta('a07quq8cozm_FYjMzPGnoeDQ6fuP1D4AdgbtwGeAP5MN')
    ddrive = deta.Drive('data')
    return ddrive.get('data_from_wk5').read().decode(), ddrive.get('stores_no_roi').read().decode(), ddrive.get('depots').read().decode()


######################################
#   Init
######################################
ff = get_data_from_deta()[0]
ll_ff = get_data_from_deta()[1]
dep_ff = get_data_from_deta()[2]

df_depots = pd.read_csv(dep_ff)
df, weeks, ss_dict = proc_file2(ff)
df_fmile = df.copy()

with st.sidebar:
    FILTER_WEEKS = st.slider('Argos Week Range', int(weeks[0]), int(weeks[-1]), (int(weeks[-2]), int(weeks[-1])))

    col1, col2 = st.columns(2)

    FILTER_DEPOTS = st.checkbox('Depots', value=False)

    with col1:
        FILTER_SHORTS = st.checkbox('Shorts', value=True)
    with col2:
        FILTER_OVERS = st.checkbox('Overs', value=False)

    FILTER_BAS = st.checkbox('Basildon - First Leg', value=True)
    expander_BAS = st.expander("BAS - Final Mile")
    FILTER_BAS_ALL = expander_BAS.checkbox('All', value=True)
    FILTER_BAS_BAS = expander_BAS.checkbox('Basildon ', value=FILTER_BAS_ALL)
    FILTER_BAS_BSTK = expander_BAS.checkbox('Basingstoke', value=FILTER_BAS_ALL)
    FILTER_BAS_DAR = expander_BAS.checkbox('Dartford', value=FILTER_BAS_ALL)
    FILTER_BAS_WP = expander_BAS.checkbox('Waltham Point', value=FILTER_BAS_ALL)

    FILTER_HEY = st.checkbox('Heywood - First Leg', value=True)
    expander_HEY = st.expander("HEY - Final Mile")
    FILTER_HEY_ALL = expander_HEY.checkbox('All ', value=True)
    FILTER_HEY_BHD = expander_HEY.checkbox('Birkenhead Docks', value=FILTER_HEY_ALL)
    FILTER_HEY_FVD = expander_HEY.checkbox('Faverdale', value=FILTER_HEY_ALL)
    FILTER_HEY_HD = expander_HEY.checkbox('Haydock', value=FILTER_HEY_ALL)
    FILTER_HEY_HEY = expander_HEY.checkbox('Heywood ', value=FILTER_HEY_ALL)
    FILTER_HEY_LL = expander_HEY.checkbox('Langlands', value=FILTER_HEY_ALL)
    FILTER_HEY_MOS = expander_HEY.checkbox('Mossend', value=FILTER_HEY_ALL)
    FILTER_HEY_SHR = expander_HEY.checkbox('Sherburn', value=FILTER_HEY_ALL)

    FILTER_KET = st.checkbox('Kettering - First Leg', value=True)
    expander_KET = st.expander("KET - Final Mile")
    FILTER_KET_ALL = expander_KET.checkbox('All  ', value=True)
    FILTER_KET_CB = expander_KET.checkbox('Conway Bailey', value=FILTER_KET_ALL)
    FILTER_KET_EP = expander_KET.checkbox('Emerald Park', value=FILTER_KET_ALL)
    FILTER_KET_HH = expander_KET.checkbox('Hams Hall', value=FILTER_KET_ALL)
    FILTER_KET_KET = expander_KET.checkbox('Kettering ', value=FILTER_KET_ALL)
    FILTER_KET_NH = expander_KET.checkbox('Northampton', value=FILTER_KET_ALL)
    FILTER_KET_PW = expander_KET.checkbox('Patchway', value=FILTER_KET_ALL)

if FILTER_WEEKS:
    df = df[df['week'] >= FILTER_WEEKS[0]]
    df = df[df['week'] <= FILTER_WEEKS[1]]

if not FILTER_DEPOTS:
    df_depots = df_depots[df_depots['value'] == 1]

if not FILTER_SHORTS:
    df = df[df['neg'] != '-']
if not FILTER_OVERS:
    df = df[df['neg'] != '+']

if not FILTER_BAS:
    df = df[df['rdc'] != 'Basildon ']
if not FILTER_HEY:
    df = df[df['rdc'] != 'Heywood ']
if not FILTER_KET:
    df = df[df['rdc'] != 'Kettering ']

if not FILTER_BAS_BAS:
    df = df[df['finalmile'] != 'Basildon ']
if not FILTER_BAS_BSTK:
    df = df[df['finalmile'] != 'Basingstoke']
if not FILTER_BAS_DAR:
    df = df[df['finalmile'] != 'Dartford']
if not FILTER_BAS_WP:
    df = df[df['finalmile'] != 'Waltham Point']

if not FILTER_HEY_BHD:
    df = df[df['finalmile'] != 'Birkenhead Docks']
if not FILTER_HEY_FVD:
    df = df[df['finalmile'] != 'Faverdale']
if not FILTER_HEY_HD:
    df = df[df['finalmile'] != 'Haydock']
if not FILTER_HEY_HEY:
    df = df[df['finalmile'] != 'Heywood ']
if not FILTER_HEY_LL:
    df = df[df['finalmile'] != 'Langlands']
if not FILTER_HEY_MOS:
    df = df[df['finalmile'] != 'Mossend']
if not FILTER_HEY_SHR:
    df = df[df['finalmile'] != 'Sherburn']

if not FILTER_KET_CB:
    df = df[df['finalmile'] != 'Conway Bailey Transport ']
if not FILTER_KET_EP:
    df = df[df['finalmile'] != 'Emerald Park']
if not FILTER_KET_HH:
    df = df[df['finalmile'] != 'Hams Hall']
if not FILTER_KET_KET:
    df = df[df['finalmile'] != 'Kettering ']
if not FILTER_KET_NH:
    df = df[df['finalmile'] != 'Northampton']
if not FILTER_KET_PW:
    df = df[df['finalmile'] != 'Patchway']

dfl = df[df['neg'] == '-']
dfg = df[df['neg'] == '+']
val_loss = dfl['value'].sum() * -1
val_gain = dfg['value'].sum()
val_net = val_loss + val_gain
st.header(f"Net of selection: £ {val_net:,.0f}")

st.markdown(f'''
    <style>
        section[data-testid="stSidebar"] .css-ng1t4o {{width: 10rem;}}
        section[data-testid="stSidebar"] .css-1d391kg {{width: 10rem;}}
    </style>
''', unsafe_allow_html=True)

hide_default_format = '''
       <style>
       #MainMenu {visibility: hidden; }
       footer {visibility: hidden;}
       </style>
       '''
st.markdown(hide_default_format, unsafe_allow_html=True)

viz = st.pydeck_chart(make_deck(df))

df_fmile = df_fmile[df_fmile['week'] >= FILTER_WEEKS[0]]
df_fmile = df_fmile[df_fmile['week'] <= FILTER_WEEKS[1]]
df_fmile['neg2'] = df_fmile['neg'].map(neg_map2)
df_fmile['value2'] = df_fmile['value'] * df_fmile['neg2']

df_fmile = df_fmile[['finalmile', 'value2']].groupby('finalmile').agg('sum')
df_fmile.index.names = ['Final Mile']
df_fmile.columns = ['Net of Week Selection']
df_fmile['Stores Serviced'] = df_fmile.index.to_series().map(ss_dict)
df_fmile = df_fmile.sort_values(by=['Net of Week Selection'], ascending=True)
df_fmile['Net of Week Selection'] = df_fmile['Net of Week Selection'].map('£ {:,.0f}'.format)
st.dataframe(df_fmile, height=633, width=430)
