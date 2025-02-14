"""
Sistema de recuperación de documentos relevantes
"""
from typing import List, Dict, Optional, Tuple
import numpy as np
from sentence_transformers import util
import torch
from src.rag.embeddings import EmbeddingGenerator

class DocumentRetriever:
    """Recupera documentos relevantes basado en similitud de embeddings"""
    
    def __init__(self):
        """Inicializa el recuperador de documentos"""
        self.embedding_generator = EmbeddingGenerator()
        self.document_embeddings = {}
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    def index_documents(self, documents: List[Dict]):
        """
        Indexa documentos para búsqueda
        
        Args:
            documents: Lista de documentos procesados
        """
        self.document_embeddings = self.embedding_generator.generate_document_embeddings(documents)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Busca documentos relevantes para una consulta
        
        Args:
            query: Consulta de búsqueda
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de documentos relevantes con sus scores
        """
        # Generar embedding para la consulta
        query_embedding = self.embedding_generator.generate_embeddings([query])[0]
        
        results = []
        
        # Buscar en cada documento
        for doc_id, doc_data in self.document_embeddings.items():
            doc_embeddings = doc_data['embeddings']
            
            # Calcular similitud con cada sección
            similarities = util.dot_score(
                torch.tensor([query_embedding]).to(self.device),
                torch.tensor(doc_embeddings).to(self.device)
            )[0]
            
            # Obtener mejores matches
            best_idx = similarities.argsort(descending=True)[0]
            best_score = similarities[best_idx].item()
            best_section = doc_data['sections'][best_idx]
            
            results.append({
                'doc_id': doc_id,
                'score': best_score,
                'section': best_section,
                'metadata': doc_data['metadata']
            })
        
        # Ordenar por score y retornar top_k
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:top_k]
    
    def search_sections(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Busca secciones relevantes para una consulta
        
        Args:
            query: Consulta de búsqueda
            top_k: Número de resultados a retornar
            
        Returns:
            Lista de secciones relevantes con sus scores
        """
        # Generar embedding para la consulta
        query_embedding = self.embedding_generator.generate_embeddings([query])[0]
        
        all_sections = []
        
        # Recopilar todas las secciones
        for doc_id, doc_data in self.document_embeddings.items():
            doc_embeddings = doc_data['embeddings']
            
            # Calcular similitud con cada sección
            similarities = util.dot_score(
                torch.tensor([query_embedding]).to(self.device),
                torch.tensor(doc_embeddings).to(self.device)
            )[0]
            
            # Agregar cada sección con su score
            for idx, (score, section) in enumerate(zip(similarities, doc_data['sections'])):
                all_sections.append({
                    'doc_id': doc_id,
                    'score': score.item(),
                    'section': section,
                    'metadata': doc_data['metadata']
                })
        
        # Ordenar por score y retornar top_k
        all_sections.sort(key=lambda x: x['score'], reverse=True)
        return all_sections[:top_k]
