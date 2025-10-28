"""
Report Assembly Agent - Assembles structured reports from extracted content
"""
import time
from typing import List, Dict, Any
from pathlib import Path
import sys
import os
sys.path.append(str(Path(__file__).parent.parent))

import google.generativeai as genai
from .extraction_agent import ExtractionAgent
from .summarization_agent import SummarizationAgent
from utils.pdf_generator import PDFReportGenerator
from loguru import logger
import config


class ReportAssemblyAgent:
    """Agent for assembling and generating reports"""
    
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=config.GOOGLE_API_KEY)
        
        self.model = genai.GenerativeModel(
            model_name=config.GEMINI_MODEL
        )
        
        # Initialize sub-agents
        self.extraction_agent = ExtractionAgent()
        self.summarization_agent = SummarizationAgent()
        
        # PDF generator
        self.pdf_generator = PDFReportGenerator()
        
        logger.info("Report Assembly Agent initialized")
    
    def generate_report(
        self,
        title: str,
        sections: List[str]
    ) -> Dict[str, Any]:
        """
        Generate a complete medical report
        
        Args:
            title: Report title
            sections: List of section names to include
            
        Returns:
            Report generation results
        """
        try:
            report_sections = []
            
            # Generate each section
            for section_name in sections:
                logger.info(f"Generating section: {section_name}")
                
                if section_name == "Summary":
                    # Use summarization agent
                    summary = self.summarization_agent.generate_summary()
                    report_sections.append({
                        'title': section_name,
                        'content': summary['content'],
                        'type': 'text'
                    })
                else:
                    # Extract section
                    extracted = self.extraction_agent.extract_section(section_name)
                    
                    if extracted['found']:
                        report_sections.append({
                            'title': section_name,
                            'content': extracted['content'],
                            'type': 'text'
                        })
                    else:
                        # Generate placeholder
                        report_sections.append({
                            'title': section_name,
                            'content': f"No specific content found for {section_name} section.",
                            'type': 'text'
                        })
            
            # Create PDF
            report_data = {
                'title': title,
                'sections': report_sections
            }
            
            # Generate output filename
            output_path = os.path.join(
                config.DATA_DIR,
                f"report_{int(time.time())}.pdf"
            )
            
            pdf_path = self.pdf_generator.generate_report(
                report_data=report_data,
                output_path=output_path
            )
            
            return {
                'success': True,
                'pdf_path': pdf_path,
                'sections_generated': len(report_sections)
            }
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return {
                'success': False,
                'error': str(e)
            }
