import pandas as pd
import shutil
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os

# Ruta del archivo original y la nueva ruta
original_file_path = 'D:/2021/viejo.xlsx'
new_file_path = 'D:/2021/viejordenado.xlsx'

# Eliminar el archivo original
if os.path.exists(new_file_path):
    os.remove(new_file_path)

# Copiar el archivo a la nueva ubicación
shutil.copyfile(original_file_path, new_file_path)

# Cargar el archivo Excel
sheet_name = 'Hoja1'
df = pd.read_excel(new_file_path, sheet_name=sheet_name)

# Unir las columnas "Débito" y "Crédito" en una sola columna llamada "Monto"
df['Monto'] = df['Débito'].fillna(0) - df['Crédito'].fillna(0)

# Eliminar las columnas originales "Débito" y "Crédito"
df.drop(columns=['Débito', 'Crédito'], inplace=True)

# Guardar el DataFrame modificado de nuevo en el archivo Excel
with pd.ExcelWriter(new_file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
    df.to_excel(writer, sheet_name=sheet_name, index=False)