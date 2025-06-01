import pandas as pd

# User inputs
xlsx_file_name = input("Enter the name of your updated .xlsx file: ")
sheet_name = input("Enter the sheet name: ")
csv_file_name = input("Enter the name for the new .csv file: ")

# Read Excel and convert to CSV
try:
    df = pd.read_excel(xlsx_file_name, sheet_name=sheet_name)
    df.to_csv(csv_file_name, index=False, encoding="utf-8-sig")
    print(f"Successfully saved to {csv_file_name}")
except Exception as e:
    print(f"Error: {e}")