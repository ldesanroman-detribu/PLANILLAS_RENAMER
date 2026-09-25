import os
import re
from difflib import get_close_matches
import csv

# Define constants
months = ["ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO", 
 "JULIO", "AGOSTO", "SETIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"]
types = ["13AVA","PL","FR","SERVICIOS","KILOMETRAJE","COMISIONES","REINTEGRO","G-D","LIQUIDACION","PL1","PL2","ST","TP","VIATICOS","CC","BONOS"]
periods = ["A","M","Q1","Q2","U","S"]
coins = ["CRC", "USD"]
clients = [
    "ASESORES FINANCIEROS", "LIBERTAD ECONOMICA", "CR MEDICA", "TUALFIP", "TMB", "DAVIVIENDA BANCA",
    "PROGRAMA SEMILLA", "NOVA SPIRIT", "TWO SHOWS", "ONE", "BENDIG", "TIENDA CREATIVA", "COLOR SOLUTION",
    "CERRO MODESTO", "G-D", "DAVIVIENDA", "SKINCENTER SP", "CASA PAZ", "DAC CLINICALS", "ALPHATHENA", "M4GC",
    "TECHCO", "NEWCO", "RIGHT PEOPLE", "PVF SERVICIOS MULTIPLES", "PC SUPPORT", "ASOC SOL AMPO", "AMPO",
    "OPTIMAL LIVING", "DAIRY PACK", "CLINICAS MEDICAS", "MEDIRED", "JIMENEZ & TANZI", "INVERSIONES AMERICA",
    "RM LOGISTIC", "FACE AND BODY CARE", "FACE AND BODY", "BIG DATA", "TECH EQUILIBRIUM", "EQUILIBRIUM",
    "HOLISTIQUE", "SOEFE", "OPUL", "MEDISER", "ALL GYN", "NOVITEC", "AVD", "QSOFTWARE", "XPANDIA", "ENTRUST",
    "ENTRUST APCP", "FLAMINGO", "CALAHAN", "GRUPO BIENESTAR", "FLAMINGO URGENT CARE", "DAVIVIENDA EXPOMOVIL",
    "THE VAULT", "SOFTECH 1", "SOFTECH", "HIKRU S.A.", "CEA AUDIOLOGIA", "JLL", "SKINCENTER CURRIDABAT",
    "HIKRU LLC", "ESN", "LEAD PEOPLE", "EK", "CARSUPPLY", "SOFTECH 2", "RESTAURANTE PANDA", "DAVIVIENDA CYC",
    "DAVIVIENDA CREDITO Y COBRO", "TIS", "PANDA GERENCIAL", "NIGAMA", "KONSULTIVA", "PRITONIC",
    "DISTRIBUIDORA LA FORTUNA", "VIDA OPTIMA", "MADAM LYRA", "AVOCASH", "REPRESENTACIONES MEDICAS",
    "CREEKSOFTWARE LLC", "ESCUELA VETERINARIA", "SOFTWARECRAFT", "EKOMERCIO", "YIN YIN", "CORP ZAMORA",
    "MULTIROLLOS", "EXPOMOVIL", "NOSFORCE", "WELLCARE SOLUTION", "MZA", "ALESTE PADEL","LESSON ATLAS", "INNOVA",
    "PAW VET","LUXDERMA","SYT", "TROPIFOOD", "CACAO LOGIC","COLOR SOLUTION", "AEGIS", "ATMOSFERA_INC", "ATMOSFERA_SRL",
    "BARAK", "CISMA", "DIST_LA_FORTUNA", "JACO", "MANUEL ANTONIO", "TROPIFOODS", "JASUMI", "REBECHA_CHAVES", "ELBA",
    "SAMIA", "GMF", "ERIZOS", "CARACOL", "TWO_HEADS", "CREATE", "CRTV","TWO HEADS", "NPS", "PURDY_MOTOR", "COCO CR", "VERAT CAPITAL"
    ]   

def correct_month(word):
    matches = get_close_matches(word, months, n=1, cutoff=0.7)
    return matches[0] if matches else None

def categorize_token(token, next_token=None):
    # Month
    month = correct_month(token)
    if month:
        return ("month", month)
    
    # Year
    if token.isdigit() and 1900 <= int(token) <= 2100:
        return ("year", token)
    
    # Type
    if token in types:
        return ("type", token)
    
    # Period
    if token in periods:
        return ("period", token)
    
    # Coin
    if token in coins:
        return ("coin", token)
    
    # Try to match client names that might be multiple words (e.g., "TIENDA CREATIVA")
    if token in clients:
        return ("client", token)
    
    # Special handling for multi-token client names
    if next_token and (f"{token} {next_token}" in clients):
        return ("client", f"{token}_{next_token}")
    
    # Percentage (with pp)
    if re.match(r"^\d{1,3},\d{1,2}PP$", token) or re.match(r"^\d{1,3}PP$", token):
        return ("percentage", token)

    return ("other", token)

def process_filename(filename):
    name, ext = os.path.splitext(filename)
    tokens = name.split(" ")

    parts = {
        "month": None,
        "year": None,
        "type": None,
        "period": None,
        "client_name": [],
        "coin": None,
        "percentage": None,
        "others": []
    }

    i = 0
    while i < len(tokens):
        token = tokens[i]
        next_token = tokens[i + 1] if i + 1 < len(tokens) else None
        
        category, value = categorize_token(token, next_token)
        
        if category in parts and category != "client_name":
            parts[category] = value
        elif category == "client":
            parts["client_name"].append(value)  # Add client to the list
            if len(value.split("_")) > 1:
                i += 1  # Skip the next token since it's part of the client name
        elif category == "other":
            parts["others"].append(value)  # Add to "others"    
        i += 1 
        
    # Join client name with underscores, if present
    client_name = "_".join(parts["client_name"]) if parts["client_name"] else "CLIENT"
    
    # Join 'others' with underscores, if present
    others = "_".join(parts["others"]) if parts["others"] else ""

    # Form the new filename using all categorized parts
    new_name = f"{parts['month'] or 'MONTH'} {parts['year'] or 'YEAR'} {parts['type'] or 'TYPE'} {parts['period'] or 'PERIOD'} {client_name} {parts['coin'] or 'COIN'} {parts['percentage'] or 'PERCENTAGE'} {others}{ext}"
    
    return new_name

def process_folder(folder_path, csv_filename):
    # Open the CSV file for writing
    with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header row
        writer.writerow(["Old Filename", "New Filename"])
        
        # Iterate through files in the folder
        for filename in os.listdir(folder_path):
            if filename.startswith("~") or not filename.lower().endswith(('.pdf', '.docx', '.xlsx')):
                continue
            new_filename = process_filename(filename)
            
            if filename != new_filename:
                # Log the old and new filenames into the CSV file
                writer.writerow([filename, new_filename])
                
                print(f"Renaming:\n  From: {filename}\n  To:   {new_filename}\n")
                # Uncomment this to actually rename:
                # os.rename(os.path.join(folder_path, filename), os.path.join(folder_path, new_filename))

# Example usage: Set the folder path and CSV filename
process_folder(r"Descargadas", "renamed_files.csv")

