import json
import pandas as pd

# Load the JSON file
with open("input_feed.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# Normalize and convert lists to strings
df = pd.json_normalize(data)
df["extractedLocations"] = df["extractedLocations"].apply(lambda x: ", ".join(x))
df["tags"] = df["tags"].apply(lambda x: ", ".join(x))

# Export to CSV
df.to_csv("news_feed_converted.csv", index=False)