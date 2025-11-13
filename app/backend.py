
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
VALVE_TYPE_FACTORS = {'Mariposa': 0.7, 'Pinch': 1.0}


class Fluid:

    all = []

    def __init__(self, name):
        self.name = name
    
    def __repr__(self):
        return(self.name)

    def __eq__(self, other):
        if isinstance(other, Fluid) and self.name == other.name:
            return(True)
        return(False)
    
    def __hash__(self):
        return(hash(self.name))

def clean_string(string):
    string = ''.join(char for char in string if char.isalnum()) #Elimina carácteres no alfanuméricos
    string = unidecode(string) #Elimina acentos
    string = string.lower()
    return(string)

def _load_fluids():
    with open(DATA_PATH / 'fluid_data.csv', mode ='r', encoding = 'utf-8') as file:
        csv_values = csv.reader(file)
        for line in csv_values:
            if csv_values.line_num == 1: #Header
                continue
            fluid_name = line[0]
            fluid = Fluid(fluid_name)
            Fluid.all.append(fluid)
    fluids = sorted(Fluid.all, key = lambda fluid: clean_string(fluid.name))
    return(fluids)

@lru_cache(maxsize = 1)
def get_fluids(edit_this_string_to_force_cache_clear_in_streamlit_cloud = 'v1'):
    return(_load_fluids())

def calculate_specific_gravity(temperature, fluid):  #Kelvin #La presión es negligible
    
    if fluid == 'water':
        specific_gravity = 1.0157 - 6.81 * 10e-4 * temperature #Aproximación lineal, <2% error entre 0 y 200 C

    return(specific_gravity)

def calculate_flow_coefficient_Cv(specific_gravity,       #Dimensionless
                                  flow,                   #GPM, gallons per minute
                                  pressure_differential): #PSIG
    
    Cv = flow * sqrt(specific_gravity / pressure_differential)
    return(Cv)

def calculate_Reynolds_number(flow,        #GPM
                              diameter,    #inches
                              viscosity,   #centistokes
                              valve_type):
    
    valve_type_factor = VALVE_TYPE_FACTORS[valve_type]
    Reynolds_number = 3160 * flow / (diameter*viscosity) * valve_type_factor #???????????
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































