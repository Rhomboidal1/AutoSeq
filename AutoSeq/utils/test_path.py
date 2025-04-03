# test_path.py
import os
import sys
# Calculate the project's root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

# Add the project's root directory to sys.path
sys.path.append(project_root)

# Now we can import config.py
from AutoSeq.config import MseqConfig  
from AutoSeq.utils.path_utils import PathUtilities

def test_path_utilities():
    path_utils = PathUtilities()
    
    # Test filename normalization
    filenames = [
        # Original, Expected normalized (adjusted to match your implementation)
        ("{01A}Sample1_KseqF.ab1", "Sample1_KseqF"),
        ("Sample+With*Illegal:Chars.ab1", "Sample&With-Illegal-Chars"), # Updated expected
        ("Sample_Premixed_RTI.ab1", "Sample"),
        ("{07E}{06G}940.9.H446_940R{PCR2961exp1}{2_28}.ab1", "940.9.H446_940R"),
    ]
    
    print("Testing filename normalization:")
    for original, expected in filenames:
        normalized = path_utils.normalize_filename(original)
        print(f"  {original} -> {normalized} == {expected}: {normalized == expected}")
    
    # Test I-number extraction
    inumber_tests = [
        ("BioI-12345_Customer_67890", "12345"),
        ("Path/To/BioI-54321", "54321"),
        ("No match here", None),
    ]
    
    print("\nTesting I-number extraction:")
    for test_string, expected in inumber_tests:
        result = path_utils.get_inumber_from_name(test_string)
        print(f"  {test_string} -> {result} == {expected}: {result == expected}")
    
    # Test PCR number extraction
    pcr_tests = [
        ("{01A}Sample_Name{PCR1234exp1}.ab1", "1234"),
        ("Sample_without_pcr.ab1", None),
    ]
    
    print("\nTesting PCR number extraction:")
    for test_string, expected in pcr_tests:
        result = path_utils.get_pcr_number(test_string)
        print(f"  {test_string} -> {result} == {expected}: {result == expected}")
    
    # Test folder type detection
    folder_tests = [
        # Folder name, expected is_bioi, expected is_order, expected is_pcr, expected is_plate
        ("BioI-12345", True, False, False, False),
        ("BioI-12345_Customer_67890", True, True, False, False),
        ("P12345_Test", False, False, False, True), # Fixed: this is a plate folder
        ("FB-PCR1234_5678", False, False, True, False),
    ]

    print("\nTesting folder type detection:")
    for folder, exp_bioi, exp_order, exp_pcr, exp_plate in folder_tests:
        is_bioi = path_utils.is_bioi_folder(folder)
        is_order = path_utils.is_order_folder(folder)
        is_pcr = path_utils.is_pcr_folder(folder)
        is_plate = path_utils.is_plate_folder(folder)
        print(f"  {folder}: bioi={is_bioi}=={exp_bioi}, order={is_order}=={exp_order}, pcr={is_pcr}=={exp_pcr}, plate={is_plate}=={exp_plate}")

if __name__ == "__main__":
    test_path_utilities()