
#encoding: utf-8

import streamlit as st
import pint ##?
import plotly.graph_objects as go
import backend2
import callbacks
from unit_registry import ureg ###
from constants import DEFAULTS, IMAGES
from load_data import VALVES, FLUIDS
from user_inputs import generate_valve_and_fluid_dropdowns, generate_multiple_inputs, generate_diameter_input_line

LOGO_WIDTH = 200
NAMES_COLUMN_SPACING = 3
TO_COLUMN = {0: 'primera', 1: 'segunda', 2: 'tercera'}

def add_vertical_spacing(pixels):
    st.markdown(f"<div style='height: {pixels}px;'></div>", unsafe_allow_html = True)

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

    valve, fluid = generate_valve_and_fluid_dropdowns(VALVES, FLUIDS) #class instances of Valve and Fluid
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
                                                     inputs_range = (0, 350), 
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
                                                        quantity_name = 'Velocidad', 
                                                        base_key = 'Velocidad del sonido', 
                                                        unit_key = 'Velocidad del sonido unidad', 
                                                        number_of_inputs = 1, 
                                                        decimals = 1, 
                                                        inputs_range = (0, None))
    
    return(inputs)

def generate_all_output_fields(dimensionamientos: list[backend2.Dimensionamiento]):

    backend2.set_all_output_values(dimensionamientos)

    generate_multiple_inputs(written_name = 'Caudal', 
                             quantity_name = 'Caudal', 
                             base_key = 'Caudal output', 
                             unit_key = 'Caudal output unidad', 
                             decimals = 0, 
                             disabled = True)

    generate_multiple_inputs(written_name = 'Apertura', 
                             quantity_name = 'Apertura', 
                             base_key = 'Apertura', 
                             unit_key = 'Apertura unidad', 
                             decimals = 1, 
                             disabled = True)
    
    generate_multiple_inputs(written_name = 'Cv', 
                             quantity_name = 'Cv', 
                             base_key = 'Cv', 
                             unit_key = 'Cv unidad', 
                             decimals = 0, 
                             disabled = True)
    
    generate_multiple_inputs(written_name = 'Diferencia de presión máxima', 
                             quantity_name = 'Presión', 
                             base_key = 'Diferencia de presión máxima', 
                             unit_key = 'Diferencia de presión máxima unidad', 
                             decimals = 1, 
                             disabled = True)
    
    generate_multiple_inputs(written_name = 'Velocidad del fluido', 
                             quantity_name = 'Velocidad', 
                             base_key = 'Velocidad del fluido', 
                             unit_key = 'Velocidad del fluido unidad', 
                             decimals = 1, 
                             disabled = True)
    
    generate_multiple_inputs(written_name = 'Predicción de ruido', 
                             quantity_name = 'Ruido', 
                             base_key = 'Predicción de ruido', 
                             unit_key = 'Predicción de ruido unidad', 
                             decimals = 1, 
                             disabled = True)

def write_flags_text(flags: list[str]):
    flag_text = {'opening_too_big': 'La válvula es demasiado pequeña para alcanzar ese caudal con esas condiciones de trabajo.', 
                 'opening_too_small': 'La válvula trabaja con un ángulo o porcentaje de abertura menor a 10%. Para durabilidad y seguridad se recomienda trabajo entre 20% y 80%.', 
                 'is_cavitating': 'El fluido cavita', 
                 'is_eroding': 'La velocidad del fluido genera erosión en la válvula'}
    for flag in flags:
        st.write(f'-{flag_text[flag]}')

def write_all_flags_text(dimensionamientos: list[backend2.Dimensionamiento]):

    all_flags = {}
    for index in range(3):
        all_flags[index] = []
        for condition in ['opening_too_big', 'opening_too_small', 'is_cavitating', 'is_eroding']:
            dimensionamiento = dimensionamientos[index]
            if getattr(dimensionamiento, condition):
                all_flags[index].append(condition)
    
    if not (all_flags[0] == [] and all_flags[1] == [] and all_flags[2] == []):
        st.subheader('Advertencias')
    for index in range(3):
        if all_flags[index] != []:
            st.write(f'Para las condiciones de la {TO_COLUMN[index]} columna:')
            write_flags_text(all_flags[index])
    
def plot_opening_vs_flow(dimensionamientos: list[backend2.Dimensionamiento]):
    valve = dimensionamientos[0].valve
    diameter = dimensionamientos[0].diameter
    if valve is None or diameter is None:
        return()

    openings = list(valve.Cv.columns)
    Cvs = list(valve.Cv.loc[diameter])

    extra_openings = []
    extra_Cvs = []

    for index in range(3):
        extra_opening = dimensionamientos[index].opening
        extra_Cv = dimensionamientos[index].Cv
        if extra_opening is not None and extra_Cv is not None:
            if 10 < extra_opening <= valve.max_opening:
                extra_openings.append(round(extra_opening, 1))
                extra_Cvs.append(round(extra_Cv))
    
    openings = sorted(openings + extra_openings)
    Cvs = sorted(Cvs + extra_Cvs)

    plot = go.Figure()
    plot.update_layout(xaxis_title = 'Apertura de la válvula (%)', yaxis_title = 'Cv')
    plot.add_trace(go.Scatter(x = openings, y = Cvs, mode = 'lines+markers'))

    for x in extra_openings:
        plot.add_vline(x = x, 
                       line = {'color': 'lightgray', 'width': 2}, 
                       layer = 'below')

    st.plotly_chart(plot)#, theme = None)



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
    inputs = backend2.process_inputs(inputs)
    dimensionamientos = backend2.get_dimensionamientos_from_triple_inputs(inputs)

with output_column:
    st.subheader('Dimensionamiento')
    generate_all_output_fields(dimensionamientos)
    plot_opening_vs_flow(dimensionamientos)

with input_column:
    write_all_flags_text(dimensionamientos)



if st.session_state['rerun']:
    st.session_state['rerun'] = False
    st.rerun()







