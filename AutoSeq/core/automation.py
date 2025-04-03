# automation.py - MSeq UI automation with compositional design
import os
import sys
import time
import re
import logging
import tkinter as tk
from tkinter import filedialog

# Calculate the project's root directory
def get_project_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.dirname(os.path.dirname(script_dir))  # Go up two levels

project_root = get_project_root()

# Add the project's root directory to sys.path
sys.path.append(project_root)

from AutoSeq.config import MseqConfig
from AutoSeq.utils import LoggingService

def get_folder_from_user():
    print("Opening folder selection dialog...")
    root = tk.Tk()
    root.withdraw()
    root.update()  # Add this line - force an update
    
    folder_path = filedialog.askdirectory(
        title="Select today's data folder to sort",
        mustexist=True
    )
    
    root.destroy()
    return folder_path

"""
This module provides UI automation for the mSeq software using a composition-based design.
It handles connecting to mSeq, navigating the UI, and processing folders of sequence files.

Key components:
- DialogHandler: Handles all dialog-related operations
- FileNavigator: Manages file/folder tree navigation
- ProcessMonitor: Tracks job completion and status
- MseqAutomation: Main class that composes other components
"""

class DialogHandler:
    """Handles dialog interactions for MSeq automation"""
    
    def __init__(self, config, logger=None):
        """Initialize with configuration and logger"""
        self.config = config
        self.logger = logger or LoggingService(__name__)
        
        # Set timing values based on OS
        self.click_delay = 0.2
        self.expand_delay = 0.3
        
        # Define standard timeout values from config
        self.timeouts = config.TIMEOUTS
    
    def wait_for_dialog(self, app, dialog_type):
        """Wait for a specific dialog to appear"""
        timeout = self.timeouts.get(dialog_type, 5)
        
        try:
            if dialog_type == "browse_dialog":
                return timings.wait_until(timeout=timeout, retry_interval=0.1,
                                        func=lambda: app.window(title_re='Browse.*Folder').exists(),
                                        value=True)
            elif dialog_type == "preferences":
                return timings.wait_until(timeout=timeout, retry_interval=0.1,
                                        func=lambda: (app.window(title='Mseq Preferences').exists() or
                                                    app.window(title='mSeq Preferences').exists()),
                                        value=True)
            elif dialog_type == "copy_files":
                return timings.wait_until(timeout=timeout, retry_interval=0.1,
                                        func=lambda: app.window(title_re='Copy.*sequence files').exists(),
                                        value=True)
            elif dialog_type == "error_window":
                return timings.wait_until(timeout=timeout, retry_interval=0.3,
                                        func=lambda: app.window(title_re='.*[Ee]rror.*').exists(),
                                        value=True)
            elif dialog_type == "call_bases":
                return timings.wait_until(timeout=timeout, retry_interval=0.3,
                                        func=lambda: app.window(title_re='Call bases.*').exists(),
                                        value=True)
            elif dialog_type == "read_info":
                return timings.wait_until(timeout=timeout, retry_interval=0.1,
                                        func=lambda: app.window(title_re='Read information for.*').exists(),
                                        value=True)
            return False
        except timings.TimeoutError:
            return False
    
    def get_dialog(self, app, title_or_pattern, use_regex=False):
        """Get a dialog window by title or pattern"""
        try:
            if use_regex:
                return app.window(title_re=title_or_pattern)
            else:
                return app.window(title=title_or_pattern)
        except:
            return None
    
    def get_browse_dialog(self, app):
        """Get browse dialog window with better reliability"""
        for title in ['Browse For Folder', 'Browse for Folder']:
            dialog = self.get_dialog(app, title)
            if dialog and dialog.exists():
                return dialog
        
        # Last resort: try with regex
        return self.get_dialog(app, 'Browse.*Folder', use_regex=True)
    
    def get_dialog_by_titles(self, app, titles):
        """Try to get a dialog window by multiple possible titles"""
        for title in titles:
            dialog = self.get_dialog(app, title)
            if dialog and dialog.exists():
                return dialog
        return None
    
    def click_button(self, dialog, button_titles):
        """Click a button in a dialog using multiple possible titles"""
        for title in button_titles:
            try:
                button = dialog.child_window(title=title, class_name="Button")
                if button.exists():
                    button.click_input()
                    time.sleep(self.click_delay)
                    return True
            except:
                pass
        
        # Try pressing Enter as fallback
        try:
            dialog.set_focus()
            send_keys('{ENTER}')
            time.sleep(self.click_delay)
            return True
        except:
            return False
    
    def select_all_files(self, dialog):
        """Select all files in a dialog"""
        try:
            # Try Windows 10 approach first
            shell_view = dialog.child_window(title="ShellView", class_name="SHELLDLL_DefView")
            if shell_view.exists():
                list_view = shell_view.child_window(class_name="DirectUIHWND")
                if list_view.exists():
                    list_view.click_input()
                    send_keys('^a')  # Ctrl+A
                    return True
        except:
            pass
        
        try:
            # Try Windows 11 approach
            list_view = dialog.child_window(class_name="DirectUIHWND")
            if list_view.exists():
                list_view.click_input()
                send_keys('^a')  # Ctrl+A
                return True
        except:
            pass
        
        # Last resort - click in the middle and press Ctrl+A
        try:
            rect = dialog.rectangle()
            dialog.click_input(coords=((rect.right - rect.left) // 2, (rect.bottom - rect.top) // 2))
            time.sleep(self.click_delay)
            send_keys('^a')  # Ctrl+A
            return True
        except:
            return False
    
    def close_all_read_info_dialogs(self, app):
        """Close all Read information for... dialogs that might be open"""
        try:
            # Find all Read information windows
            read_windows = findwindows.find_elements(
                title_re='Read information for.*', 
                process=app.process
            )
            
            for win in read_windows:
                try:
                    read_dialog = app.window(handle=win.handle)
                    self.logger.info(f"Closing read information dialog: {read_dialog.window_text()}")
                    read_dialog.close()
                except Exception as e:
                    self.logger.warning(f"Error closing read dialog: {e}")
            
            return len(read_windows) > 0
        except Exception as e:
            self.logger.warning(f"Error finding/closing read information dialogs: {e}")
            return False


class FileNavigator:
    """Handles file system navigation in dialogs"""
    
    def __init__(self, config, logger=None):
        """Initialize with configuration and logger"""
        self.config = config
        self.logger = logger or LoggingService(__name__)
        self.network_drives = config.NETWORK_DRIVES
        
        # Timing values
        self.click_delay = 0.2
        self.expand_delay = 0.3
    
    def get_tree_view(self, dialog):
        """Get tree view control from dialog"""
        try:
            # Try most reliable method first
            tree = dialog.child_window(class_name="SysTreeView32")
            if tree.exists():
                return tree
        except:
            pass
        
        # Try with known titles as fallback
        for title in ["Choose project directory", "Navigation Pane", "Tree View"]:
            try:
                tree = dialog.child_window(title=title, class_name="SysTreeView32")
                if tree.exists():
                    return tree
            except:
                pass
        
        return None
    
    def navigate_to_folder(self, dialog, path):
        """Navigate to a specific folder in tree view"""
        dialog.set_focus()
        
        # Get tree view
        tree_view = self.get_tree_view(dialog)
        if not tree_view:
            self.logger.error("Could not find tree view control")
            return False
        
        # Parse path
        if ":" in path:
            parts = path.split("\\")
            drive = parts[0]  # e.g., "C:"
            folders = parts[1:] if len(parts) > 1 else []
        else:
            parts = path.split("\\")
            drive = "\\" + "\\".join(parts[:3])  # e.g., \\server\share
            folders = parts[3:] if len(parts) > 3 else []
        
        # Find Desktop in tree view roots
        desktop_item = None
        for item in tree_view.roots():
            if "Desktop" in item.text():
                desktop_item = item
                break
        
        if not desktop_item:
            self.logger.error("Could not find Desktop in tree view")
            return False
        
        # Click and expand Desktop
        desktop_item.click_input()
        time.sleep(self.click_delay)
        desktop_item.expand()
        time.sleep(self.expand_delay)
        
        # Find This PC under Desktop
        this_pc_item = None
        for child in desktop_item.children():
            if any(term in child.text().lower() for term in ["pc", "computer"]):
                this_pc_item = child
                break
        
        if not this_pc_item:
            self.logger.error("Could not find This PC under Desktop")
            return False
        
        # Click and expand This PC
        this_pc_item.click_input()
        time.sleep(self.click_delay)
        this_pc_item.expand()
        time.sleep(self.expand_delay)
        
        # Find the drive
        drive_item = None
        for child in this_pc_item.children():
            # Support multiple drive name formats
            drive_text = child.text()
            
            # Extract drive letter for better matching
            drive_letter = None
            if ":" in drive_text:
                drive_letter_parts = re.findall(r'([A-Za-z]:)', drive_text)
                if drive_letter_parts:
                    drive_letter = drive_letter_parts[0]
            
            # Try different matching approaches
            if (drive_text == drive or                      # Exact match
                drive in drive_text or                      # Contains match
                (drive_letter and drive_letter.upper() == drive.upper())):  # Drive letter match
                drive_item = child
                break
        
        if not drive_item:
            # Check for mapped network drives
            mapped_name = self.network_drives.get(drive, None)
            if mapped_name:
                for child in this_pc_item.children():
                    if mapped_name in child.text():
                        drive_item = child
                        break
        
        if not drive_item:
            self.logger.error(f"Could not find drive {drive} in This PC")
            return False
        
        # Select the drive
        drive_item.click_input()
        time.sleep(self.click_delay)
        
        # If we only need to navigate to drive level, we're done
        if not folders:
            return True
        
        # Navigate through folder hierarchy
        current_item = drive_item
        for folder in folders:
            # Expand current folder
            current_item.expand()
            time.sleep(self.expand_delay)
            
            # Find the next folder
            next_item = None
            
            # Try exact match first
            for child in current_item.children():
                if child.text() == folder:
                    next_item = child
                    break
            
            # If not found, try partial match
            if not next_item:
                for child in current_item.children():
                    if folder.lower() in child.text().lower():
                        next_item = child
                        break
            
            if not next_item:
                self.logger.error(f"Could not find folder {folder}")
                return False
            
            # Select the folder
            next_item.click_input()
            time.sleep(self.click_delay)
            current_item = next_item
        
        # Make sure the final folder is selected
        current_item.click_input()
        return True


class ProcessMonitor:
    """Monitors MSeq processes and completion"""
    
    def __init__(self, config, dialog_handler, logger=None):
        """Initialize with configuration, dialog handler, and logger"""
        self.config = config
        self.dialog_handler = dialog_handler
        self.logger = logger or LoggingService(__name__)
        
        # Timing values
        self.interval = 0.5
        self.max_wait = config.TIMEOUTS.get("process_completion", 30)
    
    def wait_for_completion(self, app, folder_path):
        """Wait for MSeq processing to complete"""
        elapsed = 0
        
        while elapsed < self.max_wait:
            # Check for low quality dialog
            for title in ["Low quality files skipped", "Quality files skipped"]:
                dialog = app.window(title=title)
                if dialog.exists():
                    self.dialog_handler.click_button(dialog, ["OK"])
                    return True
            
            # Check for read info dialog (handle possible multiple windows)
            has_read_dialogs = self.dialog_handler.close_all_read_info_dialogs(app)
            if has_read_dialogs:
                # If we found and closed any read dialogs, consider it a completion signal
                return True
            
            # Check for output text files - most reliable completion signal
            txt_count = self.check_output_files(folder_path)
            if txt_count >= 5:
                return True
            
            # Wait before checking again
            time.sleep(self.interval)
            elapsed += self.interval
        
        return False
    
    def check_output_files(self, folder_path):
        """Check if output text files exist in the folder"""
        txt_count = 0
        for item in os.listdir(folder_path):
            if any(item.endswith(ext) for ext in self.config.TEXT_FILES):
                txt_count += 1
        
        return txt_count


class MseqAutomation:
    """Streamlined automation for controlling mSeq software using composition"""
    
    def __init__(self, config, logger=None):
        """Initialize the automation with configuration settings"""
        self.config = config
        self.logger = logger or LoggingService(__name__)
        
        # Create component objects
        self.dialog_handler = DialogHandler(config, self.logger)
        self.file_navigator = FileNavigator(config, self.logger)
        self.process_monitor = ProcessMonitor(config, self.dialog_handler, self.logger)
        
        # Application state
        self.app = None
        self.main_window = None
        self.first_time_browsing = True
        
        self.logger.info("MseqAutomation initialized")
    
    def connect_or_start_mseq(self):
        """Connect to existing mSeq instance or start a new one"""
        try:
            # Try to connect to an existing instance
            self.app = Application(backend='win32').connect(title_re='[mM]seq.*', timeout=1)
            self.logger.info("Connected to existing mSeq instance")
        except (ElementNotFoundError, timings.TimeoutError):
            # Start a new instance
            self.logger.info("Starting new mSeq instance")
            start_cmd = f'cmd /c "cd /d {self.config.MSEQ_PATH} && {self.config.MSEQ_EXECUTABLE}"'
            
            try:
                self.app = Application(backend='win32').start(start_cmd, wait_for_idle=False)
                self.app.connect(title='mSeq', timeout=self.dialog_handler.timeouts["browse_dialog"])
            except Exception as e:
                self.logger.error(f"Failed to start mSeq: {e}")
                raise
        except ElementAmbiguousError:
            # Handle multiple instances
            self.app = Application(backend='win32').connect(title_re='[mM]seq.*', found_index=0)
            self.logger.warning("Multiple mSeq windows found, connecting to first instance")
        
        # Get the main window
        for title_pattern in ['mSeq.*', 'Mseq.*']:
            try:
                self.main_window = self.app.window(title_re=title_pattern)
                if self.main_window.exists():
                    break
            except:
                pass
        
        if not self.main_window or not self.main_window.exists():
            self.logger.error("Could not find mSeq main window")
            raise RuntimeError("Could not find mSeq main window")
            
        return self.app, self.main_window
    
    def connect_or_start_mseq(self):
        """Connect to existing mSeq instance or start a new one"""
        try:
            # Try to connect to an existing instance
            self.app = Application(backend='win32').connect(title_re='[mM]seq.*', timeout=1)
            self.logger.info("Connected to existing mSeq instance")
        except (ElementNotFoundError, timings.TimeoutError):
            # Start a new instance
            self.logger.info("Starting new mSeq instance")
            start_cmd = f'cmd /c "cd /d {self.config.MSEQ_PATH} && {self.config.MSEQ_EXECUTABLE}"'
            
            try:
                self.app = Application(backend='win32').start(start_cmd, wait_for_idle=False)
                self.app.connect(title='mSeq', timeout=self.timeouts["connect"])
            except Exception as e:
                self.logger.error(f"Failed to start mSeq: {e}")
                raise
        except ElementAmbiguousError:
            # Handle multiple instances
            self.app = Application(backend='win32').connect(title_re='[mM]seq.*', found_index=0)
            self.logger.warning("Multiple mSeq windows found, connecting to first instance")
        
        # Get the main window
        for title_pattern in ['mSeq.*', 'Mseq.*']:
            try:
                self.main_window = self.app.window(title_re=title_pattern)
                if self.main_window.exists():
                    break
            except:
                pass
        
        if not self.main_window or not self.main_window.exists():
            self.logger.error("Could not find mSeq main window")
            raise RuntimeError("Could not find mSeq main window")
            
        return self.app, self.main_window



    def process_folder(self, folder_path):
        """Process a folder with mSeq - streamlined version based on successful path"""
        if not os.path.exists(folder_path):
            self.logger.warning(f"Folder does not exist: {folder_path}")
            return False
        
        # Check for AB1 files
        ab1_files = [f for f in os.listdir(folder_path) if f.endswith(self.config.ABI_EXTENSION)]
        if not ab1_files:
            self.logger.warning(f"No AB1 files found in {folder_path}")
            return False
        
        self.logger.info(f"Processing folder with {len(ab1_files)} AB1 files: {folder_path}")
        
        # Close any existing Read information windows before starting
        if self.app:
            self.dialog_handler.close_all_read_info_dialogs(self.app)
        
        # Connect to mSeq and get main window if not already connected
        if not self.app or not self.main_window or not self.main_window.exists():
            self.app, self.main_window = self.connect_or_start_mseq()
        
        self.main_window.set_focus()
        
        # Start new project (Ctrl+N)
        send_keys('^n')
        self.logger.info("Sent Ctrl+N to start new project")
        
        # Wait for and handle Browse For Folder dialog
        dialog_found = self.dialog_handler.wait_for_dialog(self.app, "browse_dialog")
        if not dialog_found:
            self.logger.error("Browse For Folder dialog not found")
            return False
        
        browse_dialog = self.dialog_handler.get_browse_dialog(self.app)
        if not browse_dialog:
            self.logger.error("Could not get Browse For Folder dialog reference")
            return False
        
        # Add a delay for the first browsing operation
        if self.first_time_browsing:
            self.first_time_browsing = False
            time.sleep(1.0)
        
        # Navigate to the target folder
        if not self.file_navigator.navigate_to_folder(browse_dialog, folder_path):
            self.logger.error(f"Failed to navigate to {folder_path}")
            return False
        
        # Click OK button
        self.dialog_handler.click_button(browse_dialog, ["OK", "&OK"])
        
        # Handle mSeq Preferences dialog
        self.dialog_handler.wait_for_dialog(self.app, "preferences")
        pref_dialog = self.dialog_handler.get_dialog_by_titles(self.app, ['Mseq Preferences', 'mSeq Preferences'])
        if pref_dialog:
            self.dialog_handler.click_button(pref_dialog, ["&OK", "OK"])
        
        # Handle Copy sequence files dialog
        self.dialog_handler.wait_for_dialog(self.app, "copy_files")
        copy_dialog = self.app.window(title_re='Copy.*sequence files')
        if copy_dialog:
            # Select all files
            self.dialog_handler.select_all_files(copy_dialog)
            self.dialog_handler.click_button(copy_dialog, ["&Open", "Open"])
        
        # Handle File error dialog (appears due to non-sequence files)
        self.dialog_handler.wait_for_dialog(self.app, "error_window")
        error_dialog = self.dialog_handler.get_dialog_by_titles(self.app, ['File error', 'Error'])
        if error_dialog:
            self.dialog_handler.click_button(error_dialog, ["OK"])
        
        # Handle Call bases dialog
        self.dialog_handler.wait_for_dialog(self.app, "call_bases")
        call_bases_dialog = self.app.window(title_re='Call bases.*')
        if call_bases_dialog:
            self.dialog_handler.click_button(call_bases_dialog, ["&Yes", "Yes"])
        
        # Wait for processing to complete
        completion_success = self.process_monitor.wait_for_completion(self.app, folder_path)
        
        # Always close any Read information windows before returning
        self.dialog_handler.close_all_read_info_dialogs(self.app)
        
        if completion_success:
            self.logger.info(f"Successfully processed {folder_path}")
        else:
            self.logger.warning(f"Processing may not have completed properly for {folder_path}")
            return False
        
        return True
    
    def close(self):
        """Close the mSeq application"""
        if self.app:
            try:
                self.app.kill()
                self.logger.info("mSeq application closed")
            except Exception as e:
                self.logger.warning(f"Error closing mSeq: {e}")
                # Try alternative approach
                if self.main_window and self.main_window.exists():
                    try:
                        self.main_window.close()
                    except:
                        pass


# For testing
def main():
    # Get folder path first before any package imports
    data_folder = get_folder_from_user()
    
    if not data_folder:
        print("No folder selected, exiting")
        return

    from pywinauto import Application, timings, findwindows
    from pywinauto.keyboard import send_keys
    from pywinauto.findwindows import ElementNotFoundError, ElementAmbiguousError
    from AutoSeq.config import MseqConfig
    from AutoSeq.utils.log_service import LoggingService
    
    # Setup basic logging
    logger = LoggingService("test_automation")
    logger.info("Testing MseqAutomation")
    
    # Get config
    config = MseqConfig()
    
    # Create automation object
    automation = MseqAutomation(config, logger)
    
    # Get folder to process
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Select folder to process")
    
    if folder_path:
        logger.info(f"Selected folder: {folder_path}")
        
        # Process the folder
        success = automation.process_folder(folder_path)
        
        logger.info(f"Processing result: {'Success' if success else 'Failed'}")
        
        # Close automation
        automation.close()
    else:
        logger.info("No folder selected")

if __name__ == "__main__":
    main()