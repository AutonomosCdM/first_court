"""
Integración con GitHub Pages para el portal informativo
"""
import os
import base64
from typing import List, Dict, Optional
from github import Github
from datetime import datetime

class GithubPagesClient:
    """Cliente para gestionar el portal en GitHub Pages"""
    
    def __init__(self, token: str, repo_name: str):
        """
        Inicializa el cliente de GitHub
        
        Args:
            token: Token de acceso a GitHub
            repo_name: Nombre del repositorio (formato: 'usuario/repo')
        """
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)
    
    def create_page(self, title: str, content: str, category: str = None) -> Dict:
        """
        Crea una nueva página en el portal
        
        Args:
            title: Título de la página
            content: Contenido en formato Markdown
            category: Categoría de la página (opcional)
            
        Returns:
            Dict con la información del commit
        """
        # Generar nombre de archivo
        filename = title.lower().replace(' ', '-')
        if category:
            path = f"docs/{category}/{filename}.md"
        else:
            path = f"docs/{filename}.md"
            
        # Agregar frontmatter
        full_content = f"""---
layout: page
title: {title}
---

{content}"""
        
        # Crear o actualizar archivo
        try:
            # Intentar obtener archivo existente
            file = self.repo.get_contents(path)
            message = f"Update {title}"
            result = self.repo.update_file(
                path=path,
                message=message,
                content=full_content,
                sha=file.sha
            )
        except:
            # Crear nuevo archivo
            message = f"Create {title}"
            result = self.repo.create_file(
                path=path,
                message=message,
                content=full_content
            )
            
        return result
    
    def create_post(self, title: str, content: str, tags: List[str] = None) -> Dict:
        """
        Crea una nueva entrada de blog
        
        Args:
            title: Título del post
            content: Contenido en formato Markdown
            tags: Lista de etiquetas
            
        Returns:
            Dict con la información del commit
        """
        # Generar nombre de archivo con fecha
        date = datetime.now().strftime('%Y-%m-%d')
        filename = f"{date}-{title.lower().replace(' ', '-')}"
        path = f"docs/_posts/{filename}.md"
        
        # Agregar frontmatter
        frontmatter = f"""---
layout: post
title: {title}
date: {date}
"""
        
        if tags:
            frontmatter += f"tags: {tags}\n"
            
        frontmatter += "---\n\n"
        
        full_content = frontmatter + content
        
        # Crear archivo
        result = self.repo.create_file(
            path=path,
            message=f"Create post: {title}",
            content=full_content
        )
        
        return result
    
    def upload_asset(self, file_path: str, destination: str) -> Dict:
        """
        Sube un archivo de recursos (imagen, PDF, etc.)
        
        Args:
            file_path: Ruta local al archivo
            destination: Ruta destino en el repositorio
            
        Returns:
            Dict con la información del commit
        """
        with open(file_path, 'rb') as file:
            content = base64.b64encode(file.read()).decode()
            
        result = self.repo.create_file(
            path=f"docs/assets/{destination}",
            message=f"Upload asset: {destination}",
            content=content
        )
        
        return result
    
    def create_tramite(self, title: str, description: str, 
                      requirements: List[str], steps: List[str]) -> Dict:
        """
        Crea una página de trámite
        
        Args:
            title: Título del trámite
            description: Descripción del trámite
            requirements: Lista de requisitos
            steps: Lista de pasos a seguir
            
        Returns:
            Dict con la información del commit
        """
        content = f"""
{description}

## Requisitos

{% for req in page.requirements %}
* {{{{ req }}}}
{% endfor %}

## Pasos a Seguir

{% for step in page.steps %}
1. {{{{ step }}}}
{% endfor %}

## Información Adicional

Para más información sobre este trámite, puede contactarnos a través de:
* Teléfono: (XX) XXXX-XXXX
* Email: tramites@tribunales.gob
* Chat en línea (Lunes a Viernes, 9:00 - 18:00)
"""
        
        return self.create_page(
            title=title,
            content=content,
            category='tramites'
        )
    
    def create_help_article(self, title: str, content: str, 
                          related_articles: List[str] = None) -> Dict:
        """
        Crea un artículo de ayuda
        
        Args:
            title: Título del artículo
            content: Contenido del artículo
            related_articles: Lista de artículos relacionados
            
        Returns:
            Dict con la información del commit
        """
        if related_articles:
            content += "\n\n## Artículos Relacionados\n\n"
            for article in related_articles:
                content += f"* [{article}](/ayuda/{article.lower().replace(' ', '-')})\n"
        
        return self.create_page(
            title=title,
            content=content,
            category='ayuda'
        )
