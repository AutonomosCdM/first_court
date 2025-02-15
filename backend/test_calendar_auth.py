from src.integrations.google_calendar import GoogleCalendarClient
from datetime import datetime, timedelta

def test_calendar():
    print("Iniciando prueba de Google Calendar...")
    
    # Crear instancia del cliente
    calendar = GoogleCalendarClient()
    
    # Intentar listar eventos para probar la autenticación
    start = datetime.now()
    end = start + timedelta(days=7)
    
    print("Verificando disponibilidad...")
    available = calendar.check_availability(start, end)
    print(f"Disponibilidad: {available}")

if __name__ == "__main__":
    test_calendar()
