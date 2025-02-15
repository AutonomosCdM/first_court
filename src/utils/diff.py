"""Utilities for calculating and applying document differences."""
from typing import Dict, Any, List, Union
import difflib
import json

def calculate_diff(content1: Dict[str, Any], content2: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Calculate differences between two document contents.
    
    Args:
        content1: First document content
        content2: Second document content
        
    Returns:
        List of changes with type and content
    """
    # Convertir contenido a formato comparable
    text1 = _extract_text(content1)
    text2 = _extract_text(content2)
    
    # Calcular diferencias a nivel de línea
    differ = difflib.SequenceMatcher(None, text1, text2)
    changes = []
    
    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        change = {
            'type': tag,
            'content': None,
            'position': {
                'start': i1,
                'end': i2
            }
        }
        
        if tag == 'replace':
            change['old_content'] = text1[i1:i2]
            change['new_content'] = text2[j1:j2]
        elif tag == 'delete':
            change['content'] = text1[i1:i2]
        elif tag == 'insert':
            change['content'] = text2[j1:j2]
            
        changes.append(change)
    
    return changes

def apply_patch(content: Dict[str, Any], changes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Apply changes to document content.
    
    Args:
        content: Original document content
        changes: List of changes to apply
        
    Returns:
        Updated document content
    """
    text = _extract_text(content)
    result = []
    last_pos = 0
    
    for change in sorted(changes, key=lambda x: x['position']['start']):
        start = change['position']['start']
        end = change['position']['end']
        
        # Mantener texto sin cambios hasta la posición actual
        result.append(text[last_pos:start])
        
        # Aplicar el cambio
        if change['type'] == 'replace':
            result.append(change['new_content'])
        elif change['type'] == 'insert':
            result.append(change['content'])
        
        last_pos = end
    
    # Agregar el resto del texto
    result.append(text[last_pos:])
    
    # Reconstruir el contenido del documento
    return _rebuild_content(''.join(result), content)

def _extract_text(content: Dict[str, Any]) -> str:
    """Extract plain text from document content."""
    if not content.get('body'):
        return ''
        
    text = []
    for element in content['body'].get('content', []):
        if 'paragraph' in element:
            for part in element['paragraph'].get('elements', []):
                if 'textRun' in part:
                    text.append(part['textRun'].get('content', ''))
    
    return ''.join(text)

def _rebuild_content(text: str, template: Dict[str, Any]) -> Dict[str, Any]:
    """Rebuild document content from text using template structure."""
    result = json.loads(json.dumps(template))  # Deep copy
    
    if not result.get('body'):
        result['body'] = {'content': []}
    
    # Crear un nuevo párrafo con el texto
    result['body']['content'] = [{
        'paragraph': {
            'elements': [{
                'textRun': {
                    'content': text
                }
            }]
        }
    }]
    
    return result
