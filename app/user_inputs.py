
#encoding: utf-8

import streamlit as st
from unit_registry import ureg
from constants import UNITS_AS_STRING


def update_number_inputs(unit_key, associated_keys):
    for key in associated_keys:
        if st.session_state['old_values'][key] is not None:
            old_quantity = st.session_state['old_values'][key]
            current_unit = st.session_state[unit_key]
            current_quantity = old_quantity.to(current_unit)
            st.session_state[key] = current_quantity.magnitude


def generate_unit_input(quantity_name, 
                        unit_key, 
                        associated_number_input_keys, 
                        callback = update_number_inputs):
    
    available_units = UNITS_AS_STRING[quantity_name]
    kwargs = {'unit_key': unit_key, 'associated_keys': associated_number_input_keys}

    st.selectbox(label = unit_key, 
                 key = unit_key, 
                 options = available_units, 
                 on_change = callback, 
                 kwargs = kwargs, 
                 index = 0, 
                 accept_new_options = False, 
                 label_visibility = 'collapsed')


def generate_number_input(quantity_name, 
                          key, 
                          unit_key, 
                          placeholder = None, 
                          decimals = 0, 
                          inputs_range = (None, None), 
                          callback = lambda: None, 
                          kwargs = None):
    
    if decimals == 0:
        step = 1
        format = '%d'
    elif 1 <= decimals <= 7:
        step = 10**(-decimals)
        format = f'%0.{decimals}f'

    current_unit = ureg(st.session_state[unit_key])
    base_unit = ureg(UNITS_AS_STRING[quantity_name][0])

    min_value, max_value = inputs_range
    if min_value is not None:
        min_value = float(((min_value * base_unit).to(current_unit)).magnitude)
    if max_value is not None:
        max_value = float(((max_value * base_unit).to(current_unit)).magnitude) #tb fallan en celcius

    st.number_input(label = key, 
                    key = key, 
                    placeholder = placeholder, 
                    min_value = min_value, 
                    max_value = max_value, 
                    on_change = callback, 
                    kwargs = kwargs, 
                    value = None, 
                    step = step, 
                    format = format, 
                    label_visibility = 'collapsed')

    if st.session_state[key] is None:
        current_quantity_in_base_unit = None
    else:
        current_quantity = st.session_state[key] * current_unit #falla en Celcius etc
        current_quantity_in_base_unit = current_quantity.to(base_unit)
    
    st.session_state['old_values'][key] = current_quantity_in_base_unit
    return(current_quantity_in_base_unit)


def generate_multiple_inputs(written_name, 
                             quantity_name, 
                             base_key, 
                             unit_key, 
                             number_of_inputs = 3, 
                             decimals = 0, 
                             inputs_range = (None, None), 
                             placeholders = None, 
                             spacing = [2, 3, 1], 
                             number_input_callback = lambda: None, 
                             number_input_kwargs = None):
    
    if placeholders is None:
        placeholders = [None] * number_of_inputs

    keys = [base_key + f' {n}' for n in range(number_of_inputs)]
    
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
                quantities_in_base_unit[index] = generate_number_input(quantity_name, 
                                                key, 
                                                unit_key, 
                                                placeholder, 
                                                decimals = decimals, 
                                                inputs_range = inputs_range, 
                                                callback = number_input_callback, 
                                                kwargs = number_input_kwargs)
    
    return(quantities_in_base_unit) #CAMBIAR LO QUE RETORNA, QUEREMOS TRABAJAR CON UNIDADES? O PLAIN FLOAT?
    
            



#eventualmente considerar dimensionless units, quizás ya estén incluidas en pint


#Celcius fix:
#st.session_state[key] = float_cast(st.session_state[key])      #(??????maybe delete this line)
#if isinstance(st.session_state[key], float):
#    try:
#        st.session_state[key] = st.session_state[key] * unit
#    except pint.errors.OffsetUnitCalculusError:
#        st.session_state[key] = pint.Quantity(st.session_state[key], unit)



