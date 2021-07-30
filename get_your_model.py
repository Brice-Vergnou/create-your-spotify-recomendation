import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
import pandas as pd
import os
import json
import urllib.parse
from stats import create_pdf

done_getting = False
done_cleaning = False
bad_playlist = []
try:
    os.mkdir("data")
except FileExistsError:
    pass
try:
    os.mkdir("stats")
except FileExistsError:
    pass

print("""Hello !
          
          Thanks for using our program , you'll be able to build your own recommandation tool.
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
                At the end , you will have a summary of the "bad" playlists to make sure they're all right
                
            Once you have these playlists , just copy their links. They will look like this
            https://open.spotify.com/playlist/[ID]?si=[a random number]
            
            When prompted , just copy the ID and paste it 
            Some files are going to be generated , you don't have to worry about them but
            DON'T DELETE THEM :(
            
            Your predictor will be the file "model.sav".
            You can't read it but once generated , head to the main.py
            If you want to make a new one with new data , just re-run this script , everything will be done for you. 
            
            Have fun :)\n\n
          """)

# Get data
try:
    # Get token 
    with open("token.txt", "r") as f:
        token = f.read().replace("\n", "")

    # Get the data from the liked playlist
    playlist_id = input("ID of the 'liked' playlist : ")
    playlist_id = urllib.parse.quote(playlist_id)
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
        i = 1
        while i < 5 :
            playlist_id = input(f"\n\nID of the 'disliked' playlist n.{i}: ")
            playlist_id = urllib.parse.quote(playlist_id)
            stream = os.popen(f'curl -X "GET" "https://api.spotify.com/v1/playlists/{playlist_id}/tracks?fields=items(track(id%2Cname))?limit=25" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
            data = stream.read()
            try :
                data = json.loads(data)["items"]
                songs_ids = ""
                for track in data:
                    songs_ids += track["track"]["id"] + ","
                songs_ids = songs_ids[:-1]
                stream = os.popen(f'curl -X "GET" "https://api.spotify.com/v1/audio-features?ids={songs_ids}" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: Bearer {token}"')
                data = stream.read()
                with open(f"data/bad{i}.json","w") as f:
                    f.write(data)
                i +=1

            except KeyError:
                    print(
                        "\n\n\nYour token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/\n\n\n")
            except IndexError:
                print("\n\n\nWe didn't find the playlist you were looking for\n\n\n")

        done_getting = True

    except KeyError:
        print("""\n\n
                       Your token has expired , create a new one : https://developer.spotify.com/console/get-several-tracks/
              
                       If you refreshed / created your token within the last hour , make sure you have the good ID
              \n\n\n""")
except FileNotFoundError:
    print("""
          FileNotFoundError : There is no token file
          
          To create one , visit this page : https://developer.spotify.com/console/get-several-tracks/
          
          Log in to your spotify Account , do not check any scope, and then copy what's in "OAuth Token" field 
          into a file called "token.txt" in the root directory of the project
          """)

# Clean and process data
if done_getting:
    with open("data/good.json", "r") as f:
        liked = json.load(f)
    liked = pd.DataFrame(liked["audio_features"])
    liked["liked"] = [1] * 100
    for i in range(1, 5):
        with open(f"data/bad{i}.json", "r") as f:
            disliked = json.load(f)
        exec(f"bad{i} = pd.DataFrame(disliked['audio_features'][:25])")
        try:
            exec(f'bad{i}["liked"] = [0] * 25')
            done_cleaning = True
        except ValueError:
            print(f"\n\n{bad_playlist[i]} wasn't long enough. It has to be at least 25 songs long.")
            break

# Modelling
if done_cleaning:
    data = pd.concat([liked, bad1, bad2, bad3, bad4])
    data.drop(["type", "id", "uri", "track_href", "analysis_url"], axis=1, inplace=True)
    data = data.sample(frac=1)
    data.to_csv("data/data.csv", index=False)
    create_pdf()
    print("\n\nCreating your model.....")
    X, y = data.drop("liked", axis=1), data.liked
    model = RandomForestClassifier()  # TODO #4 Add small hyperparameter tuning ( keep the default values in the grid to avoid any accuracy loss ! )
    model.fit(X, y)
    with open("data/model.sav", 'wb') as f:
        pickle.dump(model, f)
    print("""
          
          
          
          Your model is ready !
          
          A summary of your stats is available on stats/stats.pdf
          
          You can now use main.py , enjoy :)
          """)
    print("\n\nSummary of the bad playlists : ( make sure they are correct ) \n")
    for i in bad_playlist:
        print(i)
