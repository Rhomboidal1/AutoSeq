# regex.py - Centralized regex patterns for the entire application
import re
import os
import sys
# Calculate the project's root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

# Add the project's root directory to sys.path
sys.path.append(project_root)


class RegexPatterns:
    """Centralized regex patterns for file and folder naming conventions"""
    
    def __init__(self):
        # Core patterns used throughout the application
        self.patterns = {
            'inumber': re.compile(r'bioi-(\d+)', re.IGNORECASE),
            'pcr_number': re.compile(r'{pcr(\d+).+}', re.IGNORECASE),
            'brace_content': re.compile(r'{.*?}'),
            'bioi_folder': re.compile(r'bioi-\d+', re.IGNORECASE),
            'bioi_order_folder': re.compile(r'bioi-\d+_.+_\d+', re.IGNORECASE),
            'plate_folder': re.compile(r'p\d+.+', re.IGNORECASE),
            'pcr_folder': re.compile(r'fb-pcr\d+_\d+', re.IGNORECASE),
            'ind_blank_file': re.compile(r'{\d+[A-H]}.ab1$', re.IGNORECASE),
            'plate_blank_file': re.compile(r'^\d{2}[A-H]__.ab1$', re.IGNORECASE),
            'well_location': re.compile(r'{(\d+[A-H])}', re.IGNORECASE),
            'reinject_dilution': re.compile(r'{(\d+_\d+)}', re.IGNORECASE),
            'preemptive_flag': re.compile(r'{!P}', re.IGNORECASE),
            'order_number': re.compile(r'_(\d+)(?:$|_)', re.IGNORECASE),
            }
    
    def get(self, pattern_name):
        """Get a compiled regex pattern by name"""
        return self.patterns.get(pattern_name)
        
    def match(self, pattern_name, text):
        """Match text against a named pattern"""
        pattern = self.get(pattern_name)
        if not pattern:
            return None
        return pattern.search(text)
        
    def extract(self, pattern_name, text, group=1):
        """Extract a specific group from a pattern match"""
        match = self.match(pattern_name, text)
        if match and group <= len(match.groups()):
            return match.group(group)
        return None
        
    def contains(self, pattern_name, text):
        """Check if text contains a match for the pattern"""
        return self.match(pattern_name, text) is not None