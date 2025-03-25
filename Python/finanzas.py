import pandas as pd
import shutil
from openpyxl import load_workbook
from openpyxl.styles import PatternFill
import os
from openpyxl.formatting.rule import ColorScaleRule

# Ruta del archivo original y la nueva ruta
# original_file_path = 'C:/Users/jeacossio/Downloads/ManagedSystems.xlsx'
# new_file_path = 'C:/Users/jeacossio/OneDrive - bgeneral.com/Documentos/Nuevo Backup/Liberaciones/ManagedSystems.xlsx'
old_file_path = 'D:/2021/importante-viejo.xlsx'
original_file_path = 'D:/2021/importante-nuevo.xlsx'
new_file_path = 'D:/2021/estado-super-general.xlsx'

# Eliminar el archivo original
if os.path.exists(new_file_path):
    os.remove(new_file_path)

# Copiar el archivo a la nueva ubicación
shutil.copyfile(original_file_path, new_file_path)

# Cargar el archivo Excel viejo
old_df_h1 = pd.read_excel(old_file_path, sheet_name='Hoja1')
old_df_h2 = pd.read_excel(old_file_path, sheet_name='Hoja2')

# Cargar el archivo Excel
sheet_name = 'Hoja1'
df = pd.read_excel(new_file_path, sheet_name=sheet_name)

# Agregar todo el old_df después del df
df = pd.concat([df, old_df_h2], ignore_index=True)
df = pd.concat([df, old_df_h1], ignore_index=True)

# Convertir la columna "Fecha" a formato fecha (día, mes y año con el mes en palabras)
df['Fecha'] = pd.to_datetime(df['Fecha'], errors='coerce').dt.strftime('%d %B %Y')

# # Convertir las columnas "Monto" y "Saldo total" a formato moneda
# df['Monto'] = df['Monto'].apply(lambda x: "${:,.2f}".format(x))
# df['Saldo total'] = df['Saldo total'].apply(lambda x: "${:,.2f}".format(x))

# Eliminar la columna "Referencia"
if 'Referencia' in df.columns:
    df.drop(columns=['Referencia'], inplace=True)

# Separar la columna "Monto" en "Saliente" y "Entrante"
df['Monto'] = df['Monto'].replace('[\$,]', '', regex=True).astype(float)
df['Saliente'] = df['Monto'].apply(lambda x: x if x < 0 else None)
df['Entrante'] = df['Monto'].apply(lambda x: x if x > 0 else None)
df['Saliente'].fillna(0, inplace=True)
df['Entrante'].fillna(0, inplace=True)
# df['Monto'] = df['Monto'].apply(lambda x: "${:,.2f}".format(x))
# df['Saliente'] = df['Saliente'].apply(lambda x: "${:,.2f}".format(x))
# df['Entrante'] = df['Entrante'].apply(lambda x: "${:,.2f}".format(x))

# Insertar 4 filas y desplazar hacia abajo en cada cambio de mes en la columna "Fecha"
df['Mes'] = pd.to_datetime(df['Fecha'], format='%d %B %Y').dt.month
df['Año'] = pd.to_datetime(df['Fecha'], format='%d %B %Y').dt.year

# Eliminar la columna "Monto"
df.drop(columns=['Monto'], inplace=True)

# Mover la columna "Saldo total" al final
saldo_total = df.pop('Saldo total')
df['Saldo total'] = saldo_total

# Insertar filas en cada cambio de mes
new_rows = []
previous_month = None
previous_year = None

for index, row in df.iterrows():
    current_month = row['Mes']
    current_year = row['Año']
    if previous_month is not None and (current_month != previous_month or current_year != previous_year):
        for _ in range(4):
            new_rows.append(pd.Series([None] * len(df.columns), index=df.columns))
    new_rows.append(row)
    previous_month = current_month
    previous_year = current_year

df = pd.DataFrame(new_rows)

# Eliminar las columnas temporales
df.drop(columns=['Mes', 'Año'], inplace=True)

# Guardar el DataFrame actualizado en la hoja "Estado"
with pd.ExcelWriter(new_file_path, mode='a', engine='openpyxl') as writer:
    df.to_excel(writer, sheet_name='Estado', index=False)

# Cargar el archivo Excel con openpyxl
wb = load_workbook(new_file_path)
ws = wb["Estado"]

# Definir el color rojo
data_fill = PatternFill(start_color='FE9072', end_color='FE9072', fill_type='solid')
mante_fill = PatternFill(start_color='F8CA78', end_color='F8CA78', fill_type='solid')
tigo_fill = PatternFill(start_color='71FF74', end_color='71FF74', fill_type='solid')
idaan_fill = PatternFill(start_color='89E7E7', end_color='89E7E7', fill_type='solid')
ensa_fill = PatternFill(start_color='EAE888', end_color='EAE888', fill_type='solid')
visa_fill = PatternFill(start_color='B8B8B8', end_color='B8B8B8', fill_type='solid')
seguro_fill = PatternFill(start_color='C41212', end_color='C41212', fill_type='solid')
netflix_fill = PatternFill(start_color='8992E7', end_color='8992E7', fill_type='solid')

