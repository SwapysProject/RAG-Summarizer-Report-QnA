"""
Medical Document AI Assistant - Agent Package

This package contains all specialized AI agents for the medical document processing system.

Agents:
- OrchestratorAgent: Central controller that coordinates all agents
- DocumentLoaderAgent: Handles multi-format document ingestion  
- QAAgent: Retrieval-Augmented Generation for Q&A
- ExtractionAgent: Extracts specific data, tables, and images
- ReportAssemblyAgent: Compiles and generates PDF reports
- SummarizationAgent: Creates document summaries
"""

__version__ = "1.0.0"
__author__ = "Medical Doc AI Team"

from .orchestrator import OrchestratorAgent
from .document_loader import DocumentLoaderAgent
from .qa_agent import QAAgent
from .extraction_agent import ExtractionAgent
from .report_assembly_agent import ReportAssemblyAgent
from .summarization_agent import SummarizationAgent

__all__ = [
    'OrchestratorAgent',
    'DocumentLoaderAgent', 
    'QAAgent',
    'ExtractionAgent',
    'ReportAssemblyAgent',
    'SummarizationAgent'
]
