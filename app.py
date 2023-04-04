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
    deta = Deta(os.environ.get('db_key'))
    ddrive = deta.Drive('data')
    ffile = ddrive.get('code').read().decode()
    with open(ffile, 'rb') as f:
        to_ret = f.read()
    return to_ret


exec(get_code())
