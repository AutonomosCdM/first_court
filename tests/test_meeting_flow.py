"""
Test del flujo completo de una audiencia: Meet -> Docs -> PDF
"""
from src.integrations.google_meet import GoogleMeetClient
from src.integrations.google_docs import GoogleDocsClient
from datetime import datetime, timedelta
import json
import os

def test_complete_hearing_flow():
    """
    Prueba el flujo completo de una audiencia:
    1. Crear reunión en Meet
    2. Generar documento en Docs
    3. Exportar a PDF
    4. Verificar referencias cruzadas
    """
    print("\n=== Iniciando prueba de flujo completo de audiencia ===")
    
    # Datos de prueba
    case_data = {
        'id': 'TEST-2025-001',
        'tipo': 'Audiencia Preparatoria',
        'materia': 'Civil',
        'description': 'Caso de prueba para integración'
    }
    
    participants = [
        {'email': 'cesar@autonomos.dev', 'role': 'Juez'},
        {'email': 'tamara@autonomos.dev', 'role': 'Defensor'},
        {'email': 'secretary@autonomos.dev', 'role': 'Secretario'}
    ]
    
    try:
        # 1. Crear reunión en Meet
        print("\n1. Creando reunión en Google Meet...")
        meet_client = GoogleMeetClient()
        start_time = datetime.now() + timedelta(hours=1)
        
        meeting = meet_client.create_meeting(
            title=f"Audiencia {case_data['id']} - {case_data['tipo']}",
            start_time=start_time,
            duration_minutes=60,
            participants=participants,
            case_data=case_data
        )
        
        print(f"✓ Reunión creada: {meeting['meet_link']}")
        
        # 2. Crear documento en Google Docs
        print("\n2. Creando documento en Google Docs...")
        docs_client = GoogleDocsClient()
        
        document = docs_client.create_document(
            title=f"Acta - {case_data['id']} - {case_data['tipo']}",
            template_id=os.getenv('TEMPLATE_ACTA_ID'),  # ID del template de acta
            metadata={
                'case_id': case_data['id'],
                'hearing_type': case_data['tipo'],
                'meet_link': meeting['meet_link'],
                'creation_date': datetime.now().isoformat()
            }
        )
        
        print(f"✓ Documento creado: {document['webViewLink']}")
        
        # 3. Exportar a PDF
        print("\n3. Exportando a PDF...")
        pdf = docs_client.export_to_pdf(
            doc_id=document['id']
        )
        
        print(f"✓ PDF creado: {pdf['webViewLink']}")
        
        # 4. Crear referencias cruzadas
        print("\n4. Creando referencias cruzadas...")
        link = docs_client.create_document_link(
            doc_id=pdf['id'],
            source_doc_id=document['id']
        )
        
        print("✓ Referencias creadas entre documentos")
        
        # 5. Verificar estado final
        print("\n5. Verificando estado final...")
        
        # Verificar reunión
        meeting_status = meet_client.get_meeting_status(meeting['event_id'])
        assert meeting_status['status'] == 'confirmed', "La reunión debe estar confirmada"
        
        print("\n=== Resumen de la prueba ===")
        print(f"Caso: {case_data['id']}")
        print(f"Tipo: {case_data['tipo']}")
        print(f"Meet Link: {meeting['meet_link']}")
        print(f"Documento: {document['webViewLink']}")
        print(f"PDF: {pdf['webViewLink']}")
        print("\n✓ Prueba completada exitosamente!")
        
        # Guardar información para referencia
        test_info = {
            'case_data': case_data,
            'meeting': meeting,
            'document': document,
            'pdf': pdf,
            'timestamp': datetime.now().isoformat()
        }
        
        with open(f"test_results_{case_data['id']}.json", 'w') as f:
            json.dump(test_info, f, indent=2)
            
    except Exception as e:
        print(f"\n❌ Error durante la prueba: {str(e)}")
        raise e

if __name__ == "__main__":
    test_complete_hearing_flow()
