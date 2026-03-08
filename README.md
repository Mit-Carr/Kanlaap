<p align="center">
  <img src="assets/logo.png" width="200" alt="Logo del Proyecto">
  <h1 align="center">Kanlaap:</h1>
  <p align="center">Motor Cuantitativo RAG para Resiliencia Financiera.</p>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white" />
  <img src="https://img.shields.io/badge/Groq_IA-000000?style=for-the-badge&logo=lightning&logoColor=orange" />
  <img src="https://img.shields.io/badge/Groq_Cloud-F55036?style=for-the-badge&logo=lightning&logoColor=white" />
  <img src="https://img.shields.io/badge/Llama_3.1-0668E1?style=for-the-badge&logo=meta&logoColor=white" />
  <img src="https://img.shields.io/badge/FAISS_DB-0055FF?style=for-the-badge&logo=meta&logoColor=white" />
</p>


---
**Kanlaap** es una plataforma analítica y consultor interactivo impulsado por Inteligencia Artificial. Diseñado para contrastar empíricamente la devaluación del dinero fiduciario (fiat) frente a la escasez algorítmica de Bitcoin, el sistema combina análisis de datos históricos en tiempo real con un motor RAG (Retrieval-Augmented Generation).
Arquitectura Matemática (Motor Cuantitativo)

El dashboard no se basa en proyecciones especulativas, sino en el procesamiento de series de tiempo históricas utilizando `pandas` y `numpy`. Las simulaciones financieras operan bajo dos modelos matemáticos principales:

1. Modelo de Acumulación Constante (DCA)
La estrategia de *Dollar Cost Averaging* (DCA) mitiga la volatilidad de los activos asimétricos. El cálculo iterativo de acumulación de Bitcoin se define mediante la siguiente sumatoria:

$$BTC_{total} = \sum_{t=1}^{n} \frac{I_t}{P_t}$$

Donde:
* $I_t$ representa la inversión fiat de capital fijo en el periodo $t$.
* $P_t$ es el precio de mercado de BTC extraído en el periodo $t$.
* $n$ es el número total de periodos (días, semanas o meses) de la simulación.

2. Depreciación del Poder Adquisitivo (Inflación Fiat)
Para medir el costo de oportunidad de mantener efectivo, el sistema calcula la pérdida de valor real (poder de compra) aplicando el histórico de inflación compuesta:

$$V_{real} = V_{nominal} \prod_{t=1}^{n} \left( 1 - i_t \right)$$

Donde $V_{nominal}$ es el capital inicial no invertido y $i_t$ es la tasa de inflación fraccionaria correspondiente al periodo $t$.

---

Arquitectura RAG (Retrieval-Augmented Generation)

Para eliminar las "alucinaciones" inherentes a los Modelos de Lenguaje Grande (LLMs) en temas financieros, Kanlaap implementa una arquitectura RAG asíncrona que fundamenta cada respuesta en una base de conocimiento curada sobre fundamentos económicos e ingeniería de Bitcoin.


Flujo del Orquestador IA:
1.  **Ingesta y Vectorización:** Los documentos técnicos y económicos son procesados y transformados en *embeddings* de alta dimensionalidad utilizando el modelo `sentence-transformers` de HuggingFace.
2.  **Búsqueda Semántica (FAISS):** Los vectores se almacenan en un índice **FAISS (Facebook AI Similarity Search)**. Cuando el usuario realiza una consulta, el sistema realiza una búsqueda de vecinos más cercanos (K-Nearest Neighbors) utilizando similitud del coseno o distancia L2:
    $$d(q, v) = 1 - \frac{q \cdot v}{\|q\| \|v\|}$$
    *(Donde $q$ es el vector de la pregunta y $v$ es el vector del documento).*
3.  **Inferencia de Baja Latencia (Groq):** El contexto recuperado se inyecta en un *prompt* estructurado y se procesa a través de la API asíncrona de **Groq** utilizando el modelo **Llama 3.1**, garantizando tiempos de respuesta casi instantáneos.

---
Stack Tecnológico

* **Frontend & UI:** Streamlit (Python)
* **Procesamiento Cuantitativo:** Pandas, Numpy, yFinance
* **Base de Datos Vectorial:** FAISS (CPU-optimized)
* **Modelos de Inferencia (LLM):** Llama 3.1 (via Groq API)
* **Embeddings:** LangChain, Sentence-Transformers

---
Despliegue Local

Para auditar el código fuente e instanciar el motor RAG localmente:

1. Clona el repositorio: 
```bash
   git clone https://github.com/Mit-Carr/Kanlaap.git
   ```
2. Instala las dependencias:
```bash
   pip install -r requirements.txt
  ```
3. Configura tus variables de entorno en un archivo .env:
  ```bash
   GROQ_API_KEY=tu_clave_aqui
  ```
4. Ejecuta el orquestador:
  ```bash
   streamlit run app.py
  ```
p.py
