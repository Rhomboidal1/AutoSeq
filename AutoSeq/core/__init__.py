"""Core functionality for the AutoSeq package."""
import os
import sys
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from AutoSeq.core.file_system import FileSystem
from AutoSeq.core.automation import MseqAutomation
from AutoSeq.utils.path_utils import PathUtilities
from AutoSeq.utils.regex import RegexPatterns
from AutoSeq.utils.log_service import setup_logger, LoggingService  # Updated import

__all__ = ['FileSystem', 'AutoSeqmation', 'PathUtilities', 'RegexPatterns', 'setup_logger', 'LoggingService']