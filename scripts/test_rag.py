"""
Script para probar el sistema RAG
"""
from src.rag.rag_system import RAGSystem

# IDs de las carpetas creadas
FOLDER_IDS = {
    'root': '1KP3SAVqKQgSTUjxVPHHZehFwLGvdBiX3',
    'actas': '1C_8aXf2IBuJ-5JbHoL0uOXKMtqZn00VR',
    'resoluciones': '1KW_t-T695B-d-9lVrpBMfzaq5xNCX6uC',
    'notificaciones': '1Tj9SGOA5OUz-NUFYT5y-wnLdgyoC8zqG',
    'otros': '1QxDwnLsKvGJL8hYPIVerusNX56zgIptg'
}

def main():
    """Función principal"""
    print("\n=== Probando sistema RAG con Resoluciones ===\n")
    
    # Inicializar sistema
    rag = RAGSystem()
    
    # Convertir PDF a Google Docs
    pdf_id = '1rsyb0-9QuD183oIk7SkSyD6DU7q2KOdg'
    print("\nConvirtiendo PDF a Google Docs...")
    doc_id = rag.document_processor.convert_pdf_to_doc(pdf_id)
    
    if doc_id:
        print(f"✓ PDF convertido a Google Docs (ID: {doc_id})")
        
        # Procesar documento
        print("\nProcesando documento...")
        doc = rag.document_processor.get_document_content(doc_id)
        
        if doc:
            # Indexar documento
            print("\nIndexando documento...")
            rag.retriever.index_documents([doc])
            print("✓ Documento indexado exitosamente")
        else:
            print("⚠ Error al procesar documento")
    else:
        print("⚠ Error al convertir PDF")
    
    # Realizar algunas búsquedas de prueba
    queries = [
        "¿Cuáles son los antecedentes principales del caso?",
        "¿Qué decidió el tribunal?",
        "¿Cuáles fueron los argumentos de las partes?",
        "¿Qué leyes o normativas se mencionan?"
    ]
    
    print("\nRealizando búsquedas de prueba:")
    
    for query in queries:
        print(f"\nBúsqueda: {query}")
        print("-" * 50)
        
        # Buscar documentos
        results = rag.search(query, top_k=3)
        
        if results:
            print(rag.format_search_results(results))
        else:
            print("No se encontraron resultados")
    
    print("\n=== Prueba completada ===")

if __name__ == '__main__':
    main()
