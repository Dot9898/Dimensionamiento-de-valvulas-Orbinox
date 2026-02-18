
#encoding: utf-8

import streamlit as st
import pint
import numpy as np
from math import pi as PI
from unit_registry import ureg
from constants import BASE_UNITS, CAVITATION_SAFETY_FACTOR
from load_data import Valve, VALVES, Fluid

class Dimensionamiento:

    def __init__(self, valve, fluid, flow, in_pressure, pressure_differential, diameter, specific_gravity, vapor_pressure, viscosity):
        self.valve: Valve | None = valve
        self.fluid: Fluid | None = fluid
        self.flow = flow
        self.in_pressure = in_pressure
        self.pressure_differential = pressure_differential
        self.diameter = diameter
        self.specific_gravity = specific_gravity
        self.vapor_pressure = vapor_pressure
        self.viscosity = viscosity

        self.Reynolds_number = None
        self.correction_factor = None
        self.Cv = None
        self.opening = None
        self.FL = None
        self.allowable_pressure_differential = None
        self.velocity = None
        self.noise = None

        self.is_cavitating = None
        self.is_flashing = None
        self.is_eroding = None
        self.opening_too_small = None
        self.opening_too_big = None
        #ADD VAPOR PRESSURE MORE THAN P1 (LIQUID IS STEAM)
        self.is_noisy = None #eventualmente
    
    def __repr__(self):
        attribute_lines = []
        for name, value in self.__dict__.items():
            attribute_line = f'{name} = {value}\n'
            attribute_lines.append(attribute_line)
        attributes_string = ''.join(attribute_lines)
        return(attributes_string)

    def calculate_Reynolds_number(self):
        if self.flow is None or self.diameter is None or self.viscosity is None or self.valve is None:
            return(None)
        
        Reynolds_number = 3160 * self.flow / (self.diameter * self.viscosity) * self.valve.Reynolds_factor #CHEQUEAR FACTOR PARA OTRO TIPO DE VÁLVULAS
        return(Reynolds_number)

    def get_Reynolds_correction_factor(self):
        if self.Reynolds_number is None:
            return(None)
        if self.Reynolds_number > 4999.9:
            return(1.0)
        if self.Reynolds_number < 0.011:
            return(240.0)
        
        Reynolds_numbers = self.fluid.Reynolds_correction_factor['Reynolds_number']
        correction_factors = self.fluid.Reynolds_correction_factor['correction_factor']
        interpolated_correction_factor = np.interp(self.Reynolds_number, Reynolds_numbers, correction_factors)
        return(interpolated_correction_factor)

    def calculate_Cv(self):
        if self.specific_gravity is None or self.flow is None or self.pressure_differential is None:
            return(None)
        
        Cv = self.flow * (self.specific_gravity / self.pressure_differential)**(1/2)
        return(Cv)

    def calculate_opening(self):
        if self.Cv is None or self.diameter is None or self.valve is None:
            return(None)
        
        Cvs = self.valve.Cv.loc[self.diameter]
        openings = self.valve.Cv.columns
        max_Cv = Cvs.iloc[-1]
        if self.Cv > max_Cv:
            return(self.valve.max_opening + 1)
        
        interpolated_opening = np.interp(self.Cv, Cvs, openings)
        return(interpolated_opening)

    def get_FL(self):
        if self.opening is None or self.valve is None:
            return(None)
        if self.opening > self.valve.max_opening or self.opening < 10:
            return(None)
        
        openings = self.valve.FL['opening']
        FLs = self.valve.FL['FL']
        interpolated_FL = np.interp(self.opening, openings, FLs)
        return(interpolated_FL)

    def calculate_allowable_pressure_differential_without_cavitation(self):
        if self.FL is None or self.in_pressure is None or self.vapor_pressure is None or self.valve is None:
            return(None)
        
        allowable_pressure_differential = self.FL**2 * (self.in_pressure + 14.7 - self.valve.critical_pressure_ratio * self.vapor_pressure)
        allowable_pressure_differential = CAVITATION_SAFETY_FACTOR * allowable_pressure_differential
        allowable_pressure_differential = max(allowable_pressure_differential, 0.0)
        return(allowable_pressure_differential)

    def calculate_in_velocity(self):
        if self.flow is None or self.diameter is None:
            return(None)
        
        ratio = self.diameter / 2
        area = PI * ratio**2
        velocity = self.flow / (3.12 * area)
        return(velocity)

    def calculate_outputs(self):
        self.Reynolds_number = self.calculate_Reynolds_number()
        self.correction_factor = self.get_Reynolds_correction_factor()
        self.Cv = self.calculate_Cv()

        if self.Cv is not None and self.correction_factor is not None:
            self.Cv = self.Cv * self.correction_factor

        self.opening = self.calculate_opening()
        self.FL = self.get_FL()
        self.allowable_pressure_differential = self.calculate_allowable_pressure_differential_without_cavitation()
        self.velocity = self.calculate_in_velocity()
    
    def set_flags(self):

        if self.opening is not None:
            self.opening_too_big = False
            self.opening_too_small = False
            if self.opening < 20: #Agregar rangos
                self.opening_too_small = True
            if self.opening > self.valve.max_opening:
                self.opening_too_big = True

        if self.pressure_differential is not None and self.allowable_pressure_differential is not None:
            self.is_cavitating = False
            if self.pressure_differential > self.allowable_pressure_differential:
                self.is_cavitating = True
        
        if self.velocity is not None and self.valve is not None:
            self.is_eroding = False
            if self.velocity > self.valve.max_velocity_without_erosion:
                self.is_eroding = True
        
        self.is_flashing = False #Temporal
        self.is_noisy = False #Temporal
    

