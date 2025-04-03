"""Utility modules for the MseqAuto package."""
import os
import sys
# Calculate the project's root directory
def get_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

project_root = get_project_root()

# Add the project's root directory to sys.path
sys.path.append(project_root)

from AutoSeq.utils.path_utils import PathUtilities
from AutoSeq.utils.regex import RegexPatterns
from AutoSeq.utils.log_service import setup_logger, LoggingService  # Updated import

__all__ = ['PathUtilities', 'RegexPatterns', 'setup_logger', 'LoggingService']