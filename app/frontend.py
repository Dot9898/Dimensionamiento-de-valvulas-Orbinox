
#encoding: utf-8

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import plotly.graph_objects as go
import pint
import streamlit as st
import backend

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'
LOGO_WIDTH = 200


#Utilities

def float_cast(input):
    if isinstance(input, pint.Quantity):
        return
    try:
        return(float(input))
    except(ValueError, TypeError):
        return(None)

def substract_handling_type(x, y):
    x = float_cast(x)
    y = float_cast(y)
    if x is None or y is None:
        return(None)
    return(x - y)

def multiply_handling_type(x, y):
    x = float_cast(x)
    y = float_cast(y)
    if x is None or y is None:
        return(None)
    return(x * y)

def gt_handling_type(x, y):
    x = float_cast(x)
    y = float_cast(y)
    if x is None or y is None:
        return(None)
    return(x > y)

@st.cache_resource
def load_images():
    images = {}
    images['logo'] = Image.open(IMG_PATH / 'Orbinox_logo.png')
    return(images)

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return(base64.b64encode(buffer.getvalue()).decode())

def init_session_state(defaults):
    for key in defaults:
        if key not in st.session_state:
            st.session_state[key] = defaults[key]

def get_min_normal_max_casted_to_float(key):
    casted_vars = {'min': float_cast(st.session_state[key + '_mínimo']), 
                   'normal': float_cast(st.session_state[key + '_normal']), 
                   'max': float_cast(st.session_state[key + '_máximo'])}
    return(casted_vars)

def assign_all_input_variables():

    valve = st.session_state['Válvula']
    fluid = st.session_state['Fluido']
    flow = get_min_normal_max_casted_to_float('Caudal')
    in_pressure = get_min_normal_max_casted_to_float('Presión de entrada')

    if st.session_state['Diferencia de presión_normal_is_disabled']:
        
        out_pressure = get_min_normal_max_casted_to_float('Presión de salida')

        st.session_state['Diferencia de presión_mínimo'] = substract_handling_type(in_pressure['min'], out_pressure['min'])
        st.session_state['Diferencia de presión_normal'] = substract_handling_type(in_pressure['normal'], out_pressure['normal'])
        st.session_state['Diferencia de presión_máximo'] = substract_handling_type(in_pressure['max'], out_pressure['max'])
        pressure_differential = get_min_normal_max_casted_to_float('Diferencia de presión')

    elif st.session_state['Presión de salida_normal_is_disabled']:
        
        pressure_differential = get_min_normal_max_casted_to_float('Diferencia de presión')

        st.session_state['Presión de salida_mínimo'] = substract_handling_type(in_pressure['min'], pressure_differential['min'])
        st.session_state['Presión de salida_normal'] = substract_handling_type(in_pressure['normal'], pressure_differential['normal'])
        st.session_state['Presión de salida_máximo'] = substract_handling_type(in_pressure['max'], pressure_differential['max'])
        
        out_pressure = get_min_normal_max_casted_to_float('Presión de salida')

    else:
        out_pressure = get_min_normal_max_casted_to_float('Presión de salida')
        pressure_differential = get_min_normal_max_casted_to_float('Diferencia de presión')

    diameter = float_cast(st.session_state['Diámetro nominal'])
    temperature = float_cast(st.session_state['Temperatura'])
    
    return(valve, fluid, flow, in_pressure, out_pressure, pressure_differential, diameter, temperature)

def assign_database_variable(fluid, temperature, key):
    
    if st.session_state[key] is not None:
        return
    if fluid is None or temperature is None:
        st.session_state[key] = None
        return
    if fluid.name == 'Otro':
        return
    
    key_to_fluid_data = {'Gravedad específica': fluid.specific_gravity, 
                         'Presión de vapor': fluid.vapor_pressure, 
                         'Viscosidad': fluid.viscosity, 
                         'Velocidad del sonido': fluid.speed_of_sound}
    
    temperature_to_data = key_to_fluid_data[key]
    
    available_temperatures = temperature_to_data.keys()
    closest_temperature = backend.closest_in_list(available_temperatures, temperature)
    data_value = temperature_to_data[closest_temperature]
    st.session_state[key] = data_value

    return(data_value)

