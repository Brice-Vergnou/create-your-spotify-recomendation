import gradio as gr
import pickle
import os
import pandas as pd
import json
import urllib.parse

def get_stats(title):
    try:
        model = pickle.load(open("data/model.sav", 'rb'))
        try:
            with open("token.txt", "r") as f:
                token = f.read().replace("\n", "")
            query = urllib.parse.quote(title)
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
                return "Your token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/"
            except IndexError:
                return "We didn't find the song you were looking for"
        except FileNotFoundError:
            return """
                FileNotFoundError : There is no token file
                
                To create one , visit this page : https://developer.spotify.com/console/get-several-tracks/
                
                Log in to your spotify Account , and then copy what's in "OAuth Token" field 
                into a file called "token.txt" in the root directory of the project
                """
    except FileNotFoundError:
        return "You didn't generate a predictor yet ! Run get_your_model.py , everything will be explained"

inter = gr.Interface(fn=get_stats, inputs="text", outputs="text",title="Do you like this song ?",
                     description="Just write the name of a song and it will tell you the chances you like it. If you write the name of an artist, it'll proceed with one of the songs of this artist. If you can't find the song you're looking for , type the title AND the name of the artist. You can find your old results in the 'flagged' folder.",
                     examples=[["Megazord"],["KIKESA"],["Megazord KIKESA"]])
inter.launch(inbrowser=True)