def activate_rerun(): #unused so far
    st.session_state['rerun'] = True

def init_session_state(defaults):
    for key in defaults:
        if key not in st.session_state:
            st.session_state[key] = defaults[key]

def in_base_unit(quantity_name, key, unit_key):
    plain_quantity = st.session_state[key]
    if plain_quantity is None:
        return(None)
    
    current_unit = ureg(st.session_state[unit_key])
    try:
        quantity = plain_quantity * current_unit
    except pint.errors.OffsetUnitCalculusError:
        quantity = pint.Quantity(plain_quantity, current_unit)

    base_unit = ureg(BASE_UNITS[quantity_name])
    quantity_in_base_unit = quantity.to(base_unit)
    return(quantity_in_base_unit)

def get_dimensionable_and_available_diameters(valve: Valve):
    available_diameters = valve.available_diameters
    dimensionable_diameters = list(valve.Cv.index)
    diameters = []
    for diameter in available_diameters:
        if diameter in dimensionable_diameters:
            diameter = int(diameter) #Will fail for half diameters
            diameters.append(diameter)
    return(diameters)

def process_inputs(inputs):

    for name, subdict in inputs.items():

        if name in ['valve', 'fluid', 'diameter']:
            pass #Already processed

        if name in ['temperature', 'specific_gravity', 'vapor_pressure', 'viscosity', 'speed_of_sound']:
            value = subdict[0]
            if value is not None:
                value = value.magnitude
            inputs[name] = value

        if name in ['flow', 'in_pressure', 'out_pressure', 'pressure_differential']:
            for index, value in subdict.items():
                if value is not None:
                    value = value.magnitude
                inputs[name][index] = value
        
    return(inputs)

def get_dimensionamientos_from_triple_inputs(inputs):
    dimensionamientos = []
    for index in range(3):
        dimens = Dimensionamiento(inputs['valve'], 
                                  inputs['fluid'], 
                                  inputs['flow'][index], 
                                  inputs['in_pressure'][index], 
                                  inputs['pressure_differential'][index], 
                                  inputs['diameter'], 
                                  inputs['specific_gravity'], 
                                  inputs['vapor_pressure'], 
                                  inputs['viscosity'])
        dimens.calculate_outputs()
        dimens.set_flags()
        dimensionamientos.append(dimens)
    return(dimensionamientos)


def set_output_value_basic(dimensionamientos, key, attribute_name):
    for index in range(3):
        indexed_key = f'{key} {index}'
        quantity = getattr(dimensionamientos[index], attribute_name)
        if quantity is None:
            st.session_state[indexed_key] = None
            continue
        st.session_state[indexed_key] = quantity

def set_output_value(dimensionamientos, quantity_name, key, attribute_name):
    unit_key = f'{key} unidad'
    if unit_key not in st.session_state:
        activate_rerun()
        return()
    base_unit = ureg(BASE_UNITS[quantity_name])
    current_unit = ureg(st.session_state[unit_key])
    for index in range(3):
        indexed_key = f'{key} {index}'
        quantity = getattr(dimensionamientos[index], attribute_name)
        if quantity is None:
            st.session_state[indexed_key] = None
            continue
        quantity = quantity * base_unit
        current_quantity = quantity.to(current_unit)
        st.session_state[indexed_key] = current_quantity.magnitude

def set_all_output_values(dimensionamientos: list[Dimensionamiento]):
    set_output_value(dimensionamientos, 'Caudal', 'Caudal output', 'flow')
    set_output_value_basic(dimensionamientos, 'Apertura', 'opening')
    set_output_value_basic(dimensionamientos, 'Cv', 'Cv')
    set_output_value(dimensionamientos, 'Presión', 'Diferencia de presión máxima', 'allowable_pressure_differential')
    set_output_value(dimensionamientos, 'Velocidad', 'Velocidad del fluido', 'velocity')
    set_output_value_basic(dimensionamientos, 'Predicción de ruido', 'noise')







