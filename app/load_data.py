
#encoding: utf-8

import streamlit as st
import pandas as pd
from constants import DATA_PATH


class Fluid:

    Reynolds_correction_factor: pd.DataFrame | None = None

    def __init__(self, name, specific_gravity, vapor_pressure, viscosity, speed_of_sound):
        self.name = name
        self.specific_gravity: pd.DataFrame = specific_gravity
        self.vapor_pressure: pd.DataFrame = vapor_pressure
        self.viscosity: pd.DataFrame = viscosity
        self.speed_of_sound: pd.DataFrame = speed_of_sound
    
    def __repr__(self):
        return(self.name)

class Valve:

    def __init__(self, name, style, FL, Cv, available_diameters, max_opening, Reynolds_factor, critical_pressure_ratio, max_velocity_without_erosion):
        self.name = name
        self.style = style
        self.Cv: pd.DataFrame = Cv #valve.Cv[diameter][opening] = Cv
        self.FL: pd.DataFrame = FL #opening vs FL
        self.available_diameters: list = available_diameters
        self.max_opening = max_opening
        self.Reynolds_factor = Reynolds_factor
        self.critical_pressure_ratio = critical_pressure_ratio
        self.max_velocity_without_erosion = max_velocity_without_erosion

    def __repr__(self):
        return(self.name)


@st.cache_resource
def load_fluids():
    Reynolds_correction = pd.read_csv(DATA_PATH / 'fluids' / 'Reynolds_correction_factor.csv', 
                                      dtype = float, 
                                      header = 0, 
                                      names = ['Reynolds_number', 'correction_factor'])
    Fluid.Reynolds_correction_factor = Reynolds_correction

    fluids = {}
    for fluid_name in ['Agua']:
        dfs = []
        for quantity in ['specific_gravity', 'vapor_pressure', 'viscosity', 'speed_of_sound']:
            df = pd.read_csv(DATA_PATH / 'fluids' / fluid_name / (quantity + '.csv'), 
                             dtype = float, 
                             header = 0, 
                             names = ['temperature', quantity])
            df.sort_values(by = 'temperature', inplace = True)
            dfs.append(df)
        fluid = Fluid(fluid_name, dfs[0], dfs[1], dfs[2], dfs[3])
        fluids[fluid_name] = fluid
    fluids['Otro'] = Fluid('Otro', None, None, None, None)
    return(fluids)

@st.cache_resource
def load_valves():
    valves = {}

    valve_names = pd.read_csv(DATA_PATH / 'valves' / 'valve_names.csv', 
                              header = None)
    valve_names = list(valve_names.iloc[:, 0])
    
    for valve_name in valve_names:

        Cv = pd.read_csv(DATA_PATH / 'valves' / valve_name / 'Cv.csv', 
                         dtype = float, 
                         header = 0)
        Cv.rename(columns = {Cv.columns[0]: 'diameter'}, inplace = True)
        Cv = Cv.set_index('diameter')
        Cv.columns = Cv.columns.astype(float)

        FL = pd.read_csv(DATA_PATH / 'valves' / valve_name / 'FL.csv', 
                         dtype = float, 
                         header = 0, 
                         names = ['opening', 'FL'])
        FL.sort_values(by = 'opening', inplace = True)

        diameters_df = pd.read_csv(DATA_PATH / 'valves' / valve_name / 'available_diameters.csv', 
                                dtype = float, 
                                header = 0, 
                                names = ['available_diameters'])
        available_diameters = list(diameters_df['available_diameters'])

        constants_df = pd.read_csv(DATA_PATH / 'valves' / valve_name / 'constants.csv', 
                                header = 0)
        constants = list(constants_df.iloc[0])
        critical_pressure_ratio = constants[0]
        Reynolds_factor = constants[1]
        max_velocity_without_erosion = constants[2]
        max_opening = constants[3]
        style = constants[4]

        valve = Valve(valve_name, style, FL, Cv, available_diameters, max_opening, Reynolds_factor, critical_pressure_ratio, max_velocity_without_erosion)
        valves[valve_name] = valve
    
    return(valves)


FLUIDS = load_fluids()
VALVES = load_valves()


#import numpy as np
#SG_interpolated = np.interp(12.5, df['Temperature'], df['Specific_gravity'])
#print(SG_interpolated)



















