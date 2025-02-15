"""Script para probar el gestor de plantillas."""
from src.documents.template_manager import TemplateManager

def main():
    """Función principal para probar las plantillas."""
    # Crear gestor
    manager = TemplateManager()
    
    # Crear plantilla de demanda
    print("Creando plantilla de demanda...")
    template = manager.create_template(
        template_type='demanda',
        title='Demanda Ejecutiva',
        content="""
        EN LO PRINCIPAL: Demanda ejecutiva; PRIMER OTROSÍ: Acompaña documentos
        
        S.J.L
        
        {cliente}, en autos sobre juicio ejecutivo caratulados "{causa}", a US. respetuosamente digo:
        
        Que, en la representación que invisto, y de conformidad con lo dispuesto en los artículos {articulos}, vengo en interponer demanda ejecutiva en contra de {contraparte}, en base a los siguientes antecedentes:
        
        POR TANTO,
        
        RUEGO A US.: Tener por interpuesta demanda ejecutiva en contra de {contraparte}, acogerla a tramitación y, en definitiva, ordenar {petitorio}
        """
    )
    print(f"Plantilla creada: {template['name']} (ID: {template['id']})")
    
    # Crear documento desde plantilla
    print("\nCreando documento desde plantilla...")
    variables = {
        'cliente': 'Juan Pérez',
        'causa': 'Pérez con González',
        'articulos': '434 y siguientes del Código de Procedimiento Civil',
        'contraparte': 'Pedro González',
        'petitorio': 'se despache mandamiento de ejecución y embargo'
    }
    doc = manager.create_from_template(template['id'], variables)
    print(f"Documento creado: {doc['name']}")
    print(f"Link: {doc['webViewLink']}")
    
    print("\nPruebas completadas con éxito!")

if __name__ == "__main__":
    main()
