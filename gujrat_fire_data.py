import pandas as pd

# 🔗 Step 1: Download fire data (manually or programmatically)
url = "https://firms.modaps.eosdis.nasa.gov/data/active_fire/c6/csv/MODIS_C6_1_Global_24h.csv"
df = pd.read_csv(url)

# 🔍 Step 2: Filter for Gujarat (approximate lat/lon box)
lat_min, lat_max = 20.0, 24.75
lon_min, lon_max = 68.0, 74.5

gujarat_df = df[
    (df['latitude'] >= lat_min) & (df['latitude'] <= lat_max) &
    (df['longitude'] >= lon_min) & (df['longitude'] <= lon_max)
]

# Optional: filter high-confidence detections
gujarat_df = gujarat_df[gujarat_df['confidence'] >= 80]

# 💾 Save it
gujarat_df.to_csv("gujarat_fire_history.csv", index=False)


print("🔥 Gujarat fire data saved.")
