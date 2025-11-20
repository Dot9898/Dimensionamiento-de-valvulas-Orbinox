
#encoding: utf-8

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import streamlit as st
import backend

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'
LOGO_WIDTH = 200


#Utilities

def float_cast(input):
    try:
        return(float(input))
    except (ValueError, TypeError):
        return(None)

def substract_handling_type(x, y):
    x = float_cast(x)
    y = float_cast(y)
    if x is None or y is None:
        return(None)
    return(x - y)

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
        
        st.session_state['Presión de salida'] = substract_handling_type(in_pressure['min'], pressure_differential['min'])
        st.session_state['Presión de salida'] = substract_handling_type(in_pressure['normal'], pressure_differential['normal'])
        st.session_state['Presión de salida'] = substract_handling_type(in_pressure['max'], pressure_differential['max'])
        
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

#Callbacks

def do_nothing():
    pass

def generic_callback(callback):
    callback()
    st.session_state['rerun'] = True

def disable_pressure_differential(): #Presión de salida callback
    
    is_disabled = False
    
    for key in ['_Presión de salida_mínimo', '_Presión de salida_normal', '_Presión de salida_máximo']:
        if float_cast(st.session_state[key]) is not None: #Si al menos uno de los inputs es un float, desactivar los otros botones
            is_disabled = True

    for key in ['Diferencia de presión_mínimo', 'Diferencia de presión_normal', 'Diferencia de presión_máximo']:
        st.session_state[key + '_is_disabled'] = is_disabled

def disable_out_pressure(): #Presión de salida callback
    
    is_disabled = False
    
    for key in ['_Diferencia de presión_mínimo', '_Diferencia de presión_normal', '_Diferencia de presión_máximo']:
        if float_cast(st.session_state[key]) is not None:
            is_disabled = True

    for key in ['Presión de salida_mínimo', 'Presión de salida_normal', 'Presión de salida_máximo']:
        st.session_state[key + '_is_disabled'] = is_disabled

def disable_some_data_inputs_if_fluid_is_selected(): #Fluido callback

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

def generate_input_fields(input_names_to_units, 
                          text_input_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1], 
                          can_be_disabled = False, 
                          callback = do_nothing): #columns_spacing es [largo de los nombres, largo de cada text input, largo de las unidades]
    number_of_text_inputs = len(text_input_boxes_labels)
    columns_spacing[1] = columns_spacing[1]*number_of_text_inputs
    
    for name in input_names_to_units:
        names_column, inputs_column, units_column = st.columns(columns_spacing) #Las columnas se regeneran en cada fila (name) para alinear correctamente los nombres y los text input
        
        with names_column:
            st.write(name)

        with inputs_column:
            inputs_subcolumns = st.columns([1]*number_of_text_inputs)
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

                    if float_cast(st.session_state[key]) is not None:
                        label = st.session_state[key]
                        
                    st.session_state[key] = st.text_input(key, 
                                                          value = st.session_state[key], 
                                                          label_visibility = 'collapsed', 
                                                          placeholder = label, 
                                                          on_change = generic_callback,
                                                          args = [callback], 
                                                          disabled = disabled_state, 
                                                          key = '_' + key)
                    
        with units_column:
            units = input_names_to_units[name]
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
    valve_selection_column, fluid_selection_column = st.columns([1, 2])

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

    generate_input_fields(input_names_to_units = {'Caudal': ['GPM']}, 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    generate_input_fields(input_names_to_units = {'Presión de entrada': ['PSIA']}, 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    generate_input_fields(input_names_to_units = {'Presión de salida': ['PSIA']}, 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1], 
                          can_be_disabled = True, 
                          callback = disable_pressure_differential)
    
    generate_input_fields(input_names_to_units = {'Diferencia de presión': ['PSI']}, 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          can_be_disabled = True, 
                          columns_spacing = [2, 1, 1,], 
                          callback = disable_out_pressure)
    
    generate_input_fields(input_names_to_units = {'Diámetro nominal': ['in']})
    
    generate_input_fields(input_names_to_units = {'Temperatura': ['℃']})

    generate_input_fields(input_names_to_units = {'Gravedad específica': ['']}, 
                          can_be_disabled = True)
    
    generate_input_fields(input_names_to_units = {'Presión de vapor': ['PSIA']}, 
                          can_be_disabled = True)
    
    generate_input_fields(input_names_to_units = {'Viscosidad': ['cSt']}, 
                          can_be_disabled = True)
    
    generate_input_fields(input_names_to_units = {'Velocidad del sonido': ['m/s']}, 
                          can_be_disabled = True)


#-----------------------------------------------------------------------------------------------------------------------------------------------


valves = backend.get_valves()
fluids = backend.get_fluids()
images = load_images()


#Key initialization

keys = ['Válvula',
        'Fluido',
        'Caudal_mínimo', 'Caudal_normal', 'Caudal_máximo', 'Caudal_unit', 
        'Presión de entrada_mínimo', 'Presión de entrada_normal', 'Presión de entrada_máximo', 'Presión de entrada_unit', 
        'Presión de salida_mínimo', 'Presión de salida_normal', 'Presión de salida_máximo', 'Presión de salida_unit', 
        'Diferencia de presión_mínimo', 'Diferencia de presión_normal', 'Diferencia de presión_máximo', 'Diferencia de presión_unit', 
        'Diámetro nominal', 'Diámetro nominal_unit', 
        'Temperatura','Temperatura_unit', 
        'Gravedad específica', 'Gravedad específica_unit', 
        'Presión de vapor', 'Presión de vapor_unit', 
        'Viscosidad', 'Viscosidad_unit', 
        'Velocidad del sonido', 'Velocidad del sonido_unit']

text_input_disablers_keys = ['Presión de salida_mínimo_is_disabled', 'Presión de salida_normal_is_disabled', 'Presión de salida_máximo_is_disabled', 
                             'Diferencia de presión_mínimo_is_disabled', 'Diferencia de presión_normal_is_disabled', 'Diferencia de presión_máximo_is_disabled', 
                             'Gravedad específica_is_disabled', 
                             'Presión de vapor_is_disabled', 
                             'Viscosidad_is_disabled', 
                             'Velocidad del sonido_is_disabled']

defaults = {}
for key in keys:
    defaults[key] = None
for key in text_input_disablers_keys:
    defaults[key] = False
defaults['rerun'] = False
init_session_state(defaults)


#Frontend

st.set_page_config(layout = 'wide')

generate_title_and_logo(images)

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])

