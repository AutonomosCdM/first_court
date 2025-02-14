"""
Script de prueba para la gestión de audiencias por parte del SecretaryAgent
"""
from src.agents.secretary import SecretaryAgent
from datetime import datetime, timedelta
import time

def test_hearing_management():
    # Crear instancia del secretario
    secretary = SecretaryAgent()
    
    # Datos de prueba para un caso
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
    
    # 1. Agendar una audiencia
    print("\n1. Agendando audiencia inicial...")
    result = secretary.schedule_hearing(
        case_data=case_data,
        title="Audiencia Preparatoria",
        preferred_date=datetime.now() + timedelta(days=1),
        duration_minutes=60,
        description="Primera audiencia del caso",
        virtual=True
    )
    
    if "error" not in result:
        event_id = result.get('id')
        print(f"Audiencia agendada exitosamente:")
        print(f"ID del evento: {event_id}")
        print(f"Enlace Meet: {result.get('hangoutLink', 'No disponible')}")
        print(f"Hora inicio: {result.get('start', {}).get('dateTime')}")
        
        # Esperar un momento para que los correos se envíen
        time.sleep(2)
        
        # 2. Reagendar la audiencia
        print("\n2. Reagendando audiencia para una semana después...")
        new_date = datetime.now() + timedelta(days=7)
        result = secretary.reschedule_hearing(
            case_data=case_data,
            event_id=event_id,
            new_date=new_date
        )
        
        if "error" not in result:
            print(f"Audiencia reagendada exitosamente para: {result.get('start', {}).get('dateTime')}")
            
            # Esperar un momento para que los correos se envíen
            time.sleep(2)
            
            # 3. Cancelar la audiencia
            print("\n3. Cancelando audiencia...")
            result = secretary.cancel_hearing(
                case_data=case_data,
                event_id=event_id
            )
            
            if "error" not in result:
                print("Audiencia cancelada exitosamente")
            else:
                print(f"Error al cancelar audiencia: {result['error']}")
        else:
            print(f"Error al reagendar audiencia: {result['error']}")
    else:
        print(f"Error al agendar audiencia: {result['error']}")

if __name__ == "__main__":
    test_hearing_management()
