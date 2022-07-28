from asyncio import sleep
import requests
import json
import argparse
import csv
import pandas as pd
import time
import os
import subprocess


parser = argparse.ArgumentParser()
searchtype = parser.add_mutually_exclusive_group(required=True)
searchtype.add_argument('-s', '--song', help='Search for a song')
searchtype.add_argument('-a', '--album', help='Search for an album')
parser.add_argument('-t', '--token', help='Token to use for spotify authentication', required=True)
parser.add_argument('-e', '--export', help='Run the all-in-one export', action='store_true')
args = parser.parse_args()

song = args.song
album = args.album
spotifyToken = args.token

headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + str(spotifyToken),
}

if song != None and song != "":
    print("song: " + str(song))
if album != None and album != "":
    print("album: " + str(album))
if spotifyToken != None and spotifyToken != "":
    print("token: " + str(spotifyToken))


if song != None and song != "":
    params = {
    'q': str(song),
    'type': 'track',
    'market': 'US',
    }
elif album != None and album != "":
    params = {
    'q': str(album),
    'type': 'album',
    'market': 'US',
    }
else:
    params = {
    'q': '',
    'type': 'album',
    'market': 'US',
    }

spotifySearchResponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

print(spotifySearchResponse.text)

spotifySearchJSON = json.loads(spotifySearchResponse.text)

while 'error' in spotifySearchJSON:
    print("Error: Trying again...")
    time.sleep(1)
    spotifySearchResponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    print(spotifySearchResponse.text)
    spotifySearchJSON = json.loads(spotifySearchResponse.text)


if album != None and album != "":
    # print out the first album name
    correctAlbum = input("Album returned: " + spotifySearchJSON['albums']['items'][0]['artists'][0]['name'] + " || " + spotifySearchJSON['albums']['items'][0]['name'] + "\nIs this correct? (y/n)")
    if correctAlbum == "y":
        # print out first album spotify id
        print(spotifySearchJSON['albums']['items'][0]['id'])
        albumID = spotifySearchJSON['albums']['items'][0]['id']
elif song != None and song != "":
    # print out the first song name
    correctSong = input("Song returned: " + spotifySearchJSON['tracks']['items'][0]['artists'][0]['name'] + " || " + spotifySearchJSON['tracks']['items'][0]['name'] + "\nIs this correct? (y/n)")
    if correctSong.upper() == "Y":
        # print out first song spotify id
        print(spotifySearchJSON['tracks']['items'][0]['id'])
        songID = spotifySearchJSON['tracks']['items'][0]['id']
    elif correctSong.upper() == "N":
        correctSong = input("Song returned: " + spotifySearchJSON['tracks']['items'][1]['artists'][0]['name'] + " || " + spotifySearchJSON['tracks']['items'][1]['name'] + "\nIs this correct? (y/n)")
        if correctSong.upper() == "Y":
            # print out first song spotify id
            print(spotifySearchJSON['tracks']['items'][1]['id'])
            songID = spotifySearchJSON['tracks']['items'][1]['id']
        elif correctSong.upper() == "N":
            print("Failed to find song")
            exit()
else:
    print("No song or album specified")