def assign_all_database_variables():
    specific_gravity = assign_database_variable(fluid, temperature, 'Gravedad específica')
    vapor_pressure = assign_database_variable(fluid, temperature, 'Presión de vapor')
    viscosity = assign_database_variable(fluid, temperature, 'Viscosidad')
    speed_of_sound = assign_database_variable(fluid, temperature, 'Velocidad del sonido')
    return(specific_gravity, vapor_pressure, viscosity, speed_of_sound)

def calculate_and_assign_all_output_variables(valve, flow, in_pressure, pressure_differential, diameter, specific_gravity, vapor_pressure, viscosity, speed_of_sound):
    Reynolds_number, correction_factor, Cv, opening, FL, allowable_pressure_differential, velocity, is_cavitating, is_eroding = {}, {}, {}, {}, {}, {}, {}, {}, {}
    if valve is not None and diameter is not None:
        max_opening = max(valve.Cv[diameter].keys())
    is_opening_more_than_max_opening = {'min': False, 'normal': False, 'max': False}
    for quantity in ['min', 'normal', 'max']:
        Reynolds_number[quantity] = backend.calculate_Reynolds_number(flow[quantity], diameter, viscosity, valve)
        correction_factor[quantity] = backend.get_Reynolds_correction_factor(Reynolds_number[quantity])
        if Reynolds_number[quantity] is not None:
            if Reynolds_number[quantity] < 1:
                pass #WARNING FLUIDO DEMASIADO VISCOSO EN ESE DIÁMETRO Y CAUDAL #incluir para 10, 1, y 0.1
        Cv[quantity] = multiply_handling_type(correction_factor[quantity], backend.calculate_flow_coefficient_Cv(specific_gravity, flow[quantity], pressure_differential[quantity]))
        opening[quantity] = backend.calculate_opening_percentage_at_Cv(Cv[quantity], diameter, valve)
        if opening[quantity] is not None and valve is not None and diameter is not None:
            if opening[quantity] < 10: #MIN OPENING
                pass #WARNING APERTURA MUY PEQUEÑA
            if opening[quantity] > max_opening:
                pass #WARNING APERTURA MÁXIMA INSUFICIENTE, CAMBIAR CAUDAL Y CV A APERTURA MÁXIMA
        FL[quantity] = backend.get_pressure_recovery_factor_FL(opening[quantity], valve)
        allowable_pressure_differential[quantity] = backend.calculate_allowable_pressure_differential_without_cavitation(FL[quantity], in_pressure[quantity], vapor_pressure, valve)
        velocity[quantity] = backend.calculate_in_velocity(flow[quantity], diameter)
        is_cavitating[quantity] = gt_handling_type(pressure_differential[quantity], allowable_pressure_differential[quantity])
        if valve is not None:
            is_eroding[quantity] = gt_handling_type(velocity[quantity], valve.max_velocity_without_erosion)
    #if True in is_opening_more_than_max_opening.values():

    max_velocity = max([velocity for velocity in velocity.values() if velocity is not None], default = None)
    cavitation_message = 'Sí cavita' if True in is_cavitating.values() else 'No cavita'
    erosion_message = 'Hay erosión' if True in is_eroding.values() else 'No hay erosión'
    return(Reynolds_number, correction_factor, Cv, opening, is_opening_more_than_max_opening, FL, allowable_pressure_differential, velocity, is_cavitating, is_eroding, max_velocity, cavitation_message, erosion_message)



#Callbacks

def do_nothing():
    pass

def generic_callback(callback):
    callback()
    st.session_state['rerun'] = True

def text_input_callback(callback, name, text_input_boxes_labels):
    unit_key = name + '_unit'
    unit = st.session_state[unit_key]
    real_keys = [name + '_' + label for label in text_input_boxes_labels]

    if isinstance(unit, pint.Unit):
        for key in real_keys:
            magnitude = float_cast(st.session_state['_' + key])
            print('\n\n\n\n', magnitude, '\n\n\n\n')
            if magnitude is None:
                st.session_state[key] = None
            else:
                st.session_state[key] = magnitude * unit

    callback()
    st.session_state['rerun'] = True

