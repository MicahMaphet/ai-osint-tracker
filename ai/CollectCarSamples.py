#!.venv/bin/python3

import cv2
from tqdm import tqdm
import os
from argparse import ArgumentParser
from transformers import AutoImageProcessor, DetrForObjectDetection
import torch

parser = ArgumentParser()
parser.add_argument("inputfile", type=str, help="input video mp4 or image file path to scan")
parser.add_argument("outputfile", type=str, nargs="?", help="output video/image file path")
parser.add_argument("-frames", type=int, help="max number of frames to scan")
args = parser.parse_args()

image_processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

input = args.inputfile

if args.outputfile:
    output_path = args.outputfile

vidreader = cv2.VideoCapture(input)

frames = int(vidreader.get(cv2.CAP_PROP_FRAME_COUNT))
if args.frames:
    frames = min(frames, args.frames)
shape = (int(vidreader.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vidreader.get(cv2.CAP_PROP_FRAME_HEIGHT)))
car_dir = "train/cars/"
nocar_dir = "train/nocars/"

for i in tqdm(range(frames), desc="Scanning video for objects and writing to new video"):
    ret, frame = vidreader.read()

    img = torch.from_numpy(frame.transpose(2, 0, 1))
    inputs = image_processor(images=img, return_tensors="pt")
    outputs = model(**inputs)

    target_sizes = torch.tensor([shape[::-1]])
    results = image_processor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[0]
    labels = [model.config.id2label[label.item()] for label in results["labels"]]

    pred_boxes = results["boxes"].long()
    for box, label in zip(pred_boxes, labels):
        if label in ["car", "truck"]:
            cv2.imwrite(f"{car_dir}image{len(os.listdir(car_dir))}.png", frame[box[1]:box[3], box[0]:box[2]])    
        else:
            cv2.imwrite(f"{nocar_dir}image{len(os.listdir(nocar_dir))}.png", frame[box[1]:box[3], box[0]:box[2]])    


