"""
Utilities package initialization file for MedClarify application.
"""

from .text_processing import extract_json
from .logging_setup import setup_logger

__all__ = ["extract_json", "setup_logger"]