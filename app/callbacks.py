
#encoding: utf-8

import streamlit as st
import pint
import numpy as np
import backend2
from unit_registry import ureg
from constants import QUANTITY_NAME_TO_ATTRIBUTE_NAME, BASE_UNITS
from load_data import Fluid, FLUIDS




def update_number_inputs(unit_key, associated_keys):
    for key in associated_keys:
        if st.session_state['old_values'][key] is not None:
            old_quantity = st.session_state['old_values'][key]
            current_unit = ureg(st.session_state[unit_key])
            current_quantity = old_quantity.to(current_unit)
            st.session_state[key] = current_quantity.magnitude


def update_pressure_differential_value(index):
    in_pressure_key = f'Presión de entrada {index}'
    in_pressure_unit_key = f'Presión de entrada unidad'
    out_pressure_key = f'Presión de salida {index}'
    out_pressure_unit_key = f'Presión de salida unidad'
    pressure_differential_key = f'Diferencia de presión {index}'
    pressure_differential_unit_key = f'Diferencia de presión unidad'

    in_pressure_base = backend2.in_base_unit('Presión', in_pressure_key, in_pressure_unit_key)
    out_pressure_base = backend2.in_base_unit('Presión', out_pressure_key, out_pressure_unit_key)

    if in_pressure_base is None or out_pressure_base is None:
        st.session_state[pressure_differential_key] = None
    
    else:
        pressure_differential_unit = st.session_state[pressure_differential_unit_key]
        in_pressure_in_pdiff_unit = in_pressure_base.to(pressure_differential_unit)
        out_pressure_in_pdiff_unit = out_pressure_base.to(pressure_differential_unit)
        pressure_differential = in_pressure_in_pdiff_unit - out_pressure_in_pdiff_unit
        st.session_state[pressure_differential_key] = pressure_differential.magnitude

def enable_or_disable_pressure_differential_box(index):
    out_pressure_key = f'Presión de salida {index}'
    pressure_differential_key = f'Diferencia de presión {index}'

    if st.session_state[out_pressure_key] is None:
        disabled = False
    else:
        disabled = True

    st.session_state[f'{pressure_differential_key} is disabled'] = disabled

def set_pressure_differential_box(index):
    update_pressure_differential_value(index)
    enable_or_disable_pressure_differential_box(index)


def update_out_pressure_value(index):
    in_pressure_key = f'Presión de entrada {index}'
    in_pressure_unit_key = f'Presión de entrada unidad'
    out_pressure_key = f'Presión de salida {index}'
    out_pressure_unit_key = f'Presión de salida unidad'
    pressure_differential_key = f'Diferencia de presión {index}'
    pressure_differential_unit_key = f'Diferencia de presión unidad'

    in_pressure_base = backend2.in_base_unit('Presión', in_pressure_key, in_pressure_unit_key)
    pressure_differential_base = backend2.in_base_unit('Presión', pressure_differential_key, pressure_differential_unit_key)

    if in_pressure_base is None or pressure_differential_base is None:
        st.session_state[out_pressure_key] = None
    
    else:
        out_pressure_unit = st.session_state[out_pressure_unit_key]
        in_pressure_in_out_pressure_unit = in_pressure_base.to(out_pressure_unit)
        pdiff_in_out_pressure_unit = pressure_differential_base.to(out_pressure_unit)
        out_pressure = in_pressure_in_out_pressure_unit - pdiff_in_out_pressure_unit
        st.session_state[out_pressure_key] = out_pressure.magnitude

def enable_or_disable_out_pressure_box(index):
    out_pressure_key = f'Presión de salida {index}'
    pressure_differential_key = f'Diferencia de presión {index}'

    if st.session_state[pressure_differential_key] is None:
        disabled = False
    else:
        disabled = True

    st.session_state[f'{out_pressure_key} is disabled'] = disabled

def set_out_pressure_box(index):
    update_out_pressure_value(index)
    enable_or_disable_out_pressure_box(index)


def update_pressure_differential_and_out_pressure_value(index):
    out_pressure_key = f'Presión de salida {index}'
    pressure_differential_key = f'Diferencia de presión {index}'

    if st.session_state.get(f'{pressure_differential_key} is disabled', False):
        update_pressure_differential_value(index)

    if st.session_state.get(f'{out_pressure_key} is disabled', False):
        update_out_pressure_value(index)

def update_diameter_dropdown_value():
    if 'Diámetro' not in st.session_state['old_values']:
        return()
    old_value = st.session_state['old_values']['Diámetro']
    if st.session_state['Diámetro unidad'] == 'mm': #De inch a mm
        new_value = old_value * 25
    if st.session_state['Diámetro unidad'] == 'in': #De mm a inch
        new_value = int(old_value / 25)
    st.session_state['Diámetro'] = new_value

def fill_fluid_values(fluid: Fluid, index):
    temperature = backend2.in_base_unit('Temperatura', 'Temperatura 0', 'Temperatura unidad')
    
    keys = ['Gravedad específica 0', 'Presión de vapor 0', 'Viscosidad 0', 'Velocidad del sonido 0']
    if fluid is None:
        for key in keys:
            st.session_state[key] = None
        return()
    elif fluid.name == 'Otro':
        return()
    elif temperature is None:
        for key in keys:
            st.session_state[key] = None
        return()

    temperature = temperature.magnitude

    for quantity_name in ['Gravedad específica', 'Presión de vapor', 'Viscosidad', 'Velocidad del sonido']:
        quantity_key = f'{quantity_name} 0'
        quantity_current_unit_key = f'{quantity_name} unidad'
        quantity_current_unit = ureg(st.session_state[quantity_current_unit_key])
        quantity_base_unit = ureg(BASE_UNITS[quantity_name])
        
        attribute_name = QUANTITY_NAME_TO_ATTRIBUTE_NAME[quantity_name]
        data = getattr(fluid, attribute_name)

        temperatures = data['temperature']
        values = data[attribute_name]
        value_interpolated = np.interp(temperature, temperatures, values)

        value_in_base_unit = value_interpolated * quantity_base_unit
        value_in_current_unit = value_in_base_unit.to(quantity_current_unit)
        st.session_state[quantity_key] = value_in_current_unit.magnitude


def enable_or_disable_fluid_values_boxes():
    if st.session_state['Fluido'] == 'Otro':
        is_disabled = False
    else:
        is_disabled = True
    
    for key in ['Gravedad específica 0', 'Presión de vapor 0', 'Viscosidad 0', 'Velocidad del sonido 0']:
        disabler_key = f'{key} is disabled'
        st.session_state[disabler_key] = is_disabled

def update_fluid_values_boxes():
    fluid_name = st.session_state['Fluido']
    if fluid_name is None:
        fluid = None
    else:
        fluid = FLUIDS[fluid_name]

    fill_fluid_values(fluid, None)
    enable_or_disable_fluid_values_boxes()