def disable_pressure_differential(args): #Presión de salida callback
    
    is_disabled = False
    
    for key in ['_Presión de salida_mínimo', '_Presión de salida_normal', '_Presión de salida_máximo']:
        if float_cast(st.session_state[key]) is not None: #Si al menos uno de los inputs es un float, desactivar los otros botones
            is_disabled = True

    for key in ['Diferencia de presión_mínimo', 'Diferencia de presión_normal', 'Diferencia de presión_máximo']:
        st.session_state[key + '_is_disabled'] = is_disabled

def disable_out_pressure(args): #Presión de salida callback
    
    is_disabled = False
    
    for key in ['_Diferencia de presión_mínimo', '_Diferencia de presión_normal', '_Diferencia de presión_máximo']:
        if float_cast(st.session_state[key]) is not None:
            is_disabled = True

    for key in ['Presión de salida_mínimo', 'Presión de salida_normal', 'Presión de salida_máximo']:
        st.session_state[key + '_is_disabled'] = is_disabled

def disable_some_data_inputs_if_fluid_is_selected(args): #Fluido callback

    is_disabled = True
    fluid = st.session_state['Fluido']
    if fluid is None:
        is_disabled = False
    elif fluid.name == 'Otro':
        is_disabled = False
    
    keys = ['Gravedad específica', 'Presión de vapor', 'Viscosidad', 'Velocidad del sonido']
    for key in keys:
            st.session_state[key + '_is_disabled'] = is_disabled



#Frontend

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

def generate_input_field(name, 
                         units, 
                         text_input_boxes_labels = [''], 
                         columns_spacing = [2, 3, 1], #[largo de los nombres, largo de cada text input, largo de las unidades]
                         can_be_disabled = False, 
                         callback = do_nothing):
    number_of_text_inputs = len(text_input_boxes_labels)
    columns_spacing[1] = columns_spacing[1] * number_of_text_inputs

    names_column, inputs_column, units_column = st.columns(columns_spacing)  # Las columnas se regeneran en cada fila (name) para alinear correctamente los nombres y los text input

    with names_column:
        st.write(name)

    with units_column:
        if units != []:
            unit_key = name + '_unit'
            old_unit_key = unit_key + '_old'
            ureg = st.session_state['ureg']
            st.session_state[unit_key] = ureg[st.selectbox(unit_key, 
                                                            units, 
                                                            label_visibility = 'collapsed', 
                                                            accept_new_options = False, 
                                                            placeholder = units[0], 
                                                            on_change = generic_callback, 
                                                            args = [do_nothing], 
                                                            key='_' + unit_key)]
            unit = st.session_state[unit_key]
            old_unit = st.session_state[old_unit_key]  

            for label in text_input_boxes_labels:
                if label != '':
                    key = name + '_' + label
                else:
                    key = name
                if unit != old_unit:
                    if isinstance(st.session_state[key], pint.Quantity):
                        st.session_state[key] = st.session_state[key].to(unit)

            st.session_state[old_unit_key] = st.session_state[unit_key]

    with inputs_column:
        inputs_subcolumns = st.columns([1] * number_of_text_inputs)
        for index in range(len(inputs_subcolumns)):
            with inputs_subcolumns[index]:

                label = text_input_boxes_labels[index]
                if label != '':
                    key = name + '_' + label
                else:
                    key = name

                disabled_state = False
                if can_be_disabled:
                    disabled_state = st.session_state[key + '_is_disabled']
                
                if isinstance(st.session_state[key], pint.Quantity):
                    st.session_state['_' + key] = str(round(st.session_state[key].magnitude, 1))

                st.session_state[key] = st.text_input(key, 
                                                        label_visibility = 'collapsed', 
                                                        placeholder = label, 
                                                        on_change = text_input_callback, 
                                                        args = [callback, name, text_input_boxes_labels], 
                                                        disabled = disabled_state, 
                                                        key = '_' + key)

                st.session_state[key] = float_cast(st.session_state[key])
                if isinstance(st.session_state[key], float):
                    st.session_state[key] = st.session_state[key] * unit

