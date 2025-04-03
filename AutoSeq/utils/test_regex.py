# test_regex.py
import os
import sys

# Calculate the project's root directory
def get_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

project_root = get_project_root()

# Add the project's root directory to sys.path
sys.path.append(project_root)

# Now we can import config.py
from AutoSeq.config import MseqConfig

from AutoSeq.utils.regex import RegexPatterns


def test_regex_patterns():
    patterns = RegexPatterns()
    
    # Test cases - format: (pattern_name, test_string, expected_result, test_type)
    test_cases = [
        # Basic pattern matching
        ('inumber', 'BioI-12345_Customer_67890', '12345', 'extract'),
        ('inumber', 'bioi-54321', '54321', 'extract'),
        ('inumber', 'no_match_here', None, 'extract'),
        
        # PCR number extraction
        ('pcr_number', '{PCR1234exp1}', '1234', 'extract'),
        ('pcr_number', 'Sample_Name{PCR987exp2}', '987', 'extract'),
        
        # Brace content
        ('brace_content', '{01A}Sample_Name', True, 'contains'),
        
        # Order folders
        ('bioi_order_folder', 'BioI-12345_Customer_67890', True, 'contains'),
        ('bioi_order_folder', 'BioI-12345', False, 'contains'),
        
        # Folder type detection
        ('plate_folder', 'P12345_CustomerName', True, 'contains'),
        ('pcr_folder', 'FB-PCR1234_5678', True, 'contains'),
    ]
    
    for pattern_name, test_string, expected, test_type in test_cases:
        if test_type == 'contains':
            result = patterns.contains(pattern_name, test_string)
            print(f"Testing {pattern_name} contains '{test_string}': {result} == {expected}: {result == expected}")
        elif test_type == 'extract':
            result = patterns.extract(pattern_name, test_string)
            print(f"Testing {pattern_name} extract from '{test_string}': {result} == {expected}: {result == expected}")

if __name__ == "__main__":
    test_regex_patterns()