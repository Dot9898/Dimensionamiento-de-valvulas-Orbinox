
#encoding: utf-8

from pathlib import Path
import csv
from unidecode import unidecode
from functools import lru_cache
from math import sqrt
from math import pi


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
    Reynolds_number_to_correction_factor = {}
    Reynolds_factors = {'Pinch PA': 1.0}

    def __init__(self, name):
        self.name = name
        self.Reynolds_factor = Valve.Reynolds_factors[self.name]
        self.FL = {}
        self.Cv = {} #valve.Cv[diameter][opening] = Cv
        self.Cv_to_opening = {} #valve.Cv_to_opening[diameter][Cv]

    def __repr__(self):
        return(self.name)
    
    def fill_Cv_to_opening(self):
        for diameter in self.Cv:
            self.Cv_to_opening[diameter] = invert_keys_and_values(self.Cv[diameter])




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

def items_just_below_and_just_above_in_list(number, values_list):
    below = max([value for value in values_list if value <= number], default = None)
    above = min([value for value in values_list if value >= number], default = None)
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

def _load_valves():
    openings_percentages = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    
    header = True
    with open(DATA_PATH / 'FL_vs_opening.csv', mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            valve_name = line[0]
            valve = Valve(valve_name)
            Valve.all.append(valve)
            FL_values = map(float, line[1:])
            for opening, FL in zip(openings_percentages, FL_values):
                valve.FL[opening] = FL
    
    for valve in Valve.all:
        header = True
        with open(DATA_PATH / 'Cv_vs_opening' / (valve.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
            csv_values = csv.reader(file)
            for line in csv_values:
                if header:
                    header = False
                    continue
                diameter = float(line[0])
                valve.Cv[diameter] = {}
                Cv_values = map(float, line[1:])
                for opening, Cv in zip(openings_percentages, Cv_values):
                    valve.Cv[diameter][opening] = Cv
        
        valve.fill_Cv_to_opening()         
    
    Valve.Reynolds_number_to_correction_factor

    valves = sorted(Valve.all, key = lambda valve: clean_string(valve.name))
    return(valves)

@lru_cache(maxsize = 1)
def get_valves():
    return(_load_valves())

def process_fluid_data_from_temperature(fluid, folder_name): #cambiar todo esto para que tome solo el path y el data structure al que se le agrega
    
    folders_name_to_fluid_data = {'specific_gravity_vs_temperature': fluid.specific_gravity, 
                                  'vapor_pressure_vs_temperature': fluid.vapor_pressure, 
                                  'speed_of_sound_vs_temperature': fluid.speed_of_sound, 
                                  'viscosity_vs_temperature': fluid.viscosity}
    temperature_to_data = folders_name_to_fluid_data[folder_name]
    
    header = True
    with open(DATA_PATH / folder_name / (fluid.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            temperature = float(line[0])
            data_value = float(line[1])
            temperature_to_data[temperature] = data_value

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
        folder_names = ['specific_gravity_vs_temperature', 'vapor_pressure_vs_temperature', 'speed_of_sound_vs_temperature', 'viscosity_vs_temperature']
        for folder_name in folder_names:
            process_fluid_data_from_temperature(fluid, folder_name)

    fluids = sorted(Fluid.all, key = lambda fluid: clean_string(fluid.name))

    otro = Fluid('Otro')
    Fluid.all.append(otro)
    fluids.append(otro)

    return(fluids)

@lru_cache(maxsize = 1)
def get_fluids(edit_this_string_to_force_cache_clear_in_streamlit_cloud = 'v1'):
    return(_load_fluids())


def calculate_flow_coefficient_Cv(specific_gravity,         #Dimensionless
                                  flow,                     #GPM, gallons per minute
                                  pressure_differential):   #PSIG
    if specific_gravity is None or flow is None or pressure_differential is None:
        return(None)
    
    Cv = flow * sqrt(specific_gravity / pressure_differential)
    return(Cv)

def calculate_Reynolds_number(flow,        #GPM
                              diameter,    #inches
                              viscosity,   #centistokes
                              valve):
    if flow is None or diameter is None or viscosity is None or valve is None:
        return(None)
    
    Reynolds_number = 3160 * flow / (diameter * viscosity) * valve.Reynolds_factor
    return(Reynolds_number)

def get_Reynolds_correction_factor(Reynolds_number):
    pass

def calculate_opening_percentage_at_Cv(Cv,         #GPM
                                       diameter,   #inches
                                       valve):
    if Cv is None or diameter is None or valve is None:
        return(None)

    Cv_below, Cv_above = items_just_below_and_just_above_in_list(Cv, valve.Cv[diameter].values())
    if Cv_below is None or Cv_above is None:
        return(None)
    
    opening_below, opening_above = valve.Cv_to_opening[diameter][Cv_below], valve.Cv_to_opening[diameter][Cv_above]
    opening_percentage = linear_approximation(Cv, Cv_below, opening_below, Cv_above, opening_above)
    return(opening_percentage)

def calculate_allowable_pressure_differential_without_cavitation(pressure_recovery_factor,   #Dimensionless #   CONSIDER CRITICAL VALUE 0.94
                                                                 in_pressure,                #PSIG
                                                                 vapor_pressure):            #PSIA
    
    allowable_pressure_differential = pressure_recovery_factor**2 * (in_pressure + 14.7 - 0.94 * vapor_pressure)
    return(allowable_pressure_differential)

def calculate_in_velocity(flow, #GPM
                          diameter): #inches
    ratio = diameter / 2
    area = PI * ratio**2
    velocity = flow / (3.12 * area)
    return(velocity)

def calculate_noise(): #https://www.isa.org/intech-home/2018/july-august/departments/control-valve-noise-estimating-made-easy
    pass #pendiente































