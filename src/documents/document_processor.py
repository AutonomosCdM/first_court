from docling.document_converter import DocumentConverter
from typing import List, Dict, Any
import os

class LegalDocumentProcessor:
    def __init__(self):
        self.converter = DocumentConverter()

    def process_legal_document(self, document_path: str) -> Dict[str, Any]:
        """
        Process a legal document and extract key information
        
        Args:
            document_path (str): Path to the legal document
        
        Returns:
            Dict containing processed document information
        """
        try:
            # Special handling for markdown files
            if document_path.lower().endswith('.md'):
                with open(document_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
                
                return {
                    "format": "md",
                    "pages": 1,
                    "content_markdown": raw_text,
                    "raw_text": raw_text,
                    "file_path": document_path
                }
            
            # Convert other document types
            result = self.converter.convert(document_path)
            
            # Extract markdown content
            markdown_content = result.document.export_to_markdown()
            
            # Basic metadata extraction
            return {
                "format": os.path.splitext(document_path)[1].lstrip('.'),
                "pages": len(result.document.pages) if hasattr(result.document, 'pages') else 1,
                "content_markdown": markdown_content,
                "raw_text": result.document.text,
                "file_path": document_path
            }
        except Exception as e:
            return {
                "error": str(e),
                "document_path": document_path
            }

    def batch_process_documents(self, document_paths: List[str]) -> List[Dict[str, Any]]:
        """
        Process multiple legal documents
        
        Args:
            document_paths (List[str]): List of document paths
        
        Returns:
            List of processed document information
        """
        return [self.process_legal_document(doc_path) for doc_path in document_paths]

# Example usage
if __name__ == "__main__":
    processor = LegalDocumentProcessor()
    
    # Example document processing
    test_document = "docs/reportes_casos/caso_1234-2024_20250213_161916.md"
    processed_doc = processor.process_legal_document(test_document)
    print(processed_doc)
