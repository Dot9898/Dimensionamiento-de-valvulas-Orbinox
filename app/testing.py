
import pint
import streamlit as st


def do_nothing():
    pass

def generic_callback(callback):
    callback()
    st.session_state['rerun'] = True

def init_session_state(defaults):
    for key in defaults:
        if key not in st.session_state:
            st.session_state[key] = defaults[key]

def float_cast(input):
    try:
        return(float(input))
    except (ValueError, TypeError):
        return(None)

keys = ['Válvula',
        'Fluido', 'Velocidad', 'Velocidad_unit', 
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



def generate_input_fields(input_names_to_units, 
                          text_input_boxes_labels = [''], 
                          columns_spacing = [2, 3, 1], #[largo de los nombres, largo de cada text input, largo de las unidades]
                          can_be_disabled = False, 
                          callback = do_nothing):
    number_of_text_inputs = len(text_input_boxes_labels)
    columns_spacing[1] = columns_spacing[1]*number_of_text_inputs
    
    for name in input_names_to_units:
        names_column, inputs_column, units_column = st.columns(columns_spacing) #Las columnas se regeneran en cada fila (name) para alinear correctamente los nombres y los text input
        
        with names_column:
            st.write(name)

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
                        label = float(st.session_state[key])

                    st.session_state[key] = st.text_input(key, 
                                                          value = st.session_state[key], 
                                                          label_visibility = 'collapsed', 
                                                          placeholder = label, 
                                                          on_change = generic_callback,
                                                          args = [callback], 
                                                          disabled = disabled_state, 
                                                          key = '_' + key)
                    


ureg = pint.UnitRegistry()
quantity = 25 * ureg.meter
quantity = quantity.to(ureg.ft)
print(type(quantity))
print(ureg.meter_per_second)
print(ureg.gallon)

ureg.define('meter_per_minute = meter / min = m/min')

UREG_OBJECT_TO_NAME = {ureg.meter_per_second: 'M/s', ureg.kilometer_per_hour: 'Km/h', ureg.meter_per_minute: 'M/min'}

generate_input_fields(input_names_to_units = {'Velocidad': ['km/h', 'm/s', 'm/min']},  #['GPM', 'LPM', 'm3/s']}, 
                      text_input_boxes_labels = [''], 
                      columns_spacing = [2, 1, 1])















