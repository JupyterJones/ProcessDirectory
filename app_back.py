from flask import Flask, render_template, request
import os
import subprocess
import shutil
from datetime import datetime
import logging
import random
import glob
import os
import glob
from flask import Flask, render_template, request, send_file, url_for
from moviepy.editor import ImageSequenceClip
# Create a logging object
logging.basicConfig(filename='myapp.log', level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

app = Flask(__name__, static_folder='static')


@app.route('/')
def index():
    return '''
        <form method="post" action="/video" enctype="multipart/form-data">
            <label for="input_video">Select input video file:</label><br>
            <input type="file" id="input_video" name="input_video"><br><br>
            <input type="submit" value="Submit">
        </form>
        <br /><a href="choose_dir">Choose Director and make a video</a><br />
    '''

@app.context_processor
def context_processor():
    # Get the list of subdirectories in the current directory
    subdirectories = next(os.walk('.'))[1]
    # Filter out hidden directories and the 'EXPERIMENT' directory
    directory_list = [d for d in subdirectories if not d.startswith('.') and d != 'EXPERIMENT']
    # Add the list of directories to the context for use in the template
    return {directory_list}
              
              
@app.route('/convert', methods=['POST'])
def convert():
    images = request.files['images']
    fps = int(request.form['fps'])
    output_video = 'output_video.mp4'
    directory_list = context_processor()
    output_images_dir = {directory_list}

    # Save the uploaded images to a folder
    images.save(os.path.join(output_images_dir, images.filename))

    # Create ImageSequenceClip object from selected images
    image_list = random.sample(glob.glob(f"{output_images_dir}/*.jpg"), 30)

    # Create ImageSequenceClip object from selected images
    clip = ImageSequenceClip(image_list, fps=1)

    # Write video file using Moviepy
    clip.write_videofile(output_video, codec='libx264', fps=fps)

    # Return a download link to the newly created video file
    return f'<a href="/{output_video}" download>Download Video</a>'
           
@app.route('/choose_dir', methods=['GET', 'POST'])
def choose_dir():
    if request.method == 'POST':
        # Get the selected directory from the form
        output_images_dir = request.form['output_images_dir']
        
        # Set output file name and path
        output_video = 'lexica-warrior_video4.mp4'

        # Set the frame rate
        fps = 24
        directory_list = convert()
        # Select images from the chosen directory
        image_list = random.sample(glob.glob(f"{directory_list}/*.jpg"),50)
        # randomly sample 50 images
        # Create ImageSequenceClip object from selected images
        clip = ImageSequenceClip(image_list, fps=fps)

        # Write video file using Moviepy
        clip.write_videofile(output_video, codec='libx264', fps=fps)

        # Return the generated video file
        return send_file(output_video, as_attachment=True)
        
    # If a GET request, render the form
    return render_template('choose_dir.html')



@app.route('/video', methods=['POST'])
def process_video():
    DIR = "static/"
    input_video = request.files['input_video']
    
    # Save the uploaded video to a file
    input_video.save(f"{DIR}input_video.mp4")
    
    # Run FFmpeg commands
    command1 = f"ffmpeg -nostdin -i {DIR}input_video.mp4 -filter:v \"minterpolate='mi_mode=mci:mc_mode=aobmc:vsbmc=1:fps=10'\" -c:v libx264 -r 20 -pix_fmt yuv420p -c:a copy -y {DIR}output.mp4"    
    
    subprocess.run(command1, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    command2 = f"ffmpeg -nostdin -i {DIR}output.mp4 -vf mpdecimate,setpts=N/FRAME_RATE/TB -c:v libx264 -r 30 -pix_fmt yuv420p -c:a copy -y {DIR}mpdecimate.mp4"
    
    subprocess.run(command2, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    #DIR = "/home/jack/Desktop/ffmpeg_flask/"
    command3 = f"ffmpeg -i static/mpdecimate.mp4 -filter_complex \"[0:v]trim=duration=14,loop=500:1:0[v];[1:a]afade=t=in:st=0:d=1,afade=t=out:st=0.9:d=2[a1];[v][0:a][a1]concat=n=1:v=1:a=1\" -c:v libx264 -r 30 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest -y static/output.mp4"
    subprocess.run(command3, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    shutil.copy(f"{DIR}output.mp4", f"{DIR}{now}_output.mp4")
    logging.info(f'my_video: f"{DIR}mpdecimate.mp4"') 
    video_file="static/outputALL.mp4"     
    command4 = f'ffmpeg -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -i "{DIR}mpdecimate.mp4" -filter_complex "[0:v]trim=duration=15[v0];[1:v]trim=duration=15[v1];[2:v]trim=duration=15[v2];[3:v]trim=duration=15[v3];[4:v]trim=duration=15[v4];[v0][v1][v2][v3][v4]concat=n=5:v=1:a=0" -c:v libx264 -pix_fmt yuv420p -shortest -y {video_file}'
    subprocess.run(command4, shell=True, stderr=subprocess.PIPE, universal_newlines=True)
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    diR = f"{DIR}/square_videos/"
    logging.info(f'diR: f"{diR}mpdecimate.mp4"')
    shutil.copy(f"{video_file}", f"{diR}{now}_outputALL.mp4")
    logging.info(f'diR: {diR}mpdecimate.mp4')

    
    return render_template('final.html', video_file=f"/square_videos/{now}_outputALL.mp4")




if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5100))
    app.run(debug=True, host='0.0.0.0', port=port)
