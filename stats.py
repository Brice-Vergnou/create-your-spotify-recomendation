## saving image on pdf code from here :
##  https://code-maven.com/add-image-to-existing-pdf-file-in-python


from reportlab.pdfgen.canvas import Canvas
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image


def create_pdf():
    data = pd.read_csv("data/data.csv")
    file_pdf = "stats/stats.pdf"
    img_file = 'stats/heatmap.png'

    corr = data.corr()[["liked"]]

    stats = ["danceability", "energy", "key", "loudness", "mode", "speechiness", "acousticness",
             "instrumentalness", "liveness", "valence", "tempo", "duration_ms", "time_signature"]
    sentences = []

    for i in range(len(stats)):
        nb = corr.iloc[i]["liked"]
        if i == 0:
            if nb > 0.15:
                sentences.append("are danceable")
            elif nb < -0.15:
                sentences.append("are not danceable")
        elif i == 1:
            if nb > 0.15:
                sentences.append("are intense")
            elif nb < -0.15:
                sentences.append("are calm")
        elif i == 2:
            if nb > 0.15:
                sentences.append("are high-pitched")
            elif nb < -0.15:
                sentences.append("are low-pitched")
        elif i == 3:
            if nb > 0.15:
                sentences.append("are loud")
            elif nb < -0.15:
                sentences.append("are quiet")
        elif i == 4:
            if nb > 0.15:
                sentences.append("have a major modality")
            elif nb < -0.15:
                sentences.append("have a minor modality")
        elif i == 5:
            if nb > 0.15:
                sentences.append("have a lot of spoken words")
            elif nb < -0.15:
                sentences.append("have few spoken words")
        elif i == 6:
            if nb > 0.15:
                sentences.append("are acoustic")
            elif nb < -0.15:
                sentences.append("are \"electric\" ( not acoustic )")
        elif i == 7:
            if nb > 0.15:
                sentences.append("are instrumental")
            elif nb < -0.15:
                sentences.append("are vocal")
        elif i == 8:
            if nb > 0.15:
                sentences.append("were performed live")
            elif nb < -0.15:
                sentences.append("were performed in a studio")
        elif i == 9:
            if nb > 0.15:
                sentences.append("are postive")
            elif nb < -0.15:
                sentences.append("are  negative")
        elif i == 10:
            if nb > 0.15:
                sentences.append("are fast")
            elif nb < -0.15:
                sentences.append("are slow")
        elif i == 11:
            if nb > 0.15:
                sentences.append("are long")
            elif nb < -0.15:
                sentences.append("are short")
        elif i == 12:
            pass

    fig, ax = plt.subplots(figsize=(10, 10))
    svm = sns.heatmap(
        corr,
        annot=True,
        ax=ax
    )
    figure = svm.get_figure()
    figure.savefig(img_file, dpi=400)
    foo = Image.open(img_file)
    foo = foo.resize((575, 575), Image.ANTIALIAS)
    foo.save(img_file, quality=100)

    canvas = Canvas(file_pdf)
    canvas.drawImage(img_file, 50, 300)
    canvas.setFont("Helvetica", 8)
    canvas.drawString(225, 335, "( sorry for low resolution , I did my best ) ")
    canvas.setFont("Helvetica", 20)
    canvas.drawString(185, 250, "This is your heatmap")
    canvas.setFont("Helvetica", 12)
    canvas.drawString(50, 200, "\n    A heatmap represents how a value depending on the others .")
    canvas.drawString(50, 180, "         In this case , the variable we're looking at is 'liked'.")
    canvas.drawString(50, 150,
                      "\n    Basically , if a variable has a positive correlation with liked ( greater than 0 ),")
    canvas.drawString(50, 130, "         it means that when this variable rises , 'liked' rises as well.")
    canvas.drawString(50, 100, "\n    The opposite is true as well when when the correlation is negative.")
    canvas.drawString(50, 70, "\n    A null correlation means the variable doesn't affect the result")
    canvas.setFont("Helvetica", 10)
    canvas.drawString(50, 45, "\n    An explanation of your stats is available on the next page.")
    canvas.drawString(50, 25, "\n    You can check the high quality image in heatmap.png")
    canvas.showPage()

    canvas.setFont("Helvetica", 20)
    canvas.drawString(20, 800, "Your Stats")
    canvas.setFont("Helvetica", 15)
    canvas.drawString(50, 750, "You like songs when they ... ")
    canvas.setFont("Helvetica", 12)
    h = 720
    for sentence in sentences:
        canvas.drawString(75, h, "\n   " + sentence)
        h -= 30

    canvas.save()