#this builds the database from reading the accompanying monthly
#playlist tracks csv

track_file = "MonthlyPlaylistsTracks.csv"
import csv


with open(track_file) as file:
    tracklist = list(csv.DictReader(file))

db = {}

for track in tracklist:
    key = track['name'] + ' by ' + track['artists']
    if key in db:
        print("Duplicate: " + key + " on " + track['playlist'] + " matches " + db[key]['name'] + " by " + db[key]['artists'] + " on " + db[key]['playlist'])
    else:
        db[key] = track