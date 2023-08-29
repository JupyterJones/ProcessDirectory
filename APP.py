from flask import Flask, request, send_file, render_template
from moviepy.editor import ImageSequenceClip
import os
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Specify the upload folder path
app.config['STATIC_FOLDER'] = 'static'   # Specify the static folder path


@app.route('/', methods=['GET'])
def index():
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Upload Files</title>
        </head>
        <body>
            <form method="post" action="/process" enctype="multipart/form-data">
                <label for="input_files">Select image files:</label><br>
                <input type="file" id="input_files" name="input_files" accept=".jpg, .jpeg, .png" multiple><br><br>
                <label for="fps">FPS (Frames per second):</label><br>
                <input type="number" id="fps" name="fps" min="1" max="30" value="24"><br><br>
                <input type="submit" value="Convert">
            </form>
        </body>
        </html>
    '''




@app.route('/process', methods=['POST'])
def process():
    try:
        input_files = request.files.getlist('input_files')
        fps = int(request.form['fps'])

        # Create a temporary directory to store uploaded image files
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        os.makedirs(temp_dir, exist_ok=True)

        # Save uploaded image files to the temporary directory
        image_paths = []
        for file in input_files:
            file_path = os.path.join(temp_dir, file.filename)
            file.save(file_path)
            image_paths.append(file_path)

        # Create ImageSequenceClip object from selected images
        #clip = ImageSequenceClip(image_paths, fps=fps)
        clip = ImageSequenceClip(image_paths, durations=[1.0] * len(image_paths))  # Display each image for 1 second


        # Generate the output video file path based on current date and time
        current_datetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        output_video_path = os.path.join(app.config['STATIC_FOLDER'], 'video', f'{current_datetime}.mp4')

        # Write video file using Moviepy
        clip.write_videofile(output_video_path, codec='libx264', fps=fps)

        # Return the generated video file
        return send_file(output_video_path, as_attachment=True)

    except Exception as e:
        # Log the exception details
        app.logger.exception('An error occurred during processing:')

        # Handle the exception
        return render_template('error.html', error_message=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
