import pandas as pd

# --- Función Orquestadora de Transformación ---

def transform_all_data(raw_data):
    """
    Toma los datos crudos y los transforma en un Esquema Estrella "Puro".
    Las Dims son descriptivas.
    Las Facts solo contienen IDs (claves) y Medidas (números).
    """
    
    # --- 1. Creación de Dimensiones ---
    print("      -> Creando Dimensiones...")
    dim_channel = build_dim_channel(raw_data['channel'])
    dim_province = build_dim_province(raw_data['province'])
    dim_customer = build_dim_customer(raw_data['customer'])
    dim_location = build_dim_location(raw_data['address'], dim_province)
    dim_product = build_dim_product(raw_data['product'], raw_data.get('product_category'))
    dim_store = build_dim_store(raw_data['store'], dim_location)
    dim_date = build_dim_date(raw_data) # Genera la dim de tiempo

    # --- 2. Creación de Hechos ---
    print("      -> Creando Tablas de Hechos...")
    fact_sales_order = build_fact_sales_order(raw_data['sales_order'])
    fact_sales_order_item = build_fact_sales_order_item(raw_data['sales_order_item'])
    fact_payment = build_fact_payment(raw_data['payment'])
    fact_shipment = build_fact_shipment(raw_data['shipment'])
    fact_web_session = build_fact_web_session(raw_data['web_session'])
    fact_nps_response = build_fact_nps(raw_data['nps_response'])

    # --- 3. Retorno del Esquema Estrella ---
    star_schema_tables = {
        "dim_channel": dim_channel,
        "dim_province": dim_province,
        "dim_customer": dim_customer,
        "dim_location": dim_location,
        "dim_product": dim_product,
        "dim_store": dim_store,
        "dim_date": dim_date,
        "fact_sales_order": fact_sales_order,
        "fact_sales_order_item": fact_sales_order_item,
        "fact_payment": fact_payment,
        "fact_shipment": fact_shipment,
        "fact_web_session": fact_web_session,
        "fact_nps_response": fact_nps_response
    }
    
    return star_schema_tables

# =============================================================================
# --- Funciones Auxiliares (BUILDERS) ---
# =============================================================================

# --- DIMENSION BUILDERS ---

def build_dim_channel(df_channel):
    """Crea la dimensión Canal."""
    return df_channel.copy()

def build_dim_province(df_province):
    """Crea la dimensión Provincia."""
    return df_province.copy()

def build_dim_customer(df_customer):
    """Crea la dimensión Cliente."""
    # Seleccionamos solo las columnas descriptivas
    return df_customer[['customer_id', 'email', 'first_name', 'last_name', 'status', 'created_at']].copy()

def build_dim_location(df_address, df_province):
    """Crea una dimensión de Localización unificada (Address + Province)."""
    dim_location = pd.merge(
        df_address,
        df_province,
        on='province_id',
        how='left',
        suffixes=('_addr', '_prov')
    )
    # Seleccionamos y renombramos
    dim_location = dim_location.rename(columns={'name': 'province_name', 'code': 'province_code'})
    return dim_location[['address_id', 'line1', 'line2', 'city', 'province_id', 'province_name', 'province_code', 'postal_code', 'country_code']]

def build_dim_product(df_product, df_category):
    """Crea la dimensión Producto, uniendo su categoría si existe."""
    dim_product = df_product.copy()
    if df_category is not None:
        dim_product = pd.merge(
            dim_product,
            df_category,
            on='category_id',
            how='left',
            suffixes=('_prod', '_cat')
        )
        dim_product = dim_product.rename(columns={'name_prod': 'product_name', 'name_cat': 'category_name'})
    else:
        dim_product = dim_product.rename(columns={'name': 'product_name'})
    
    cols_to_keep = ['product_id', 'sku', 'product_name', 'list_price', 'status', 'category_id', 'category_name', 'parent_id']
    return dim_product[[col for col in cols_to_keep if col in dim_product.columns]]

