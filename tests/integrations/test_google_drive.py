"""Tests reales para la integración con Google Drive."""
import os
import pytest
from datetime import datetime, UTC
from pathlib import Path
from src.integrations.google_drive import GoogleDriveClient
from src.config import settings

@pytest.fixture(scope='session')
def drive_client():
    """Cliente de Google Drive para pruebas."""
    # Verificar credenciales de prueba
    if not os.path.exists(settings.TEST_GOOGLE_CREDENTIALS_FILE):
        pytest.skip('Credenciales de prueba no encontradas')
    if not settings.TEST_DRIVE_ROOT_FOLDER:
        pytest.skip('ID de carpeta de pruebas no configurado')
        
    # Configurar cliente
    os.environ['GOOGLE_CREDENTIALS_FILE'] = settings.TEST_GOOGLE_CREDENTIALS_FILE
    os.environ['GOOGLE_TOKEN_FILE'] = settings.TEST_GOOGLE_TOKEN_FILE
    
    client = GoogleDriveClient()
    return client

@pytest.fixture(autouse=True)
def cleanup(drive_client):
    """Limpiar archivos de prueba después de cada test."""
    yield
    # Listar archivos en la carpeta de pruebas
    files = drive_client.service.files().list(
        q=f"'{settings.TEST_DRIVE_ROOT_FOLDER}' in parents",
        fields='files(id)'
    ).execute().get('files', [])
    
    # Eliminar archivos
    for file in files:
        drive_client.service.files().delete(
            fileId=file['id'],
            supportsAllDrives=True
        ).execute()

@pytest.fixture
def test_file():
    """Crear archivo temporal para pruebas."""
    file_path = settings.TEMP_DIR / 'test.txt'
    file_path.write_text('Contenido de prueba')
    yield file_path
    file_path.unlink(missing_ok=True)

def test_init(drive_client):
    """Probar inicialización del cliente."""
    assert drive_client.service is not None
    # Verificar conexión listando archivos
    response = drive_client.service.files().list(pageSize=1).execute()
    assert 'files' in response

def test_upload_file(drive_client, test_file):
    """Probar subida de archivo."""
    # Subir archivo
    result = drive_client.upload_file(
        file_path=str(test_file),
        folder_id=settings.TEST_DRIVE_ROOT_FOLDER,
        title='test_upload.txt'
    )
    
    # Verificar
    assert result['id']
    assert result['name'] == 'test_upload.txt'
    
    # Verificar que existe en Drive
    file = drive_client.service.files().get(
        fileId=result['id'],
        fields='id,name,mimeType'
    ).execute()
    assert file['name'] == 'test_upload.txt'
    
    # Verificar que existe en Drive
    file = drive_client.service.files().get(
        fileId=result['id'],
        fields='id,name,mimeType'
    ).execute()
    assert file['name'] == 'test_upload.txt'

def test_create_case_structure(drive_client):
    """Probar creación de estructura de caso."""
    case_id = 'TEST-2025-001'
    case_type = 'Civil'
    participants = [
        {'email': 'test.juez@autonomos.dev', 'rol': 'juez'},
        {'email': 'test.fiscal@autonomos.dev', 'rol': 'fiscal'},
        {'email': 'test.defensor@autonomos.dev', 'rol': 'defensor'}
    ]
    
    # Crear estructura
    structure = drive_client.create_case_structure(
        case_id=case_id,
        case_type=case_type,
        participants=participants,
        title=f'Caso {case_id} - {case_type}'
    )
    
    # Verificar carpeta principal
    assert structure['case_folder']['name'] == f'Caso {case_id} - {case_type}'
    
    # Verificar carpetas confidenciales
    for role in ['Juez', 'Fiscal', 'Defensor']:
        folder_name = f'Confidencial {role}'
        folder = drive_client.service.files().list(
            q=f"name = '{folder_name}' and '{structure['case_folder']['id']}' in parents",
            fields='files(id,name)'
        ).execute()
        assert len(folder['files']) == 1
    
    # Verificar
    drive_client.service.files.return_value.get.assert_called_once_with(
        fileId=file_id,
        fields=fields,
        supportsAllDrives=True
    )
    assert metadata['id'] == file_id
    assert metadata['name'] == 'test_file.pdf'
    assert metadata['mimeType'] == 'application/pdf'

