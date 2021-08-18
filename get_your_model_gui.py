import gradio as gr
import pickle
import os
import pandas as pd
import json
import urllib.parse
from stats import create_pdf
from pycaret.classification import *

welcome_message = """
          Hello !

          Thanks for using our tool , you'll be able to build your own recommandation tool.
          You'll be able to find out if you like or not a song just giving its name , we analyse it for you
          and we tell you if it's your taste or not.

          NB : The algorithm being lightweight , it won't be absolutely perfect , but will work most of the time

          To make it work , you'll just have to :

            -   Get a Spotify playlist ready. This playlist will cointain at least 100 songs ( you can have more but only the 100 first will be used ).
                Try to use the BEST songs in your opinion so the algorithm will perfectly know what you like
                The 'Liked songs' playlist can't work because it is private
                ( don't worry about privacy , we don't even have servers to store your data , it will then remain private and on your computer )
                You will have to give us its ID
                Just copy its link. It will look like this
                https://open.spotify.com/playlist/[ID]?si=[a random number]
                When prompted , paste the ID

            -   4 shorts Spotify playlists of a gender / artist you don't like. Try to use different genders so the algorithm will better know
                what you don't like.
                And don't worry ! You don't have to create these playlist. You can just use the "This is [name of the artist]" playlists
                made by Spotify , or type the name of the gender you don't like and take the first playlist.
                Each of these playlists have to be at least 25 songs long
                You will have to give us its ID

            -   Get a token, to access the Spotify's API.
                To do so, visit this link :  https://developer.spotify.com/console/get-several-tracks/
                Click on "Get Token", log in and then copy the token in a file called tokent.txt in the root directory of the project

            Some files are going to be generated , you don't have to worry about them but
            DON'T DELETE THEM :(

            Your predictor will be the file "model.sav" in the data folder, with other files.
            You can't read it but once generated , you can run main.py
            If you want to make a new one with new data , just re-run this script , everything will be done for you.

            You can check your stats in the stats folder after that

            Have fun :)\n\n
          """


def bad(playlist_id, i):
    playlist_id = urllib.parse.quote(str(playlist_id).replace(" ", ""))
    stream = os.popen(
        f'curl -X "GET" "https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items(track(id%2Cname))?limit=25" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
    data = stream.read()
    try:
        data = json.loads(data)["items"]
        songs_ids = ""
        for track in data:
            songs_ids += track["track"]["id"] + ","
        songs_ids = songs_ids[:-1]
        stream = os.popen(
            f'curl -X "GET" "https://api.spotify.com/v1/audio-features?ids={songs_ids}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
        data = stream.read()
        with open(f"data/bad{i}.json", "w") as f:
            f.write(data)

    except KeyError:
        return "\n\n\nYour token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/\n\n\n"
    except IndexError:
        return "\n\n\nWe didn't find the playlist you were looking for\n\n\n"


try:
    os.mkdir("data")
except FileExistsError:
    pass
try:
    os.mkdir("stats")
except FileExistsError:
    pass


def get_stats(liked_Playlist,
              disliked_Playlist_1,
              disliked_Playlist_2,
              disliked_Playlist_3,
              disliked_Playlist_4):
    global token, done_getting
    # Get data
    try:
        # Get token
        with open("token.txt", "r") as f:
            token = f.read().replace("\n", "")

        # Get the data from the liked playlist
        playlist_id = urllib.parse.quote(liked_Playlist.replace(" ", ""))
        stream = os.popen(
            f'curl -X "GET" "https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items(track(id%2Cname))" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
        data = stream.read()
        try:
            data = json.loads(data)["items"]
            songs_ids = ""
            for track in data:
                songs_ids += track["track"]["id"] + ","
            songs_ids = songs_ids[:-1]
            stream = os.popen(
                f'curl -X "GET" "https://api.spotify.com/v1/audio-features?ids={songs_ids}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
            data = stream.read()
            with open("data/good.json", "w") as f:
                f.write(data)

            # Get the data from the disliked playlists
            bad(disliked_Playlist_1, 1)
            bad(disliked_Playlist_2, 2)
            bad(disliked_Playlist_3, 3)
            bad(disliked_Playlist_4, 4)
            done_getting = True

        except KeyError:
            return """\n\n
                        Your token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/

                        If you refreshed / created your token within the last hour , make sure you have the good ID
                \n\n\n"""
    except FileNotFoundError:
        return """
            FileNotFoundError : There is no token file

            To create one , visit this page : https://developer.spotify.com/console/get-several-tracks/

            Log in to your spotify Account , do not check any scope, and then copy what's in "OAuth Token" field
            into a file called "token.txt" in the root directory of the project
            """

    # Clean and process data
    if done_getting:
        with open("data/good.json", "r") as f:
            liked = json.load(f)
        try:
            liked = pd.DataFrame(liked["audio_features"])
            liked["liked"] = [1] * 100
        except ValueError:
            return "\n\nYour 'liked' playlist wasn't long enough. It has to be at least 100 songs long."
        with open("data/bad1.json", "r") as f:
            disliked = json.load(f)
        bad1 = pd.DataFrame(disliked['audio_features'][:25])
        with open("data/bad2.json", "r") as f:
            disliked = json.load(f)
        bad2 = pd.DataFrame(disliked['audio_features'][:25])
        with open("data/bad3.json", "r") as f:
            disliked = json.load(f)
        bad3 = pd.DataFrame(disliked['audio_features'][:25])
        with open("data/bad4.json", "r") as f:
            disliked = json.load(f)
        bad4 = pd.DataFrame(disliked['audio_features'][:25])
        try:
            bad1["liked"] = [0] * 25
        except ValueError:
            return "\n\n'Disliked' playlist n.1 wasn't long enough. It has to be at least 25 songs long."
        try:
            bad2["liked"] = [0] * 25
        except ValueError:
            return "\n\n'Disliked' playlist n.2 wasn't long enough. It has to be at least 25 songs long."
        try:
            bad3["liked"] = [0] * 25
        except ValueError:
            return "\n\n'Disliked' playlist n.3 wasn't long enough. It has to be at least 25 songs long."
        try:
            bad4["liked"] = [0] * 25
        except ValueError:
            return "\n\n'Disliked' playlist n.4 wasn't long enough. It has to be at least 25 songs long."

        # Modelling
        data = pd.concat([liked, bad1, bad2, bad3, bad4])
        data.drop(["type", "id", "uri", "track_href",
                  "analysis_url"], axis=1, inplace=True)
        data = data.sample(frac=1)
        data.to_csv("data/data.csv", index=False)
        data = pd.read_csv("data/data.csv")
        setup(data, target='liked', session_id=123, silent=True)
        create_pdf()
        model = create_model('rf', fold=5)
        model.fit(data.drop("liked", axis=1), data.liked)
        with open("data/model.sav", 'wb') as f:
            pickle.dump(model, f)
        return """



            Your model is ready !

            A summary of your stats is available in stats/stats.pdf

            You can now use main.py , enjoy :)
            """


inter = gr.Interface(fn=get_stats,
                     inputs=["text", "text", "text", "text", "text"],
                     outputs="textbox",
                     article=welcome_message,
                     title="Create your recommandation algorithm!",
                     description="Please read the notice right below. Additionnal note : The creation process can take several minutes depending on your compute power",
                     allow_flagging=False,
                     allow_screenshot=False)
inter.launch(inbrowser=True)
