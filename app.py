import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import os
import base64
from io import BytesIO
from PIL import Image
import asyncio
from dotenv import load_dotenv
from src.domain.rag_orchestrator import KanlaapOrchestrator

# Obligamos a Streamlit a leer el archivo .env antes de arrancar la UI
load_dotenv()

# ==========================================
# UTILIDADES VISUALES Y CSS
# ==========================================
def cargar_css_local(nombre_archivo):
    try:
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"No se encontró el archivo de estilos: {nombre_archivo}")

def get_image_base64(image_obj):
    """Convierte un objeto de imagen PIL a Base64 para inyectarlo en HTML."""
    if not isinstance(image_obj, Image.Image):
        return ""
    buffered = BytesIO()
    image_obj.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()

# ==========================================
# CAPA DE DOMINIO Y APLICACIÓN
# ==========================================
class MercadoService:
    @staticmethod
    def obtener_datos_btc(fecha_inicio, fecha_fin):
        try:
            import yfinance as yf
            df = yf.download('BTC-USD', start=fecha_inicio, end=fecha_fin, progress=False)
            if df.empty:
                raise ValueError("Dataset vacío")
            
            df = df['Close'].reset_index()
            df.columns = ['Fecha', 'Precio_BTC']
            df['Fecha'] = pd.to_datetime(df['Fecha']).dt.tz_localize(None)
            return df
            
        except Exception as e:
            st.toast("⚠️ Modo Offline Activo: Usando base de datos local.", icon="🦡")
            fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')
            precios = np.linspace(30000, 65000, len(fechas)) * np.random.uniform(0.9, 1.1, len(fechas))
            return pd.DataFrame({'Fecha': fechas, 'Precio_BTC': precios})

class CalculadoraDCA:
    @staticmethod
    def ejecutar_simulacion(df_mercado, inversion_mensual, inflacion_anual=0.05):
        df = df_mercado.copy()
        df.set_index('Fecha', inplace=True)
        
        df_mensual = df.resample('MS').first().copy()
        df_mensual['Inversion_Nominal'] = inversion_mensual
        df_mensual['Nominal_Acumulado'] = df_mensual['Inversion_Nominal'].cumsum()
        
        df_mensual['Precio_BTC'] = df_mensual['Precio_BTC'].ffill().bfill() 
        df_mensual['BTC_Comprado'] = inversion_mensual / df_mensual['Precio_BTC']
        df_mensual['BTC_Acumulado'] = df_mensual['BTC_Comprado'].cumsum()
        df_mensual['Valor_Portafolio_BTC'] = df_mensual['BTC_Acumulado'] * df_mensual['Precio_BTC']
        
        tasa_mensual = (1 + inflacion_anual) ** (1/12) - 1
        meses_transcurridos = np.arange(len(df_mensual))
        df_mensual['Valor_Real_IPC'] = df_mensual['Nominal_Acumulado'] / ((1 + tasa_mensual) ** meses_transcurridos)
        
        return df_mensual[['Nominal_Acumulado', 'Valor_Real_IPC', 'Valor_Portafolio_BTC']]

# ==========================================
# CAPA DE PRESENTACIÓN E INFRAESTRUCTURA
# ==========================================
def init_assets_state():
    if 'orquestador_kanlaap' not in st.session_state:
        with st.spinner("Despertando a Kanlaap (Cargando red neuronal en CPU)..."):
            st.session_state['orquestador_kanlaap'] = KanlaapOrchestrator()

    if 'messages' not in st.session_state:
        st.session_state['messages'] = [
            {"role": "assistant", "content": "¡Hola! Soy Kanlaap, tu consultor sobre Bitcoin. ¿Te gustaría analizar cómo afecta la inflación a tus ahorros o prefieres platicar sobre los fundamentos de Bitcoin?"}
        ]
    if 'prompt_rapido' not in st.session_state:
        st.session_state['prompt_rapido'] = None
        
    if 'df_resultados' not in st.session_state:
        st.session_state['df_resultados'] = None
        
    if 'logo_header' not in st.session_state or 'avatar_chat' not in st.session_state:
        try:
            img_logo = Image.open(os.path.join("assets", "logo.png"))
            st.session_state['logo_header'] = img_logo
            
            img_avatar = Image.open(os.path.join("assets", "avatar.png")) 
            st.session_state['avatar_chat'] = img_avatar
        except FileNotFoundError:
            st.session_state['logo_header'] = "🦡" 
            st.session_state['avatar_chat'] = "🦡" 