def test_share_case_files(drive_client, test_file):
    """Probar compartir archivos de caso."""
    # Crear archivo
    file = drive_client.upload_file(
        file_path=str(test_file),
        folder_id=settings.TEST_DRIVE_ROOT_FOLDER,
        title='documento_compartido.txt',
        share_with=['test.juez@autonomos.dev']
    )
    
    # Verificar permisos
    permissions = drive_client.service.permissions().list(
        fileId=file['id'],
        fields='permissions(emailAddress,role)'
    ).execute()
    
    assert any(
        p['emailAddress'] == 'test.juez@autonomos.dev'
        for p in permissions.get('permissions', [])
    )

def test_create_folder_structure(drive_client):
    """Probar creación de estructura de carpetas."""
    # Crear estructura
    root = drive_client.create_folder(
        name='Root Test',
        parent_id=settings.TEST_DRIVE_ROOT_FOLDER
    )
    
    subfolder = drive_client.create_folder(
        name='Subfolder',
        parent_id=root['id']
    )
    
    # Verificar estructura
    files = drive_client.service.files().list(
        q=f"'{root['id']}' in parents",
        fields='files(id,name,mimeType)'
    ).execute()
    
    assert any(
        f['name'] == 'Subfolder' and
        f['mimeType'] == 'application/vnd.google-apps.folder'
        for f in files.get('files', [])
    )

def test_error_handling(drive_client):
    """Probar manejo de errores."""
    # Intentar acceder a archivo inexistente
    with pytest.raises(Exception) as exc_info:
        drive_client.service.files().get(
            fileId='archivo_inexistente',
            fields='id,name'
        ).execute()
    
    assert 'File not found' in str(exc_info.value)
    
    # Intentar crear carpeta sin permisos
    with pytest.raises(Exception) as exc_info:
        drive_client.create_folder(
            name='Carpeta Sin Permisos',
            parent_id='carpeta_inexistente'
        )
    
    assert any(
        error in str(exc_info.value)
        for error in ['File not found', 'insufficient permissions']
    )

def test_create_case_structure_with_participants(drive_client):
    """Test creating a case structure with participants."""
    # Preparar
    case_id = 'CASE-2025-002'
    case_type = 'Penal'
    participants = [
        {'email': 'juez@court.com', 'rol': 'juez'},
        {'email': 'fiscal@court.com', 'rol': 'fiscal'},
        {'email': 'defensor@court.com', 'rol': 'defensor'}
    ]
    
    # Ejecutar
    structure = drive_client.create_case_structure(
        case_id=case_id,
        case_type=case_type,
        participants=participants
    )
    
    # Verificar estructura base
    assert structure['case_folder']['name'] == f'Caso {case_id} - {case_type}'
    
    # Verificar carpetas confidenciales
    folders = drive_client.service.files().list(
        q=f"'{structure['case_folder']['id']}' in parents and mimeType='application/vnd.google-apps.folder'",
        fields='files(id,name,mimeType)'
    ).execute().get('files', [])
    
    folder_names = [f['name'] for f in folders]
    assert 'Confidencial' in folder_names
    assert 'Documentos Principales' in folder_names
    assert 'Pruebas' in folder_names
    
    # Verificar permisos de juez
    judge_folder = next(f for f in folders if f['name'] == 'Confidencial Juez')
    perms = drive_client.service.permissions().list(
        fileId=judge_folder['id'],
        fields='permissions(emailAddress,role)'
    ).execute().get('permissions', [])
    
    assert any(p.get('emailAddress') == 'juez@court.com' for p in perms)

def test_error_handling_upload(drive_client):
    """Test error handling during file upload."""
    # Preparar
    file_path = '/nonexistent/file.pdf'
    
    # Ejecutar y verificar
    with pytest.raises(FileNotFoundError):
        drive_client.upload_file(
            file_path=file_path,
            folder_id=settings.TEST_DRIVE_ROOT_FOLDER,
            title='error.pdf'
        )
