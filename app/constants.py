
#encoding: utf-8

from pathlib import Path
import streamlit as st
from PIL import Image
from base64 import b64encode
from io import BytesIO


def img_to_base64(img):
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return(b64encode(buffer.getvalue()).decode())

@st.cache_data
def load_images():
    images = {}
    images['logo'] = img_to_base64(Image.open(IMG_PATH / 'Orbinox_logo.png'))
    return(images)


ROOT_PATH = Path(__file__).resolve().parent.parent
IMG_PATH = ROOT_PATH / 'img'
DATA_PATH = ROOT_PATH / 'data'

IMAGES = load_images()

DEFAULTS = {'old_values': {}, #old_values always has pint quantities
            'rerun': False, 
            'Gravedad específica 0 is disabled': True, 
            'Presión de vapor 0 is disabled': True, 
            'Viscosidad 0 is disabled': True, 
            'Velocidad del sonido 0 is disabled': True}

UNITS_AS_STRING = {'Caudal': ['m³/h', 'L/min', 'GPM'], 
                   'Presión': ['PSI', 'bar'], 
                   'Temperatura': ['°C', '°F', '°K'], 
                   'Gravedad específica': ['dimensionless'], 
                   'Viscosidad': ['cSt'], 
                   'Velocidad': ['m/s', 'ft/s', 'km/h', 'mph'], 
                   'Apertura': ['%'], 
                   'Cv': ['Cv'], 
                   'Ruido': ['dB']} #Each unit is readable by an ureg call: ureg('m³/h'). The first unit is the canonical one.

BASE_UNITS = {'Caudal': 'GPM', 
              'Presión': 'PSI', 
              'Temperatura': '°C', 
              'Gravedad específica': 'dimensionless', 
              'Presión de vapor': 'PSI', 
              'Viscosidad': 'cSt', 
              'Velocidad': 'ft/s', 
              'Velocidad del sonido': 'ft/s', 
              'Apertura': '%', 
              'Cv': 'Cv', 
              'Ruido': 'dB'}

QUANTITY_NAME_TO_ATTRIBUTE_NAME = {'Gravedad específica': 'specific_gravity', 
                                   'Presión de vapor': 'vapor_pressure', 
                                   'Viscosidad': 'viscosity', 
                                   'Velocidad del sonido': 'speed_of_sound'}

