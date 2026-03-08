import asyncio
from typing import Dict, Any
from src.adapters.faiss_adapter import FaissLocalAdapter
from src.adapters.groq_adapter import GroqAsyncAdapter

class KanlaapOrchestrator:
    def __init__(self):
        """
        Inicialización perezosa (Lazy Loading).
        Instanciamos los adaptadores al crear el orquestador para inyectar las dependencias.
        """
        print("[Sistema] Iniciando red neuronal de Kanlaap...")
        self.vector_db = FaissLocalAdapter(docs_dir="docs")
        self.llm_engine = GroqAsyncAdapter()
        
        # Cargar documentos a la memoria RAM en el arranque
        self.vector_db.cargar_e_indexar_directorio()
        print("[Sistema] Base vectorial indexada localmente.")

    async def consultar_oraculo(self, mensaje_usuario: str, estado_streamlit: Dict[str, Any]) -> str:
        """
        Flujo de ejecución principal del RAG asíncrono.
        """
        # 1. Recuperación Local (Velocidad de CPU, O(N) optimizado)
        # Extraemos solo el top 2 de fragmentos para no saturar la ventana de contexto de Groq.
        contexto_rag = self.vector_db.buscar_contexto(query=mensaje_usuario, k=2)

        # 2. Extracción y Formateo de Métricas Estáticas (Protegiendo st.session_state)
        # Extraemos los datos calculados por Pandas en la capa de dominio sin romper la inmutabilidad.
        metricas_texto = "Métricas actuales no disponibles."
        if 'df_resultados' in estado_streamlit and estado_streamlit['df_resultados'] is not None:
            df = estado_streamlit['df_resultados']
            # Evitamos bucles for; usamos agregaciones directas de Pandas
            total_invertido = df['Inversion_Acumulada'].max() if 'Inversion_Acumulada' in df else 0
            valor_actual = df['Valor_Portafolio'].max() if 'Valor_Portafolio' in df else 0
            
            metricas_texto = (
                f"Total Invertido (DCA): {total_invertido:.2f} MXN\n"
                f"Valor de la Cartera Hoy: {valor_actual:.2f} MXN\n"
                f"NOTA: Evalúa siempre cómo afecta la inflación a tus finanzas a largo plazo."
            )

        # 3. Delegación Asíncrona 
        # Hacemos await para ceder el control al event loop mientras esperamos la API de Groq.
        respuesta_tlacuache = await self.llm_engine.generar_respuesta(
            pregunta=mensaje_usuario,
            contexto_documental=contexto_rag,
            metricas_financieras=metricas_texto
        )

        return respuesta_tlacuache