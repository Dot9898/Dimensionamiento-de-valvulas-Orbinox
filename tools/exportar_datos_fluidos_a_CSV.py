
import pandas as pd
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_PATH / 'data'

excel_file = DATA_PATH / 'datos_fluidos.xlsx'
csv_file = DATA_PATH / 'fluid_data.csv'

df = pd.read_excel(excel_file)
df.to_csv(csv_file, index = False)




