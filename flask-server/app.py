import json
import requests
import subprocess
import time
from flask import Flask, jsonify, request
import os
import IPython.display as ipd
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sklearn as skl
import sklearn.utils, sklearn.preprocessing, sklearn.decomposition, sklearn.svm
import librosa
import librosa.display
import json
import stumpy


spotifyToken = "BQAP5lsHV860fcLf0w_A4K8Caoclvj3ukJMG0hOBK_qgMihuGpmiOOiNtHtBr5U7mrUlb-0iK4zOhnL754X9hRd2i3WQoHy_LLR8vhRXTrjzkBXWFek_4dKeoL_68YJXv2UTO7Bx_YzzREsMQ6ZMVpmGPk0xMQ8l3ACh8qA8LF-17EJ-"

def kmeans(songArtistName):

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + str(spotifyToken),
    }

    params = {
        'q': songArtistName,
        'type': 'track',
        'limit': '2',
        'market': 'US',
    }

    spotifySearchResponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)


    while 'error' in spotifySearchResponse or spotifySearchResponse.status_code != 200:
                print('Error: ')
                time.sleep(1)
                spotifySearchResponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

    spotifySearchJSON = json.loads(spotifySearchResponse.text)

    songID = spotifySearchJSON['tracks']['items'][0]['id']

    trackParams = {
                    'ids': songID,
                }
                
    trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(songID), headers=headers, params=trackParams)

    while 'error' in trackFeaturesResponse or trackFeaturesResponse.status_code != 200:
        print('Error: ')
        time.sleep(1)
        trackFeaturesResponse = requests.get('https://api.spotify.com/v1/audio-features/' + str(songID), headers=headers, params=trackParams)

    trackFeaturesJSON = json.loads(trackFeaturesResponse.text)


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

    ##
    print("Example output:")
    print(spotifySearchJSON['tracks']['items'][0]['name'])

    # Remove keys from trackFeaturesJSON
    del trackFeaturesJSON['type']
    del trackFeaturesJSON['track_href']
    del trackFeaturesJSON['analysis_url']

    # Add track name to trackFeaturesJSON
    trackFeaturesJSON['track_name'] = spotifySearchJSON['tracks']['items'][0]['name']
    # Add artist name to trackFeaturesJSON
    trackFeaturesJSON['artist_name'] = spotifySearchJSON['tracks']['items'][0]['artists'][0]['name']
    # Add realkey to trackFeaturesJSON
    trackFeaturesJSON['realkey'] = trackFeaturesJSON['key'] + trackFeaturesJSON['mode']
    # Add blank preview_url to trackFeaturesJSON
    trackFeaturesJSON['preview_url'] = ""
    print(trackFeaturesJSON)

    ###################################
    #k-means
    
    # Convert trackFeaturesJSON to pandas dataframe
    spotifyAPISongFeatures = pd.DataFrame(trackFeaturesJSON, index=[0])
    print(spotifyAPISongFeatures)
    print(spotifyAPISongFeatures.shape)
    print("\n-----------------------------------------------------\n")

    plt.rcParams['figure.figsize'] = (17, 5)

    # optional setting to ignore SettingWithCopyWarning warnings
    pd.options.mode.chained_assignment = None

    # Directory where mp3 are stored.
    AUDIO_DIR = os.environ.get('our_data')
    # csv where audio features are stored
    data = pd.read_csv('our_data/lyrical_data.csv')

    data.index[0]

    from sklearn.preprocessing import MinMaxScaler,LabelEncoder
    features = data[['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness',
                    'liveness','valence','tempo','time_signature']]
    label_encoder = LabelEncoder()
    scaler = MinMaxScaler()
    features['key'] = label_encoder.fit_transform(features['key'])
    features['mode'] = label_encoder.fit_transform(features['mode'])
    features[['key','mode','time_signature','loudness','tempo']] = scaler.fit_transform(features[['key','mode','time_signature','loudness','tempo']])

    from sklearn.cluster import KMeans
    random.seed()
    kmeans = KMeans(n_clusters=random.randrange(50,225), random_state=0).fit(features)
    print("\n#$#$%#$#$#%$#%#")
    print(kmeans.n_clusters)

    # Add spotifyAPISongFeatures to features
    #features = features.append(spotifyAPISongFeatures)

    spotifyFeatures = spotifyAPISongFeatures[['danceability','energy','key','loudness','mode','speechiness','acousticness','instrumentalness',
                    'liveness','valence','tempo','time_signature']]
    spotifyFeatures['key'] = label_encoder.fit_transform(spotifyFeatures['key'])
    spotifyFeatures['mode'] = label_encoder.fit_transform(spotifyFeatures['mode'])
    spotifyFeatures[['key','mode','time_signature','loudness','tempo']] = scaler.fit_transform(spotifyFeatures[['key','mode','time_signature','loudness','tempo']])

    song_choice = spotifyFeatures

    # Collect most similar songs (all songs within cluster of song_choice)
    features['kmeans_label'] = kmeans.labels_
    most_sim = features[features.kmeans_label == kmeans.predict(song_choice)[0]]

    # Pick random song from most_sim and display full song data
    rand_sim = random.choice(most_sim.index)
    data[data.index == rand_sim]

    test = data[data.index == rand_sim].to_json(orient="records", lines=True)
    parsed = json.loads(test)
    print("\n\n")
    print(parsed)

    print(most_sim)

    return parsed



