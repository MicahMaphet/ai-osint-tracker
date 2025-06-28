#!.venv/bin/python3

import cv2
import numpy as np
from tqdm import tqdm
from argparse import ArgumentParser
from transformers import AutoImageProcessor, DetrForObjectDetection
import torch
import os
import subprocess
import json

parser = ArgumentParser()
parser.add_argument("inputfile", type=str, help="input video mp4 or image file path to scan")
parser.add_argument("outputvid", type=str, nargs="?", help="output mp4 video file path")
parser.add_argument("outputgeos", type=str, nargs="?", help="output geo coordanites .json file")
parser.add_argument("H", type=str, help="homography matrix .json file")
parser.add_argument("-frames", type=int, help="max number of frames to scan")
args = parser.parse_args()

image_processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

# load Homography matrix
with open(args.H, "rb") as f:
    H = json.load(f)

input = args.inputfile

vidreader = cv2.VideoCapture(input)

fps = vidreader.get(cv2.CAP_PROP_FPS)
frames = int(vidreader.get(cv2.CAP_PROP_FRAME_COUNT))
if args.frames:
    frames = min(frames, args.frames)
shape = (int(vidreader.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vidreader.get(cv2.CAP_PROP_FRAME_HEIGHT)))
intermediate_file = "__inter__.mp4"

vidwriter = cv2.VideoWriter(intermediate_file, cv2.VideoWriter_fourcc(*"mp4v"), fps, shape)
input = args.inputfile

if args.outputvid:
    output_path = args.outputvid
else:
    output_path = "watchcars.mp4"

if args.outputgeos:
    output_geos = args.outputgeos
else:
    output_geos = "geos.json"

geos = []
# For every frame in the input video, load it, draw detection boxes from detr and save images to new video
for i in tqdm(range(frames), desc="Scanning video for objects and writing to new video"):
    # load frame from input and process it for the detr
    ret, image = vidreader.read()
    frame = torch.from_numpy(image.transpose(2, 0, 1))
    inputs = image_processor(images=frame, return_tensors="pt")

    # scan processed images for objects
    outputs = model(**inputs)

    # process model outputs
    target_sizes = torch.tensor([shape[::-1]])
    results = image_processor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[0]
    pred_boxes = results["boxes"].long()
    
    geos.append([])
    for j, box in enumerate(pred_boxes):
        if model.config.id2label[results["labels"][j].item()] not in ["car", "truck"]:
            continue
        center = [(int((box[0] + box[2]) / 2)), (int((box[1] + box[3]) / 2))]
        dest = [float((center[0] * H[0][0] + center[1] * H[0][1] + H[0][2])/(center[0] * H[2][0] + center[1] * H[2][1] + H[2][2])),
                float((center[0] * H[1][0] + center[1] * H[1][1] + H[1][2])/(center[0] * H[2][0] + center[1] * H[2][1] + H[2][2]))]
        geos[i].append(dest)
        cv2.circle(image, center=center, radius=2, color=(255, 0, 0), thickness=-1)
    vidwriter.write(image)
vidwriter.release()
with open(output_geos, "w") as f:
    json.dump(geos, f)
# delete targed video if it exists, don't want any errors
if os.path.exists(output_path):
    os.remove(output_path)
# the media is corrupt in curtain file editors for whatever reason, running it through ffmpeg fixes this
subprocess.run(["ffmpeg", "-i", intermediate_file, output_path])
os.remove(intermediate_file)