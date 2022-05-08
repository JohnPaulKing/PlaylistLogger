#author: JP King
#Date April-May 2022
#spotipy: https://spotipy.readthedocs.io/en/2.19.0/
#spotify WEP API: https://developer.spotify.com/documentation/web-api/

from functools import reduce #calculating runtime
import spotipy #spotify API
import re #pattern matching in names
from spotipy.oauth2 import SpotifyOAuth #authorization
#authorization process
scope = "playlist-read-private"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

#this function returns true if the name matches the
#monthly playlist scheme, and false otherwise
def checkIfMonthlyPlaylist(playlist: dict) -> bool:
    name = playlist['name']
    #match pattern like '04/02' 
    return re.search(r"\d\d/\d\d",name) != None

#this function makes the spotify API call to get the
#list of user playlists. It filters out the ones that
#match the monthly playlist expression, and returns only
#the essential fields
def getMonthlyPlaylists() -> dict:
    results = sp.current_user_playlists()['items']
    monthlyPlaylists = []
    #create new dict, which we will populate with
    #only the playlist name, and the unique identifier
    keys = ['name','uri']
    for item in results:
        if checkIfMonthlyPlaylist(item):
            filteredItem = {} #new item with essential fields
            for key in item:
                if key in keys:
                    filteredItem[key] = item[key]
            monthlyPlaylists.append(filteredItem)
    #sort results by year, month
    monthlyPlaylists= sorted(monthlyPlaylists, key= lambda x: (x['name'][3:], x['name'][:2]) )
    return monthlyPlaylists

def getArtists(artists_data : list ):
    artistString = ''
    for artist in artists_data:
        #if more than one artist, need separator
        #because its in a CSV, we escape it
        if len(artistString) != 0:
            artistString += ' & '
        artistString += artist['name']
    return artistString

#take in a number of milliseconds, and return 
#a string in the format HH:MM:SS, or if less than
#1 hour, just MM:SS
def getMinutesSeconds(milliseconds : int) -> str:
    seconds = round(milliseconds / 1000 )#convert to discrete seconds
    minutes = seconds // 60 #figure out how many minutes there are
    hours = minutes // 60 #figure out how many hours based on minutes
    minutes = minutes % 60 #subtract minutes counted towards hour
    seconds = seconds % 60 #subtract seconds counted towards minute
    #format time 
    if hours > 0:
        return "%02d:%02d:%02d" % (hours,minutes, seconds) 
    else:
        return "%02d:%02d" % (minutes, seconds) 

#this function calculates the time length of a playlist in milliseconds
def calculateRunTime(playlist: list) -> int:
    runtimes = list(map(lambda x: x['track']['duration_ms'],playlist))
    milliseconds = reduce(lambda x,y: x + y,runtimes)
    return milliseconds

#this function takes a playlist object and returns the list
#of tracks with their metadeta. as well as the total tracks and runtime
def getTracks(playlist: dict) -> tuple: #<int, int, list>
    tracklist = []
    #call to spotify api to get tracks
    tracks = sp.user_playlist_tracks(playlist_id=playlist['uri'])
    total = tracks['total']
    #get total runtime of the playlist
    runtime = calculateRunTime(tracks['items'])
    #pl_track is the full data in reference to the playlist
    #who added the track,  etc
    #track data is the spotify metadata: artist, band, etc
    for pl_track in tracks['items']:
        trackdata = pl_track['track']
        filteredTrack = {}
        #append artist data
        #save song data
        filteredTrack['name'] = trackdata['name']
        filteredTrack['artists'] = getArtists(trackdata['artists'])
        #append album data
        filteredTrack['album'] = trackdata['album']['name']
        #only keep year, if longer date format is given, year is always first 4 chars
        filteredTrack['year'] = trackdata['album']['release_date'][:4]
        filteredTrack['length'] = getMinutesSeconds(trackdata['duration_ms'])
        filteredTrack['playlist'] = playlist['name']
        tracklist.append(filteredTrack)
    #add them to the dictionary
    return (total,runtime, tracklist)

#return comma separated column names
def getHeader(firstTrack : dict) -> str:
    header = ''
    for key in firstTrack:
        if len(header) != 0:
            header += ','
        header += key
    header += '\n' 
    return header

#write the tracklist in a csv, which contains information about each track
def writeToTrackCSV(playlists: list):
    with open("MonthlyPlaylistsTracks.csv", 'w') as output:
        output.write(getHeader(playlists[0]['tracks'][0]))
        for playlist in playlists: #for each playlist
            for track in playlist['tracks']: #for each track
                line = ''
                for key in track: #for each datapoint
                    if len(line) != 0:
                        line += ','
                    text = str(track[key])
                    #add double quotes if data contains comma
                    #to differentiate from separator, per csv standard
                    if ',' in text:
                        text = '"' + text + '"'
                    line += text
                output.write(line)
                output.write('\n')

#write the playlist CSV, which contains information about each playlist
def writeToPlaylistCSV(playlists : list):
    with open("MonthlyPlaylists.csv",'w') as output:
        output.write('name,total,runtime\n')
        for playlist in playlists:
            line = playlist['name'] + ',' + str(playlist['total']) + ',' + getMinutesSeconds(playlist['runtime'])
            output.write(line)
            output.write('\n')
        #calculate average total and runtime
        totals = list(map(lambda x: x['total'], playlists))
        runtimes = list(map(lambda x: x['runtime'], playlists))
        func = lambda x,y: x + y
        av_total = reduce(func, totals) / len(totals)
        av_runtime = reduce(func, runtimes) / len(runtimes)
        output.write('average,'+'%.2f' % av_total + ',' + getMinutesSeconds(av_runtime))


#get filtered monthly playlists
data = getMonthlyPlaylists()

#add the track data to the playlists
for d in data:
    d['total'], d['runtime'], d['tracks'] = getTracks(d)


#write the csv
writeToTrackCSV(data)

#write playlist statistics
writeToPlaylistCSV(data)