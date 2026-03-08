import logging
import sys

def setup_logger(name="btc_architect"):
    """Configura un logger profesional para evitar usar print() en Streamlit."""
    logger = logging.getLogger(name)
    
    # Evitar que se dupliquen los mensajes si Streamlit recarga 
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Mandar los mensajes a la consola
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.INFO)
        
        # Formato: Fecha - Nivel - [Archivo] - Mensaje
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s] - %(message)s')
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        
    return logger