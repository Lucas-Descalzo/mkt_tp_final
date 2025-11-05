import sys
import os
import time

# Forzamos a Python a ver la carpeta 'scripts'
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importamos las funciones principales de nuestro pipeline ETL
from scripts.extract import extract_all_data
from scripts.transform import transform_all_data
from scripts.load import load_all_data

def main():
    """
    Orquesta el proceso ETL completo:
    1. Extrae datos de /RAW
    2. Transforma los datos en un esquema estrella
    3. Carga los datos transformados en /DW
    """
    print("Iniciando Proceso ETL para EcoBottle...")
    
    start_time = time.time()
    
    # Definir rutas
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RAW_DIR = os.path.join(BASE_DIR, 'RAW')
    DW_DIR = os.path.join(BASE_DIR, 'DW')
    
    try:
        # --- 1. FASE DE EXTRACCIÓN (E) ---
        print("Fase 1: Extrayendo datos de RAW...")
        raw_data = extract_all_data(RAW_DIR)
        print(f"   -> Extracción completada. {len(raw_data)} tablas cargadas.\n")
        
        # --- 2. FASE DE TRANSFORMACIÓN (T) ---
        print("Fase 2: Transformando datos a Esquema Estrella...")
        star_schema_tables = transform_all_data(raw_data)
        print(f"   -> Transformación completada. {len(star_schema_tables)} tablas (Dims/Facts) creadas.\n")
        
        # --- 3. FASE DE CARGA (L) ---
        print("Fase 3: Cargando datos en DW...")
        load_all_data(star_schema_tables, DW_DIR)
        print("   -> Carga de datos completada.\n")
        
        # --- Finalización ---
        end_time = time.time()
        total_time = end_time - start_time
        
        print("-----------------------------------------------------")
        print(f"Proceso ETL completado exitosamente.")
        print(f"Tiempo total de ejecución: {total_time:.2f} segundos.")
        print("-----------------------------------------------------")

    except Exception as e:
        print(f"\n¡ERROR INESPERADO EN EL PROCESO PRINCIPAL!")
        print(f"Detalle: {e}")

if __name__ == "__main__":
    main()