def generate_output_field(name, 
                          values, 
                          units,
                          output_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1]):
    number_of_outputs = len(output_boxes_labels)
    columns_spacing[1] = columns_spacing[1]*number_of_outputs
    
    name_column, output_column, units_column = st.columns(columns_spacing)
        
    with name_column:
        st.write(name)

    with output_column:
        output_subcolumns = st.columns([1]*number_of_outputs)
        for index in range(len(output_subcolumns)):
            with output_subcolumns[index]:
                label = output_boxes_labels[index]
                value = values[index]
                if value == None:
                    value = label
                elif float_cast(value) is not None:
                    value = round(value, 1)
                    
                st.text_input(name + '_' + label + str(value), 
                              value = value, 
                              label_visibility = 'collapsed', 
                              placeholder = label, 
                              disabled = True, 
                              key = name + '_' + label + '_' + str(value))

    with units_column:
        if len(units) >= 2:
            st.selectbox(name + '_' + label + '_unit', 
                         units, 
                         label_visibility = 'collapsed', 
                         accept_new_options = False, 
                         placeholder = 'unidad', 
                         key = name + '_' + label + '_unit')
        elif len(units) == 1:
            st.write(units[0])

def generate_dropdown_input_field(name, 
                                  options, 
                                  units, 
                                  label = '', 
                                  columns_spacing = [2, 3, 1], 
                                  callback = do_nothing):
        
    name_column, input_column, units_column = st.columns(columns_spacing)

    with name_column:
        st.write(name)
    
    with input_column:
        key = name
        if float_cast(st.session_state[key]) is not None: #and st.session_state[key] in options:
            label = str(st.session_state[key])
        
        st.selectbox(key, 
                     options, 
                     label_visibility = 'collapsed', 
                     accept_new_options = False, 
                     index = None, 
                     placeholder = label, 
                     on_change = generic_callback, 
                     args = [callback], 
                     key = key)
        
    with units_column:
        if len(units) >= 2:
            key = name + '_unit'
            st.selectbox(key, 
                         units, 
                         label_visibility = 'collapsed', 
                         accept_new_options = False, 
                         placeholder = 'unidad', 
                         key = key)
        elif len(units) == 1:
            st.write(units[0])

def generate_title_and_logo(images):
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
        logo = images['logo']
        logo = img_to_base64(logo)
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
    
def generate_header_and_dropdowns(valves, fluids):
    st.subheader('Condiciones de trabajo')
    valve_selection_column, fluid_selection_column, empty_column = st.columns([2, 3, 1])

    with valve_selection_column:
        st.selectbox('Tipo de válvula', 
                     valves, 
                     label_visibility = 'collapsed', 
                     accept_new_options = False, 
                     index = None, 
                     placeholder = 'Válvula', 
                     on_change = generic_callback, 
                     args = [do_nothing], 
                     key = 'Válvula')

    with fluid_selection_column:
        st.selectbox('Fluido', 
                     fluids, 
                     label_visibility = 'collapsed', 
                     accept_new_options = False, 
                     index = None, 
                     placeholder = 'Fluido', 
                     on_change = generic_callback, 
                     args = [disable_some_data_inputs_if_fluid_is_selected], 
                     key = 'Fluido')

