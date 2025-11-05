import pandas as pd

# --- Función Orquestadora de Transformación ---

def transform_all_data(raw_data):
    """
    Toma los datos crudos y los transforma en un Esquema Estrella.
    
    Args:
        raw_data (dict): Diccionario con los DataFrames crudos.

    Returns:
        dict: Diccionario con los DataFrames del Esquema Estrella (dims y facts).
    """
    
    # --- 1. Creación de Dimensiones ---
    print("      -> Creando Dimensiones...")
    dim_channel = build_dim_channel(raw_data['channel'])
    dim_province = build_dim_province(raw_data['province'])
    dim_customer = build_dim_customer(raw_data['customer'])
    dim_product = build_dim_product(raw_data['product'], raw_data.get('product_category'))
    dim_store = build_dim_store(raw_data['store'], raw_data['address'], dim_province)
    
    # Crearemos una dim_location unificada para simplificar
    dim_location = build_dim_location(raw_data['address'], dim_province)

    # --- 2. Creación de Hechos ---
    # (Añadiremos las llamadas a los hechos aquí más adelante)
    print("      -> Creando Tablas de Hechos...")
    fact_sales = build_fact_sales(raw_data['sales_order'], raw_data['sales_order_item'], dim_location)
    fact_nps = build_fact_nps(raw_data['nps_response'])
    fact_users = build_fact_users(raw_data['web_session'])


    # --- 3. Retorno del Esquema Estrella ---
    star_schema_tables = {
        # Dimensiones
        "dim_channel": dim_channel,
        "dim_province": dim_province,
        "dim_customer": dim_customer,
        "dim_product": dim_product,
        "dim_store": dim_store,
        "dim_location": dim_location,
        
        # Hechos
        "fact_sales": fact_sales,
        "fact_nps": fact_nps,
        "fact_users": fact_users,
        # (Añadiremos más hechos aquí)
    }
    
    return star_schema_tables

# =============================================================================
# --- Funciones Auxiliares (BUILDERS) ---
# =============================================================================

# --- DIMENSION BUILDERS ---

def build_dim_channel(df_channel):
    """Crea la dimensión Canal."""
    dim_channel = df_channel.copy()
    dim_channel = dim_channel.rename(columns={'name': 'channel_name'})
    return dim_channel

def build_dim_province(df_province):
    """Crea la dimensión Provincia."""
    dim_province = df_province.copy()
    dim_province = dim_province.rename(columns={'name': 'province_name'})
    return dim_province

def build_dim_customer(df_customer):
    """Crea la dimensión Cliente."""
    dim_customer = df_customer.copy()
    # Limpieza: seleccionar y renombrar columnas clave
    dim_customer = dim_customer[['customer_id', 'email', 'first_name', 'last_name', 'status', 'created_at']]
    return dim_customer

def build_dim_product(df_product, df_category):
    """Crea la dimensión Producto, uniendo su categoría si existe."""
    dim_product = df_product.copy()
    
    if df_category is not None:
        # Unir con categorías
        dim_product = pd.merge(
            dim_product,
            df_category,
            on='category_id',
            how='left',
            suffixes=('_prod', '_cat')
        )
        # Renombrar 'name_cat' a 'category_name' y 'name_prod' a 'product_name'
        dim_product = dim_product.rename(columns={'name_prod': 'product_name', 'name_cat': 'category_name'})
    else:
        # Si no hay categoría, solo renombrar el nombre del producto
        dim_product = dim_product.rename(columns={'name': 'product_name'})

    # Seleccionar columnas finales
    cols_to_keep = ['product_id', 'sku', 'product_name', 'list_price', 'status', 'category_name']
    # Filtramos solo las columnas que existen
    dim_product = dim_product[[col for col in cols_to_keep if col in dim_product.columns]]
    return dim_product

