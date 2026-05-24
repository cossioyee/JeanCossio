import pandas as pd
from openpyxl import load_workbook
from sqlalchemy import create_engine



# Leer el archivo Excel
df = pd.read_excel('cuentas.xlsx')

# Mostrar el DataFrame
print(df)

# seleccionar columnas B-F desde fila 8 hacia abajo (fila 8 -> índice 7, columnas B-F -> índices 1-5)
data = df.iloc[7:, 1:6].copy()
data = data.reset_index(drop=True)

# ajustar nombres de columna si es necesario (opcional)
data.columns = ['fecha','referencia','descripcion','monto','total']

# conectar a Postgres (reemplaza USERNAME, PASSWORD, HOST, PORT, DBNAME)
engine = create_engine("sqlite:////data/finanzas.db")

# Eliminar la tabla 'finanzas' si existe
with engine.connect() as connection:
    connection.exec_driver_sql("DROP TABLE IF EXISTS finanzas")
    connection.commit()
    engine.dispose()

# insertar en la tabla 'finanzas' (crea la tabla si no existe)
data.to_sql('finanzas', engine, if_exists='append', index=False)
