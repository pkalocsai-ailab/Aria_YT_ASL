import os
import cv2
import csv

# Specify the directory containing .mp4 files
directory = '../../DATA/videos2'  # Replace with your target directory

# List to store video information
video_info = []

# Get all .mp4 files in the directory
mp4_files = [f for f in os.listdir(directory) if f.endswith('.mp4')]

# Calculate total number of 1000s of videos
total_thousands = len(mp4_files) // 1000

# Iterate over all .mp4 files
for index, filename in enumerate(mp4_files):
    # Full path to the video file
    filepath = os.path.join(directory, filename)

    # Open the video file
    cap = cv2.VideoCapture(filepath)

    # Get the width and height of the video
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Get the number of frames in the video
    num_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Get the frame rate (FPS) of the video
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Calculate the length of the video in seconds
    length_in_seconds = round(num_frames / fps) if fps > 0 else 0

    # Append the information to the list
    video_info.append((filename, width, height, num_frames, fps, length_in_seconds))

    # Release the video capture object
    cap.release()

    # Print progress every 1000 videos
    if (index + 1) % 1000 == 0:
        current_thousand = (index + 1) // 1000
        print(f"Processing {current_thousand} out of {total_thousands} thousands of videos.")

# Save the data to a .csv file
output_csv = '../../DATA/video_info.csv'
with open(output_csv, mode='w', newline='') as file:
    writer = csv.writer(file)

    # Write header
    writer.writerow(['Video Name', 'Width', 'Height', 'Number of Frames', 'FPS', 'Length in seconds'])

    # Write video information rows
    writer.writerows(video_info)

print(f"Video information has been saved to {output_csv}")