def build_dim_store(df_store, dim_location):
    """Crea la dimensión Tienda, uniendo su dirección (ya procesada)."""
    dim_store = pd.merge(
        df_store,
        dim_location, # Usamos la dim_location que ya tiene la provincia
        on='address_id',
        how='left',
        suffixes=('_store', '_loc')
    )
    return dim_store.rename(columns={'name': 'store_name'})

def build_dim_date(raw_data):
    """Crea una dimensión de Fecha (Calendario) a partir de todas las fechas del modelo."""
    print("        -> Generando dim_date...")
    # Recolectar todas las fechas de las tablas de hechos
    dates = pd.concat([
        pd.to_datetime(raw_data['sales_order']['order_date']),
        pd.to_datetime(raw_data['payment']['paid_at']),
        pd.to_datetime(raw_data['shipment']['shipped_at']),
        pd.to_datetime(raw_data['shipment']['delivered_at']),
        pd.to_datetime(raw_data['web_session']['started_at']),
        pd.to_datetime(raw_data['web_session']['ended_at']),
        pd.to_datetime(raw_data['nps_response']['responded_at'])
    ]).dropna().unique()
    
    dim_date = pd.DataFrame(data={'date': pd.to_datetime(dates)})
    dim_date = dim_date.drop_duplicates().sort_values(by='date')
    
    # Enriquecer la dimensión de fecha
    dim_date['date_key'] = dim_date['date'].dt.strftime('%Y%m%d').astype(int)
    dim_date['year'] = dim_date['date'].dt.year
    dim_date['quarter'] = dim_date['date'].dt.quarter
    dim_date['month'] = dim_date['date'].dt.month
    dim_date['month_name'] = dim_date['date'].dt.month_name()
    dim_date['day'] = dim_date['date'].dt.day
    dim_date['day_of_week'] = dim_date['date'].dt.dayofweek
    dim_date['day_name'] = dim_date['date'].dt.day_name()
    dim_date['is_weekend'] = dim_date['day_of_week'].isin([5, 6])
    
    return dim_date.dropna(subset=['date'])

# --- FACT BUILDERS ---
# Estas tablas solo contienen Claves (IDs) y Medidas (Números)

def build_fact_sales_order(df_orders):
    """Crea la tabla de hechos de Encabezado de Orden."""
    # Seleccionar solo claves y medidas
    fact_cols = [
        'order_id', 'customer_id', 'channel_id', 'store_id', 
        'billing_address_id', 'shipping_address_id', 'order_date',
        'subtotal', 'tax_amount', 'shipping_fee', 'total_amount', 'status'
    ]
    return df_orders[fact_cols].copy()

def build_fact_sales_order_item(df_items):
    """Crea la tabla de hechos de Ítems de Orden."""
    # Seleccionar solo claves y medidas
    fact_cols = [
        'order_item_id', 'order_id', 'product_id', 
        'quantity', 'unit_price', 'discount_amount', 'line_total'
    ]
    return df_items[fact_cols].copy()

def build_fact_payment(df_payment):
    """Crea la tabla de hechos de Pagos."""
    fact_cols = [
        'payment_id', 'order_id', 'method', 'status', 'amount', 'paid_at'
    ]
    return df_payment[fact_cols].copy()

def build_fact_shipment(df_shipment):
    """Crea la tabla de hechos de Envíos."""
    fact_cols = [
        'shipment_id', 'order_id', 'carrier', 'tracking_number', 'status', 
        'shipped_at', 'delivered_at'
    ]
    return df_shipment[fact_cols].copy()

def build_fact_web_session(df_session):
    """Crea la tabla de hechos de Sesiones Web."""
    fact_cols = [
        'session_id', 'customer_id', 'started_at', 'ended_at', 'source', 'device'
    ]
    return df_session[fact_cols].copy()

def build_fact_nps(df_nps):
    """Crea la tabla de hechos de Respuestas NPS."""
    fact_cols = [
        'nps_id', 'customer_id', 'channel_id', 'score', 'comment', 'responded_at'
    ]
    return df_nps[fact_cols].copy()