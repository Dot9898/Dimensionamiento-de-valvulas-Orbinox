
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
                             placeholder = 'Tipo de fluido', 
                             key = 'fluid_dropdown')


def lo_que_sigue():
    names_column, inputs_column = st.columns([1, 2])


#-----------------------------------------------------------------------------------------------------------------------------------------------


fluids = get_fluids()
valve_types = ['Mariposa', 'Pinch']
images = load_images()
st.set_page_config(layout = 'wide')


generate_title_and_logo(images)

input_column, separator_column, output_column = st.columns([19.5, 1, 19.5])


with input_column:
    generate_header_and_dropdowns(valve_types, fluids)

with separator_column:
    generate_vertical_divider(height = 640)
































