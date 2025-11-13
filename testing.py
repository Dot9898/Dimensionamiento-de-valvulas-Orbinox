
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