# Obtener el índice de la columna "Descripcion"
desc_col_index = 0
for idx, cell in enumerate(ws[1]):
    if cell.value == 'Descripción':
        desc_col_index = idx + 1
        break
        
# Aplicar el color rojo a las filas que contengan la Descripcion "BANCA MOVIL ITBMS RECARGA TELEFONIA"
for row in ws.iter_rows(min_row=2):
    if row[desc_col_index - 1].value is not None:
        if "BANCA MOVIL ITBMS RECARGA TELEFONIA" in row[desc_col_index - 1].value:
            for cell in row:
                cell.fill = data_fill
        elif "BANCA MOVIL RECARGA TELEFONIA +MÓVIL" in row[desc_col_index - 1].value:
            for cell in row:
                cell.fill = data_fill
        elif "BANCA MOVIL TRANSFERENCIA A 0301011162515 ASAMBLEA DE PROPIETARIOS DEL P.H. ALTATERRA" in row[desc_col_index - 1].value:
            for cell in row:
                cell.fill = mante_fill
        elif "BANCA MÓVIL TIGO HOGAR - PYME (94827659)" in row[desc_col_index - 1].value:
            for cell in row:
                    cell.fill = tigo_fill
        elif "BANCA MÓVIL IDAAN (945168)" in row[desc_col_index - 1].value:
            for cell in row:
                    cell.fill = idaan_fill
        elif "BANCA MÓVIL ENSA (ELEKTRA NORESTE) (000021426294)" in row[desc_col_index - 1].value:
            for cell in row:
                    cell.fill = ensa_fill
        elif "BANCA MOVIL PAGO VISA 4931-23XX-XXXX-9827 JEAN CARLOS COSSIO YEE" in row[desc_col_index - 1].value:
            for cell in row:
                    cell.fill = visa_fill
        elif "BANCA EN LINEA CIA INTERNACIONAL DE SEGU (000000000300442612)" in row[desc_col_index - 1].value:
            for cell in row:
                    cell.fill = seguro_fill
        elif "BANCA EN LINEA TRANSFERENCIA A 0472997148051 LUIS ALBERTO GONZALEZ REAL nefli" in row[desc_col_index - 1].value:
            for cell in row:
                    cell.fill = netflix_fill


# for row in ws.iter_rows(min_row=2):
#     if row[desc_col_index - 1].value is not None:
#         if "PAGO YAPPY A Pedidos Ya" in row[desc_col_index - 1].value:
#             for cell in row:
#                 cell.fill = data_fill
#         elif "BANCA MOVIL RECARGA TELEFONIA +MÓVIL" in row[desc_col_index - 1].value:
#             for cell in row:
#                 cell.fill = data_fill
#         elif "MANADA SIBARITA" in row[desc_col_index - 1].value:
#             for cell in row:
#                 cell.fill = mante_fill
#         elif "BANCA MÓVIL TIGO HOGAR - PYME (94827659)" in row[desc_col_index - 1].value:
#             for cell in row:
#                     cell.fill = tigo_fill
#         elif "GOOGLE  WyzeAppAndroid" in row[desc_col_index - 1].value:
#             for cell in row:
#                     cell.fill = idaan_fill
#         elif "TEXACO" in row[desc_col_index - 1].value:
#             for cell in row:
#                     cell.fill = ensa_fill
#         elif "SMARTFIT" in row[desc_col_index - 1].value:
#             for cell in row:
#                     cell.fill = visa_fill
#         elif "Amazon Prime" in row[desc_col_index - 1].value:
#             for cell in row:
#                     cell.fill = seguro_fill
#         elif "ACH - BGENERAL PLANILL" in row[desc_col_index - 1].value:
#             for cell in row:
#                     cell.fill = netflix_fill

# Guardar los cambios en el archivo Excel
wb.save(new_file_path)

# # Filtrar las filas que contienen "Stella" en la columna "Area Responsable"
# df_filtered = df[df['Area Responsable'].str.contains('Stella', na=False)].copy()

# # Convertir la columna "Computer Name" a minúsculas
# df_filtered.loc[:, 'Computer Name'] = df_filtered['Computer Name'].str.lower()

# # Clasificar la columna "Computer Name"
# def classify_computer_name(name):
#     if name.startswith('bgcd'):
#         return 'dev'
#     elif name.startswith('bgcp'):
#         return 'amb'
#     elif name.startswith('bgca'):
#         return 'dr'
#     elif name.startswith('bgdc'):
#         return 'prod'
#     else:
#         return 'unknown'

# df_filtered.loc[:, 'Classification'] = df_filtered['Computer Name'].apply(classify_computer_name)

