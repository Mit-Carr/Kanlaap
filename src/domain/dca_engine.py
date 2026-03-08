import pandas as pd
import numpy as np

def calcular_estrategia_dca(df_precios: pd.DataFrame, df_ipc: pd.DataFrame, inversion_mensual: float = 1000.0) -> pd.DataFrame:
    """
    Motor cuantitativo puro para el cálculo de DCA y ajuste inflacionario.
    Diseñado bajo Arquitectura Hexagonal: Agnóstico a la infraestructura de red o web.
    """
    df = df_precios.copy()
    
    # 1. Limpieza de Zonas Horarias: Evita choques al unir con el IPC
    if df.index.tz is not None:
        df.index = df.index.tz_localize(None)
        
    df_compras = df.resample('MS').first().copy()

    # --- VECTORIZACIÓN EXTREMA Y GESTIÓN DE MEMORIA ---
    df_compras['btc_adquirido'] = inversion_mensual / df_compras['Close']
    df_compras['acumulado_btc'] = df_compras['btc_adquirido'].cumsum()
    df_compras['valor_portafolio_mxn'] = df_compras['acumulado_btc'] * df_compras['Close']

    # --- CÁLCULO DE LA INVERSIÓN NOMINAL ---
    df_compras['inversion_nominal_acumulada'] = (np.ones(len(df_compras)) * inversion_mensual).cumsum()

    # --- CÁLCULO DE LA DEVALUACIÓN INFLACIONARIA (IPC) ---
    if not df_ipc.empty:
        # Aseguramos compatibilidad de índices temporales
        if df_ipc.index.tz is not None:
            df_ipc.index = df_ipc.index.tz_localize(None)
            
        # Unimos las tablas. ffill() y bfill() curan cualquier "NaN" por desfase de días
        df_compras = df_compras.join(df_ipc, how='left')
        df_compras['IPC'] = df_compras['IPC'].ffill().bfill()
        
        # LA MATEMÁTICA DE VALOR PRESENTE:
        ipc_actual = df_compras['IPC'].iloc[-1]
        
        # Invertimos la fracción: IPC_Histórico / IPC_Actual
        df_compras['aportacion_mensual_real'] = inversion_mensual * (df_compras['IPC'] / ipc_actual)
        
        # Sumamos la escalera de aportaciones devaluadas
        df_compras['poder_adquisitivo_real'] = df_compras['aportacion_mensual_real'].cumsum()
    
    return df_compras
    
