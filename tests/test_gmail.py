"""
Script de prueba para la integración con Gmail
"""
from src.integrations.gmail import GmailClient
from datetime import datetime, timedelta

def test_email_notifications():
    # Crear instancia del cliente de Gmail
    gmail = GmailClient()
    
    # Datos de prueba
    case_data = {
        "id": "2024-001",
        "tipo": "Civil",
        "materia": "Cobro de Pesos",
        "participantes": [
            {
                "nombre": "César",
                "rol": "Juez",
                "email": "cesar@autonomos.dev"
            },
            {
                "nombre": "Tamara",
                "rol": "Defensora",
                "email": "tamara@autonomos.dev"
            }
        ]
    }
    
    # Datos de la audiencia
    hearing_data = {
        "title": "Audiencia Preparatoria",
        "datetime": (datetime.now() + timedelta(days=7)).isoformat(),
        "virtual": True,
        "meet_link": "https://meet.google.com/abc-defg-hij"
    }
    
    # Lista de destinatarios
    recipients = ["cesar@autonomos.dev", "tamara@autonomos.dev"]
    
    print("\n1. Enviando notificación de audiencia programada...")
    result = gmail.send_hearing_notification(
        to=recipients,
        case_data=case_data,
        hearing_data=hearing_data,
        notification_type='scheduled'
    )
    print(f"Resultado: {result}")
    
    # Simular cambio de fecha
    hearing_data["datetime"] = (datetime.now() + timedelta(days=14)).isoformat()
    
    print("\n2. Enviando notificación de audiencia reagendada...")
    result = gmail.send_hearing_notification(
        to=recipients,
        case_data=case_data,
        hearing_data=hearing_data,
        notification_type='rescheduled'
    )
    print(f"Resultado: {result}")
    
    print("\n3. Enviando notificación de audiencia cancelada...")
    result = gmail.send_hearing_notification(
        to=recipients,
        case_data=case_data,
        hearing_data=hearing_data,
        notification_type='cancelled'
    )
    print(f"Resultado: {result}")

if __name__ == "__main__":
    test_email_notifications()
