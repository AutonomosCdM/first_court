import pytest
from src.documents.document_processor import LegalDocumentProcessor

def test_legal_document_processor_initialization():
    """Test that the LegalDocumentProcessor can be initialized"""
    processor = LegalDocumentProcessor()
    assert processor is not None

def test_process_markdown_document():
    """Test processing a markdown document"""
    processor = LegalDocumentProcessor()
    test_document = "docs/reportes_casos/caso_1234-2024_20250213_161916.md"
    
    try:
        processed_doc = processor.process_legal_document(test_document)
        
        # Check basic structure of processed document
        assert "format" in processed_doc
        assert "pages" in processed_doc
        assert "content_markdown" in processed_doc
        assert "raw_text" in processed_doc
        
        # Ensure no error occurred
        assert "error" not in processed_doc
    except Exception as e:
        pytest.fail(f"Document processing failed: {str(e)}")

def test_batch_document_processing():
    """Test batch processing of multiple documents"""
    processor = LegalDocumentProcessor()
    test_documents = [
        "docs/reportes_casos/caso_1234-2024_20250213_161916.md",
        "docs/reportes_casos/caso_1234-2024_20250213_163645.md"
    ]
    
    processed_docs = processor.batch_process_documents(test_documents)
    
    assert len(processed_docs) == len(test_documents)
    for doc in processed_docs:
        assert "format" in doc
        assert "raw_text" in doc
