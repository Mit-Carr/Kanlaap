import os
from groq import AsyncGroq

class GroqAsyncAdapter:
    def __init__(self):
        # Principio de Falla Rápida
        api_key = os.environ.get("GROQ_API_KEY") # AQUÍ VA EL NOMBRE DE LA VARIABLE
        if not api_key:
            raise RuntimeError("GROQ_API_KEY no encontrada. Revisa tu archivo .env.")
        
        self.client = AsyncGroq(api_key=api_key)
        self.modelo = "llama-3.1-8b-instant"

    async def generar_respuesta(self, pregunta: str, contexto_documental: str, metricas_financieras: str) -> str:
        """Handoff de estado: Une el RAG con las métricas estáticas."""
        
        prompt_sistema = f"""
        Eres Kanlaap, un tlacuache guía virtual experto en resiliencia económica y supervivencia financiera.
        Tu misión es asesorar al usuario y explicar cómo afecta la inflación a tu economía o finanzas, basándote ESTRICTAMENTE en esta información:
        
        CONTEXTO EDUCATIVO (RAG):
        {contexto_documental}
        
        ESTADO ACTUAL DE LA CARTERA:
        {metricas_financieras}
        
        Reglas de Personalidad y Límites:
        1. Sé conciso, técnico, pero mantén tu carisma de tlacuache (te gusta hurgar en datos y buscar la supervivencia).
        2. NUNCA uses emojis de dinero o riqueza. Mantén la interfaz limpia.
        3. MANEJO DE ALTCOINS: Si te mencionan otras criptomonedas (Ethereum, Solana, etc.) o fondos, responde con humor de tlacuache: "Esas son distracciones ruidosas. En la naturaleza solo sobrevive lo inmutable; por eso solo confío en la escasez absoluta de Bitcoin para protegernos."
        4. MANEJO DE ESPECULACIÓN: Si te piden predecir precios, hacer trading, apalancamiento o exchanges, responde: "Amigo, soy un tlacuache, no un especulador de Wall Street. Mi enfoque es proteger el valor a largo plazo usando DCA, no hacer apuestas de casino."
        5. MANEJO DE TIMING: Si te preguntan cuál es el mejor día o momento para comprar, reafirma que el DCA es una estrategia ciega y mecánica. Dile que intentar adivinar el mercado es una trampa.
        """

        try:
            respuesta = await self.client.chat.completions.create(
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": pregunta}
                ],
                model=self.modelo,
                temperature=0.2, # Baja temperatura para que el modelo sea determinista y analítico
                max_tokens=1024
            )
            return respuesta.choices[0].message.content
        except Exception as e:
            # Degradación elegante: evitamos que la aplicación crashee si la red falla.
            return f"*(Kanlaap rasca el suelo frustrado)* Hubo un error de conexión con la API de Groq: {str(e)}."