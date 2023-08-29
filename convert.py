#!/home/jack/Desktop/ProcessDirectory/ffmpeg_server/bin/python
from flask import Flask, render_template, redirect
import os
import subprocess 
import shutil  
import logging
import random
from random import randint
import glob
import datetime
import time
from werkzeug.utils import secure_filename
from time import sleep
from PIL import Image, ImageDraw, ImageFont
from logging.handlers import RotatingFileHandler
import uuid

app = Flask(__name__)

app.secret_key = os.urandom(24)

# Create a logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create a formatter for the log messages
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')

# Create a file handler to write log messages to a file
file_handler = RotatingFileHandler('Logs/app.log', maxBytes=10000, backupCount=1)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)

# Add the file handler to the logger
logger.addHandler(file_handler)

# Now you can use the logger to log messages




TEXT = "TEXT TEST abcd"
logger.debug('This is a debug message: %s', TEXT)
# Set up logging for the Flask app
app.logger.addHandler(file_handler)
# Create a logger object
logging.basicConfig(level=logging.DEBUG)



@app.route('/')
def index():
    image_dir = 'static/images'
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg') or f.endswith('.png')]
    random_image_file = random.choice(image_files)
    return render_template('index.html', random_image_file="images/"+random_image_file)

@app.route('/mk_background', methods=['GET', 'POST'])
def mk_background():
    #im = Image.new("RGB", (8000, 512), (127, 255, 127)) 
    im = Image.new("RGB", (8000, 512), (0, 0, 0))
    for i in range(0, 1000):
        if i > 500:
            DIR = "/mnt/HDD500/0WORKSHOP-with-NOTEBOOKS/clouds/*.png"
            #DIR = "static/images/small/*.jpg"
        else:
            DIR = "static/images/medium/*.jpg"
        thumb = random.choice(glob.glob(DIR))
        logger.debug('This is a debug message: %s', thumb)
        print("THUMB:", thumb)
        Thum = Image.open(thumb)
        im.paste(Thum, ((randint(0, im.size[0])), randint(0, im.size[1]) - 50))
        filename = "static/images/assets/ThumbNails_Background.png"
        im.save(filename)
    uid = str(uuid.uuid4())  # Generate a unique ID using uuid
    # static/images/assets/UNIQUE_ID.mp4
    png_bak = os.path.join("static", "images/assets", f"{uid}.png")
    shutil.copy("static/images/assets/ThumbNails_Background.png", png_bak)
    return redirect('/mkvid')
NewFile = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")+".mp4"
print('NewFile: ',NewFile)
@app.route('/mkvid')
def mkvid():
    Filename = "static/images/ThumbNails_Background.png"
    Video_file = "static/images/ThumbNails_Background_FFmpeg.mp4"
    command = [
        'FFmpeg', '-hide_banner',
        '-loop', '1', '-i', f'{Filename}',
        '-vf', 'scale=8000:512,scroll=horizontal=0.0001,crop=768:512:0:0,format=yuv420p',
        '-t', '240', '-y', f'{Video_file}'
    ]
    subprocess.run(command)
    reprocess = "static/images/assets/ThumbNails_Background_FFmpeg.mp4" 
    reprocessed = "static/images/assets/Good_ThumbNails_Background_FFmpeg.mp4"   
    command2 = [
    'ffmpeg', '-hide_banner',
    '-i', f'{reprocess}',
    '-c:a', 'copy', '-y', f'{reprocessed}'
    ]
    subprocess.run(command2)      
    
    
    return redirect('/mkvid2')

@app.route('/mkvid2')
def mkvid2():
    reprocessed = "static/images/assets/Good_ThumbNails_Background_FFmpeg.mp4"
    final = 'static/images/assets/long_512-768.mp4'  
    command2 = [
    'ffmpeg', '-hide_banner',
    '-i', f'{reprocessed}',
    '-vf', 'scale=512:768,setsar=1/1',
    '-c:a', 'copy', '-y', f'{final}'
    ]
    app.logger.info("FINAL_FILE",f'{final}')
    subprocess.run(command2)
    Filenamez = "images/assets/ThumbNails_Background.png"
    Video_filez = "images/assets/long_512-768.mp4" 
    Video_filel = "images/assets/Good_ThumbNails_Background_FFmpeg.mp4" 
    uid = str(uuid.uuid4())
    shutil.copy("static/images/assets/ThumbNails_Background.png", f"static/images/assets/{uid}.png")
    shutil.copy("static/images/assets/long_512-768.mp4", f"static/images/assets/{uid}long_512-768.mp4")
    shutil.copy("static/images/assets/Good_ThumbNails_Background_FFmpeg.mp4", f"static/images/assets/{uid}Good_ThumbNails_Background_FFmpeg.mp4") 
    return render_template("mkvid2.html", filename=Filenamez, video=Video_filez,video2=Video_filel)
@app.route('/mkmoz', methods=['GET', 'POST'])
def mkmoz():
    im = Image.new("RGB", (2048,2048), (0,0,0))
    for i in range(0, 1000):
        if i > 500:
            DIR = "static/images/small/*.jpg"
        else:
            DIR = "static/images/medium/*.jpg"
        thumb = random.choice(glob.glob(DIR))       
        print("THUMB:",thumb)
        Thum = Image.open(thumb)            
        im.paste(Thum,((randint(0,im.size[0])),randint(0,im.size[1])-50))
        filename = "static/images/assets/ThumbNails.png"
        im.save(filename)
        Filename="images/assets/ThumbNails.png"
    return render_template("mkmoz.html", filename=Filename)



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5200)
