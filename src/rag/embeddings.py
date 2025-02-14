"""
Generador de embeddings para el sistema RAG
"""
from typing import List, Dict, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

class EmbeddingGenerator:
    """Genera embeddings para documentos usando SentenceTransformers"""
    
    def __init__(self, model_name: str = 'paraphrase-multilingual-mpnet-base-v2'):
        """
        Inicializa el generador de embeddings
        
        Args:
            model_name: Nombre del modelo de SentenceTransformer a usar
        """
        self.model = SentenceTransformer(model_name)
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.model.to(self.device)
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Genera embeddings para una lista de textos
        
        Args:
            texts: Lista de textos
            batch_size: Tamaño del batch para procesamiento
            
        Returns:
            Array de embeddings
        """
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings
    
    def generate_document_embeddings(self, documents: List[Dict]) -> Dict[str, np.ndarray]:
        """
        Genera embeddings para documentos estructurados
        
        Args:
            documents: Lista de documentos procesados
            
        Returns:
            Dict con embeddings por documento
        """
        doc_embeddings = {}
        
        for doc in documents:
            # Generar embeddings por sección
            section_texts = []
            section_metadata = []
            
            for section in doc['content']:
                # Combinar encabezado y contenido
                section_text = f"{section['heading']}\n{section['content']}"
                section_texts.append(section_text)
                section_metadata.append({
                    'heading': section['heading'],
                    'style': section['style']
                })
            
            # Generar embeddings
            embeddings = self.generate_embeddings(section_texts)
            
            # Guardar resultados
            doc_embeddings[doc['doc_id']] = {
                'embeddings': embeddings,
                'sections': section_metadata,
                'metadata': doc['metadata']
            }
        
        return doc_embeddings
