import os
import shutil

def flatten_folder(root_folder):
    for dirpath, dirnames, filenames in os.walk(root_folder, topdown=False):
        for filename in filenames:
            source_path = os.path.join(dirpath, filename)
            destination_path = os.path.join(root_folder, filename)
            shutil.move(source_path, destination_path)
        
        # Remove the now-empty directories (except root)
        if dirpath != root_folder:
            os.rmdir(dirpath)


path = r"Descargadas"

# Example usage:
flatten_folder(path)
