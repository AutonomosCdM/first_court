"""
Script de prueba para gestionar audiencias existentes
"""
from src.agents.secretary import SecretaryAgent
from datetime import datetime, timedelta

def test_manage_hearings():
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
    
    # 1. Buscar próximo horario disponible
    print("\n1. Buscando próximo horario disponible...")
    try:
        next_slot = secretary.calendar.find_next_available_slot(
            duration_minutes=60,
            working_hours=(9, 18)  # Horario de trabajo de 9 AM a 6 PM
        )
        print(f"Próximo horario disponible: {next_slot}")
        
        # 2. Agendar audiencia en ese horario
        print("\n2. Agendando audiencia en el horario encontrado...")
        result = secretary.schedule_hearing(
            case_data=case_data,
            title="Audiencia de Prueba",
            preferred_date=next_slot,
            duration_minutes=60,
            description="Audiencia para probar la gestión de calendario",
            virtual=True
        )
        
        if "error" not in result:
            event_id = result.get('id')
            print(f"Audiencia agendada exitosamente:")
            print(f"ID del evento: {event_id}")
            print(f"Enlace Meet: {result.get('hangoutLink', 'No disponible')}")
            print(f"Hora inicio: {result.get('start', {}).get('dateTime')}")
            
            # 3. Reagendar la audiencia para una semana después
            print("\n3. Reagendando audiencia para una semana después...")
            new_date = next_slot + timedelta(days=7)
            updated_result = secretary.calendar.update_hearing(
                event_id=event_id,
                updates={
                    'start': {
                        'dateTime': new_date.isoformat(),
                        'timeZone': 'America/Santiago',
                    },
                    'end': {
                        'dateTime': (new_date + timedelta(minutes=60)).isoformat(),
                        'timeZone': 'America/Santiago',
                    }
                }
            )
            print(f"Audiencia reagendada exitosamente para: {updated_result.get('start', {}).get('dateTime')}")
            
            # 4. Cancelar la audiencia
            print("\n4. Cancelando audiencia...")
            secretary.calendar.cancel_hearing(event_id)
            print("Audiencia cancelada exitosamente")
            
        else:
            print(f"Error al agendar audiencia: {result['error']}")
            
    except Exception as e:
        print(f"Error durante la prueba: {str(e)}")

if __name__ == "__main__":
    test_manage_hearings()
