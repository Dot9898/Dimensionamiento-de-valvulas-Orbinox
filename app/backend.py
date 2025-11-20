
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

    #def __eq__(self, other):
    #    if isinstance(other, Fluid) and self.name == other.name:
    #        return(True)
    #    return(False)
    
    #def __hash__(self):
    #    return(hash(self.name))

class Valve:

    all = []

    def __init__(self, name):
        self.name = name
        self.Reynolds_factor = 1
        self.FL = {}
        self.Cv = {}
#VALVE_REYNOLDS_FACTOR = {'Mariposa': 0.7, 'Pinch PA': 1.0}

    def __repr__(self):
        return(self.name)

def clean_string(string):
    string = ''.join(char for char in string if char.isalnum()) #Elimina carácteres no alfanuméricos
    string = unidecode(string) #Elimina acentos
    string = string.lower()
    return(string)

def closest_in_list(values_list, number):
    closest = min(values_list, key = lambda value: abs(value - number))
    return(closest)

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
                diameter = line[0]
                Cv_values = map(int, line[1:])
                for opening, Cv in zip(openings_percentages, Cv_values):
                    valve.Cv[(diameter, opening)] = Cv

                
    


    valves = sorted(Valve.all, key = lambda valve: clean_string(valve.name))
    return(valves)

@lru_cache(maxsize = 1)
def get_valves():
    return(_load_valves())

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

    header = True
    with open(DATA_PATH / 'specific_gravity_vs_temperature' / (fluid.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            temperature = float(line[0])
            specific_gravity = float(line[1])
            fluid.specific_gravity[temperature] = specific_gravity
    
    header = True
    with open(DATA_PATH / 'vapor_pressure_vs_temperature' / (fluid.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            temperature = float(line[0])
            vapor_pressure = float(line[1])
            fluid.vapor_pressure[temperature] = vapor_pressure
    
    header = True
    with open(DATA_PATH / 'speed_of_sound_vs_temperature' / (fluid.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            temperature = float(line[0])
            speed_of_sound = float(line[1])
            fluid.speed_of_sound[temperature] = speed_of_sound
    
    header = True
    with open(DATA_PATH / 'viscosity_vs_temperature' / (fluid.name + '.csv'), mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if header:
                header = False
                continue
            temperature = float(line[0])
            viscosity = float(line[1])
            fluid.viscosity[temperature] = viscosity
    

    fluids = sorted(Fluid.all, key = lambda fluid: clean_string(fluid.name))

    otro = Fluid('Otro')
    Fluid.all.append(otro)
    fluids.append(otro)

    return(fluids)

@lru_cache(maxsize = 1)
def get_fluids(edit_this_string_to_force_cache_clear_in_streamlit_cloud = 'v1'):
    return(_load_fluids())


def calculate_flow_coefficient_Cv(specific_gravity,       #Dimensionless
                                  flow,                   #GPM, gallons per minute
                                  pressure_differential): #PSIG
    if specific_gravity is None or flow is None or pressure_differential is None:
        return(None)
    
    Cv = flow * sqrt(specific_gravity / pressure_differential)
    return(Cv)

def calculate_Reynolds_number(flow,        #GPM
                              diameter,    #inches
                              viscosity,   #centistokes
                              valve):
    
    Reynolds_number = 3160 * flow / (diameter * viscosity) * valve.Reynolds_factor #???????????
    return(Reynolds_number)

def calculate_pressure_recovery_factor_FL(in_pressure,  #PSIA
                                          out_pressure, #PSIA
                                          vc_pressure): #PSIA
    
    FL = sqrt((in_pressure - out_pressure) / (in_pressure - vc_pressure))
    return(FL)

def calculate_allowable_pressure_differential_without_cavitation(pressure_recovery_factor, #Dimensionless
                                                                 in_pressure,              #PSIG
                                                                 vapor_pressure):          #PSIA
    
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































