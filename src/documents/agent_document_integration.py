from typing import List, Dict, Any
from src.documents.document_processor import LegalDocumentProcessor

class DocumentAgentAssistant:
    def __init__(self):
        self.document_processor = LegalDocumentProcessor()

    def extract_key_evidence(self, document_path: str) -> Dict[str, Any]:
        """
        Extract key evidence from a document for the Prosecutor
        
        Args:
            document_path (str): Path to the legal document
        
        Returns:
            Dict of extracted key information
        """
        processed_doc = self.document_processor.process_legal_document(document_path)
        
        # Advanced text analysis for evidence extraction
        return {
            "document_summary": self._summarize_document(processed_doc['raw_text']),
            "potential_evidence_keywords": self._extract_evidence_keywords(processed_doc['raw_text']),
            "document_metadata": {
                "format": processed_doc['format'],
                "pages": processed_doc['pages'],
                "file_path": processed_doc['file_path']
            }
        }

    def prepare_case_brief(self, document_paths: List[str]) -> Dict[str, Any]:
        """
        Prepare a comprehensive case brief from multiple documents
        
        Args:
            document_paths (List[str]): List of document paths to process
        
        Returns:
            Comprehensive case brief
        """
        processed_documents = self.document_processor.batch_process_documents(document_paths)
        
        return {
            "total_documents": len(processed_documents),
            "document_summaries": [
                {
                    "file_path": doc['file_path'],
                    "format": doc['format'],
                    "summary": self._summarize_document(doc['raw_text'])
                } for doc in processed_documents
            ],
            "combined_text": " ".join(doc['raw_text'] for doc in processed_documents)
        }

    def _summarize_document(self, text: str, max_length: int = 500) -> str:
        """
        Generate a basic summary of the document text
        
        Args:
            text (str): Full document text
            max_length (int): Maximum summary length
        
        Returns:
            Summarized text
        """
        # Simple summarization by truncating
        return text[:max_length] + "..." if len(text) > max_length else text

    def _extract_evidence_keywords(self, text: str) -> List[str]:
        """
        Extract potential evidence keywords
        
        Args:
            text (str): Document text
        
        Returns:
            List of potential evidence keywords
        """
        # Basic keyword extraction (can be enhanced with NLP techniques)
        legal_keywords = [
            "evidencia", "prueba", "testigo", "declaración", 
            "documento", "fecha", "lugar", "persona", 
            "incidente", "delito"
        ]
        
        # Simple keyword matching
        return [
            keyword for keyword in legal_keywords 
            if keyword.lower() in text.lower()
        ]

    def assist_prosecutor(self, document_path: str) -> Dict[str, Any]:
        """
        Assist Prosecutor with document analysis
        
        Args:
            document_path (str): Path to the legal document
        
        Returns:
            Analysis to support prosecution
        """
        evidence = self.extract_key_evidence(document_path)
        return {
            "potential_charges": self._suggest_charges(evidence),
            "evidence_strength": self._evaluate_evidence_strength(evidence)
        }

    def assist_defender(self, document_path: str) -> Dict[str, Any]:
        """
        Assist Defender with document analysis
        
        Args:
            document_path (str): Path to the legal document
        
        Returns:
            Analysis to support defense
        """
        evidence = self.extract_key_evidence(document_path)
        return {
            "potential_defense_strategies": self._suggest_defense_strategies(evidence),
            "evidence_weaknesses": self._identify_evidence_weaknesses(evidence)
        }

    def _suggest_charges(self, evidence: Dict[str, Any]) -> List[str]:
        """
        Suggest potential charges based on evidence
        
        Args:
            evidence (Dict): Extracted evidence
        
        Returns:
            List of potential charges
        """
        # Basic charge suggestion logic
        keywords = evidence.get('potential_evidence_keywords', [])
        suggested_charges = []
        
        if any(kw in keywords for kw in ["delito", "crimen"]):
            suggested_charges.append("Investigación criminal")
        
        return suggested_charges

    def _evaluate_evidence_strength(self, evidence: Dict[str, Any]) -> str:
        """
        Evaluate the strength of the evidence
        
        Args:
            evidence (Dict): Extracted evidence
        
        Returns:
            Evidence strength rating
        """
        keywords_count = len(evidence.get('potential_evidence_keywords', []))
        
        if keywords_count > 5:
            return "Fuerte"
        elif keywords_count > 2:
            return "Moderado"
        else:
            return "Débil"

    def _suggest_defense_strategies(self, evidence: Dict[str, Any]) -> List[str]:
        """
        Suggest potential defense strategies
        
        Args:
            evidence (Dict): Extracted evidence
        
        Returns:
            List of potential defense strategies
        """
        # Basic defense strategy suggestion
        strategies = []
        
        if evidence.get('document_metadata', {}).get('pages', 0) < 2:
            strategies.append("Insuficiencia de pruebas")
        
        return strategies

    def _identify_evidence_weaknesses(self, evidence: Dict[str, Any]) -> List[str]:
        """
        Identify potential weaknesses in the evidence
        
        Args:
            evidence (Dict): Extracted evidence
        
        Returns:
            List of evidence weaknesses
        """
        weaknesses = []
        
        if len(evidence.get('potential_evidence_keywords', [])) < 3:
            weaknesses.append("Evidencia circumstancial")
        
        return weaknesses

# Example usage
if __name__ == "__main__":
    assistant = DocumentAgentAssistant()
    
    # Example document processing for prosecution
    test_document = "docs/reportes_casos/caso_1234-2024_20250213_161916.md"
    prosecutor_analysis = assistant.assist_prosecutor(test_document)
    print("Prosecutor Analysis:", prosecutor_analysis)
    
    defender_analysis = assistant.assist_defender(test_document)
    print("Defender Analysis:", defender_analysis)
