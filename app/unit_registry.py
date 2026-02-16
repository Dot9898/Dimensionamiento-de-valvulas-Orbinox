
#encoding: utf-8

from pathlib import Path
import streamlit as st
import pint

ROOT_PATH = Path(__file__).resolve().parent.parent


@st.cache_resource
def get_ureg():
    ureg = pint.UnitRegistry()
    ureg.load_definitions(ROOT_PATH / 'data' / 'pint_extra_units.txt')
    ureg.formatter.default_format = 'P'
    return(ureg)

ureg = get_ureg()

