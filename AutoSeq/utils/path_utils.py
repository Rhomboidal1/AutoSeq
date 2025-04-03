# path.py - Path manipulation utilities
import os
import re
import sys
# Add the project's root directory to sys.path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels
sys.path.append(project_root)

from AutoSeq.utils.regex import RegexPatterns

class PathUtilities:
    """Utilities for path and filename manipulation"""
    
    def __init__(self, regex_patterns=None):
        """Initialize path utilities with regex patterns"""
        self.regex = regex_patterns or RegexPatterns()
        
        # Character translation table for ABI compatibility
        self.abi_translation_table = str.maketrans({
            ' ': '',
            '+': '&',
            '*': '-',
            '|': '-',
            '/': '-',
            '\\': '-',
            ':': '-',
            '"': '',
            "'": '',
            '<': '-',
            '>': '-',
            '?': '',
            ',': ''
        })
    
    def normalize_filename(self, file_name, remove_extension=True):
        """Normalize a filename for consistent comparison"""
        # Step 1: Adjust characters for ABI compatibility
        adjusted_name = self.adjust_abi_chars(file_name)
        
        # Step 2: Remove extension if requested
        if remove_extension and '.' in adjusted_name:
            adjusted_name = os.path.splitext(adjusted_name)[0]
            
        # Step 3: Remove suffixes like _Premixed and _RTI
        normalized_name = self.neutralize_suffixes(adjusted_name)
        
        # Step 4: Remove brace content
        normalized_name = self.remove_brace_content(normalized_name)
        
        return normalized_name
    
    def adjust_abi_chars(self, file_name):
        """Adjust characters in filename to match ABI naming conventions"""
        return file_name.translate(self.abi_translation_table)
    
    def neutralize_suffixes(self, file_name):
        """Remove standard suffixes from filenames"""
        name = file_name
        name = name.replace('_Premixed', '')
        name = name.replace('_RTI', '')
        return name
    
    def remove_brace_content(self, text):
        """Remove content within braces from text"""
        return self.regex.get('brace_content').sub('', text)
    
    def get_inumber_from_name(self, name):
        """Extract I number from a name"""
        return self.regex.extract('inumber', str(name))
    
    def get_pcr_number(self, file_name):
        """Extract PCR number from file name"""
        return self.regex.extract('pcr_number', file_name)
    
    def get_order_number(self, folder_name):
        """Extract order number from folder name"""
        return self.regex.extract('order_number', folder_name)
    
    def is_bioi_folder(self, folder_name):
        """Check if folder is a BioI folder"""
        return self.regex.contains('bioi_folder', folder_name)
    
    def is_order_folder(self, folder_name):
        """Check if folder is an order folder"""
        return self.regex.contains('bioi_order_folder', folder_name)
    
    def is_plate_folder(self, folder_name):
        """Check if folder is a plate folder"""
        return self.regex.contains('plate_folder', folder_name)
    
    def is_pcr_folder(self, folder_name):
        """Check if folder is a PCR folder"""
        return self.regex.contains('pcr_folder', folder_name)
    
    def join_paths(self, *args):
        """Join path components"""
        return os.path.join(*args)
    
    def get_basename(self, path):
        """Get the basename of a path"""
        return os.path.basename(path)
    
    def get_dirname(self, path):
        """Get the directory name of a path"""
        return os.path.dirname(path)