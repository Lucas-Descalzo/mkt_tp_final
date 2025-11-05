# Trabajo Práctico Final - Introducción al Marketing Online y los Negocios Digitales

**Alumno:** Lucas Descalzo

Este proyecto implementa un pipeline de ETL (Extract, Transform, Load) para la empresa "EcoBottle". El proceso toma los datos crudos (archivos `.csv`) de las operaciones de la empresa, los transforma en un **Esquema Estrella** (Modelo Kimball) y los carga en un Data Warehouse (carpeta `DW/`) listo para ser analizado y visualizado en PowerBI.

---

## 🛠️ 1. Instrucciones de Ejecución

Para ejecutar este proyecto y generar el Data Warehouse en tu máquina local, seguí estos pasos:

1.  **Clonar el repositorio:**
    ```bash
    git clone [https://github.com/Lucas-Descalzo/mkt_tp_final.git](https://github.com/Lucas-Descalzo/mkt_tp_final.git)
    cd mkt_tp_final
    ```

2.  **Crear y activar un entorno virtual:**
    ```bash
    # Crear el entorno
    python -m venv venv

    # Activar en Windows (Command Prompt)
    .\venv\Scripts\activate
    ```

3.  **Instalar las dependencias:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar el Pipeline ETL:**
    ```bash
    python main.py
    ```

Tras la ejecución, la carpeta `DW/` contendrá las 13 tablas (Dimensiones y Hechos) del Esquema Estrella en formato `.csv`, listas para ser consumidas por PowerBI.

---

## 🌌 2. Modelo de Datos (Esquema Estrella)

El pipeline transforma los datos crudos en una **Constelación de Hechos** (múltiples esquemas estrella) que comparten dimensiones comunes ("conformadas") como `dim_date`, `dim_customer` y `dim_channel`.

El modelo final se compone de 7 Dimensiones y 6 Tablas de Hechos.

### A. Constelación de Ventas (Pedidos, Items, Pagos y Envíos)
![Diagrama de Ventas](esquema_estrella/Fact_sales_order.jpeg)
![Diagrama de Items](esquema_estrella/Fact_sales_order_item.jpeg)
![Diagrama de Pagos](esquema_estrella/Fact_payment.jpeg)
![Diagrama de Envíos](esquema_estrella/Fact_shipment.jpeg)

### B. Esquema de Sesiones Web (Usuarios Activos)
![Diagrama de Sesiones](esquema_estrella/Fact_web_session.jpeg)

### C. Esquema de NPS
![Diagrama de NPS](esquema_estrella/Fact_nps_response.jpeg)

---

## 📚 3. Diccionario de Datos (Data Warehouse)

El pipeline genera las siguientes 13 tablas en la carpeta `DW/`:

### Dimensiones (Tablas Descriptivas)
* **`dim_customer`**: Maestro de clientes (Fuente: `customer.csv`).
* **`dim_product`**: Maestro de productos (Fuente: `product.csv`, `product_category.csv`).
* **`dim_location`**: Maestro de direcciones (Fuente: `address.csv`, `province.csv`).
* **`dim_store`**: Maestro de tiendas físicas (Fuente: `store.csv`).
* **`dim_channel`**: Catálogo de canales de venta (Fuente: `channel.csv`).
* **`dim_province`**: Catálogo de provincias (Fuente: `province.csv`).
* **`dim_date`**: Dimensión de calendario generada automáticamente.

### Hechos (Tablas Transaccionales)
* **`fact_sales_order`**: Cabeceras de pedidos (Fuente: `sales_order.csv`).
* **`fact_sales_order_item`**: Detalle (ítems) de pedidos (Fuente: `sales_order_item.csv`).
* **`fact_payment`**: Eventos de pago (Fuente: `payment.csv`).
* **`fact_shipment`**: Eventos de envío (Fuente: `shipment.csv`).
* **`fact_web_session`**: Sesiones web para Usuarios Activos (Fuente: `web_session.csv`).
* **`fact_nps_response`**: Respuestas de encuestas NPS (Fuente: `nps_response.csv`).

---

## 🎯 4. KPIs del Dashboard

[cite_start]Los archivos `.csv` generados en `DW/` son la fuente de datos para el dashboard en PowerBI, el cual debe responder a los siguientes KPIs clave[cite: 6]:

* **Ventas Totales ($M)**
* **Usuarios Activos (nK)**
* **Ticket Promedio ($K)**
* **NPS (ptos.)**
* **Ventas por Provincia**
* **Ranking Mensual por Producto**