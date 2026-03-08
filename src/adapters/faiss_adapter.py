import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List

class FaissLocalAdapter:
    def __init__(self, docs_dir: str = "docs", dimension: int = 384): 
        self.docs_dir = docs_dir
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        
        # Modelo ultra ligero para no provocar swapping en los 12GB de RAM
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')

    def cargar_e_indexar_directorio(self):
        """Lee los .txt de la carpeta docs/ y los vectoriza en memoria."""
        textos = []
        
        if not os.path.exists(self.docs_dir):
            os.makedirs(self.docs_dir)
            print(f"Directorio {self.docs_dir} creado. Añade documentos de contexto aquí.")
            return

        for filename in os.listdir(self.docs_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.docs_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    textos.append(f.read())
        
        if not textos:
            return # Falla silenciosa si no hay documentos 

        # Generar embeddings localmente
        embeddings = self.encoder.encode(textos)
        
        # Insertar en FAISS
        self.index.add(np.array(embeddings).astype('float32'))
        self.documents.extend(textos)

    def buscar_contexto(self, query: str, k: int = 2) -> str:
        """Convierte la pregunta a vector y busca en el índice local."""
        if self.index.ntotal == 0:
            return "El oráculo no tiene documentos indexados en docs/."
            
        query_embedding = self.encoder.encode([query])
        distancias, indices = self.index.search(np.array(query_embedding).astype('float32'), k)
        
        fragmentos = [self.documents[idx] for idx in indices[0] if idx != -1]
        return "\n---\n".join(fragmentos)