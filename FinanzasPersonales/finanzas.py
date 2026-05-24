import glob
import os
import time
import pandas as pd
from sqlalchemy import create_engine
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

DB = "sqlite:////data/finanzas.db"


def cargar_ahorros():
    archivos = glob.glob('/estados_de_cuenta/cda*.xlsx')
    if not archivos:
        print("No se encontraron archivos cda*.xlsx en /estados_de_cuenta")
        return

    frames = []
    for archivo in sorted(archivos):
        try:
            df = pd.read_excel(archivo)
            frames.append(df.iloc[7:, 1:6].copy())
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    if not frames:
        return

    data = pd.concat(frames, ignore_index=True)
    data.columns = ['fecha', 'referencia', 'descripcion', 'monto', 'total']
    data['fecha'] = pd.to_datetime(data['fecha']).dt.date
    data = data.sort_values('fecha').reset_index(drop=True)
    data.insert(0, 'orden', range(1, len(data) + 1))
    data = data.set_index('orden')

    engine = create_engine(DB)
    with engine.connect() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS ahorros")
        conn.commit()
    data.to_sql('ahorros', engine, if_exists='append', index=True)
    print(f"Tabla 'ahorros' actualizada con {len(data)} registros.")


def cargar_tarjetas():
    archivos = glob.glob('/estados_de_cuenta/tarjeta*.xlsx')
    if not archivos:
        print("No se encontraron archivos tarjeta*.xlsx en /estados_de_cuenta")
        return

    frames = []
    for archivo in sorted(archivos):
        try:
            df = pd.read_excel(archivo, header=None)
            frames.append(df.iloc[8:, [3, 4, 5, 8, 9, 10, 11]].copy())
        except Exception as e:
            print(f"Error leyendo {archivo}: {e}")

    if not frames:
        return

    data = pd.concat(frames, ignore_index=True)
    data.columns = ['fecha_transaccion', 'fecha_proceso', 'descripcion',
                    'referencia', 'categoria', 'cargos_db', 'pagos_cr']
    data = data.dropna(subset=['fecha_transaccion', 'descripcion'])
    data['fecha_transaccion'] = pd.to_datetime(data['fecha_transaccion'], dayfirst=True).dt.date
    data['fecha_proceso'] = pd.to_datetime(data['fecha_proceso'], dayfirst=True).dt.date
    data = data.sort_values('fecha_transaccion').reset_index(drop=True)
    data.insert(0, 'orden', range(1, len(data) + 1))
    data = data.set_index('referencia')

    engine = create_engine(DB)
    with engine.connect() as conn:
        conn.exec_driver_sql("DROP TABLE IF EXISTS tarjetas")
        conn.commit()
    data.to_sql('tarjetas', engine, if_exists='append', index=True)
    print(f"Tabla 'tarjetas' actualizada con {len(data)} registros.")


class EstadosHandler(FileSystemEventHandler):
    def _dispatch(self, path):
        nombre = os.path.basename(path)
        if nombre.startswith('cda') and nombre.endswith('.xlsx'):
            print(f"Cambio detectado en {nombre}, actualizando ahorros...")
            cargar_ahorros()
        elif nombre.startswith('tarjeta') and nombre.endswith('.xlsx'):
            print(f"Cambio detectado en {nombre}, actualizando tarjetas...")
            cargar_tarjetas()

    def on_modified(self, event):
        if not event.is_directory:
            self._dispatch(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self._dispatch(event.src_path)


if __name__ == '__main__':
    print("Carga inicial de ahorros...")
    cargar_ahorros()

    print("Carga inicial de tarjetas...")
    cargar_tarjetas()

    observer = Observer()
    observer.schedule(EstadosHandler(), path='/estados_de_cuenta', recursive=False)
    observer.start()
    print("Watcher activo, esperando cambios...")

    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
