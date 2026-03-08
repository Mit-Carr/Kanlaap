import yfinance as yf
import pandas as pd
import os
from src.adapters.logger_config import setup_logger

# Instanciamos el logger profesional 
logger = setup_logger("market_data")

def obtener_datos_mercado(ticker: str = "BTC-MXN", fecha_inicio: str = "2016-01-01") -> pd.DataFrame:
    """
    Patrón Repositorio con Disyuntor (Circuit Breaker).
    Intenta extraer datos vectoriales de la API; si falla, aplica Degradación Elegante a CSV.
    """
    logger.info(f"Iniciando extracción de datos para {ticker} desde {fecha_inicio}")
    
    # --- ADAPTADOR DE RED (yfinance) ---
    try:
        # yfinance actúa como Wrapper, ocultando la complejidad del HTTP
        # y retornando directamente un DataFrame de Pandas.
        df_mercado = yf.download(ticker, start=fecha_inicio, progress=False)
        
        if df_mercado.empty:
            raise ValueError("La API retornó una matriz vacía.")
            
        logger.info("Extracción de red exitosa. Matriz lista.")
        # Retornamos solo la columna de Cierre para ahorrar memoria RAM
        return df_mercado[['Close']]
        
    # --- DISYUNTOR Y ADAPTADOR DE REFUGIO (CSV Local) ---
    except Exception as e:
        logger.warning(f"Caída crítica en yfinance API detectada ({e}). Conmutando a fallback estático CSV de emergencia. Modo degradado activo.")
        
        ruta_csv = "data/btc_mxn_historical_backup.csv"
        
        if os.path.exists(ruta_csv):
            try:
                # 1. Leemos el CSV
                df_contingencia = pd.read_csv(
                    ruta_csv, 
                    parse_dates=['Date'], 
                    index_col='Date'
                )
                
                # 2. Ordenamos del pasado al presente
                df_contingencia.sort_index(inplace=True)
                
                # 3. EL FIX MAESTRO: Recortamos la matriz para que empiece EXACTAMENTE en la fecha solicitada
                df_contingencia = df_contingencia[df_contingencia.index >= fecha_inicio]
                
                logger.info(f"Fallback ejecutado exitosamente. Matriz filtrada desde {fecha_inicio}.")
                
                # Retornamos la matriz con la columna Close
                return df_contingencia[['Close']]
                
            except Exception as ex_csv:
                logger.error(f"Fallo catastrófico al leer el archivo de contingencia: {ex_csv}")
                return pd.DataFrame() # Retorna matriz vacía para evitar crash
        else:
            logger.error("Fallo catastrófico: Archivo CSV de contingencia no encontrado en el sistema.")
            return pd.DataFrame()