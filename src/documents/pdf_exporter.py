"""Módulo para exportar anotaciones a PDF."""
from typing import List, Dict, Any, Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import inch
from io import BytesIO

class AnnotationPDFExporter:
    """Exportador de anotaciones a PDF."""

    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        """Configurar estilos personalizados."""
        self.styles.add(ParagraphStyle(
            name='Tag',
            parent=self.styles['Normal'],
            textColor=colors.white,
            backColor=colors.blue,
            fontSize=8,
            leading=10,
            spaceBefore=2,
            spaceAfter=2,
            borderPadding=3,
            borderRadius=5
        ))

    def _create_header(self, doc_info: Dict[str, Any]) -> List[Any]:
        """Crear encabezado del documento."""
        elements = []
        
        # Título
        title = Paragraph(
            f"Anotaciones: {doc_info['title']}",
            self.styles['Title']
        )
        elements.append(title)
        elements.append(Spacer(1, 0.25*inch))
        
        # Información del documento
        info_table_data = [
            ['Documento', doc_info['title']],
            ['Fecha de exportación', datetime.now().strftime('%Y-%m-%d %H:%M')],
            ['Total de anotaciones', str(doc_info['total_annotations'])],
            ['Autor', doc_info['author']]
        ]
        
        info_table = Table(
            info_table_data,
            colWidths=[2*inch, 4*inch],
            style=TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.lightgrey),
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('BACKGROUND', (0, 0), (-1, -1), colors.white),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('BOX', (0, 0), (-1, -1), 2, colors.black),
            ])
        )
        elements.append(info_table)
        elements.append(Spacer(1, 0.5*inch))
        
        return elements

    def _format_annotation(self, annotation: Dict[str, Any]) -> List[Any]:
        """Formatear una anotación para el PDF."""
        elements = []
        
        # Contenido principal
        content = Paragraph(
            annotation['content'],
            self.styles['Normal']
        )
        
        # Metadatos
        metadata = [
            [
                Paragraph('Página', self.styles['Bullet']),
                str(annotation['position']['page']),
                Paragraph('Creado', self.styles['Bullet']),
                annotation['created_at'].strftime('%Y-%m-%d %H:%M')
            ]
        ]
        
        meta_table = Table(
            metadata,
            colWidths=[inch, 1.5*inch, inch, 1.5*inch],
            style=TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), colors.grey),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
            ])
        )
        
        # Etiquetas
        if annotation.get('tags'):
            tags = [
                Paragraph(
                    tag['name'],
                    ParagraphStyle(
                        'Tag',
                        parent=self.styles['Tag'],
                        backColor=colors.HexColor(tag['color'])
                    )
                )
                for tag in annotation['tags']
            ]
            tag_table = Table(
                [tags],
                colWidths=[inch]*len(tags),
                style=TableStyle([
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ])
            )
            elements.append(tag_table)
        
        elements.extend([content, meta_table, Spacer(1, 0.25*inch)])
        return elements

    async def export_annotations(
        self,
        annotations: List[Dict[str, Any]],
        doc_info: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> BytesIO:
        """Exportar anotaciones a PDF.
        
        Args:
            annotations: Lista de anotaciones
            doc_info: Información del documento
            output_path: Ruta de salida opcional
            
        Returns:
            BytesIO con el contenido del PDF
        """
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            output_path or buffer,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Construir documento
        elements = []
        
        # Agregar encabezado
        elements.extend(self._create_header(doc_info))
        
        # Agregar anotaciones
        for annotation in sorted(
            annotations,
            key=lambda x: (x['position']['page'], x['position']['y'])
        ):
            elements.extend(self._format_annotation(annotation))
        
        # Generar PDF
        doc.build(elements)
        
        if output_path:
            return None
        
        buffer.seek(0)
        return buffer