def build_dim_location(df_address, df_province):
    """Crea una dimensión de Localización unificada (Address + Province)."""
    # Unimos address y province
    dim_location = pd.merge(
        df_address,
        df_province,
        on='province_id',
        how='left',
        suffixes=('_addr', '_prov')
    )
    # Renombramos
    dim_location = dim_location.rename(columns={
        'name': 'province_name',
        'code': 'province_code'
    })
    # Seleccionamos columnas
    dim_location = dim_location[[
        'address_id', 'line1', 'line2', 'city', 'province_id', 'province_name', 
        'province_code', 'postal_code', 'country_code'
    ]]
    return dim_location

def build_dim_store(df_store, df_address, df_province):
    """Crea la dimensión Tienda, uniendo su dirección y provincia."""
    # Unir tienda con la dimensión de localización que ya creamos
    dim_store = pd.merge(
        df_store,
        build_dim_location(df_address, df_province), # Reutilizamos la lógica
        on='address_id',
        how='left'
    )
    dim_store = dim_store.rename(columns={'name': 'store_name'})
    return dim_store


# --- FACT BUILDERS (Simplificados para el Dashboard) ---
# Estas tablas SÍ son las que alimentarán directamente el Dashboard.
# Están denormalizadas (incluyen provincia, nombre de producto, etc.) 
# para hacer los cálculos en Looker más fáciles.

def build_fact_sales(df_orders, df_items, dim_location):
    """Crea la tabla de hechos de ventas, lista para el dashboard."""
    
    # 1. Filtrar solo ventas válidas
    sales_status_filter = ['PAID', 'FULFILLED']
    df_sales = df_orders[df_orders['status'].isin(sales_status_filter)].copy()

    # 2. Unir con items para tener el detalle del producto
    df_sales_fact = pd.merge(
        df_sales,
        df_items,
        on='order_id',
        how='left'
    )
    
    # 3. Unir con dim_location para tener la provincia
    df_sales_fact = pd.merge(
        df_sales_fact,
        dim_location[['address_id', 'province_name']],
        left_on='shipping_address_id',
        right_on='address_id',
        how='left'
    )
    
    # 4. Limpieza de columnas
    df_sales_fact['order_date'] = pd.to_datetime(df_sales_fact['order_date']).dt.date
    
    # Seleccionamos las columnas necesarias para TODOS los KPIs de ventas
    fact_columns = [
        'order_id', 'order_date', 'channel_id', 'total_amount', 'province_name',
        'product_id', 'quantity', 'line_total'
    ]
    df_sales_fact = df_sales_fact[fact_columns]
    
    return df_sales_fact

def build_fact_nps(df_nps):
    """Crea la tabla de hechos de NPS, lista para el dashboard."""
    fact_nps = df_nps.copy()
    
    # 1. Convertir fecha
    fact_nps['date'] = pd.to_datetime(fact_nps['responded_at']).dt.date
    
    # 2. Clasificar Score
    def classify_nps(score):
        if score >= 9: return 'Promotor'
        elif score >= 7: return 'Pasivo'
        else: return 'Detractor'
    
    fact_nps['nps_category'] = fact_nps['score'].apply(classify_nps)
    
    # 3. Seleccionar columnas
    fact_nps = fact_nps[['nps_id', 'date', 'channel_id', 'score', 'nps_category']]
    return fact_nps

def build_fact_users(df_sessions):
    """Crea la tabla de hechos de Usuarios Activos, lista para el dashboard."""
    fact_users = df_sessions.copy()
    
    # 1. Convertir fecha
    fact_users['date'] = pd.to_datetime(fact_users['started_at']).dt.date
    
    # 2. Crear 'user_key' único (como hicimos antes)
    fact_users['user_key'] = 'anon_' + fact_users['session_id'].astype(str)
    fact_users.loc[fact_users['customer_id'].notna(), 'user_key'] = \
        'user_' + fact_users['customer_id'].astype(str)
        
    # 3. Seleccionar columnas
    fact_users = fact_users[['session_id', 'date', 'user_key']]
    return fact_users