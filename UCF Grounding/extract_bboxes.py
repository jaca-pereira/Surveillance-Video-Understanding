import json
import os
import random
import shutil
import zipfile

import cv2

# Load the UCFCrime_Train.json file
with open('UCFCrime_Train.json') as f:
    data = json.load(f)

# Load the example task.json file
with open('task.json') as f:
    task_template = json.load(f)
# Load the example annotations.json file
with open('annotations.json') as f:
    annotations_template = json.load(f)


# Iterate over each video
def generate_color(current_colors):
    while True:
        color = '#%06x' % random.randint(0, 0xFFFFFF)
        if color not in current_colors:
            return color

for video, video_info in data.items():


    # Create a new task dictionary based on the example task.json file
    task = task_template.copy()
    annotations = annotations_template.copy()
    # Get the fps of the video
    cap = cv2.VideoCapture(f'{video}.mp4')
    fps = cap.get(cv2.CAP_PROP_FPS)
    cap.release()

    # Change the shapes key to a list with an item per bounding box of the video
    shapes = []
    for frame, frame_info in video_info['response'].items():
        for bbox in frame_info['bboxes']:
            # Create a new shape entry based on the template
            shape = annotations_template[0]['shapes'][0].copy()
            # Replace the "points" entry with the bounding box coordinates
            shape['points'] = bbox
            # Replace the "frame" entry with the frame number multiplied by the fps of the video
            shape['frame'] = int(frame) * fps
            shapes.append(shape)
    annotations[0]['shapes'] = shapes


    # Change the name key to the video name
    task['name'] = video

    # Change the labels key to the objects in the video
    objects = set(obj for frame in video_info['response'].values() for obj in frame['objects'])


    task['labels'] = [{'name': obj, 'color': generate_color([label['color'] for label in task['labels']]), 'attributes': [], 'type': 'rectangle', 'sublabels': []} for obj in objects]

    # Change the start_frame and stop_frame of the job to the start and end frame of the video
    frames = [int(frame) for frame in video_info['response'].keys()]
    start_frame, stop_frame = min(frames), max(frames)
    task['data']['start_frame'] = start_frame
    task['data']['stop_frame'] = stop_frame
    task['jobs'][0]['start_frame'] = start_frame
    task['jobs'][0]['stop_frame'] = stop_frame

    # Save the new task dictionary to a new task.json file named after the video
    with open(f'{video}_task.json', 'w') as f:
        json.dump(task, f)

    # Save the new annotations dictionary to a new annotations.json file named after the video
    with open(f'{video}_annotations.json', 'w') as f:
        json.dump(annotations, f)

    video_dir = os.path.join('Surveillance-Video-Understanding', 'UCF Grounding', video)
    os.makedirs(video_dir, exist_ok=True)
    # Copy the annotations.json and task.json files of the video to the new directory
    shutil.copy(f'{video}_annotations.json', video_dir)
    shutil.copy(f'{video}_task.json', video_dir)

    # Create a new 'data' directory inside the new directory and copy the actual video to this 'data' directory
    data_dir = os.path.join(video_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    shutil.copy(f'{video}.mp4', data_dir)

    # Create a zip file of the new directory
    with zipfile.ZipFile(f'{video_dir}.zip', 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(video_dir):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), video_dir))

    # Remove the directory after creating the zip file
    shutil.rmtree(video_dir)
