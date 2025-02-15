"""
Test del módulo de integración con Google Drive
"""
from src.integrations.google_drive import GoogleDriveClient
import tempfile
from pathlib import Path
import json

def test_drive_integration():
    """Prueba las funcionalidades básicas de Google Drive"""
    
    print("\n1. Iniciando cliente de Google Drive...")
    drive_client = GoogleDriveClient()
    
    print("\n2. Creando estructura de caso de prueba...")
    case_structure = drive_client.create_case_structure(
        case_id="TEST-001",
        title="Caso de Prueba Drive"
    )
    
    # Guardar IDs para referencia
    with open('drive_test_structure.json', 'w') as f:
        json.dump(case_structure, f, indent=2)
    
    print("\nEstructura creada:")
    print(f"- Carpeta principal: {case_structure['case_folder']['id']}")
    print("\nSubcarpetas:")
    for name, folder in case_structure['subfolders'].items():
        print(f"- {name}: {folder['id']}")
    
    print("\n3. Creando archivo de prueba...")
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp:
        temp.write("Este es un archivo de prueba para Google Drive")
        temp_path = temp.name
    
    # Subir archivo a la carpeta de documentos principales
    uploaded_file = drive_client.upload_file(
        file_path=temp_path,
        folder_id=case_structure['subfolders']['Documentos Principales']['id']
    )
    
    print(f"Archivo subido: {uploaded_file['webViewLink']}")
    
    print("\n4. Configurando permisos...")
    # Asignar permisos al juez
    permission = drive_client.set_permissions(
        file_id=case_structure['subfolders']['Documentos Principales']['id'],
        email="cesar@autonomos.dev",
        role="writer"
    )
    
    print(f"Permiso asignado a: {permission['emailAddress']} con rol: {permission['role']}")
    
    print("\n5. Listando archivos...")
    # Listar archivos en la carpeta principal
    files = drive_client.list_files(
        folder_id=case_structure['case_folder']['id']
    )
    
    print("Archivos encontrados:")
    for file in files:
        print(f"- {file['name']}")
    
    # Limpiar archivo temporal
    Path(temp_path).unlink()
    
    print("\nPrueba completada exitosamente!")

if __name__ == "__main__":
    test_drive_integration()
