# file_system.py - File system operations
import os
import re
import shutil
import gc
from zipfile import ZipFile, ZIP_DEFLATED
from datetime import datetime, timedelta
import sys
import time
import numpy as np
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from AutoSeq.utils.path_utils import PathUtilities
from AutoSeq.utils.log_service import LoggingService

class FileSystem:
    """
    Core file system operations for AutoSeq
    
    Provides unified interface for file operations with logging and error handling
    """
    
    def __init__(self, config, path_utils=None, logger=None):
        """Initialize with configuration"""
        self.config = config
        self.path_utils = path_utils or PathUtilities()
        
        # Set up logging
        self._logger = logger or LoggingService(__name__)
        self.log = self._logger.info
        
        # Cache for directory contents
        self.directory_cache = {}
    
    # Directory Operations
    def get_directory_contents(self, path, refresh=False):
        """Get directory contents with caching"""
        if path not in self.directory_cache or refresh:
            if not os.path.exists(path):
                self.directory_cache[path] = []
                return []

            try:
                contents = os.listdir(path)
                self.directory_cache[path] = contents
            except Exception as e:
                self.log(f"Error reading directory {path}: {e}")
                self.directory_cache[path] = []

        return self.directory_cache[path]
    
    def get_folders(self, path, pattern=None):
        """Get folders matching an optional regex pattern"""
        folder_list = []
        for item in self.get_directory_contents(path):
            full_path = os.path.join(path, item)
            if os.path.isdir(full_path):
                if pattern is None or re.search(pattern, item.lower()):
                    folder_list.append(full_path)
        return folder_list
    
    def get_files_by_extension(self, folder, extension):
        """Get all files with specified extension in a folder"""
        files = []
        for item in self.get_directory_contents(folder):
            if item.endswith(extension):
                files.append(os.path.join(folder, item))
        return files
    
    def contains_file_type(self, folder, extension):
        """Check if folder contains files with specified extension"""
        for item in self.get_directory_contents(folder):
            if item.endswith(extension):
                return True
        return False
    
    def create_folder_if_not_exists(self, path):
        """Create folder if it doesn't exist"""
        if not os.path.exists(path):
            try:
                os.makedirs(path)
                self.log(f"Created folder: {path}")
            except Exception as e:
                self.log(f"Error creating folder {path}: {e}")
                return None
        return path
    
    # File Operations
    def move_file(self, source, destination, create_parents=True):
        """
        Move a file with error handling
        
        Args:
            source: Source file path
            destination: Destination file path
            create_parents: Create parent directories if needed
            
        Returns:
            bool: True if successful
        """
        try:
            # Create parent directory if it doesn't exist
            if create_parents:
                parent_dir = os.path.dirname(destination)
                if not os.path.exists(parent_dir):
                    os.makedirs(parent_dir)
            
            # Move the file
            shutil.move(source, destination)
            self.log(f"Moved file: {os.path.basename(source)} -> {os.path.basename(destination)}")
            return True
        except Exception as e:
            self.log(f"Error moving file {source}: {e}")
            return False
    
    def move_folder(self, source, destination, max_retries=3, delay=1.0):
        """
        Move folder with proper error handling and retries
        
        Args:
            source: Source folder path
            destination: Destination folder path
            max_retries: Maximum number of retries (default 3)
            delay: Delay between retries in seconds (default 1.0)
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Make sure destination parent folder exists
        dest_parent = os.path.dirname(destination)
        if not os.path.exists(dest_parent):
            try:
                os.makedirs(dest_parent)
            except Exception as e:
                self.log(f"Error creating destination parent folder: {e}")
                return False
        
        # Try multiple times with delay between attempts
        for attempt in range(max_retries):
            try:
                # Force garbage collection to release file handles
                gc.collect()
                
                # Attempt to move the folder
                shutil.move(source, destination)
                self.log(f"Successfully moved {os.path.basename(source)} to {os.path.basename(destination)}")
                return True
            except Exception as e:
                self.log(f"Error moving folder on attempt {attempt+1}/{max_retries}: {e}")
                # Wait before next attempt
                if attempt < max_retries - 1:
                    time.sleep(delay)
        
        self.log(f"Failed to move folder after {max_retries} attempts: {os.path.basename(source)}")
        return False
    
    def rename_file_without_braces(self, file_path):
        """Rename a file to remove anything in braces"""
        if '{' not in file_path and '}' not in file_path:
            return file_path

        dir_name = os.path.dirname(file_path)
        base_name = os.path.basename(file_path)
        new_name = self.path_utils.remove_brace_content(base_name)

        new_path = os.path.join(dir_name, new_name)

        try:
            if os.path.exists(file_path):
                os.rename(file_path, new_path)
                self.log(f"Renamed {base_name} to {new_name}")
                return new_path
        except Exception as e:
            self.log(f"Error renaming file {file_path}: {e}")

        return file_path
    
    # Zip operations
    def check_for_zip(self, folder_path):
        """Check if folder contains any zip files"""
        for item in self.get_directory_contents(folder_path):
            file_path = os.path.join(folder_path, item)
            if os.path.isfile(file_path) and file_path.endswith(self.config.ZIP_EXTENSION):
                return True
        return False

    def zip_files(self, source_folder, zip_path, file_extensions=None, exclude_extensions=None):
        """
        Create a zip file from files in source_folder matching extensions
        
        Args:
            source_folder: Folder containing files to zip
            zip_path: Path for the output zip file
            file_extensions: List of file extensions to include (None = all files)
            exclude_extensions: List of file extensions to exclude
            
        Returns:
            bool: True if successful
        """
        try:
            with ZipFile(zip_path, 'w') as zip_file:
                files_added = 0
                
                for item in self.get_directory_contents(source_folder):
                    # Convert item to string if needed
                    item_str = str(item)
                    file_path = os.path.join(source_folder, item_str)
                    
                    # Skip directories and non-matching files
                    if not os.path.isfile(file_path):
                        continue
                        
                    if file_extensions and not any(item_str.endswith(ext) for ext in file_extensions):
                        continue

                    if exclude_extensions and any(item_str.endswith(ext) for ext in exclude_extensions):
                        continue

                    # Add file to zip
                    zip_file.write(file_path, arcname=item_str, compress_type=ZIP_DEFLATED)
                    files_added += 1
                    
            self.log(f"Created zip file with {files_added} files: {os.path.basename(zip_path)}")
            return True
        except Exception as e:
            self.log(f"Error creating zip file {zip_path}: {e}")
            return False

    def get_zip_contents(self, zip_path):
        """Get list of files in a zip archive"""
        try:
            with ZipFile(zip_path, 'r') as zip_ref:
                return zip_ref.namelist()
        except Exception as e:
            self.log(f"Error reading zip file {zip_path}: {e}")
            return []

    def copy_zip_to_dump(self, zip_path, dump_folder):
        """Copy zip file to dump folder"""
        if not os.path.exists(dump_folder):
            os.makedirs(dump_folder)

        dest_path = os.path.join(dump_folder, os.path.basename(zip_path))
        try:
            shutil.copyfile(zip_path, dest_path)
            self.log(f"Copied zip to dump folder: {os.path.basename(zip_path)}")
            return dest_path
        except Exception as e:
            self.log(f"Error copying zip to dump folder: {e}")
            return None
    
    # Data loading
    def load_order_key(self, key_file_path):
        """Load the order key file"""
        try:
            return np.loadtxt(key_file_path, dtype=str, delimiter='\t')
        except Exception as e:
            self.log(f"Error loading order key file: {e}")
            return None
    
    # Date-based operations
    def get_most_recent_inumber(self, path):
        """Find the most recent I number based on folder modification times"""
        try:
            # Current timestamp and cutoff (7 days ago)
            current_timestamp = datetime.now().timestamp()
            cutoff_timestamp = current_timestamp - (7 * 24 * 3600)

            recent_dirs = []

            # Get folders modified in the last 7 days
            with os.scandir(path) as entries:
                for entry in entries:
                    if entry.is_dir():
                        last_modified_timestamp = entry.stat().st_mtime
                        if last_modified_timestamp >= cutoff_timestamp:
                            recent_dirs.append(entry.name)

            # Sort folders by modification time (newest first)
            sorted_dirs = sorted(recent_dirs, key=lambda f: os.path.getmtime(os.path.join(path, f)), reverse=True)

            # Extract I number from the most recent folder
            if sorted_dirs:
                inum = self.path_utils.get_inumber_from_name(sorted_dirs[0])
                self.log(f"Found most recent I number: {inum}")
                return inum

            return None
        except Exception as e:
            self.log(f"Error getting most recent I number: {e}")
            return None

    def get_recent_files(self, paths, days=None, hours=None):
        """
        Get list of files modified within specified time period
        
        Args:
            paths: List of paths to search
            days: Number of days to look back (default: None)
            hours: Number of hours to look back (default: None)
            
        Returns:
            List of recently modified filenames
        """
        # Set cutoff date based on days or hours
        current_date = datetime.now()
        if days:
            cutoff_date = current_date - timedelta(days=days)
        elif hours:
            cutoff_date = current_date - timedelta(hours=hours)
        else:
            cutoff_date = current_date - timedelta(days=1)  # Default to 1 day

        # Collect recent files from all specified paths
        file_info_list = []
        for directory in paths:
            try:
                with os.scandir(directory) as entries:
                    for entry in entries:
                        if entry.is_file():
                            last_modified_timestamp = entry.stat().st_mtime
                            last_modified_date = datetime.fromtimestamp(last_modified_timestamp)

                            if last_modified_date >= cutoff_date and entry.name.endswith('.txt'):
                                file_info_list.append((entry.name, last_modified_timestamp))
            except Exception as e:
                self.log(f"Error scanning directory {directory}: {e}")

        # Sort by modification time (newest first)
        sorted_files = sorted(file_info_list, key=lambda x: x[1], reverse=True)

        # Return just the file names
        return [file_info[0] for file_info in sorted_files]

    def get_inumbers_greater_than(self, files, lower_inum):
        """Get files with I number greater than specified value"""
        if not lower_inum:
            return files

        try:
            lower_inum_int = int(lower_inum)
            result = []

            for file_name in files:
                inum = self.path_utils.get_inumber_from_name(file_name)
                if inum and int(inum) > lower_inum_int:
                    result.append(file_name)

            return result
        except ValueError:
            # If conversion to int fails, return the original list
            return files


# Test code
if __name__ == "__main__":
    from AutoSeq.config import MseqConfig
    import tempfile
    
    def test_file_system():
        print("Testing FileSystem class...")
        
        # Create test config
        config = MseqConfig()
        
        # Create file system with logging
        fs = FileSystem(config)
        
        # Test with temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            print(f"\nTest directory: {temp_dir}")
            
            # Test directory creation
            test_subdir = os.path.join(temp_dir, "test_subdir")
            fs.create_folder_if_not_exists(test_subdir)
            print(f"Created folder: {test_subdir}, exists: {os.path.exists(test_subdir)}")
            
            # Test file creation and moving
            test_file1 = os.path.join(temp_dir, "test_file1.txt")
            test_file2 = os.path.join(test_subdir, "test_file2.txt")
            
            # Create test files
            with open(test_file1, "w") as f:
                f.write("Test content 1")
            
            with open(test_file2, "w") as f:
                f.write("Test content 2")
            
            # Test moving file
            dest_file = os.path.join(test_subdir, "moved_file.txt")
            fs.move_file(test_file1, dest_file)
            print(f"Moved file exists: {os.path.exists(dest_file)}")
            
            # Test file with braces
            brace_file = os.path.join(temp_dir, "{01A}test{PCR123}file.txt")
            with open(brace_file, "w") as f:
                f.write("File with braces")
            
            # Test renaming without braces
            renamed_file = fs.rename_file_without_braces(brace_file)
            print(f"Renamed file: {os.path.basename(renamed_file)}")
            
            # Test directory listing
            contents = fs.get_directory_contents(temp_dir)
            print(f"Directory contents: {contents}")
            
            # Test zip creation
            zip_path = os.path.join(temp_dir, "test.zip")
            fs.zip_files(temp_dir, zip_path)
            print(f"Zip created: {os.path.exists(zip_path)}")
            
            # Test zip contents
            if os.path.exists(zip_path):
                contents = fs.get_zip_contents(zip_path)
                print(f"Zip contents: {contents}")
        
        print("\nFileSystem tests completed")
    
    test_file_system()