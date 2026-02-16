
#encoding: utf-8

import streamlit as st
import pint
from unit_registry import ureg
from constants import UNITS_AS_STRING, BASE_UNITS
from load_data import VALVES, FLUIDS
from backend import in_base_unit, get_dimensionable_and_available_diameters
from callbacks import update_number_inputs, update_fluid_values_boxes, update_diameter_dropdown_value


def generate_valve_and_fluid_dropdowns(valves: dict, fluids: dict):
    valve_selection_column, fluid_selection_column = st.columns([2, 4])

    valve_names = list(valves.keys()) #Aquí va el sort si eventualmente se necesita
    with valve_selection_column:
        valve_name = st.selectbox(label = 'Series Orbinox', 
                                  key = 'Válvula', 
                                  options = valve_names, 
                                  index = None, 
                                  accept_new_options = False, 
                                  label_visibility = 'collapsed', 
                                  placeholder = 'Series Orbinox')
    
    fluid_names = list(fluids.keys())
    with fluid_selection_column:
        fluid_name = st.selectbox(label = 'Fluido', 
                                  key = 'Fluido', 
                                  options = fluid_names, 
                                  index = None, 
                                  accept_new_options = False, 
                                  label_visibility = 'collapsed', 
                                  placeholder = 'Fluido', 
                                  on_change = update_fluid_values_boxes)
    
    if valve_name is not None:
        valve = VALVES[valve_name]
    else:
        valve = None
    if fluid_name is not None:
        fluid = FLUIDS[fluid_name]
    else:
        fluid = None
    
    return(valve, fluid)

def generate_unit_input(quantity_name, 
                        unit_key, 
                        associated_number_input_keys: list, 
                        callback = update_number_inputs):
    
    available_units = UNITS_AS_STRING[quantity_name]
    is_disabled = False
    if len(available_units) == 1:
        is_disabled = True
    kwargs = {'unit_key': unit_key, 'associated_keys': associated_number_input_keys}

    st.selectbox(label = unit_key, 
                 key = unit_key, 
                 options = available_units, 
                 disabled = is_disabled, 
                 on_change = callback, 
                 kwargs = kwargs, 
                 index = 0, 
                 accept_new_options = False, 
                 label_visibility = 'collapsed')

def generate_number_input(quantity_name, 
                          key, 
                          unit_key, 
                          placeholder: str | None = None, 
                          decimals = 1, 
                          inputs_range = (None, None), 
                          disabled = False, 
                          callback = lambda: None, 
                          kwargs = None):

    current_unit = ureg(st.session_state[unit_key])
    base_unit = ureg(BASE_UNITS[quantity_name])

    min_value, max_value = inputs_range
    if min_value is not None:
        try:
            min_value = float(((min_value * base_unit).to(current_unit)).magnitude) #esto es lo que falla con psia
        except pint.errors.OffsetUnitCalculusError:
            min_value = float((pint.Quantity(min_value, base_unit).to(current_unit)).magnitude)
    if max_value is not None:
        try:
            max_value = float(((max_value * base_unit).to(current_unit)).magnitude)
        except pint.errors.OffsetUnitCalculusError:
            max_value = float((pint.Quantity(max_value, base_unit).to(current_unit)).magnitude)

    if disabled:
        is_disabled = True
    else:
        is_disabled = st.session_state.get(f'{key} is disabled', False)

    st.number_input(label = key, 
                    key = key, 
                    placeholder = placeholder, 
                    min_value = min_value, 
                    max_value = max_value, 
                    on_change = callback, 
                    kwargs = kwargs, 
                    disabled = is_disabled, 
                    value = None, 
                    step = 10**(-12), 
                    format = f'%0.{decimals}f', 
                    label_visibility = 'collapsed')

    current_quantity_in_base_unit = in_base_unit(quantity_name, key, unit_key)
    st.session_state['old_values'][key] = current_quantity_in_base_unit
    return(current_quantity_in_base_unit)

def generate_multiple_inputs(written_name, 
                             quantity_name, 
                             base_key, 
                             unit_key, 
                             number_of_inputs = 3, 
                             decimals = 0, 
                             inputs_range = (None, None), 
                             placeholders: list[str] | None = None, 
                             disabled = False, 
                             spacing = [2, 3, 1], 
                             number_input_callback = lambda **kwargs: None, 
                             number_input_kwargs = {}):
    
    if placeholders is None:
        placeholders = [None] * number_of_inputs

    keys = [f'{base_key} {n}' for n in range(number_of_inputs)]
    
    name_column, inputs_column, units_column = st.columns(spacing)

    with name_column:
        st.write(written_name)

    with units_column:
        generate_unit_input(quantity_name, 
                            unit_key, 
                            keys,
                            callback = update_number_inputs)

    with inputs_column:
        quantities_in_base_unit = {}
        inputs_subcolumns = st.columns([1] * number_of_inputs)
        for index in range(number_of_inputs):
            with inputs_subcolumns[index]:
                key = keys[index]
                placeholder = placeholders[index]
                actual_kwargs = dict(number_input_kwargs) #Creates a copy so it doesn't just take the last index value
                actual_kwargs['index'] = index
                quantities_in_base_unit[index] = generate_number_input(quantity_name, 
                                                                       key, 
                                                                       unit_key, 
                                                                       placeholder, 
                                                                       decimals = decimals, 
                                                                       inputs_range = inputs_range, 
                                                                       disabled = disabled, 
                                                                       callback = number_input_callback, 
                                                                       kwargs = actual_kwargs)
    
    return(quantities_in_base_unit) #CAMBIAR LO QUE RETORNA, QUEREMOS TRABAJAR CON UNIDADES? O PLAIN FLOAT?

def generate_diameter_input_line(valve): #Quick patch to use it only on diameter
    name_column, inputs_column, units_column = st.columns([2, 3, 1])

    with name_column:
        st.write('Diámetro')

    with units_column:
        st.selectbox(label = 'Diámetro unidad', 
                     key = 'Diámetro unidad', 
                     options = ['mm', 'in'], 
                     on_change = update_diameter_dropdown_value,
                     index = 0, 
                     accept_new_options = False, 
                     label_visibility = 'collapsed')

    with inputs_column:
        if valve is None:
            display_diameters = None
        else:
            diameters_in_inch = get_dimensionable_and_available_diameters(valve)
            if st.session_state['Diámetro unidad'] == 'mm':
                display_diameters = [25 * diameter for diameter in diameters_in_inch]
            else:
                display_diameters = diameters_in_inch

        diameter = st.selectbox(label = 'Diámetro', 
                                key = 'Diámetro', 
                                options = display_diameters, 
                                index = 0, 
                                placeholder = '', 
                                accept_new_options = False, 
                                label_visibility = 'collapsed')
        
        st.session_state['old_values']['Diámetro'] = diameter
        
        if diameter is not None:
            if st.session_state['Diámetro unidad'] == 'mm':
                diameter = float(diameter/25)
    
    return(diameter)


#eventualmente considerar dimensionless units, quizás ya estén incluidas en pint






