# test_logging.py
import os
import sys
# Calculate the project's root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

# Add the project's root directory to sys.path
sys.path.append(project_root)

# Now we can import config.py
from AutoSeq.config import MseqConfig  
import tempfile
import logging as py_logging 
from AutoSeq.utils.log_service import setup_logger, LoggingService 

def test_logging():
    # Create a temporary directory that we'll manage manually
    temp_dir = tempfile.mkdtemp()
    try:
        print(f"Testing logging to temporary directory: {temp_dir}")
        
        # Test basic logger setup
        logger = setup_logger("test_logger", log_dir=temp_dir)
        logger.info("Test info message")
        logger.warning("Test warning message")
        logger.error("Test error message")
        
        # Check if log file was created
        log_files = os.listdir(temp_dir)
        print(f"Log files created: {log_files}")
        
        if log_files:
            log_path = os.path.join(temp_dir, log_files[0])
            print(f"First few lines of log file content:")
            with open(log_path, 'r') as f:
                for i, line in enumerate(f):
                    if i < 3:  # Just show first 3 lines
                        print(f"  {line.strip()}")
        
        # Test LoggingService
        print("\nTesting LoggingService class:")
        service = LoggingService("test_service", log_dir=temp_dir)
        service.info("Service info message")
        service.warning("Service warning message")
        service.error("Service error message")
        
        print("\nAll logging tests completed successfully!")
        
        # Important: Close all handlers before deleting files
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
            
        # Also close the service's logger handlers
        for handler in service.logger.handlers[:]:
            handler.close()
            service.logger.removeHandler(handler)
        
    finally:
        # Clean up temporary directory
        try:
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)
            print(f"Temporary directory {temp_dir} removed successfully")
        except Exception as e:
            print(f"Could not remove temporary directory {temp_dir}: {e}")

if __name__ == "__main__":
    test_logging()