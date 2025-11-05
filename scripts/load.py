import os

def load_all_data(star_schema_tables, dw_dir):
    """
    Guarda cada DataFrame del esquema estrella en un archivo .csv separado
    dentro del directorio DW.

    Args:
        star_schema_tables (dict): Diccionario de DataFrames (dims y facts).
        dw_dir (str): La ruta al directorio 'DW'.
    """
    
    # Asegurarnos de que el directorio DW exista
    os.makedirs(dw_dir, exist_ok=True)
    
    count = 0
    # Iteramos sobre el diccionario (ej: "dim_customer", df_customer)
    for table_name, df in star_schema_tables.items():
        # Definimos el nombre del archivo
        file_name = f"{table_name}.csv"
        output_path = os.path.join(dw_dir, file_name)
        
        try:
            # Guardamos el DataFrame como CSV
            df.to_csv(output_path, index=False)
            print(f"   -> Tabla '{file_name}' guardada exitosamente.")
            count += 1
        except Exception as e:
            print(f"   -> Error al guardar la tabla {file_name}: {e}")
            
    print(f"\n   -> {count} tablas guardadas en {dw_dir}")