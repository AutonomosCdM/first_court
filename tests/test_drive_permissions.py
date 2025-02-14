"""
Test de permisos y estructura confidencial en Google Drive
"""
from src.integrations.google_drive import GoogleDriveClient
import tempfile
from pathlib import Path
import json
from datetime import datetime

def test_confidential_structure():
    """Prueba la gestión de documentos confidenciales y permisos"""
    
    print("\n1. Iniciando cliente de Google Drive...")
    drive_client = GoogleDriveClient()
    
    # Crear un caso de prueba con timestamp para evitar duplicados
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    case_id = f"TEST-CONF-{timestamp}"
    
    print(f"\n2. Creando caso de prueba {case_id}...")
    case_structure = drive_client.create_case_structure(
        case_id=case_id,
        title="Prueba de Documentos Confidenciales"
    )
    
    # Guardar estructura para referencia
    with open(f'drive_test_conf_{timestamp}.json', 'w') as f:
        json.dump(case_structure, f, indent=2)
    
    print("\n3. Configurando permisos por rol...")
    
    # Configurar permisos para el juez
    print("\nConfigurando permisos para el juez...")
    judge_permissions = [
        (case_structure['confidential_juez']['id'], 'writer'),
        (case_structure['public']['id'], 'writer'),
        (case_structure['communications']['id'], 'writer')
    ]
    
    for folder_id, role in judge_permissions:
        permission = drive_client.set_permissions(
            file_id=folder_id,
            email="cesar@autonomos.dev",
            role=role
        )
        print(f"- Asignado {role} a {permission['emailAddress']} en {folder_id}")
    
    # Configurar permisos para el defensor
    print("\nConfigurando permisos para el defensor...")
    defender_permissions = [
        (case_structure['confidential_defensor']['id'], 'writer'),
        (case_structure['public']['id'], 'reader'),
        (case_structure['communications']['id'], 'commenter')
    ]
    
    for folder_id, role in defender_permissions:
        permission = drive_client.set_permissions(
            file_id=folder_id,
            email="tamara@autonomos.dev",
            role=role
        )
        print(f"- Asignado {role} a {permission['emailAddress']} en {folder_id}")
    
    print("\n4. Subiendo documentos de prueba...")
    
    # Crear y subir documento confidencial para el juez
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_judge:
        temp_judge.write("Documento confidencial del juez - Solo acceso autorizado")
        temp_judge_path = temp_judge.name
    
    judge_doc = drive_client.upload_file(
        file_path=temp_judge_path,
        parent_id=case_structure['confidential_juez']['id']
    )
    print(f"Documento del juez: {judge_doc['webViewLink']}")
    
    # Crear y subir documento confidencial para el defensor
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_defender:
        temp_defender.write("Documento confidencial del defensor - Solo acceso autorizado")
        temp_defender_path = temp_defender.name
    
    defender_doc = drive_client.upload_file(
        file_path=temp_defender_path,
        parent_id=case_structure['confidential_defensor']['id']
    )
    print(f"Documento del defensor: {defender_doc['webViewLink']}")
    
    # Crear y subir documento público
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_public:
        temp_public.write("Documento público del caso - Acceso general")
        temp_public_path = temp_public.name
    
    public_doc = drive_client.upload_file(
        file_path=temp_public_path,
        parent_id=case_structure['public']['id']
    )
    print(f"Documento público: {public_doc['webViewLink']}")
    
    print("\n5. Verificando estructura final...")
    # Buscar todos los documentos en el caso
    files = drive_client.search_files(
        query=case_id,
        parent_id=case_structure['public']['id']
    )
    
    print("\nDocumentos encontrados:")
    for file in files:
        print(f"- {file['name']}: {file['webViewLink']}")
    
    # Limpiar archivos temporales
    for path in [temp_judge_path, temp_defender_path, temp_public_path]:
        Path(path).unlink()
    
    print("\nPrueba completada exitosamente!")
    print("\nNOTA: Verifica manualmente que:")
    print("1. El juez puede ver y editar sus documentos confidenciales y públicos")
    print("2. El defensor puede ver y editar solo sus documentos confidenciales")
    print("3. El defensor puede ver pero no editar documentos públicos")
    print("4. Ninguno puede ver los documentos confidenciales del otro")

if __name__ == "__main__":
    test_confidential_structure()
