
#import pint
#from unit_registry import ureg

#quantity = 25 * ureg.meter
#quantity = quantity.to(ureg.ft)
#print(type(quantity))
#print(ureg.meter_per_second)
#print(ureg.gallon)

#unit = ureg.meter
#old_unit = None

#if unit != old_unit:
#    print('works')
#print(ureg['LPM'])

#print('Unidad presión de entrada' and 'Presión de entrada')

#import pint
#from unit_registry import ureg

#orig = pint.Quantity(20, ureg('°C'))
#print(orig)

#offset = orig.to(ureg('°C'))
#print(offset)

#orig = offset.to(ureg('°C'))
#print(orig)

#for t in range(-20, 410, 20):
#    sg = round(1.8437 - 0.00094 * (t - 15.6), 4)
#    print(f'{t},{sg}')


import pandas as pd
from constants import DATA_PATH

df = pd.read_csv(DATA_PATH / 'valves' / 'HPBV' / 'Cv.csv', delim_whitespace=True)
df.set_index('INCH')
df.to_csv('output.csv')


