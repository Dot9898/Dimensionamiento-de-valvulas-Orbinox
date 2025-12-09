
import pint

ureg = pint.UnitRegistry()
quantity = 25 * ureg.meter
quantity = quantity.to(ureg.ft)
print(type(quantity))
print(ureg.meter_per_second)
print(ureg.gallon)

unit = ureg.meter
old_unit = None

if unit != old_unit:
    print('works')
print(ureg['LPM'])




ureg.Quantity(float, pint.Unit) #ureg.meter por ejemplo







