
#encoding: utf-8

import streamlit as st
import pint ##?
import backend2
import callbacks
from unit_registry import ureg ###
from constants import DEFAULTS, IMAGES
from load_data import VALVES, FLUIDS
from user_inputs import generate_valve_and_fluid_dropdowns, generate_multiple_inputs, generate_diameter_input_line

LOGO_WIDTH = 200


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

def generate_title_and_logo():
    title_column, logo_column = st.columns([3, 1])

    with title_column:
        st.markdown("""
                    <div style="display: flex; flex-direction: column; justify-content: flex-end; height: 150px;">
                        <h4 style="margin: 0; font-size: 3rem; font-weight: 450;">
                            Dimensionamiento de válvulas
                        </h4>
                    </div>
                    """,
                    unsafe_allow_html=True)

    with logo_column:
        logo = IMAGES['logo']
        st.markdown(f"""
                    <div style="
                        display: flex;
                        justify-content: flex-end;
                        align-items: flex-end;
                        height: 122px;
                    ">
                        <img src="data:image/png;base64,{logo}" width="{LOGO_WIDTH}">
                    </div>
                    """,
                    unsafe_allow_html=True)
    
    st.write('')

def generate_all_input_fields():

    inputs = {}

    valve, fluid = generate_valve_and_fluid_dropdowns(VALVES, FLUIDS)
    inputs['valve'] = valve
    inputs['fluid'] = fluid

    inputs['flow'] = generate_multiple_inputs(written_name = 'Caudal', 
                                              quantity_name = 'Caudal', 
                                              base_key = 'Caudal', 
                                              unit_key = 'Caudal unidad', 
                                              decimals = 0, 
                                              inputs_range = (0, None), 
                                              placeholders = ['mínimo', 'normal', 'máximo'])
    
    inputs['in_pressure'] = generate_multiple_inputs(written_name = 'Presión de entrada', 
                                                     quantity_name = 'Presión', 
                                                     base_key = 'Presión de entrada', 
                                                     unit_key = 'Presión de entrada unidad', 
                                                     decimals = 1, 
                                                     inputs_range = (0, None), 
                                                     placeholders = ['mínimo', 'normal', 'máximo'], 
                                                     number_input_callback = callbacks.update_pressure_differential_and_out_pressure_value)
    
    inputs['out_pressure'] = generate_multiple_inputs(written_name = 'Presión de salida', 
                                                      quantity_name = 'Presión', 
                                                      base_key = 'Presión de salida', 
                                                      unit_key = 'Presión de salida unidad', 
                                                      decimals = 1, 
                                                      inputs_range = (0, None), #presión de salida menos que la de entrada
                                                      placeholders = ['mínimo', 'normal', 'máximo'], 
                                                      number_input_callback = callbacks.set_pressure_differential_box)

    inputs['pressure_differential'] = generate_multiple_inputs(written_name = 'Diferencia de presión', 
                                                               quantity_name = 'Presión', 
                                                               base_key = 'Diferencia de presión', 
                                                               unit_key = 'Diferencia de presión unidad', 
                                                               decimals = 1, 
                                                               inputs_range = (0, None), #max pressure diff es presión de entrada
                                                               placeholders = ['mínimo', 'normal', 'máximo'], 
                                                               number_input_callback = callbacks.set_out_pressure_box)

    inputs['diameter'] = generate_diameter_input_line(valve)

    inputs['temperature'] = generate_multiple_inputs(written_name = 'Temperatura', 
                                                     quantity_name = 'Temperatura', 
                                                     base_key = 'Temperatura', 
                                                     unit_key = 'Temperatura unidad', 
                                                     number_of_inputs = 1, 
                                                     decimals = 1, 
                                                     inputs_range = (0, None), 
                                                     number_input_callback = callbacks.fill_fluid_values, 
                                                     number_input_kwargs = {'fluid': fluid})

    inputs['specific_gravity'] = generate_multiple_inputs(written_name = 'Gravedad específica', 
                                                          quantity_name = 'Gravedad específica', 
                                                          base_key = 'Gravedad específica', 
                                                          unit_key = 'Gravedad específica unidad', 
                                                          number_of_inputs = 1, 
                                                          decimals = 4, 
                                                          inputs_range = (0, None))

    inputs['vapor_pressure'] = generate_multiple_inputs(written_name = 'Presión de vapor', 
                                                          quantity_name = 'Presión', 
                                                          base_key = 'Presión de vapor', 
                                                          unit_key = 'Presión de vapor unidad', 
                                                          number_of_inputs = 1, 
                                                          decimals = 1, 
                                                          inputs_range = (0, None))

    inputs['viscosity'] = generate_multiple_inputs(written_name = 'Viscosidad', 
                                                          quantity_name = 'Viscosidad', 
                                                          base_key = 'Viscosidad', 
                                                          unit_key = 'Viscosidad unidad', 
                                                          number_of_inputs = 1, 
                                                          decimals = 4, 
                                                          inputs_range = (0, None))
    
    inputs['speed_of_sound'] = generate_multiple_inputs(written_name = 'Velocidad del sonido', 
                                                          quantity_name = 'Velocidad del sonido', 
                                                          base_key = 'Velocidad del sonido', 
                                                          unit_key = 'Velocidad del sonido unidad', 
                                                          number_of_inputs = 1, 
                                                          decimals = 1, 
                                                          inputs_range = (0, None))
    
    return(inputs)



#-------------------------------------------------------------------------------------------------



backend2.init_session_state(DEFAULTS)

st.set_page_config(layout = 'wide')

generate_title_and_logo()

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])

with separator_column:
    vertical_divider(height = 920)

with input_column:
    st.subheader('Condiciones de trabajo')
    inputs = generate_all_input_fields()
    #inputs




if st.session_state['rerun']:
    st.session_state['rerun'] = False
    st.rerun()


#AGREGAR TYPE CHECKING?





