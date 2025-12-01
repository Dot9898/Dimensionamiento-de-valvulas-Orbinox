
#encoding: utf-8

from pathlib import Path
import csv
from unidecode import unidecode
from functools import lru_cache
from math import sqrt
from math import pi
from math import log10

import streamlit as st

PI = pi
ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_PATH / 'data'


class Fluid:

    all = []

    def __init__(self, name):
        self.name = name
        self.specific_gravity = {}
        self.vapor_pressure = {}
        self.viscosity = {}
        self.speed_of_sound = {}
    
    def __repr__(self):
        return(self.name)
    


class Valve:

    all = []
    Reynolds_factors = {'Pinch PA': 1.0}
    critical_pressure_ratios = {'Pinch PA': 0.94}
    max_velocities_without_erosion = {'Pinch PA': 22.0}

    def __init__(self, name):
        self.name = name
        self.Reynolds_factor = Valve.Reynolds_factors[self.name]
        self.critical_pressure_ratio = Valve.critical_pressure_ratios[self.name]
        self.max_velocity_without_erosion = Valve.max_velocities_without_erosion[self.name]
        self.FL = {} #valve.FL[opening] = FL
        self.Cv = {} #valve.Cv[diameter][opening] = Cv
        self.Cv_to_opening = {} #valve.Cv_to_opening[diameter][Cv] = opening

    def __repr__(self):
        return(self.name)
    
    def fill_Cv_to_opening(self):
        for diameter in self.Cv:
            self.Cv_to_opening[diameter] = invert_keys_and_values(self.Cv[diameter])



#Utilities

def clean_string(string):
    string = ''.join(char for char in string if char.isalnum()) #Elimina carácteres no alfanuméricos
    string = unidecode(string) #Elimina acentos
    string = string.lower()
    return(string)

def invert_keys_and_values(original):
    inverted = {}
    for key in original:
        value = original[key]
        inverted[value] = key
    return(inverted)

def closest_in_list(values_list, number):
    closest = min(values_list, key = lambda value: abs(value - number))
    return(closest)

def items_just_below_and_just_above_in_list(number, values_list, default_below = None, default_above = None):
    below = max([value for value in values_list if value <= number], default = default_below)
    above = min([value for value in values_list if value >= number], default = default_above)
    return(below, above)

def linear_approximation(x_between, x1, y1, x2, y2):
    if x1 is None or x2 is None or y1 is None or y2 is None or x_between is None:
        return(None)
    if x_between == x1:
        return(y1)
    if x_between == x2:
        return(y2)
    slope = (y2 - y1) / (x2 - x1)
    approximation = slope * (x_between - x1) + y1
    return(approximation)

def get_linear_approximation_from_dict(x_target, 
                                       dictionnary, 
                                       default_x_below = None, 
                                       default_y_below = None, 
                                       default_x_above = None, 
                                       default_y_above = None):

    x_below, x_above = items_just_below_and_just_above_in_list(x_target, 
                                                               list(dictionnary.keys()), 
                                                               default_below = default_x_below, 
                                                               default_above = default_x_above) #CHEQUEAR EDGE CASES CADA VEZ Q SE USA

    if x_below is None or x_above is None:
        return(None)
    
    if x_below in dictionnary:
        y_below = dictionnary[x_below]
    else:
        y_below = default_y_below
    if x_above in dictionnary:
        y_above = dictionnary[x_above]
    else:
        y_above = default_y_above

    y_target = linear_approximation(x_target, x_below, y_below, x_above, y_above)
    return(y_target)

