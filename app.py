import os
import streamlit as st
import pandas as pd
import pydeck as pdk
from deta import Deta

st.set_page_config(layout="wide",
                   page_title="Delivery Code 5 Map",
                   page_icon="uk.png")


@st.cache_data
def get_code():
    # deta = Deta(os.environ.get('db_key'))
    deta = Deta('a07quq8cozm_FYjMzPGnoeDQ6fuP1D4AdgbtwGeAP5MN')
    ddrive = deta.Drive('data')
    with open(ddrive.get('code').read().decode(), 'rb') as f:
        to_ret = f.read()
    return to_ret


exec(get_code())