def generate_all_input_fields():

    generate_input_field('Caudal', 
                         ['GPM', 'L/min', 'm³/h'], 
                         text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                         columns_spacing = [2, 1, 1])
    
    generate_input_field('Presión de entrada', 
                         ['PSIG'], 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])

    generate_input_field('Presión de salida', 
                         ['PSIG'], 
                         text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                         columns_spacing = [2, 1, 1], 
                         can_be_disabled = True, 
                         callback = disable_pressure_differential)
    for quantity in ['mínimo', 'normal', 'máximo']:
        if st.session_state['Presión de salida_' + quantity] is not None and st.session_state['Presión de entrada_' + quantity] is not None:
            if st.session_state['Presión de salida_' + quantity] >= st.session_state['Presión de entrada_' + quantity]: #AGREGAR MENSAJE DE PRESIÓN DE SALIDA DEBE SER MENOR A LA DE ENTRADA
               st.session_state['Presión de salida_' + quantity] = None

    generate_input_field('Diferencia de presión', 
                         ['PSI'], 
                         text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                         can_be_disabled = True, 
                         columns_spacing = [2, 1, 1,], 
                         callback = disable_out_pressure)
    
    if st.session_state['Válvula'] is not None:
        possible_diameters = sorted(list(st.session_state['Válvula'].Cv.keys()))
    else:
        possible_diameters = []
    generate_dropdown_input_field('Diámetro nominal', 
                                  possible_diameters, 
                                  ['in'], 
                                  label = '', 
                                  columns_spacing = [2, 3, 1], 
                                  callback = do_nothing)

    generate_input_field('Temperatura', 
                         ['°C'])

    generate_input_field('Gravedad específica', 
                         [], 
                         can_be_disabled = True)
    
    generate_input_field('Presión de vapor', 
                         ['PSIA'], 
                         can_be_disabled = True)
    
    generate_input_field('Viscosidad', 
                         ['cSt'], 
                         can_be_disabled = True)
    
    generate_input_field('Velocidad del sonido', 
                         ['m/s'], 
                         can_be_disabled = True)

def generate_all_output_fields(flow, opening, Cv, allowable_pressure_differential, max_velocity, cavitation_message, erosion_message):

    generate_output_field('Caudal', 
                          [flow['min'], flow['normal'], flow['max']], 
                          ['GPM'], 
                          output_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    shown_opening = opening.copy()
    shown_allowable_pressure_differential = allowable_pressure_differential.copy()
    for key in shown_opening:
        if float_cast(shown_opening[key]) is not None:
            if shown_opening[key] > 500:
                shown_opening[key] = '>100'
                shown_allowable_pressure_differential[key] = ' '
    
    generate_output_field('Apertura', 
                          [shown_opening['min'], shown_opening['normal'], shown_opening['max']], 
                          ['%'], 
                          output_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    generate_output_field('Cv', 
                          [Cv['min'], Cv['normal'], Cv['max']], 
                          ['GPM'], 
                          output_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    generate_output_field('Diferencia de presión permitida', 
                          [shown_allowable_pressure_differential['min'], shown_allowable_pressure_differential['normal'], shown_allowable_pressure_differential['max']], 
                          ['PSI'], 
                          output_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])

    generate_output_field('Velocidad máxima', 
                          [max_velocity], 
                          ['ft/s'])
    
    generate_output_field('Ruido estimado', 
                          [None], 
                          ['dB'])
    
    generate_output_field('Estabilidad de la válvula', 
                          [cavitation_message, None, erosion_message], 
                          [''], 
                          output_boxes_labels = ['Cavitación', 'Flashing?', 'Erosión'], 
                          columns_spacing = [2, 1, 1])

def plot_opening_vs_flow(valve, diameter, pressure_differential, extra_openings, extra_flows):

    if valve is None or diameter is None or pressure_differential is None:
        return

    all_openings = list(valve.Cv[diameter].keys())
    min_opening, max_opening = min(all_openings), max(all_openings)

    opening_to_flow = {}
    for quantity in ['min', 'normal', 'max']:
        extra_flows[quantity], extra_openings[quantity] = float_cast(extra_flows[quantity]), float_cast(extra_openings[quantity])
        if extra_openings[quantity] is not None and extra_flows[quantity] is not None:
            if extra_openings[quantity] >= min_opening and extra_openings[quantity] <= max_opening:
                opening_to_flow[round(extra_openings[quantity], 1)] = round(extra_flows[quantity])

    for opening in all_openings:
        Cv = valve.Cv[diameter][opening]
        approximated_pressure_differential = pressure_differential #CAMBIAR ESTO SEGÚN SE REQUIERA Y AGREGAR A PARÁMETROS DE FUNCIÓN
        flow = float_cast(backend.calculate_flow_from_Cv(Cv, specific_gravity, approximated_pressure_differential))
        if opening is not None and flow is not None:
            opening_to_flow[opening] = round(flow)

    all_openings = sorted(opening_to_flow.keys())
    all_flows = [opening_to_flow[opening] for opening in all_openings]

    if all_openings == []:
        return

    plot = go.Figure()
    plot.add_trace(go.Scatter(x = all_openings, y = all_flows, mode = 'lines+markers'))
    plot.update_layout(xaxis_title = 'Apertura de la válvula (%)', yaxis_title = f'Caudal ({st.session_state['Caudal_unit']})')
    st.plotly_chart(plot)#, theme = None)


#-----------------------------------------------------------------------------------------------------------------------------------------------

valves, fluids = backend.get_data()
images = load_images()

if 'ureg' not in st.session_state:
    st.session_state['ureg'] = pint.UnitRegistry()
    st.session_state['ureg'].load_definitions(ROOT_PATH / 'data/pint_extra_units.txt')

#Key initialization

single_names = ['Válvula', 'Fluido', 'Diámetro nominal', 'Temperatura', 'Gravedad específica', 'Presión de vapor', 'Viscosidad', 'Velocidad del sonido']
single_keys = single_names
triple_names = ['Caudal', 'Presión de entrada', 'Presión de salida', 'Diferencia de presión']
triple_keys = [name + '_' + quantity for name in triple_names for quantity in ['mínimo', 'normal', 'máximo']]

widget_keys = ['_' + key for key in single_keys + triple_keys]
units_keys = [name + '_unit' for name in single_names + triple_names]
old_units_keys = [key + '_old' for key in units_keys]
disablers_keys = [key + '_is_disabled' for key in single_keys + triple_keys]

defaults = {}
for key in single_keys + triple_keys + units_keys + old_units_keys:
    defaults[key] = None
for key in disablers_keys:
    defaults[key] = False
defaults['rerun'] = False
init_session_state(defaults)


#Frontend

st.set_page_config(layout = 'wide')

generate_title_and_logo(images)

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])

