#!/home/jack/Desktop/ffmpeg_flask/ffmpeg_server/bin/python 
from flask import Flask, render_template, request, redirect, url_for, send_from_directory, Response,flash
from flask import send_file, make_response,g
import os
import pygame
from gtts import gTTS
import cv2
import dlib
import numpy as np
from random import randint
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from moviepy.editor import concatenate_videoclips, AudioFileClip, TextClip
import moviepy.editor
import subprocess 
import shutil  
from pathlib import Path as change_ext
import logging
from io import BytesIO
import sqlite3
import random
import glob
import base64
import tempfile
import datetime
import imageio
import time
import re
from werkzeug.utils import secure_filename
import shutil
from time import sleep
from pydub import AudioSegment
from PIL import Image, ImageDraw, ImageFont
from logging.handlers import RotatingFileHandler
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import uuid
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
TExt = "TEXT TEST 6789"
logger.debug('This is a debug message: %s', TExt)
TEXT = "TEXT TEST abcd"
logger.debug('This is a debug message: %s', TEXT)
# Set up logging for the Flask app


app = Flask(__name__)

app.secret_key = os.urandom(24)
app.logger.addHandler(file_handler)
# Create a logger object


logging.basicConfig(level=logging.DEBUG)
directory_path = "static/current_project"

if not os.path.exists(directory_path):
    os.makedirs(directory_path)
app.config['UPLOAD_FOLDER'] = 'static/images/uploads'
app.config['RESULTS_FOLDER'] = 'static/videos/results'
app.config['THUMBNAILS_FOLDER'] = 'static/images/thumbnails'
app.config['CHECKPOINT_PATH'] = 'checkpoints/wav2lip_gan.pth'
app.config['AUDIO_PATH'] = 'sample_data/input_audio.wav'
app.config['video_PATH'] = 'sample_data/input_videio.mp4'
app.config['DATABASE'] = 'code.db'  # SQLite database file
@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# use the search function as a route
#app.add_url_rule('/search', 'search', search)

def zip_lists(list1, list2):
    return zip(list1, list2)

app.jinja_env.filters['zip'] = zip_lists

directory_path = 'temp'  # Replace with the desired directory path
# Create the directory if it doesn't exist
os.makedirs(directory_path, exist_ok=True)

@app.route('/')
def index():
    image_dir = 'static/images'
    image_files = [f for f in os.listdir(image_dir) if f.endswith('.jpg')]
    random_image_file = random.choice(image_files)
    return render_template('index.html', random_image_file="images/"+random_image_file)

existing_subdirectories = glob.glob(os.path.join("static/current_project", "*"))
@app.route('/get_files', methods=['POST'])
def get_files():
    subdirectory = request.form.get('subdirectory')
    file_options = []
    if subdirectory and subdirectory in existing_subdirectories:
        subdirectory_path = os.path.join("static/current_project", subdirectory)
        files = os.listdir(subdirectory_path)
        file_options = [
            f'<option value="{file}">{file}</option>'
            for file in files
            if os.path.isfile(os.path.join(subdirectory_path, file))
        ]
    return ''.join(file_options)

@app.route('/image_list')
def image_list():
    image_directory = 'static/current_project/Narrators'
    image_list = [
        filename
        for filename in os.listdir(image_directory)
        if filename.endswith('.jpg')
    ]
    return render_template('image_list.html', image_list=image_list)

@app.route('/upload', methods=['POST','GET'])
def upload():
    filename = request.form['filename']
    if filename:
        src_path = 'static/current_project/Narrators/' + filename
        dest_path = 'static/TEMP.jpg'
        shutil.copyfile(src_path, dest_path)
        return redirect('/')
    else:
        return 'No file selected.'



