# Sistema de Simulación Judicial Chileno

## Descripción
Sistema de simulación judicial basado en agentes autónomos para el entrenamiento y práctica de procedimientos legales chilenos.

## Estructura del Proyecto
```
.
├── config/               # Configuración del sistema
├── src/
│   ├── agents/          # Agentes judiciales autónomos
│   ├── data/            # Base de datos legal
│   ├── llm/             # Integración con modelos de lenguaje
│   ├── simulation/      # Motor de simulación
│   └── utils/           # Utilidades
└── tests/               # Pruebas unitarias e integración
```

## Configuración del Entorno
1. Instalar Poetry:
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Instalar dependencias:
```bash
poetry install
```

3. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con las credenciales necesarias
```

## Uso
```python
from src.simulation.court import CourtSimulation
from config.judicial_settings import JudicialSettings

# Inicializar simulación
settings = JudicialSettings()
simulation = CourtSimulation(settings)

# Agregar agentes
simulation.add_agent("juez", JudgeAgent(settings))
simulation.add_agent("abogado", LawyerAgent(settings))

# Ejecutar simulación
case_data = {"tipo": "civil", "materia": "arrendamiento"}
results = simulation.run_simulation(case_data)
```
