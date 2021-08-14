# Spotify Recommandation
### _Create your own recommandation system_

![image](https://user-images.githubusercontent.com/86613710/129451225-cbad9100-7969-42f5-9947-d1dfd736bc84.png)


This tool allows you to build your own recommandation system based on a few playlists

## Features

- Create a recommandation system from a nice-looking GUI made with Gradio
- Build a dataset with audio features of your selected songs
- Build a stat report based on what you listen
- Find your affinity with a specific track, or a list of tracks within a playlist or an album

## Installation & Usage

Dillinger requires [Python3](https://www.python.org/downloads/) and [Pip](https://pip.pypa.io/en/stable/installation/) to run.

Install the repository

```sh
git clone git@github.com:Brice-Vergnou/create-your-spotify-recomendation.git
```

Install the dependencies

```sh
cd create-your-spotify-recomendation
pip install -r requirements.txt
```

Create your model ( instructions are going to be given )

```sh
python3 get_your_model_gui.py                       # This is going to open your web browser
```

Use your model ( usage is pretty straight forward for this one )

```sh
python3 main.py                                     # This is going to open your web browser
```


## Files

| File | Usefulness |
| ------ | ------ |
| data/bad[number].json | Tracks' audio features from a disliked playlist |
| data/good.json | Tracks' audio features from the liked playlist |
| data/data.csv | Dataframe made from merging all the data files and adding their "liking state" ( 1 or 0 ) |
| data/model.sav | Saved model |
| stats/heatmap.png | Correlation map |
| stats/stats.pdf | Correlation map + explainations about it |
| flagged/log.csv | If you flag a result in main.py, they'll be stored in this file |