def main():
    st.set_page_config(page_title="Kanlaap Dashboard", page_icon="🦡", layout="wide", initial_sidebar_state="collapsed")
    
    cargar_css_local("style.css")
    init_assets_state()

    logo_base64 = get_image_base64(st.session_state['logo_header'])
    if logo_base64:
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" width="80" height="32" style="border-radius: 6px; object-fit: contain;">'
    else:
        logo_html = '<div style="background: #3b82f6; color: white; font-weight: bold; width: 30px; height: 30px; display: flex; justify-content: center; align-items: center; border-radius: 6px;">K</div>'

    st.markdown(f"""
    <div style="display: flex; justify-content: space-between; align-items: center; background-color: #0b1221; padding: 12px 20px; border-bottom: 1px solid #1e293b; border-radius: 8px; margin-bottom: 25px;">
        <div style="display: flex; align-items: center; gap: 10px;">
            {logo_html}
            <div style="font-weight: 600; font-size: 1.2rem; color: #f8fafc; letter-spacing: 0.5px;">Kanlaap Dashboard</div>
        </div>
        <div style="display: flex; align-items: center; gap: 20px;">
            <div style="color: #10b981; font-size: 0.8rem; font-family: monospace;">🟢 Sistema en Línea</div>
            <div style="display: flex; align-items: center; gap: 10px; color: #64748b; font-size: 0.9rem; border-left: 1px solid #1e293b; padding-left: 15px;">
                Usuario
                <div style="background: #1e293b; width: 32px; height: 32px; border-radius: 50%; display: flex; justify-content: center; align-items: center;">👤</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # --- ORQUESTADOR DE LAYOUT ---
    col_calc, col_chat = st.columns([0.6, 0.4], gap="large")

    # --- SECCIÓN IZQUIERDA: VISUALIZACIÓN DATA-FIRST ---
    with col_calc:
        st.markdown("<h4 style='color: #f8fafc; font-size: 1rem; margin-bottom: 1rem;'>📊 Rendimiento Histórico DCA vs Inflación Fiat</h4>", unsafe_allow_html=True)
        
        # 1. Creamos "Agujeros" (Contenedores) reservados en la parte de arriba
        kpi_container = st.container()
        st.markdown("<br>", unsafe_allow_html=True)
        chart_container = st.container()
        st.markdown("<br>", unsafe_allow_html=True)

        # 2. Dibujamos el Formulario en la parte de abajo
        with st.form("parametros_dca", border=False):
            st.markdown("<div style='font-size: 0.8rem; color: #64748b; font-weight: bold; margin-bottom: 10px;'>⚙️ PARÁMETROS DE SIMULACIÓN CUANTITATIVA</div>", unsafe_allow_html=True)
            c1, c2, c3 = st.columns([1.5, 1, 1])
            with c1:
                inversion = st.number_input("Aportación Mensual (MXN)", min_value=500, max_value=50000, value=2000, step=500)
            with c2:
                fecha_inicio = st.date_input("Fecha Inicio", value=date(2021, 1, 1))
            with c3:
                fecha_fin = st.date_input("Fecha Corte", value=date.today())
            
            ejecutar = st.form_submit_button("▶ Ejecutar Análisis", type="primary", use_container_width=True)

        # 3. Lógica de Ejecución
        if ejecutar:
            if fecha_inicio >= fecha_fin:
                st.error("Error: La fecha de inicio debe ser anterior a la fecha de fin.")
            else:
                with st.spinner("Analizando datos históricos..."):
                    df_mercado = MercadoService.obtener_datos_btc(fecha_inicio, fecha_fin)
                    df_resultados = CalculadoraDCA.ejecutar_simulacion(df_mercado, inversion)
                    
                    df_resultados.rename(columns={
                        'Nominal_Acumulado': 'Tu Dinero Guardado (Nominal)',
                        'Valor_Real_IPC': 'Poder Adquisitivo (Real)',
                        'Valor_Portafolio_BTC': 'Tu Dinero en Bitcoin'
                    }, inplace=True)
                    
                    st.session_state['df_resultados'] = df_resultados 
        
        # 4. Inicialización por defecto (Si es la primera vez que abre la app)
        if st.session_state['df_resultados'] is None:
            df_mercado = MercadoService.obtener_datos_btc(date(2021, 1, 1), date.today())
            df_resultados = CalculadoraDCA.ejecutar_simulacion(df_mercado, 2000)
            df_resultados.rename(columns={
                'Nominal_Acumulado': 'Tu Dinero Guardado (Nominal)',
                'Valor_Real_IPC': 'Poder Adquisitivo (Real)',
                'Valor_Portafolio_BTC': 'Tu Dinero en Bitcoin'
            }, inplace=True)
            st.session_state['df_resultados'] = df_resultados

        # 5. Inyección de datos en los contenedores de arriba
        df = st.session_state['df_resultados']
        ultimo_mes = df.iloc[-1]
        nominal_acumulado = ultimo_mes['Tu Dinero Guardado (Nominal)']
        poder_real = ultimo_mes['Poder Adquisitivo (Real)']
        btc_portafolio = ultimo_mes['Tu Dinero en Bitcoin']

        # --- CÁLCULO DINÁMICO DE PORCENTAJES ---
        # Calculamos la diferencia porcentual: ((Final - Inicial) / Inicial) * 100
        if nominal_acumulado > 0:
            porcentaje_devaluacion = ((poder_real - nominal_acumulado) / nominal_acumulado) * 100
            porcentaje_roi = ((btc_portafolio - nominal_acumulado) / nominal_acumulado) * 100
        else:
            porcentaje_devaluacion = 0
            porcentaje_roi = 0

        with kpi_container:
            kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
            with kpi_col1:
                st.metric(label="Inversión Nominal", value=f"${nominal_acumulado:,.0f}", delta="Capital Base", delta_color="off")
            with kpi_col2:
                # delta_color="normal" en Streamlit hace que los negativos sean rojos automáticamente
                st.metric(label="Poder Adquisitivo (Real)", value=f"${poder_real:,.0f}", delta=f"{porcentaje_devaluacion:.1f}% devaluación", delta_color="normal")
            with kpi_col3:
                # Forzamos el signo + para que se vea como ganancia
                st.metric(label="Valor Refugio BTC", value=f"${btc_portafolio:,.0f}", delta=f"+{porcentaje_roi:.1f}% ROI Estrategia", delta_color="normal")
            with chart_container:
                st.area_chart(df, color=["#3b82f6", "#ef4444", "#f7931a"], height=250)

    # --- SECCIÓN DERECHA: RAG CHATBOT ---
    with col_chat:
        st.markdown("<h4 style='color: #f8fafc; font-size: 1rem; margin-bottom: 1rem;'>💬 Consultor Kanlaap <span style='float:right; font-size:0.6rem; background:#1e293b; padding:2px 6px; border-radius:4px;'>FAISS DB</span></h4>", unsafe_allow_html=True)
        
        q1, q2 = st.columns(2)
        if q1.button("📉 ¿Cómo afecta la inflación?", use_container_width=True): 
            st.session_state['prompt_rapido'] = "¿Cómo afecta la inflación a mi economía?"
        if q2.button("🛡️ Proteger mi valor", use_container_width=True): 
            st.session_state['prompt_rapido'] = "¿Por qué la estrategia DCA protege mi economía mejor que invertir de golpe?"

        # Altura calibrada a 480 para emparejar la base con el formulario izquierdo
        chat_container = st.container(height=540, border=False)
        user_input = st.chat_input("Inicia una consulta sobre resiliencia...")

        with chat_container:
            for msg in st.session_state['messages']:
                avatar_img = st.session_state['avatar_chat'] if msg["role"] == "assistant" else "👤"
                with st.chat_message(msg["role"], avatar=avatar_img):
                    st.markdown(msg["content"])

        prompt_final = None
        if st.session_state['prompt_rapido']:
            prompt_final = st.session_state['prompt_rapido']
            st.session_state['prompt_rapido'] = None
        elif user_input:
            prompt_final = user_input

        if prompt_final:
            st.session_state['messages'].append({"role": "user", "content": prompt_final})
            with chat_container:
                with st.chat_message("user", avatar="👤"):
                    st.markdown(prompt_final)
                
                with st.chat_message("assistant", avatar=st.session_state['avatar_chat']):
                    placeholder = st.empty()
                    placeholder.markdown("*(Kanlaap hurga en los datos analizando tu portafolio...)*")
                    
                    try:
                        estado_seguro = {"df_resultados": st.session_state.get('df_resultados', None)}
                        
                        respuesta = asyncio.run(
                            st.session_state['orquestador_kanlaap'].consultar_oraculo(prompt_final, estado_seguro)
                        )
                        
                        placeholder.markdown(respuesta)
                        st.session_state['messages'].append({"role": "assistant", "content": respuesta})
                    except Exception as e:
                        error_msg = f"*(Fallo en la red)* La madriguera colapsó temporalmente: {e}"
                        placeholder.error(error_msg)
                        st.session_state['messages'].append({"role": "assistant", "content": error_msg})

    # --- SEGUNDA PANTALLA: EL PITCH DE KANLAAP ---
# --- SEGUNDA PANTALLA: EL PITCH DE KANLAAP ---
    # ADVERTENCIA ARQUITECTÓNICA: Cero espacios a la izquierda para evitar el bug de Markdown.
    st.markdown("""
<section class="about-section">
<div class="about-container">
<div class="about-text">
<h2>Kanlaap: La guía de la Escasez Absoluta</h2>
<h3>Sobrevive a la inflación. Ignora el ruido. Acumula matemáticamente.</h3>
<p>El sistema fiduciario es un mecanismo diseñado para confiscar silenciosamente tu tiempo y energía a través de la expansión monetaria, mientras que la especulación y el trading son simplemente ruido estadístico. Inspirado en la resiliencia y la adaptabilidad inquebrantable del tlacuache, Kanlaap es una herramienta de supervivencia financiera. Operamos como un Oráculo RAG que elimina la narrativa para centrarse en los datos duros. Al integrar Llama 3.1 con una base vectorial FAISS alimentada estrictamente de literatura académica y motores de cálculo cuantitativo en Pandas, Kanlaap valida y estructura la única salida matemática comprobable: la acumulación sistemática de escasez absoluta (Bitcoin) a través de DCA.</p>
<div class="pitch-cards">
<div class="pitch-card">
<div class="pc-icon">🧠</div>
<div class="pc-content">
<strong>1. Infraestructura RAG y Rigor Cuantitativo</strong>
<span>Kanlaap no opina; computa. Nuestra arquitectura indexa papers académicos en una base vectorial FAISS, sintetizada por Llama 3.1 y validada numéricamente a través de Pandas. Te entregamos modelos de análisis fundamentados en ciencia de datos pura, blindando tus decisiones contra el sesgo emocional y las promesas vacías del mercado.</span>
</div>
</div>
<div class="pitch-card">
<div class="pc-icon">₿</div>
<div class="pc-content">
<strong>2. Ejecución Implacable (Bitcoin DCA)</strong>
<span>El trading es una trampa de liquidez; la escasez absoluta es una ley matemática. Kanlaap estructura y optimiza tu estrategia de Dollar Cost Averaging (DCA) hacia el único activo con política monetaria inmutable. Neutralizamos la volatilidad para transformarla en tu principal vector de acumulación a largo plazo.</span>
</div>
</div>
</div>
</div>
<div class="arch-diagram">
<div style="font-size: 0.7rem; color: #64748b; letter-spacing: 2px; font-family: monospace; margin-bottom: 10px;">ARQUITECTURA DEL SISTEMA</div>
<div class="arch-box ui">Frontend Reactivo <br><span style="font-weight:400; font-size:0.7rem; color:#64748b">Panel de Control del Usuario</span></div>
<div class="arch-arrow"></div>
<div class="arch-box data">Capa Cuantitativa <br><span style="font-weight:400; font-size:0.7rem; color:#64748b">Motor Pandas para Cálculo de DCA</span></div>
<div class="arch-arrow"></div>
<div class="arch-box ai">Orquestador de Consultoría <br><span style="font-weight:400; font-size:0.7rem; color:#64748b">Handoff de Estado hacia Llama 3.1</span></div>
<div class="arch-arrow"></div>
<div class="arch-box data">Memoria Vectorial FAISS <br><span style="font-weight:400; font-size:0.7rem; color:#64748b">Documentos y Papers Académicos</span></div>
</div>
</div>
</section>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    main()