
#encoding: utf-8

import streamlit as st
import pint ##?
from unit_registry import ureg ###
from user_inputs import generate_multiple_inputs
from constants import DEFAULTS


def activate_rerun(): #unused so far
    st.session_state['rerun'] = True

def init_session_state(defaults): #pal backend
    for key in defaults:
        if key not in st.session_state:
            st.session_state[key] = defaults[key]

def vertical_divider(height):
    st.html(
        f'''
            <div class="divider-vertical-line"></div>
            <style>
                .divider-vertical-line {{
                    border-left: 2px solid rgba(49, 51, 63, 0.2);
                    height: {height}px;
                    margin: auto;
                }}
            </style>
        '''
    )



#-------------------------------------------------------------------------------------------------



init_session_state(DEFAULTS)
st.set_page_config(layout = 'wide')

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])

with separator_column:
    vertical_divider(height = 920)

with input_column:
    flow = generate_multiple_inputs(written_name = 'Caudal', 
                                    quantity_name = 'Caudal', 
                                    base_key = 'Caudal', 
                                    unit_key = 'Caudal unidad', 
                                    decimals = 1, 
                                    inputs_range = (10, None), 
                                    placeholders = ['mínimo', 'normal', 'máximo'])

    st.write(flow)



if st.session_state['rerun']:
    st.session_state['rerun'] = False
    st.rerun()


#AGREGAR TYPE CHECKING?





