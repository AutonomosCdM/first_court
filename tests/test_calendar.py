"""
Script de prueba para la integración con Google Calendar
"""
from src.agents.secretary import SecretaryAgent
from datetime import datetime, timedelta

def test_schedule_hearing():
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
    
    # Programar audiencia para mañana a las 10:00
    tomorrow = datetime.now() + timedelta(days=1)
    hearing_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0)
    
    # Agendar la audiencia
    result = secretary.schedule_hearing(
        case_data=case_data,
        title="Audiencia Preparatoria",
        preferred_date=hearing_time,
        duration_minutes=60,
        description="Primera audiencia del caso para establecer los hechos y pruebas.",
        virtual=True
    )
    
    # Imprimir resultado
    if "error" in result:
        print(f"Error al agendar audiencia: {result['error']}")
    else:
        print("Audiencia agendada exitosamente:")
        print(f"ID del evento: {result.get('id')}")
        print(f"Enlace Meet: {result.get('hangoutLink', 'No disponible')}")
        print(f"Hora inicio: {result.get('start', {}).get('dateTime')}")
        
        # Guardar el ID del evento para futuras pruebas
        with open("last_event_id.txt", "w") as f:
            f.write(result.get('id', ''))

if __name__ == "__main__":
    test_schedule_hearing()