def outline_blue(filename1, outfile_jpg, sigma=0.33):
    """
    USE:
    filename1 = '/home/jack/Desktop/Imagedata/0-original-images/07082orig.jpg'
    outfile_jpg = '/home/jack/Desktop/dockercommands/images/useresult.png'
    outlineJ(filename1, outfile_jpg)
    """
    # Load the image using OpenCV
    image = cv2.imread(filename1)

    # Apply Canny edge detection using the auto_canny function
    edged = auto_canny(image, sigma=0.33)

    # Invert the image to have white outlines on black background
    inverted = cv2.bitwise_not(edged)

    # Save the inverted image temporarily
    cv2.imwrite("static/outlines/temp2.png", inverted)

    # Load the inverted image using PIL
    frontimage = Image.open('static/outlines/temp2.png').convert("1")
    frontImage = frontimage.convert("RGBA")

    # Modify the RGBA data to change white pixels to light blue
    datas = frontImage.getdata()
    newData = []
    for item in datas:
        if item[0] == 255 and item[1] == 255 and item[2] == 255:
            newData.append((173, 216, 230, 0))  # Light blue color
        else:
            newData.append(item)

    frontImage.putdata(newData)

    # Open the background image
    background = Image.open(filename1)

    # Calculate the position to paste the frontImage at the center
    width = (background.width - frontImage.width) // 2
    height = (background.height - frontImage.height) // 2

    # Paste the frontImage onto the background
    background.paste(frontImage, (width, height), frontImage)

    # Save the resulting image with light blue outlines
    background.save(outfile_jpg)

    # Save the background image with time-based filename
    savefile = FilenameByTime("static/outlines/")
    background.save(savefile)

    # Convert the background image to RGB format
    background_rgb = background.convert("RGB")

    # Log a message indicating completion
    logging.info("Outline processing complete.")

    return background_rgb

# Define the auto_canny function used for edge detection

def auto_canny(image, sigma=0.33):
    # compute the median of the single channel pixel intensities
    v = np.median(image)
    # apply automatic Canny edge detection using the computed median
    lower = int(max(0, (1.0 - sigma) * v))
    upper = int(min(255, (1.0 + sigma) * v))
    edged = cv2.Canny(image, lower, upper)
    # return the edged image
    return edged

# Define the FilenameByTime function
def FilenameByTime(directory):
    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = directory+"/"+timestr+"_.png"
    return filename 

@app.route('/mk_background', methods=['GET', 'POST'])
def mk_background():
    #im = Image.new("RGB", (8000, 512), (127, 255, 127)) 
    im = Image.new("RGB", (8000, 512), (0, 0, 0))
    for i in range(0, 1000):
        if i > 500:
            DIR = "static/images/small/*.jpg"
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


def extract_code_blocks(file_path):
    with open(file_path) as file:
        content = file.read()
    return content.split("--Code Start:")[1:]

def format_datetime(datetime_str):
    return datetime_str.replace("_", " ")

def get_first_two_lines(file_path):
    with open(file_path) as file:
        lines = [next(file).strip() for _ in range(3)]
    return lines

@app.route('/enter_code', methods=['GET', 'POST'])
def enter_code():
    formatted_datetime = ""  # Initialize the variable
    if request.method == 'POST':
        code_block = request.form['code_block']
        formatted_datetime = datetime.datetime.now().strftime("%a_%d_%b_%Y %H:%M:%S")
        with open('codeshints.txt', 'a') as file:
            file.write(f"--Code Start:\n{formatted_datetime}\n{code_block}\n--Code End:\n\n")
        # Log code entry
        logger.debug('New code entered: %s', code_block)
        
        
    first_two_lines = get_first_two_lines('codeshints.txt')    
    return render_template('enter_data.html', formatted_datetime=formatted_datetime, first_two_lines=first_two_lines)

@app.route('/search_code', methods=['GET', 'POST'])
def search_code():
    if request.method == 'POST':
        keyword = request.form['keyword']
        code_blocks = extract_code_blocks('codeshints.txt')
        filtered_blocks = [block for block in code_blocks if keyword in block]
        formatted_datetime_blocks = []
        
        for block in filtered_blocks:
            match = re.search(r"\w+_\d+_\w+_\d+_\d+:\d+:\d+", block)
            if match:
                formatted_datetime = format_datetime(match.group(0))
            else:
                formatted_datetime = "Unknown datetime format"
            
            formatted_datetime_blocks.append(
                {"datetime": formatted_datetime, "code_block": block}
            )
            
        # Log search activity
        logger.debug('Keyword searched: %s', keyword)
        return render_template('search_results.html', keyword=keyword, code_blocks=formatted_datetime_blocks)
    
    return render_template('search_data.html')



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5300)

