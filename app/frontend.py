
#encoding: utf-8

from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
import streamlit as st
from backend import get_fluids

ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'
LOGO_WIDTH = 200


@st.cache_resource
def load_images():
    images = {}
    images['logo'] = Image.open(IMG_PATH / 'Orbinox_logo.png')
    return(images)

def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()

def generate_input_fields(input_names_to_units = {}, text_input_boxes_labels = [], columns_spacing = [1, 1, 1]): #columns_spacing es [largo de los nombres, largo de cada text input, largo de las unidades]
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
                    key = name + '_' + label
                    st.text_input(key, 
                                  label_visibility = 'collapsed', 
                                  placeholder = label, 
                                  key = key)
                    
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

def generate_vertical_divider(height):
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
    
def generate_header_and_dropdowns(valve_types, fluids):
    st.subheader('Condiciones de trabajo')
    valve_selection_column, fluid_selection_column = st.columns([1, 2])

    with valve_selection_column:
        valve = st.selectbox('Tipo de válvula', 
                             valve_types, 
                             label_visibility = 'collapsed', 
                             accept_new_options = False, 
                             index = None, 
                             placeholder = 'Tipo de válvula', 
                             key = 'valve_dropdown')

    with fluid_selection_column:
        fluid = st.selectbox('Fluido', 
                             fluids + ['Otro'], 
                             label_visibility = 'collapsed', 
                             accept_new_options = False, 
                             index = None, 
                             placeholder = 'Fluido', 
                             key = 'fluid_dropdown')

#def generate_triple_input_fields()

def generate_all_input_fields():

    generate_input_fields(input_names_to_units = {'Caudal': ['km', 'm', 'cm'], 
                                                  'Presión de entrada': ['test1', 'test2'], 
                                                  'Presión de salida': ['abc'], 
                                                  'Diferencia de presión': ['3']}, 
                          text_input_boxes_labels = ['mínimo', 'normal', 'máximo'], 
                          columns_spacing = [2, 1, 1])
    
    generate_input_fields(input_names_to_units = {'Diámetro nominal': ['km', 'm', 'cm'], 
                                                  'Temperatura': ['test1', 'test2'], 
                                                  'Gravedad específica': ['abc'], 
                                                  'Presión de vapor': ['3'], 
                                                  'Viscosidad': ['centistokes'], 
                                                  'Velocidad del sonido': ['m/s']}, 
                          text_input_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1])





#-----------------------------------------------------------------------------------------------------------------------------------------------


fluids = get_fluids()
valve_types = ['Mariposa', 'Pinch']
images = load_images()
st.set_page_config(layout = 'wide')


generate_title_and_logo(images)

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])


with input_column:
    generate_header_and_dropdowns(valve_types, fluids)
    generate_all_input_fields()

with separator_column:
    generate_vertical_divider(height = 640)