with separator_column:
    vertical_divider(height = 920)

with input_column:
    generate_header_and_dropdowns(valves, fluids)
    generate_all_input_fields()

valve, fluid, flow, in_pressure, out_pressure, pressure_differential, diameter, temperature = assign_all_input_variables()
specific_gravity, vapor_pressure, viscosity, speed_of_sound = assign_all_database_variables()

(Reynolds_number, correction_factor, Cv, opening, is_opening_more_than_max_opening, FL, allowable_pressure_differential, 
 velocity, is_cavitating, is_eroding, max_velocity, cavitation_message, erosion_message
) = calculate_and_assign_all_output_variables(valve, flow, in_pressure, pressure_differential, 
                                              diameter, specific_gravity, vapor_pressure, viscosity, speed_of_sound)

with output_column:
    st.subheader('‎')
    st.subheader('‎')
    generate_all_output_fields(flow, opening, Cv, allowable_pressure_differential, max_velocity, cavitation_message, erosion_message)

    plot_column = st.columns([5, 1])[0]
    with plot_column:
        TESTPRESSUREDIFF = pressure_differential['min']
        plot_opening_vs_flow(valve, diameter, TESTPRESSUREDIFF, opening, flow)

#caudal, apertura, Cv, velocidad, cavitación check
#Falta ruido y erosión / abrasión para pegar todo. luego preguntar diámetro propuesto, y preguntar detalle gráfico y hacerlo.
#Falta flashing, erosión / abrasión, ruido estimado, diámetro propuesto(?), gráfico



if st.session_state['rerun']: #Reruns on any text input or selection, to avoid input lag
    st.session_state['rerun'] = False
    st.rerun()





#seguir primero con el overwrite text inputs, después con el diameter selectbox, 
#después el flujo general considerando las unidades, después ordenar la carpeta data, 
#después agregar fluidos nuevos, después válvulas nuevas, 
#y después todo lo demás (incluido gráfico y alineamiento)


















