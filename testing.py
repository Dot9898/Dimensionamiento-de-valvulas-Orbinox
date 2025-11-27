
import streamlit as st


col1, col2, col3, col4 = st.columns([1, 1, 1, 0.5])

fields = [
    ("Caudal", ["mínimo", "normal", "máximo"], "km"),
    ("Presión de entrada", ["mínimo", "normal", "máximo"], "t..."),
    ("Presión de salida", ["mínimo", "normal", "máximo"], "t..."),
    ("Diferencia de presión", ["mínimo", "normal", "máximo"], "abc"),
    ("...", ["mínimo", "normal", "máximo"], "3"),
]

for label, inputs, unit in fields:
    with col1:
        st.write(label)

    with col2:
        st.text_input(label="", placeholder=inputs[0])

    with col3:
        st.text_input(label="", placeholder=inputs[1])

    with col4:
        st.text_input(label="", placeholder=inputs[2])

    with col4:
        st.selectbox("", options=["a", "b", "c"], key=f"unit_{label}")




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
                    
                st.text_input(label, 
                              value = value, 
                              label_visibility = 'collapsed', 
                              placeholder = label, 
                              disabled = True)

    with units_column:
        if len(units) >= 2:
            st.selectbox(label, 
                         units, 
                         label_visibility = 'collapsed', 
                         accept_new_options = False, 
                         placeholder = 'unidad')
        elif len(units) == 1:
            st.write(units[0])


