import os
import glob

def remove_all_files_in_folder(folder_path):
    """
    Deletes all files in the specified folder without deleting the folder itself.
    
    Parameters:
    folder_path (str): The path to the folder where files should be deleted.
    """
    # Ensure the folder path is valid
    if not os.path.isdir(folder_path):
        print(f"The path {folder_path} is not a valid directory.")
        return
    
    # Get all file paths in the folder
    files = glob.glob(os.path.join(folder_path, '*'))
    
    # Iterate over the files and delete them
    for file in files:
        try:
            if os.path.isfile(file):
                os.remove(file)
                print(f"Deleted file: {file}")
        except Exception as e:
            print(f"Error deleting file {file}: {e}")