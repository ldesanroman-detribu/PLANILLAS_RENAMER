import os
import pandas as pd

# CONFIGURE HERE:
folder_path = r"Final"
csv_path = r"Nombrador.csv"
original_column = "Old Filename"  # Name of the column with the current filenames
corrected_column = "Final"  # Name of the column with the new filenames

# Load the CSV file
df = pd.read_csv(csv_path, encoding="latin1", sep=";", quotechar='"')

for index, row in df.iterrows():
    original_name = row[original_column]
    new_name = row[corrected_column]

    old_path = os.path.join(folder_path, original_name)
    new_path = os.path.join(folder_path, new_name)

    if not os.path.exists(old_path):
        print(f"⚠️  Archivo no encontrado: {original_name}")
        continue  # No se cae, sigue con el siguiente

    if os.path.exists(new_path):
        print(f"⚠️  Ya existe destino: {new_name}")
        continue  # No se cae, sigue con el siguiente

    # Ahora sí, renombrar
    os.rename(old_path, new_path)
    print(f"✅ Renombrado: {original_name} -> {new_name}")
