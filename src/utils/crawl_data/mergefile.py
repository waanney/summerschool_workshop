import pandas as pd

# List of Excel files to merge
file_list = [
    "vitamin_supplements_20250713_092744.xlsx",
    "bone_joint_medicines_20250713_092321.xlsx",
    "dermatology_medicines_20250713_092037.xlsx",
    "allergy_medicines_20250713_091532.xlsx",
    "pain_fever_antiinflammatory_20250713_093752.xlsx",
    "respiratory_medicines_20250713_094240.xlsx",
    "antibiotics_antifungal_20250713_094522.xlsx",
    "ear_nose_throat_medicines_20250713_095324.xlsx"
]

# Combine all DataFrames
all_dfs = []
for file in file_list:
    df = pd.read_excel(file)
    all_dfs.append(df)

# Merge and remove duplicates based on 'Medicine Name'
df_final = pd.concat(all_dfs, ignore_index=True)
df_final.drop_duplicates(subset=["Medicine Name"], keep="last", inplace=True)

# Save the merged file
df_final.to_excel("merged_medicines.xlsx", index=False)
print("✅ Merged Excel file saved as 'merged_medicines.xlsx'")
