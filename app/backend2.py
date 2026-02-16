
#encoding: utf-8

import streamlit as st
import pint
from unit_registry import ureg
from constants import BASE_UNITS
from load_data import Valve, VALVES


def activate_rerun(): #unused so far
    st.session_state['rerun'] = True

def init_session_state(defaults):
    for key in defaults:
        if key not in st.session_state:
            st.session_state[key] = defaults[key]

def in_base_unit(quantity_name, key, unit_key):
    plain_quantity = st.session_state[key]
    if plain_quantity is None:
        return(None)
    
    current_unit = ureg(st.session_state[unit_key])
    try:
        quantity = plain_quantity * current_unit
    except pint.errors.OffsetUnitCalculusError:
        quantity = pint.Quantity(plain_quantity, current_unit)

    base_unit = ureg(BASE_UNITS[quantity_name])
    quantity_in_base_unit = quantity.to(base_unit)
    return(quantity_in_base_unit)

def get_dimensionable_and_available_diameters(valve: Valve):
    available_diameters = valve.available_diameters
    dimensionable_diameters = list(valve.Cv.index)
    diameters = []
    for diameter in available_diameters:
        if diameter in dimensionable_diameters:
            diameter = int(diameter) #Will fail for half diameters
            diameters.append(diameter)
    return(diameters)