with separator_column:
    vertical_divider(height = 640)

with input_column:
    generate_header_and_dropdowns(valves, fluids)
    generate_all_input_fields()


valve, fluid, flow, in_pressure, out_pressure, pressure_differential, diameter, temperature = assign_all_input_variables()
specific_gravity, vapor_pressure, viscosity, speed_of_sound = assign_all_database_variables()

def calculate_specific_gravity(fluid, temperature):  #Kelvin? #La presión es negligible
    if fluid is None or temperature is None:
        return(None)

    
    if fluid.name == 'Agua':
        specific_gravity = 1.0157 - 6.81e-4 * temperature #Aproximación lineal, <2% error entre 0 y 200 C

    return(specific_gravity)








#need backend functions from data
vapor_pressure = float_cast(st.session_state['Presión de vapor'])
viscosity = float_cast(st.session_state['Viscosidad'])
speed_of_sound = float_cast(st.session_state['Velocidad del sonido'])


Cv = {}
for quantity in ['min', 'normal', 'max']:
    Cv[quantity] = backend.calculate_flow_coefficient_Cv(specific_gravity, flow[quantity], pressure_differential[quantity])

Cv


#---------not final code

Reynolds_number = {}
for quantity in ['min, normal, max']:
    #Reynolds_number[quantity] = backend.calculate_reynolds_number(flow[quantity], diameter, )
    pass


def calculate_Reynolds_number(flow,        #GPM
                              diameter,    #inches
                              viscosity,   #centistokes
                              valve):
    
    valve_factor = VALVE_REYNOLDS_FACTOR[valve.name]
    Reynolds_number = 3160 * flow / (diameter * viscosity) * valve_factor #???????????
    return(Reynolds_number)

def calculate_pressure_recovery_factor_FL(in_pressure,  #PSIA
                                          out_pressure, #PSIA
                                          vc_pressure): #PSIA
    
    FL = sqrt((in_pressure - out_pressure) / (in_pressure - vc_pressure))
    return(FL)



st.session_state['Diferencia de presión_mínimo']

#--------------


if st.session_state['rerun']: #Reruns on any text input to avoid lag
    st.session_state['rerun'] = False
    st.rerun()
