if album != None and album != "":

    albumParams = {
        'market': 'US',
        'limit': '50',
    }   

    # get album tracks
    albumTracksResponse = requests.get('https://api.spotify.com/v1/albums/' + str(albumID) + '/tracks', headers=headers, params=albumParams)
    albumTracksJSON = json.loads(albumTracksResponse.text)

    print(albumTracksJSON)
    # if albumTracksJSON contains an error, print it
    while 'error' in albumTracksJSON:
        print("Sleeping for a bit")
        time.sleep(5)
        albumTracksResponse = requests.get('https://api.spotify.com/v1/albums/' + str(albumID) + '/tracks', headers=headers, params=albumParams)
        albumTracksJSON = json.loads(albumTracksResponse.text)
        print(albumTracksJSON)


    if correctAlbum == "y":
        # print out number of tracks
        print("Track total: " + str(albumTracksJSON))

        outCSV = str(album) + ".csv" 
        outCSV = outCSV.replace(" ", "_")
        
        # print out all the track names
        for track in albumTracksJSON['items']:
            print(track['artists'][0]['name'] + " || " + track['name'])

        # for each track, get the audio features
        for track in albumTracksJSON['items']:
            trackParams = {
                'ids': track['id'],
            }
            trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(track['id']), headers=headers, params=trackParams)
            trackFeaturesJSON = json.loads(trackFeaturesResponse.text)
            print(trackFeaturesJSON)

            # If it returns error, sleep for a bit and try again
            while 'error' in trackFeaturesJSON:
                print("Sleeping for a bit")
                time.sleep(5)
                trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(track['id']), headers=headers, params=trackParams)
                trackFeaturesJSON = json.loads(trackFeaturesResponse.text)
                print(trackFeaturesJSON)

            # Remove redundant keys
            del trackFeaturesJSON['track_href']
            del trackFeaturesJSON['analysis_url']
            del trackFeaturesJSON['type']

            trackFeaturesJSON['track_name'] = track['name'][:22]
            trackFeaturesJSON['artist_name'] = track['artists'][0]['name'][:22]

            if trackFeaturesJSON['key'] == 0:
                trackFeaturesJSON['key'] = "C"
            elif trackFeaturesJSON['key'] == 1:
                trackFeaturesJSON['key'] = "C#"
            elif trackFeaturesJSON['key'] == 2:
                trackFeaturesJSON['key'] = "D"
            elif trackFeaturesJSON['key'] == 3:
                trackFeaturesJSON['key'] = "D#"
            elif trackFeaturesJSON['key'] == 4:
                trackFeaturesJSON['key'] = "E"
            elif trackFeaturesJSON['key'] == 5:
                trackFeaturesJSON['key'] = "F"
            elif trackFeaturesJSON['key'] == 6:
                trackFeaturesJSON['key'] = "F#"
            elif trackFeaturesJSON['key'] == 7:
                trackFeaturesJSON['key'] = "G"
            elif trackFeaturesJSON['key'] == 8:
                trackFeaturesJSON['key'] = "G#"
            elif trackFeaturesJSON['key'] == 9:
                trackFeaturesJSON['key'] = "A"
            elif trackFeaturesJSON['key'] == 10:
                trackFeaturesJSON['key'] = "A#"
            elif trackFeaturesJSON['key'] == 11:
                trackFeaturesJSON['key'] = "B"


            if trackFeaturesJSON['mode'] == 0:
                trackFeaturesJSON['mode'] = "Minor"
            elif trackFeaturesJSON['mode'] == 1:
                trackFeaturesJSON['mode'] = "Major"
            

            trackFeaturesJSON['realkey'] = trackFeaturesJSON['key'] + trackFeaturesJSON['mode']

            
            url = 'https://api.spotify.com/v1/tracks/' + str(track['id'])
            response = requests.get(url, headers=headers)
            previewurl_json_response = response.json()
            print(previewurl_json_response)

            while 'error' in previewurl_json_response:
                print('Error: ')
                time.sleep(1)
                response = requests.get(url, headers=headers)
                previewurl_json_response = response.json()
                print(previewurl_json_response)

            strippedURL = previewurl_json_response['preview_url']
            # Remove [:23] to get the actual filename
            strippedURL = strippedURL[30:]
            #strippedURL = strippedURL.split('?', 1)[0]
            trackFeaturesJSON['preview_url'] = strippedURL
            

            with open(outCSV, 'a') as file:
                w = csv.DictWriter(file, trackFeaturesJSON.keys())
                if file.tell() == 0:
                    w.writeheader()
            with open(outCSV, 'a') as csvfile:
                    fieldnames = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'id', 'uri', 'duration_ms', 'time_signature', 'track_name', 'artist_name', 'realkey', 'preview_url']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'danceability': trackFeaturesJSON['danceability'], 'energy': trackFeaturesJSON['energy'], 'key': trackFeaturesJSON['key'], 'loudness': trackFeaturesJSON['loudness'], 'mode': trackFeaturesJSON['mode'], 'speechiness': trackFeaturesJSON['speechiness'], 'acousticness': trackFeaturesJSON['acousticness'], 'instrumentalness': trackFeaturesJSON['instrumentalness'], 'liveness': trackFeaturesJSON['liveness'], 'valence': trackFeaturesJSON['valence'], 'tempo': trackFeaturesJSON['tempo'], 'id': trackFeaturesJSON['id'], 'uri': trackFeaturesJSON['uri'], 'duration_ms': trackFeaturesJSON['duration_ms'], 'time_signature': trackFeaturesJSON['time_signature'], 'track_name': trackFeaturesJSON['track_name'], 'artist_name': trackFeaturesJSON['artist_name'], 'realkey': trackFeaturesJSON['realkey'], 'preview_url': trackFeaturesJSON['preview_url']})

        # Get offset of spotify search
        offset = albumTracksJSON['offset']
        print("offset: " + str(offset))
        # Get total number of tracks
        totalTracks = albumTracksJSON['total']
        print("totalTracks: " + str(totalTracks))
        # Get limit of spotify search
        limit = albumTracksJSON['limit']
        print("limit: " + str(limit))
        # Get next URL
        nextURL = albumTracksJSON['next']
        print("nextURL: " + str(nextURL))

        if nextURL != None and nextURL != "":
            albumTracksResponse = requests.get(nextURL, headers=headers, params=albumParams)
            albumTracksJSON = json.loads(albumTracksResponse.text)

            # print out all the track names
            for track in albumTracksJSON['items']:
                print(track['artists'][0]['name'] + " || " + track['name'])

            # for each track, get the audio features
            for track in albumTracksJSON['items']:
                trackParams = {
                    'ids': track['id'],
                }
                trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(track['id']), headers=headers, params=trackParams)
                trackFeaturesJSON = json.loads(trackFeaturesResponse.text)
                #print(trackFeaturesJSON)

                # If it returns error, sleep for a bit and try again
                while 'error' in albumTracksJSON:
                    print("Sleeping for a bit")
                    time.sleep(5)
                    trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(track['id']), headers=headers, params=trackParams)
                    trackFeaturesJSON = json.loads(trackFeaturesResponse.text)
                print(trackFeaturesJSON)

            # for each track, add the audio features to a csv file
            for track in albumTracksJSON['items']:
                trackParams = {
                    'ids': track['id'],
                }
                trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(track['id']), headers=headers, params=trackParams)
                trackFeaturesJSON = json.loads(trackFeaturesResponse.text)
                #print(trackFeaturesJSON)

                # If it returns error, sleep for a bit and try again
                while 'error' in albumTracksJSON or 'error' in trackFeaturesJSON:
                    print("Sleeping for a bit")
                    time.sleep(5)
                    trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(track['id']), headers=headers, params=trackParams)
                    trackFeaturesJSON = json.loads(trackFeaturesResponse.text)
                print(trackFeaturesJSON)

                

                # Remove redundant keys
                del trackFeaturesJSON['track_href']
                del trackFeaturesJSON['analysis_url']
                del trackFeaturesJSON['type']

                trackFeaturesJSON['track_name'] = track['name']
                trackFeaturesJSON['artist_name'] = track['artists'][0]['name']

                if trackFeaturesJSON['key'] == 0:
                    trackFeaturesJSON['key'] = "C"
                elif trackFeaturesJSON['key'] == 1:
                    trackFeaturesJSON['key'] = "C#"
                elif trackFeaturesJSON['key'] == 2:
                    trackFeaturesJSON['key'] = "D"
                elif trackFeaturesJSON['key'] == 3:
                    trackFeaturesJSON['key'] = "D#"
                elif trackFeaturesJSON['key'] == 4:
                    trackFeaturesJSON['key'] = "E"
                elif trackFeaturesJSON['key'] == 5:
                    trackFeaturesJSON['key'] = "F"
                elif trackFeaturesJSON['key'] == 6:
                    trackFeaturesJSON['key'] = "F#"
                elif trackFeaturesJSON['key'] == 7:
                    trackFeaturesJSON['key'] = "G"
                elif trackFeaturesJSON['key'] == 8:
                    trackFeaturesJSON['key'] = "G#"
                elif trackFeaturesJSON['key'] == 9:
                    trackFeaturesJSON['key'] = "A"
                elif trackFeaturesJSON['key'] == 10:
                    trackFeaturesJSON['key'] = "A#"
                elif trackFeaturesJSON['key'] == 11:
                    trackFeaturesJSON['key'] = "B"


                if trackFeaturesJSON['mode'] == 0:
                    trackFeaturesJSON['mode'] = "Minor"
                elif trackFeaturesJSON['mode'] == 1:
                    trackFeaturesJSON['mode'] = "Major"


                trackFeaturesJSON['realkey'] = trackFeaturesJSON['key'] + trackFeaturesJSON['mode']


                trackFeaturesJSON['realkey'] = trackFeaturesJSON['key'] + trackFeaturesJSON['mode']

            
                url = 'https://api.spotify.com/v1/tracks/' + str(track['id'])
                response = requests.get(url, headers=headers)
                previewurl_json_response = response.json()
                print(previewurl_json_response)

                while 'error' in previewurl_json_response:
                    print('Error: ')
                    time.sleep(1)
                    response = requests.get(url, headers=headers)
                    previewurl_json_response = response.json()
                    print(previewurl_json_response)

                strippedURL = previewurl_json_response['preview_url']
                # Remove [:23] to get the actual filename
                strippedURL = strippedURL[30:]
                #strippedURL = strippedURL.split('?', 1)[0]
                trackFeaturesJSON['preview_url'] = strippedURL


                with open(outCSV, 'a') as csvfile:
                    fieldnames = ['danceability', 'energy', 'key', 'loudness', 'mode', 'speechiness', 'acousticness', 'instrumentalness', 'liveness', 'valence', 'tempo', 'id', 'uri', 'duration_ms', 'time_signature', 'track_name', 'artist_name', 'realkey', 'preview_url']
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writerow({'danceability': trackFeaturesJSON['danceability'], 'energy': trackFeaturesJSON['energy'], 'key': trackFeaturesJSON['key'], 'loudness': trackFeaturesJSON['loudness'], 'mode': trackFeaturesJSON['mode'], 'speechiness': trackFeaturesJSON['speechiness'], 'acousticness': trackFeaturesJSON['acousticness'], 'instrumentalness': trackFeaturesJSON['instrumentalness'], 'liveness': trackFeaturesJSON['liveness'], 'valence': trackFeaturesJSON['valence'], 'tempo': trackFeaturesJSON['tempo'], 'id': trackFeaturesJSON['id'], 'uri': trackFeaturesJSON['uri'], 'duration_ms': trackFeaturesJSON['duration_ms'], 'time_signature': trackFeaturesJSON['time_signature'], 'track_name': trackFeaturesJSON['track_name'], 'artist_name': trackFeaturesJSON['artist_name'], 'realkey': trackFeaturesJSON['realkey'], 'preview_url': trackFeaturesJSON['preview_url']})


    if args.export:
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + str(spotifyToken),
        }


        # input a csv file and a column name and return a list of values in that column
        def get_column(csv_file, column_name):
            df = pd.read_csv(csv_file)
            return df[column_name]

        input_file = outCSV
        column_name = 'id'
        audio_urls = get_column(input_file, column_name)

        # Append the audio urls to a list
        audio_urls_list = []
        for i in range(len(audio_urls)):
            audio_urls_list.append(audio_urls[i])

        # Combine the list of audio urls into a string
        audio_urls_string = ','.join(audio_urls_list)

        print(audio_urls_string)


        # for each audio url, change the songID to the audio url
        def get_audio_url(songID):
            url = 'https://api.spotify.com/v1/tracks/' + songID
            response = requests.get(url, headers=headers)
            json_response = response.json()
            print(json_response)

            while 'error' in json_response:
                print('Error: ')
                time.sleep(1)
                response = requests.get(url, headers=headers)
                json_response = response.json()
                print(json_response)

            return json_response['preview_url']


        os.mkdir(input_file[:-4])
        os.rename(input_file, input_file[:-4] + '/' + input_file)
        os.chdir(input_file[:-4])

        # for each song, get the audio url
        for i in range(len(audio_urls_list)):
            audio_urls_list[i] = get_audio_url(audio_urls_list[i])
            print(audio_urls_list[i])
            time.sleep(1)
            # write the audio url to a text file
            with open(str(input_file) + '_audio_urls.txt', 'a+') as f:
                f.write(audio_urls_list[i] + '\n')


        # download the audio files
        subprocess.run('wget -i ' + str(input_file) + '_audio_urls.txt', shell=True)
        time.sleep(2)
        subprocess.run('for file in * ; do mv "$file" "$file".mp3; done', shell=True)
        time.sleep(1)
        subprocess.run("rename 's/\.csv\.mp3$/.csv/' *.csv.mp3", shell=True)
        time.sleep(1)
        subprocess.run("rename 's/\.txt\.mp3$/.txt/' *.txt.mp3", shell=True)
        time.sleep(1)

        os.chdir('..')
        #move dir to exports dir
        os.rename(input_file[:-4], 'exports/' + input_file[:-4])

        # Remove header from csv file and merge with another csv file
        #df = pd.read_csv(input_file)
        #df.drop(df.columns[0], axis=1, inplace=True)
        #df.to_csv(str(input_file) + '_audio_urls.csv', index=False)


elif song != None and song != "":
    # get song audio features
    songAudioFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(songID), headers=headers)
    songAudioFeaturesJSON = json.loads(songAudioFeaturesResponse.text)

    print(songAudioFeaturesJSON)
    # print out the key of the song
    print("Key: " + str(songAudioFeaturesJSON['key']))
    # print out the mode of the song
    print("Mode: " + str(songAudioFeaturesJSON['mode']))
    # print out the tempo of the song
    print("Tempo: " + str(songAudioFeaturesJSON['tempo']))
    # print out the time signature of the song
    print("Time Signature: " + str(songAudioFeaturesJSON['time_signature']))
