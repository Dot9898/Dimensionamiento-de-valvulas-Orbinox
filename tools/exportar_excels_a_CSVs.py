
import pandas as pd
from pathlib import Path

ROOT_PATH = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT_PATH / 'data'

fluid_data_excel = DATA_PATH / 'fluid_data.xlsx'
fluid_data_csv = DATA_PATH / 'fluid_data.csv'
df = pd.read_excel(fluid_data_excel)
df.to_csv(fluid_data_csv, index = False)

FL_data_excel = DATA_PATH / 'FL_vs_opening.xlsx'
FL_data_csv = DATA_PATH / 'FL_vs_opening.csv'

cv_PA_excel = DATA_PATH / 'Cv_tables' / 'Pinch_PA.xlsx'
cv_PA_csv = DATA_PATH / 'Cv_tables' / 'Cv_vs_opening_Pinch PA.csv'

excels = [fluid_data_excel, FL_data_excel, cv_PA_excel]
csvs = [fluid_data_csv, FL_data_csv, cv_PA_csv]

for excels_and_csvs in zip(excels, csvs):
    df = pd.read_excel(excels_and_csvs[0])
    df.to_csv(excels_and_csvs[1], index = False)








