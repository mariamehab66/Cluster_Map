import pandas as pd
import json
import os

# Define the full path to the files
base_path = r'C:\Users\mariam\Downloads\clustering model'
avg_data_file = os.path.join(base_path, 'averaged_attributes_by_season.csv')
cluster_min_max_file = os.path.join(base_path, 'cluster_attributes_min_max_by_season.csv')
plant_mapping_file = os.path.join(base_path, 'cluster_season_plant_mapping.csv')

# Load data from CSV files
avg_data = pd.read_csv(avg_data_file)
cluster_min_max = pd.read_csv(cluster_min_max_file)
plant_mapping = pd.read_csv(plant_mapping_file)

# Handle missing values
avg_data = avg_data.fillna('null')
cluster_min_max = cluster_min_max.fillna('null')
plant_mapping = plant_mapping.fillna('null')

# Restructure avg_data to include Season column
seasonal_cols = [col for col in avg_data.columns if '_avg_' in col]
attributes = set(col.split('_avg_')[0] for col in seasonal_cols)
seasons = set(col.split('_avg_')[1] for col in seasonal_cols)

seasonal_data = []
for idx, row in avg_data.iterrows():
    for season in seasons:
        new_row = row[['LAT', 'LON', 'Cluster', 'elevation', 'land_cover', 'Distance_to_Nile_km', 'Distance_to_Nearest_Coast_km', 'City', 'GOV']].copy()
        new_row['Season'] = season.capitalize()
        for attr in attributes:
            col_name = f"{attr}_avg_{season}"
            if col_name in row:
                new_row[attr] = row[col_name] if pd.notna(row[col_name]) else 'null'
        seasonal_data.append(new_row)
seasonal_df = pd.DataFrame(seasonal_data)

# Convert cluster_min_max to the correct JSON format
cluster_min_max_dict = {}
for idx, row in cluster_min_max.iterrows():
    cluster = str(row['Cluster']) if pd.notna(row['Cluster']) else '0'
    season = str(row['Season']) if pd.notna(row['Season']) else 'Unknown'
    key = f"{cluster}_{season}"
    row_dict = row.drop(['Cluster', 'Season']).to_dict()
    cluster_min_max_dict[key] = {k: None if v == 'null' else v for k, v in row_dict.items()}

# Convert plant_mapping to the correct JSON format
plant_mapping_dict = {}
for idx, row in plant_mapping.iterrows():
    cluster = str(row['Cluster']) if pd.notna(row['Cluster']) else '0'
    season = str(row['Season']) if pd.notna(row['Season']) else 'Unknown'
    key = f"{cluster}_{season}"
    if key not in plant_mapping_dict:
        plant_mapping_dict[key] = []
    plant_mapping_dict[key].append(row['Plant'] if pd.notna(row['Plant']) else 'Unknown')

# Convert data to JSON-compatible format
data = {
    'avgData': avg_data.replace('null', None).to_dict('records'),
    'seasonalDf': seasonal_df.replace('null', None).to_dict('records'),
    'clusterMinMax': cluster_min_max_dict,
    'plantMapping': plant_mapping_dict
}

# Save to a JSON file
with open('data.json', 'w') as f:
    json.dump(data, f, indent=2)