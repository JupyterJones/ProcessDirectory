from flask import Flask, render_template, request, send_file, url_for
import os
import subprocess
import shutil
from datetime import datetime
import logging
import random
import glob
from moviepy.editor import ImageSequenceClip, VideoFileClip

app = Flask(__name__, template_folder='templates')
app.config['UPLOAD_FOLDER'] = 'uploads'
# Configure logging
log_formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_handler = logging.FileHandler('myapp.log')
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(log_formatter)

app.logger.addHandler(file_handler)

app.config['UPLOAD_FOLDER'] = 'uploads'

# Define the path to the video file
video_file = 'uploads/SE2.mp4'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Process the uploaded files
        # ... (your existing code)

        # Return the generated video file
        output_video = 'static/uploads/SE2a.mp4'
        return send_file(output_video, as_attachment=True)

    # Render the upload form
    return render_template('index.html')
@app.route('/slow_video', methods=['GET'])
def slow_video():
    # Perform any necessary processing or calculations
    video_path = 'uploads/SUPER_EFFECT_Output.mkv'
    output_path = '/home/jack/Desktop/ProcessDirectory/static/uploads/SE.mp4'

    # Load the video using MoviePy
    video = VideoFileClip(video_path)

    # Apply the desired filters using MoviePy
    processed_video = video.fx('time_symmetrize').fx('speedx', 0.025)

    # Write the processed video to the output path
    processed_video.write_videofile(output_path, codec='libx264', fps=video.fps)

    # Return the rendered template with the video URL
    return render_template('slow_video.html', video_url=output_path)

# Rest of the code remains the same

@app.route('/process', methods=['GET', 'POST'])
def process():
    input_directory = request.files['input_directory']
    logging.debug('input_directory:', input_directory.filename)
    output_video = 'output_video.mp4'

    # Save the uploaded directory to a folder
    input_directory.save(os.path.join(app.config['UPLOAD_FOLDER'], input_directory.filename))
    logging.debug('Saved input directory:', input_directory.filename)

    # Get a list of image files in the chosen directory
    image_files = glob.glob(os.path.join(app.config['UPLOAD_FOLDER'], input_directory.filename, '*.jpg'))
    logging.debug('Image files:', image_files)
    logging.debug('input_directory: %s', input_directory.filename)
    logging.debug('Saved input directory: %s', input_directory.filename)
    logging.debug('Image files: %s', image_files)

    # Create ImageSequenceClip object from selected images
    clip = ImageSequenceClip(image_files, fps=24)

    # Write video file using Moviepy
    clip.write_videofile(output_video, codec='libx264', fps=24)

    # Return the generated video file
    return send_file(output_video, as_attachment=True)

@app.route('/choose_dir', methods=['GET', 'POST'])
def choose_dir():
    if request.method == 'POST':
        # Get the selected directory from the form
        output_images_dir = request.form['output_images_dir']
        
        # Set output file name and path
        output_video = 'static/uploads/output_video.mp4'

        # Set the frame rate
        fps = 24

        # Select images from the chosen directory
        image_list = random.sample(glob.glob(os.path.join(output_images_dir, '*.jpg')), 50)

        # Create ImageSequenceClip object from selected images
        clip = ImageSequenceClip(image_list, fps=fps)

        # Write video file using Moviepy
        clip.write_videofile(output_video, codec='libx264', fps=fps)

        # Return the generated video file
        return send_file(output_video, as_attachment=True)
        
    # If a GET request, render the form
    return render_template('choose_dir.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5100))
    app.run(debug=True, host='0.0.0.0', port=port)