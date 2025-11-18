
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

def do_nothing():
    pass

def float_cast(input):
    try:
        return(float(input))
    except:
        return(None)
    
@st.cache_resource
def load_images():
    images = {}
    images['logo'] = Image.open(IMG_PATH / 'Orbinox_logo.png')
    return(images)

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def init_session_state(defaults):
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

def generate_input_fields(input_names_to_units = {}, text_input_boxes_labels = [], columns_spacing = [1, 1, 1], callback = do_nothing): #columns_spacing es [largo de los nombres, largo de cada text input, largo de las unidades]
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
                    st.session_state[key] = st.text_input(key, 
                                                          value = st.session_state[key], 
                                                          label_visibility = 'collapsed', 
                                                          placeholder = label, 
                                                          on_change = callback, 
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
                     key = 'Válvula')

    with fluid_selection_column:
        st.selectbox('Fluido', 
                     fluids + ['Otro'], 
                     label_visibility = 'collapsed', 
                     accept_new_options = False, 
                     index = None, 
                     placeholder = 'Fluido', 
                     key = 'Fluido')


def generate_all_input_fields():

    generate_input_fields(input_names_to_units = {'Caudal': ['km', 'm', 'cm'], 
                                                  'Presión de entrada': ['test1', 'test2'], 
                                                  'Presión de salida': ['abc'], 
                                                  'Diferencia de presión': ['3']}, 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    generate_input_fields(input_names_to_units = {'Diámetro nominal': ['km', 'm', 'cm']}, 
                          text_input_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1])
    
    generate_input_fields(input_names_to_units = {'Temperatura': ['test1', 'test2']}, 
                          text_input_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1], 
                          callback = do_nothing)

    generate_input_fields(input_names_to_units = {'Gravedad específica': ['abc'], 
                                                  'Presión de vapor': ['3'], 
                                                  'Viscosidad': ['centistokes'], 
                                                  'Velocidad del sonido': ['m/s']}, 
                          text_input_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1])


#-----------------------------------------------------------------------------------------------------------------------------------------------


valves = backend.get_valves()
fluids = backend.get_fluids()
images = load_images()
st.set_page_config(layout = 'wide')

names = ['Válvula',
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
defaults = {}
for key in names:
    defaults[key] = None
init_session_state(defaults)



generate_title_and_logo(images)

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])

with separator_column:
    vertical_divider(height = 640)

with input_column:
    generate_header_and_dropdowns(valves, fluids)
    generate_all_input_fields()


valve = st.session_state['Válvula']
fluid = st.session_state['Fluido']
flow = {'min': float_cast(st.session_state['Caudal_mínimo']), 'normal': float_cast(st.session_state['Caudal_normal']), 'max': float_cast(st.session_state['Caudal_máximo'])}
in_pressure = {'min': float_cast(st.session_state['Presión de entrada_mínimo']), 'normal': float_cast(st.session_state['Presión de entrada_normal']), 'max': float_cast(st.session_state['Presión de entrada_máximo'])}
out_pressure = {'min': float_cast(st.session_state['Presión de salida_mínimo']), 'normal': float_cast(st.session_state['Presión de salida_normal']), 'max': float_cast(st.session_state['Presión de salida_máximo'])}
pressure_differential = {'min': float_cast(st.session_state['Diferencia de presión_mínimo']), 'normal': float_cast(st.session_state['Diferencia de presión_normal']), 'max': float_cast(st.session_state['Diferencia de presión_máximo'])}
diameter = float_cast(st.session_state['Diámetro nominal'])
temperature = float_cast(st.session_state['Temperatura'])



if st.session_state['Gravedad específica'] is None:
    st.session_state['Gravedad específica'] = backend.calculate_specific_gravity(temperature, fluid)  #Kelvin #La presión es negligible
specific_gravity = float_cast(st.session_state['Gravedad específica'])

#need backend functions from data
vapor_pressure = float_cast(st.session_state['Presión de vapor'])
viscosity = float_cast(st.session_state['Viscosidad'])
speed_of_sound = float_cast(st.session_state['Velocidad del sonido'])


Cv = {}
for quantity in ['min', 'normal', 'max']:
    Cv[quantity] = backend.calculate_flow_coefficient_Cv(specific_gravity, flow[quantity], pressure_differential[quantity])

Cv

Reynolds_number = {}
for quantity in ['min, normal, max']:
    Reynolds_number[quantity] = backend.

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