def stumpymodel(songArtistName):

    params = {
        'q': songArtistName,
        'type': 'track',
        'limit': '2',
        'market': 'US',
    }

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + str(spotifyToken),
    }

    spotifySearchResponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)

    #print(spotifySearchResponse.text)

    spotifySearchJSON = json.loads(spotifySearchResponse.text)
    print(spotifySearchJSON)

    while 'error' in spotifySearchJSON:
        print("Error: Trying again...")
        time.sleep(1)
        spotifySearchResponse = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
        #print(spotifySearchResponse.text)
        spotifySearchJSON = json.loads(spotifySearchResponse.text)

    #print(spotifySearchJSON['tracks']['items'][0]['id'])
    songID = spotifySearchJSON['tracks']['items'][0]['id']
    songNameAPI = spotifySearchJSON['tracks']['items'][0]['name']


    url = 'https://api.spotify.com/v1/tracks/' + str(songID)
    response = requests.get(url, headers=headers)
    previewurl_json_response = response.json()
    #print(previewurl_json_response)

    while 'error' in previewurl_json_response:
        print('Error: ')
        time.sleep(1)
        response = requests.get(url, headers=headers)
        previewurl_json_response = response.json()
        #print(previewurl_json_response)

    strippedURL = previewurl_json_response['preview_url']
    # Remove [:23] to get the actual filename
    #strippedURL = strippedURL[30:]
    #strippedURL = strippedURL.split('?', 1)[0]
    print("\n---------------------------------------------\n")
    print(strippedURL)

    # If file already exists, don't download it again
    if os.path.isfile(songNameAPI + ".mp3"):
        print("File already exists")
    else:
        subprocess.run('wget ' + '\"' + str(strippedURL) + '\"' + ' -O ' + '\"' + songNameAPI + '.mp3' + '\"', shell=True)
        time.sleep(1)

    # Grab preview mp3 from spotify and point to this directory
    # pattern, pattern_srate = librosa.load('our_data/'+data['preview_url'][index]+'.mp3', dtype=np.float64, sr=500)
    pattern = librosa.load(songNameAPI+'.mp3', dtype=np.float64, sr=250)[0]
    # samples = np.float64(samples)

    samples_per_song = pattern.shape[0]
    df_test = pd.read_csv('stumpy_250.csv')
    
    matches = stumpy.match(pattern, df_test['0'], max_matches=20)

    most_sim = pd.DataFrame()
    most_sim['distance'] = matches[:,0]
    most_sim.index = np.rint(np.float64(matches[:,1]/samples_per_song)).astype(int)
    most_sim = most_sim.groupby(most_sim.index, sort=False).first()

    #print(most_sim.head(20))
    print(most_sim)
    chosenSong = most_sim.index[1]
    print(chosenSong)

    data = pd.read_csv('our_data/lyrical_data.csv')

    print(data[data.index == chosenSong])

    outputData = data[data.index == chosenSong].to_json(orient="records", lines=True)

    parsed = json.loads(outputData)

    # print song name
    print(parsed['artist_name'])
    print(parsed['track_name'])

    #songnameYoutube = parsed['artist_name'] + ' ' + parsed['track_name']

    SongMp3result = subprocess.run(["python3", "/usr/local/bin/youtube-dl", 'ytsearch:' + parsed['artist_name'] + ' - ' + parsed['track_name'] + ' Music', "--dump-json"], stdout=subprocess.PIPE)\
        .stdout.decode("utf-8")

    SongMp3result = json.loads(SongMp3result)

    #print(SongMp3result)

    parsed["url"] = SongMp3result["formats"][0]["url"]

    print(parsed)

    # Remove downloaded mp3 file
    print("\n---------------------------------------------\n")
    print("Removing mp3 file..." + songNameAPI + ".mp3")
    os.remove(songNameAPI + ".mp3")
    print("\n---------------------------------------------\n")

    return parsed
    #return data[data.index == chosenSong].to_json(orient="records", lines=True)

####################################


app = Flask(__name__)
@app.route('/')
def index():
    songInput = request.args.get('songInput')

    kmeansJson = kmeans(str(songInput))

    if songInput != None:
        SongMp3result = subprocess.run(["python3", "/usr/local/bin/youtube-dl", 'ytsearch:' + kmeansJson['artist_name'] + ' - ' + kmeansJson['track_name'] + ' Music', "--dump-json"], stdout=subprocess.PIPE)\
            .stdout.decode("utf-8")

        SongMp3result = json.loads(SongMp3result)

        print(SongMp3result["title"])
        print(SongMp3result["formats"][0]["url"])

        # add new jsonifyd youtube url to kmeansJson
        kmeansJson["url"] = SongMp3result["formats"][0]["url"]

        return jsonify(kmeansJson)
    else:
        return "No song input"


@app.route('/spotifytoken', methods=['GET'])
def get_token():
    return jsonify({'token': spotifyToken})


@app.route('/stumpy/', methods=['GET'])
def run_stumpy():
    songInput = request.args.get('songInput')
    if songInput != None:
        return stumpymodel(request.args.get('songInput'))

app.run()

