import pandas as pd
import os
import glob

def extract_all_data(raw_dir):
    """
    Carga todos los archivos .csv del directorio RAW en un diccionario de DataFrames.
    
    Args:
        raw_dir (str): La ruta al directorio 'RAW'.

    Returns:
        dict: Un diccionario donde la clave es el nombre de la tabla (sin .csv)
              y el valor es el DataFrame de pandas correspondiente.
    """
    
    # Usamos glob para encontrar todos los archivos .csv en la carpeta RAW
    csv_files = glob.glob(os.path.join(raw_dir, '*.csv'))
    
    if not csv_files:
        print(f"   -> Error: No se encontraron archivos .csv en el directorio: {raw_dir}")
        raise FileNotFoundError(f"No se encontraron CSVs en {raw_dir}")

    raw_data = {}
    
    print(f"   -> Encontrados {len(csv_files)} archivos CSV. Cargando...")
    
    for file_path in csv_files:
        # Obtenemos el nombre del archivo sin la extensión (ej: 'sales_order')
        table_name = os.path.basename(file_path).replace('.csv', '')
        
        try:
            # Cargamos el CSV en un DataFrame
            df = pd.read_csv(file_path)
            # Guardamos el DataFrame en el diccionario
            raw_data[table_name] = df
        except Exception as e:
            print(f"   -> Error al cargar el archivo {table_name}.csv: {e}")
            # Opcional: podrías decidir parar el pipeline si un archivo falla
            # raise e

    return raw_data