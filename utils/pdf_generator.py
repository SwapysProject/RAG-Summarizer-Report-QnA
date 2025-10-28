"""
PDF Report Generation using ReportLab
"""
from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, Image as RLImage, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd
from loguru import logger
import config


class PDFReportGenerator:
    """Generate structured PDF reports"""
    
    def __init__(self):
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=18,
                textColor=colors.HexColor('#1a1a1a'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        # Section heading style
        if 'SectionHeading' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeading',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#2c3e50'),
                spaceBefore=20,
                spaceAfter=12,
                fontName='Helvetica-Bold'
            ))
        
        # Body text style - use a custom name to avoid conflict
        if 'CustomBodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomBodyText',
                parent=self.styles['BodyText'],
                fontSize=11,
                leading=16,
                alignment=TA_JUSTIFY,
                spaceAfter=12
            ))
    
    def generate_report(
        self,
        report_data: Dict[str, Any],
        output_path: str
    ) -> str:
        """
        Generate a PDF report from structured data
        
        Args:
            report_data: Dictionary containing report sections
            output_path: Path to save the PDF
            
        Returns:
            Path to generated PDF
        """
        try:
            # Create PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=config.REPORT_TEMPLATE['margin'],
                leftMargin=config.REPORT_TEMPLATE['margin'],
                topMargin=config.REPORT_TEMPLATE['margin'],
                bottomMargin=config.REPORT_TEMPLATE['margin']
            )
            
            # Build story (content)
            story = []
            
            # Add title
            title = report_data.get('title', 'Medical Document Report')
            story.append(Paragraph(title, self.styles['CustomTitle']))
            story.append(Spacer(1, 0.3*inch))
            
            # Add generation date
            date_text = f"Generated on: {datetime.now().strftime('%B %d, %Y at %H:%M')}"
            story.append(Paragraph(date_text, self.styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            
            # Add sections
            sections = report_data.get('sections', [])
            
            for section in sections:
                section_title = section.get('title', '')
                section_content = section.get('content', '')
                section_type = section.get('type', 'text')
                
                # Add section heading
                if section_title:
                    story.append(Paragraph(section_title, self.styles['SectionHeading']))
                    story.append(Spacer(1, 0.2*inch))
                
                # Add section content based on type
                if section_type == 'text':
                    # Regular text paragraph
                    paragraphs = section_content.split('\n\n')
                    for para in paragraphs:
                        if para.strip():
                            story.append(Paragraph(para, self.styles['CustomBodyText']))
                    story.append(Spacer(1, 0.3*inch))
                
                elif section_type == 'table':
                    # Table data
                    table_data = section.get('table_data', [])
                    if table_data:
                        story.append(self._create_table(table_data))
                        story.append(Spacer(1, 0.3*inch))
                
                elif section_type == 'image':
                    # Image
                    image_path = section.get('image_path', '')
                    if image_path and Path(image_path).exists():
                        story.append(self._create_image(image_path))
                        story.append(Spacer(1, 0.3*inch))
                
                elif section_type == 'list':
                    # Bullet points
                    items = section_content.split('\n')
                    for item in items:
                        if item.strip():
                            bullet_text = f"• {item.strip()}"
                            story.append(Paragraph(bullet_text, self.styles['CustomBodyText']))
                    story.append(Spacer(1, 0.3*inch))
            
            # Build PDF
            doc.build(story)
            logger.info(f"PDF report generated: {output_path}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {e}")
            raise
    
    def _create_table(self, data: List[List[Any]]) -> Table:
        """Create a formatted table"""
        # Create table
        table = Table(data, hAlign='LEFT')
        
        # Style the table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        return table
    
    def _create_image(self, image_path: str, max_width: float = 5*inch) -> RLImage:
        """Create an image element"""
        try:
            img = RLImage(image_path)
            
            # Scale image if needed
            if img.drawWidth > max_width:
                aspect = img.drawHeight / img.drawWidth
                img.drawWidth = max_width
                img.drawHeight = max_width * aspect
            
            return img
        except Exception as e:
            logger.error(f"Error creating image: {e}")
            return Paragraph(f"[Image could not be loaded: {image_path}]", self.styles['Normal'])
    
    def dataframe_to_table_data(self, df: pd.DataFrame) -> List[List[str]]:
        """Convert pandas DataFrame to table data"""
        # Get headers
        headers = list(df.columns)
        
        # Get data rows
        data_rows = df.values.tolist()
        
        # Convert all to strings
        table_data = [[str(h) for h in headers]]
        for row in data_rows:
            table_data.append([str(cell) for cell in row])
        
        return table_data
