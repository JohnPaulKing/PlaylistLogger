#This program takes the output of DatabaseBuilder, a CSV of tracks in each monthly playlist
#And searches for any duplicates

track_file = "MonthlyPlaylistsTracks.csv"
import csv


with open(track_file) as file:
    tracklist = list(csv.DictReader(file))

#For each track, add the concatanated name and artist to a set
#If that name and artist already exist in the set, it must be a
#duplicate. Print out the information
db = {}
for track in tracklist:
    key = track['name'] + ' by ' + track['artists']
    if key in db:
        print("Duplicate: " + key + " on " + track['playlist'] + " matches " + db[key]['name'] + " by " + db[key]['artists'] + " on " + db[key]['playlist'])
    else:
        db[key] = track