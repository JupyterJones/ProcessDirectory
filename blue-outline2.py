import cv2
from PIL import Image
import os
import numpy as np
# Set up logging
import logging
logging.basicConfig(filename='video_outline_creation_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def create_blue_outlines_from_video(video_path, output_dir, sigma=0.33):
    """
    Create transparent blue outlines from frames of a video and save them in the output directory.
    """
    # Create the output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    frame_number = 0
    while cap.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        # Apply Canny edge detection using the auto_canny function
        edged = auto_canny(frame, sigma=0.33)

        # Invert the image to have white outlines on black background
        inverted = cv2.bitwise_not(edged)

        # Load the inverted image using PIL
        frontImage = Image.fromarray(inverted).convert("RGBA")

        # Modify the RGBA data to change white pixels to transparent blue
        datas = frontImage.getdata()
        newData = []
        for item in datas:
            if item[0] == 255 and item[1] == 255 and item[2] == 255:
                newData.append((173, 216, 230, 0))  # Transparent blue color
            else:
                newData.append(item)

        frontImage.putdata(newData)

        # Save the transparent blue outline frame
        outline_filename = f"frame_{frame_number:04d}_outline.png"
        outline_path = os.path.join(output_dir, outline_filename)
        frontImage.save(outline_path)

        logging.info(f"Saved transparent blue outline frame: {outline_filename}")

        frame_number += 1

    cap.release()
    cv2.destroyAllWindows()

    logging.info("Outline creation from video frames complete.")

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

# Call the create_blue_outlines_from_video function with your video file and output directory
if __name__ == "__main__":
    video_path = '/home/jack/Desktop/ProcessDirectory/static/video/20230820113937.mp4'
    output_directory = 'static/images/frames'
    create_blue_outlines_from_video(video_path, output_directory)
    
