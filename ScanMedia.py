#!.venv/bin/python3

import cv2
from tqdm import tqdm
import os
from argparse import ArgumentParser
from transformers import AutoImageProcessor, DetrForObjectDetection
import torch
from torchvision.utils import draw_bounding_boxes
from torchvision.io import decode_image
from torchvision.utils import save_image
import matplotlib.pyplot as plot

parser = ArgumentParser()
parser.add_argument("inputfile", type=str, help="input video mp4 or image file path to scan")
parser.add_argument("outputfile", type=str, nargs="?", help="output video/image file path")
parser.add_argument("-plot", action="store_true", help="display image instead of saving (unless outputfile is set)")
parser.add_argument("-frames", type=int, help="max number of frames to scan")
args = parser.parse_args()

image_processor = AutoImageProcessor.from_pretrained("facebook/detr-resnet-50")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

input = args.inputfile

if args.outputfile:
    output_path = args.outputfile

# convert single image 
if input[-4:] != ".mp4":
    if not args.outputfile:
        output_path = "tracked.png"
    image = decode_image(input)
    inputs = image_processor(images=image, return_tensors="pt")

    # scan processed image for objects
    outputs = model(**inputs)

    # process model outputs
    target_sizes = torch.tensor([[image.shape[1], image.shape[2]]])

    results = image_processor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[0]

    image = (255.0 * (image - image.min()) / (image.max() - image.min())).to(torch.uint8)
    image = image[:3, ...]
    pred_boxes = results["boxes"].long()
    labels = [f"{model.config.id2label[label.item()]}: {score} " for label, score in zip(results["labels"], results["scores"])]
    output_image = draw_bounding_boxes(image, pred_boxes, labels, colors="red")
    if args.plot:
        if args.outputfile:
            save_image(output_image / 255, output_path)
        plot.imshow(output_image.permute(1, 2, 0))
        plot.show()
    else:
        save_image(output_image / 255, output_path)
    exit()

if not args.outputfile:
    output_path = "trackedmedia.mp4"
if os.path.exists(output_path):
    os.remove(output_path)

vidreader = cv2.VideoCapture(input)

fps = vidreader.get(cv2.CAP_PROP_FPS)
total_frames = int(vidreader.get(cv2.CAP_PROP_FRAME_COUNT))
if args.frames:
    total_frames = min(total_frames, args.frames)
shape = (int(vidreader.get(cv2.CAP_PROP_FRAME_WIDTH)), int(vidreader.get(cv2.CAP_PROP_FRAME_HEIGHT)))

vidwriter = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, shape)

# For every frame in the input video, load it, draw detection boxes from detr and save images to new video
for i in tqdm(range(total_frames), desc="Scanning video for objects and writing to new video"):
    # load frame from input and process it for the detr
    ret, frame = vidreader.read()
    frame = torch.from_numpy(frame.transpose(2, 0, 1))
    inputs = image_processor(images=frame, return_tensors="pt")

    # scan processed images for objects
    outputs = model(**inputs)

    # process model outputs
    target_sizes = torch.tensor([shape[::-1]])
    results = image_processor.post_process_object_detection(outputs, threshold=0.9, target_sizes=target_sizes)[0]

    frame = (255.0 * (frame - frame.min()) / (frame.max() - frame.min())).to(torch.uint8)
    frame = frame[:3, ...]
    pred_boxes = results["boxes"].long()
    labels = [f"{model.config.id2label[label.item()]}: {score} " for label, score in zip(results["labels"], results["scores"])]
    output_image = draw_bounding_boxes(frame, pred_boxes, labels, colors="red")

    # write the decoded frame to the new video
    vidwriter.write(output_image.cpu().numpy().transpose(1, 2, 0))
vidwriter.release()