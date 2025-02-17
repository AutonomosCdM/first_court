"""
Sistema RAG completo para el Tribunal Autónomo
"""
from typing import List, Dict, Optional
from src.rag.document_processor import DocumentProcessor
from src.rag.retriever import DocumentRetriever
from src.auth.oauth_client import OAuth2Client

class RAGSystem:
    """Sistema RAG para procesamiento y recuperación de documentos judiciales"""
    
    def __init__(self):
        """Inicializa el sistema RAG"""
        self.document_processor = DocumentProcessor()
        self.retriever = DocumentRetriever()
        self.oauth_client = OAuth2Client()
        self.drive_service = self.oauth_client.drive
        self.indexed_docs = set()
    
    def index_folder(self, folder_id: str):
        """
        Indexa todos los documentos en una carpeta de Drive
        
        Args:
            folder_id: ID de la carpeta en Google Drive
        """
        try:
            # Listar archivos en la carpeta
            results = self.drive_service.files().list(
                q=f"'{folder_id}' in parents and mimeType='application/vnd.google-apps.document'",
                fields="files(id, name)"
            ).execute()
            
            files = results.get('files', [])
            doc_ids = [file['id'] for file in files]
            
            # Procesar documentos
            documents = self.document_processor.process_document_batch(doc_ids)
            
            # Indexar documentos
            self.retriever.index_documents(documents)
            
            # Actualizar set de documentos indexados
            self.indexed_docs.update(doc_ids)
            
            print(f"✓ {len(documents)} documentos indexados exitosamente")
            
        except Exception as e:
            print(f"⚠ Error al indexar carpeta: {str(e)}")
    
    def search(self, query: str, top_k: int = 5, search_type: str = 'documents') -> List[Dict]:
        """
        Busca documentos o secciones relevantes
        
        Args:
            query: Consulta de búsqueda
            top_k: Número de resultados a retornar
            search_type: Tipo de búsqueda ('documents' o 'sections')
            
        Returns:
            Lista de resultados relevantes
        """
        if not self.retriever.document_embeddings:
            print("⚠ No hay documentos indexados")
            return []
        
        if search_type == 'documents':
            return self.retriever.search(query, top_k)
        else:
            return self.retriever.search_sections(query, top_k)
    
    def get_document_url(self, doc_id: str) -> str:
        """
        Obtiene la URL de un documento
        
        Args:
            doc_id: ID del documento
            
        Returns:
            URL del documento
        """
        return f"https://docs.google.com/document/d/{doc_id}/edit"
    
    def format_search_results(self, results: List[Dict]) -> str:
        """
        Formatea resultados de búsqueda para visualización
        
        Args:
            results: Lista de resultados de búsqueda
            
        Returns:
            Texto formateado con los resultados
        """
        output = []
        
        for i, result in enumerate(results, 1):
            doc_url = self.get_document_url(result['doc_id'])
            score = result['score'] * 100  # Convertir a porcentaje
            
            output.append(f"\n{i}. {result['metadata']['title']}")
            output.append(f"   Relevancia: {score:.1f}%")
            output.append(f"   Sección: {result['section']['heading']}")
            output.append(f"   URL: {doc_url}")
            output.append(f"   ID: {result['doc_id']}")
            output.append("   " + "-" * 50)
        
        return "\n".join(output)
