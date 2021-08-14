import gradio as gr
import pickle
import os
import pandas as pd
import json
import urllib.parse

def get_stats(title,type):
    try:
        model = pickle.load(open("data/model.sav", 'rb'))
        try:
            with open("token.txt", "r") as f:
                token = f.read().replace("\n", "")
            query = urllib.parse.quote(title)
            if type=="Track":
                stream = os.popen(
                    f'curl -X "GET" "https://api.spotify.com/v1/search?q={query}&type=track" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                data = stream.read()
                try:
                    data = json.loads(data)["tracks"]["items"][0]
                    song_id = data["id"]
                    artist = data["artists"][0]["name"]
                    title = data["name"]
                    stream = os.popen(
                        f'curl -X "GET" "https://api.spotify.com/v1/audio-features/{song_id}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                    data = stream.read()
                    data = json.loads(data)
                    data = pd.DataFrame(data, index=[0])
                    data.drop(["type", "id", "uri", "track_href", "analysis_url"], axis=1, inplace=True)
                    return f"There is {list(model.predict_proba(data)[0])[1] * 100:.2f}% chance that you like \"{title}\" by {artist}"
                except KeyError:
                    if "expired" in data:
                        return "Your token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/"
                except IndexError:
                    return "We didn't find the song you were looking for"
                except:
                    return data
            elif type=="Album":
                stream = os.popen(
                    f'curl -X "GET" "https://api.spotify.com/v1/search?q={query}&type=album" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                data = stream.read()
                try:
                    data = json.loads(data)["albums"]["items"][0]
                    album_id = data["id"]
                    artist = data["artists"][0]["name"]
                    album_name = data["name"]
                    stream = os.popen(
                        f'curl -X "GET" "https://api.spotify.com/v1/albums/{album_id}/tracks" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                    data_2 = stream.read()
                    items = json.loads(data_2)["items"]
                    songs = [(song["name"],song["id"]) for song in items]
                    probas = []
                    for song in songs:
                        song = song[1]
                        stream = os.popen(
                        f'curl -X "GET" "https://api.spotify.com/v1/audio-features/{song}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                        data = stream.read()
                        data = json.loads(data)
                        data = pd.DataFrame(data, index=[0])
                        data.drop(["type", "id", "uri", "track_href", "analysis_url"], axis=1, inplace=True)
                        probas.append(list(model.predict_proba(data)[0])[1])
                    merged_list = list(zip(songs, probas))
                    merged_list.sort(key = lambda liste: liste[1],reverse = True)
                    result_string = "".join([f'\n\n\tThere is {song[1]* 100:.2f}% chance that you like "{song[0][0]}"' for song in merged_list])
                    return f"""Here's your affinity with each song of {album_name} by {artist}:{result_string}
                """
                except KeyError:
                    if "expired" in data:
                        return "Your token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/"
                except IndexError:
                    return "We didn't find the song you were looking for"
                except:
                    return data
            else:
                stream = os.popen(
                    f'curl -X "GET" "https://api.spotify.com/v1/playlists/{query}/tracks?fields=items(track(id%2Cname))" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                data = stream.read()
                try:
                    data = json.loads(data)["items"]
                    songs = [(song["track"]["name"],song["track"]["id"]) for song in data]
                    probas = []
                    for song in songs:
                        song = song[1]
                        stream = os.popen(
                        f'curl -X "GET" "https://api.spotify.com/v1/audio-features/{song}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                        data = stream.read()
                        data = json.loads(data)
                        data = pd.DataFrame(data, index=[0])
                        data.drop(["type", "id", "uri", "track_href", "analysis_url"], axis=1, inplace=True)
                        probas.append(list(model.predict_proba(data)[0])[1])
                    merged_list = list(zip(songs, probas))
                    merged_list.sort(key = lambda liste: liste[1],reverse = True)
                    result_string = "".join([f'\n\n\tThere is {song[1]* 100:.2f}% chance that you like "{song[0][0]}"' for song in merged_list])
                    return f"""Here's your affinity with each song of this playlist:{result_string}
                """

                except KeyError:
                    return """\n\n
                                Your token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/
                        
                                If you refreshed / created your token within the last hour , make sure you have the good ID
                        \n\n\n"""
        except FileNotFoundError:
            return """
                FileNotFoundError : There is no token file
                
                To create one , visit this page : https://developer.spotify.com/console/get-several-tracks/
                
                Log in to your spotify Account , and then copy what's in "OAuth Token" field 
                into a file called "token.txt" in the root directory of the project
                """
    except FileNotFoundError:
        return "You didn't generate a predictor yet ! Run get_your_model.py , everything will be explained"

inter = gr.Interface(get_stats, inputs=["text",gr.inputs.Radio(["Track", "Album", "Playlist ID ( only 100 songs will be used )"])], outputs="text",title="Do you like this song ?",
                     description="Just write the name of a song and it will tell you the chances you like it. If you write the name of an artist, it'll proceed with one of the songs of this artist. If you can't find the song you're looking for , type the title AND the name of the artist. You can find your old results in the 'flagged' folder.",
                     examples=[["37i9dQZF1DZ06evO2h94tp","Playlist ID ( only 100 songs will be used )"],["Puzzle","Album"],["Megazord KIKESA","Track"]])
inter.launch(inbrowser=True)