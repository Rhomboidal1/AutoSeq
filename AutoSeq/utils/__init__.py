"""Utility modules for the MseqAuto package."""
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from mseqauto.utils.path_utils import PathUtilities
from mseqauto.utils.regex import RegexPatterns
from mseqauto.utils.log_service import setup_logger, LoggingService  # Updated import

__all__ = ['PathUtilities', 'RegexPatterns', 'setup_logger', 'LoggingService']