def process_two_column_csv_to_dict(csv_path, target_dict, header = True):
    with open(csv_path, mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            key = float(line[0])
            value = float(line[1])
            target_dict[key] = value


#Data processing

def _load_valves():
    
    valve_names = []
    with open(DATA_PATH / 'valve_names.csv', mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            name = line[0]
            valve_names.append(name)
    
    for name in valve_names:
        valve = Valve(name)
        Valve.all.append(valve)
    
    valve_name_to_Valve = {}
    for valve in Valve.all:
        valve_name_to_Valve[valve.name] = valve

    for valve in Valve.all:

        FL_path = DATA_PATH / 'FL_vs_opening' / (valve.name + '.csv')
        target = valve.FL
        process_two_column_csv_to_dict(FL_path, target)

        header = True
        with open(DATA_PATH / 'Cv_vs_opening' / (valve.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
            csv_values = csv.reader(file)
            for line in csv_values:
                if header:
                    openings_percentages = list(map(float, line[1:]))
                    header = False
                    continue
                diameter = float(line[0])
                valve.Cv[diameter] = {}
                Cv_values = map(float, line[1:])
                for opening, Cv in zip(openings_percentages, Cv_values):
                    valve.Cv[diameter][opening] = Cv
        valve.fill_Cv_to_opening()         

    valves = sorted(Valve.all, key = lambda valve: clean_string(valve.name))
    return(valves)

def _load_fluids():

    fluid_names = []
    with open(DATA_PATH / 'fluid_names.csv', mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            name = line[0]
            fluid_names.append(name)

    for name in fluid_names:
        fluid = Fluid(name)
        Fluid.all.append(fluid)

    for fluid in Fluid.all:
        paths_to_target_dicts = {DATA_PATH / 'specific_gravity_vs_temperature' / (fluid.name + '.csv'): fluid.specific_gravity, 
                                 DATA_PATH / 'vapor_pressure_vs_temperature' / (fluid.name + '.csv'): fluid.vapor_pressure, 
                                 DATA_PATH / 'speed_of_sound_vs_temperature' / (fluid.name + '.csv'): fluid.speed_of_sound, 
                                 DATA_PATH / 'viscosity_vs_temperature' / (fluid.name + '.csv'):  fluid.viscosity}
        
        for path in paths_to_target_dicts:
            target = paths_to_target_dicts[path]
            process_two_column_csv_to_dict(path, target)

    fluids = sorted(Fluid.all, key = lambda fluid: clean_string(fluid.name))

    otro = Fluid('Otro')
    Fluid.all.append(otro)
    fluids.append(otro)

    return(fluids)

@lru_cache(maxsize = 1)
def _get_Reynolds_number_to_correction_factor():
    Reynolds_number_to_correction_factor = {}
    process_two_column_csv_to_dict(DATA_PATH / 'Reynolds_number_vs_correction_factor.csv', Reynolds_number_to_correction_factor)
    return(Reynolds_number_to_correction_factor)

@lru_cache(maxsize = 1)
def _get_noise_factor_A_data():
    noise_factor_A = {}

    return(noise_factor_A)

@lru_cache(maxsize = 1)
def _get_noise_factor_C_data():
    noise_factor_C_not_cavitating = {}
    noise_factor_C_cavitating = {}

    return(noise_factor_C_not_cavitating, noise_factor_C_cavitating)

@lru_cache(maxsize = 1)
def get_data(edit_this_string_to_force_cache_clear_in_streamlit_cloud = 'v2'):
    return(_load_valves(), _load_fluids())


#Sizing calculations

def calculate_flow_coefficient_Cv(specific_gravity,         #Dimensionless
                                  flow,                     #GPM, gallons per minute
                                  pressure_differential):   #PSIG
    if specific_gravity is None or flow is None or pressure_differential is None:
        return(None)
    Cv = flow * sqrt(specific_gravity / pressure_differential)
    return(Cv)

def calculate_flow_from_Cv(Cv, 
                           specific_gravity, 
                           pressure_differential):
    if Cv is None or specific_gravity is None or pressure_differential is None:
        return(None)
    flow = Cv * sqrt(pressure_differential / specific_gravity)
    return(flow)

def calculate_Reynolds_number(flow,        #GPM
                              diameter,    #inches
                              viscosity,   #centistokes
                              valve):
    if flow is None or diameter is None or viscosity is None or valve is None:
        return(None)
    Reynolds_number = 3160 * flow / (diameter * viscosity) * valve.Reynolds_factor #CHEQUEAR FACTOR PARA OTRO TIPO DE VÁLVULAS
    return(Reynolds_number)

def get_Reynolds_correction_factor(Reynolds_number):
    if Reynolds_number is None:
        return(None)
    if Reynolds_number > 4999.9:
        return(1.0)
    if Reynolds_number < 0.011:
        return(240.0)
    Reynolds_to_correction = _get_Reynolds_number_to_correction_factor()
    correction_factor = get_linear_approximation_from_dict(Reynolds_number, Reynolds_to_correction)
    return(correction_factor)

def calculate_opening_percentage_at_Cv(Cv,         #GPM
                                       diameter,   #inches
                                       valve):
    if Cv is None or diameter is None or valve is None:
        return(None)
    max_opening = max(valve.Cv[diameter].keys())
    if Cv > valve.Cv[diameter][max_opening]:
        return(999.0)
    opening_percentage = get_linear_approximation_from_dict(Cv, valve.Cv_to_opening[diameter], default_x_below = 0, default_y_below = 0)
    return(opening_percentage)

def get_pressure_recovery_factor_FL(opening,   #% or angle
                                    valve):
    if opening is None or valve is None:
        return(None)
    FL = get_linear_approximation_from_dict(opening, valve.FL, default_x_below = 0, default_y_below = 0) #CHEQUEAR ESTO, APROX LINEAL PUEDE NO SER SUFICIENTE
    return(FL)

def calculate_allowable_pressure_differential_without_cavitation(pressure_recovery_factor,   #Dimensionless #   CONSIDER CRITICAL VALUE 0.94
                                                                 in_pressure,                #PSIG
                                                                 vapor_pressure,             #PSIA
                                                                 valve):
    if pressure_recovery_factor is None or in_pressure is None or vapor_pressure is None or valve is None:
        return(None)
    allowable_pressure_differential = pressure_recovery_factor**2 * (in_pressure + 14.7 - valve.critical_pressure_ratio * vapor_pressure) #CHEQUEAR CRIT PRESSURE RATIO
    return(allowable_pressure_differential)

def calculate_in_velocity(flow, #GPM
                          diameter): #inches
    if flow is None or diameter is None:
        return(None)
    ratio = diameter / 2
    area = PI * ratio**2
    velocity = flow / (3.12 * area)
    return(velocity)

def get_noise_factor_A(Cv,         #GPM
                       diameter):   #in
    if Cv is None or diameter is None:
        return(None)
    curve_number = Cv / diameter**2
    available_data = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0]
    below_curve_number, above_curve_number = items_just_below_and_just_above_in_list(curve_number, available_data, default_below = 1.0)
    noise_factor_A_data = _get_noise_factor_A_data()
    below_curve = noise_factor_A_data[below_curve_number] #diameter to Db
    above_curve = noise_factor_A_data[above_curve_number]
    below_Db = get_linear_approximation_from_dict(diameter, below_curve)
    above_Db = get_linear_approximation_from_dict(diameter, above_curve)
    noise_factor_A = linear_approximation(curve_number, below_curve_number, below_Db, above_curve_number, above_Db)
    return(noise_factor_A)

def get_noise_factor_B(in_pressure):
    if in_pressure is None:
        return(None)
    if in_pressure <= 10:
        return(0)
    noise_factor_B = 35 * log10(in_pressure) - 35
    return(noise_factor_B)

def get_noise_factor_C(in_pressure, out_pressure, vapor_pressure, is_cavitating):
    if in_pressure is None or out_pressure is None or vapor_pressure is None or is_cavitating is None:
        return(None)
    X_10 = 10 * (in_pressure - out_pressure) / (in_pressure - vapor_pressure)
    if X_10 < 1:
        return(0)
    noise_factor_C_data_not_cavitating, noise_factor_C_data_cavitating = _get_noise_factor_C_data()
    if not is_cavitating:
        noise_factor_C = noise_factor_C_data_not_cavitating[X_10]
    else:
        if False:
            curve_number = Cv / diameter**2
            available_data = [1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0]
            below_curve_number, above_curve_number = items_just_below_and_just_above_in_list(curve_number, available_data, default_below = 1.0)
            noise_factor_A_data = _get_noise_factor_A_data()
            below_curve = noise_factor_A_data[below_curve_number] #diameter to Db
            above_curve = noise_factor_A_data[above_curve_number]
            below_Db = get_linear_approximation_from_dict(diameter, below_curve)
            above_Db = get_linear_approximation_from_dict(diameter, above_curve)
            noise_factor_A = linear_approximation(curve_number, below_curve_number, below_Db, above_curve_number, above_Db)
        
    
    

def calculate_noise(): #https://www.isa.org/intech-home/2018/july-august/departments/control-valve-noise-estimating-made-easy
    
    
    pass































