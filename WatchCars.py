#!.venv/bin/python3

import cv2
import json
import subprocess
import os
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("map", type=str, help="Image file to overlay car locations")
parser.add_argument("output", type=str, help="mp4 output file")
parser.add_argument("geocoordanites", type=str, help="Geocoordanites of all cars on each frame .json file")
parser.add_argument("H", type=str, help="Homography 3x3 matrix converting geocoorinates to map image pixel locations .json file")
parser.add_argument("-show_geos", action="store_true", help="Show geocoordanites of cars")
args = parser.parse_args()

map_img = cv2.imread(args.map)
height, width, _ = map_img.shape

output_path = args.output
intermediate_file = "__inter__.mp4"
vidwriter = cv2.VideoWriter(intermediate_file, fps=15, fourcc=cv2.VideoWriter_fourcc(*"mp4v"), frameSize=(width, height))

with open(args.geocoordanites, "r") as f:
    geos = json.load(f)
with open(args.H, "r") as f:
    H = json.load(f)

for geoList in geos:
    img = map_img.copy()
    for geo in geoList:
        dest = [int((geo[0] * H[0][0] + geo[1] * H[0][1] + H[0][2])/(geo[0] * H[2][0] + geo[1] * H[2][1] + H[2][2])),
                int((geo[0] * H[1][0] + geo[1] * H[1][1] + H[1][2])/(geo[0] * H[2][0] + geo[1] * H[2][1] + H[2][2]))]
        if args.show_geos:
            cv2.putText(img, text=f"{geo[0]} {geo[1]}", org=(dest[0]-100, dest[1]-10), fontFace=cv2.LINE_AA, fontScale=0.5, thickness=2, color=(255, 0, 0))
        cv2.circle(img=img, radius=10, color=[255, 0, 0], center=dest, thickness=-1)    
    vidwriter.write(img)
vidwriter.release()

if os.path.exists(output_path):
    os.remove(output_path)
# the media is corrupt in curtain file editors for whatever reason, running it through ffmpeg fixes this
subprocess.run(["ffmpeg", "-i", intermediate_file, output_path])
os.remove(intermediate_file)