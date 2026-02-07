import pandas as pd
import mainpage as mp

csv_path = 'data_for_trending_song.csv'
df = pd.read_csv(csv_path)
df = df[["Time", "Date Updated", "Song name", "Song rank", "Artist", "Views (Real)", "Shares (Real)"]]

print(f"\nFound the top {len(mp.list_top_trending)} trending Vpop songs\n")
print(df.to_markdown(index=False))