# # Clasificar la columna "Computer Name" por tecnología
# def classify_tech(name):
#     if 'ntps' in name:
#         return 'ntp'
#     if 'dynatrace' in name:
#         return 'dynatrace'
#     if 'nortexdc' in name:
#         return 'decision center'
#     if 'dsg' in name:
#         return 'designer'
#     if 'log' in name:
#         return 'ELK'
#     if 'lic' in name:
#         return 'designer licencia'
#     if 'hpv' in name or 'hyper' in name:
#         return 'hypervisor'
#     if 'rh0' in name:
#         return 'hosts'
#     if 'mon' in name:
#         return 'monitoreo'
#     if 'odmrs' in name:
#         return 'odm rs'
#     if 'odmbd' in name:
#         return 'odm db'
#     if 'xace' in name:
#         return 'ace'
#     if 'ecrionap' in name:
#         return 'ecrion ap'
#     if 'ecriondb' in name or 'ecrionbd' in name:
#         return 'ecrion db'
#     if 'engagelb' in name:
#         return 'engage lb'
#     if 'engagedb' in name or 'engdb' in name:
#         return 'engage db'
#     if 'engageap' in name or 'engap' in name or 'engagecap' in name:
#         return 'engage ap'
#     if 'lb' in name or 'ngx' in name:
#         return 'nginx'
#     if 'cg' in name or 'cgen' in name:
#         return 'jboss / tomcat'
#     if 'xels' in name or 'xes' in name or 'aes' in name:
#         return 'elasticsearch'
#     if 'camdb' in name or 'db' in name:
#         return 'db'
#     if 'api' in name or 'apr' in name:
#         return 'container'
#     if 'ap' in name:
#         return 'ap liferay'
#     else:
#         return 'unknown'

# df_filtered.loc[:, 'Tech'] = df_filtered['Computer Name'].apply(classify_tech)

# # Convertir la columna "Last Patched Time" a formato fecha (día, mes y año con el mes en palabras)
# df_filtered['Last Patched Time'] = pd.to_datetime(df_filtered['Last Patched Time'], errors='coerce').dt.strftime('%Y-%m-%d')
# df_filtered['Last Boot Time'] = pd.to_datetime(df_filtered['Last Boot Time'], errors='coerce').dt.strftime('%Y-%m-%d')
# df_filtered['Last Patched Month'] = pd.to_datetime(df_filtered['Last Patched Time'], errors='coerce').dt.strftime('%B')
# df_filtered['Last Boot Month'] = pd.to_datetime(df_filtered['Last Boot Time'], errors='coerce').dt.strftime('%B')

# # Eliminar las columnas especificadas
# columns_to_drop = ['Area Responsable', 'Last Successful Scan', 'Remote Office', 'Area Responsable AP']
# df_filtered.drop(columns=columns_to_drop, inplace=True)

# # Guardar el DataFrame filtrado en una nueva hoja llamada "Stella"
# with pd.ExcelWriter(new_file_path, mode='a', engine='openpyxl') as writer:
#     df_filtered.to_excel(writer, sheet_name='Stella', index=False)

# # Cargar el archivo Excel con openpyxl
# wb = load_workbook(new_file_path)
# ws = wb['Stella']

# # Obtener el mes actual
# current_month = pd.Timestamp.now().strftime('%B')
# previous_month = (pd.Timestamp.now() - pd.DateOffset(months=1)).strftime('%B')

# # Definir los colores
# green_fill = PatternFill(start_color='00FF00', end_color='00FF00', fill_type='solid')
# red_fill = PatternFill(start_color='FF0000', end_color='FF0000', fill_type='solid')
# yellow_fill = PatternFill(start_color='FFFF00', end_color='FFFF00', fill_type='solid')

# # Obtener el índice de la columna "Last Patched Month"
# lpm_col_index = None
# for idx, cell in enumerate(ws[1]):
#     if cell.value == 'Last Patched Month':
#         lpm_col_index = idx + 1
#         break

# # Aplicar el color a la columna "Last Patched Month"
# for row in ws.iter_rows(min_row=2, min_col=lpm_col_index, max_col=lpm_col_index):
#     for cell in row:
#         if cell.value == current_month:
#             cell.fill = green_fill
#         elif cell.value == previous_month:
#             cell.fill = yellow_fill
#         else:
#             cell.fill = red_fill

# # Aplicar el color a la columna "Last Boot Month"
# for row in ws.iter_rows(min_row=2, min_col=ws.max_column, max_col=ws.max_column):
#     for cell in row:
#         if cell.value == current_month:
#             cell.fill = green_fill
#         elif cell.value == previous_month:
#             cell.fill = yellow_fill
#         else:
#             cell.fill = red_fill

# # Obtener el índice de la columna "Health"
# health_col_index = None
# for idx, cell in enumerate(ws[1]):
#     if cell.value == 'Health':
#         health_col_index = idx + 1
#         break

# # Aplicar el color a la columna "Health"
# if health_col_index:
#     for row in ws.iter_rows(min_row=2, min_col=health_col_index, max_col=health_col_index):
#         for cell in row:
#             if cell.value == 'Healthy':
#                 cell.fill = green_fill
#             elif cell.value == 'Vulnerable':
#                 cell.fill = yellow_fill
#             elif cell.value == 'Highly Vulnerable':
#                 cell.fill = red_fill

# # Guardar los cambios en el archivo Excel
# wb.save(new_file_path)