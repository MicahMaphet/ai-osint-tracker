#!.venv/bin/python3
import os
from argparse import ArgumentParser
import subprocess
import shutil

parser = ArgumentParser()
parser.add_argument("camera", type=str, help="camera media directory")
parser.add_argument("output", type=str, nargs="?", help="output file")
parser.add_argument("-clips", type=int, help="max numbers of clips to aggregate")
args = parser.parse_args()

if not args.camera[:6] == "media/":
    args.camera = "media/" + args.camera

if args.clips:
    aggregate_number = min(args.clips, len(os.listdir(f"{args.camera}")))
else:
    aggregate_number = len(os.listdir(f"{args.camera}"))

if args.output:
    output_file = args.output
else:
    output_file = "output.mp4"

concat = "concat:"

if os.path.exists("intermediate"):
    shutil.rmtree("intermediate")
os.mkdir("intermediate")
for i in range(aggregate_number):
    concat += f"intermediate/{i}.ts|"
    subprocess.run(["ffmpeg", "-i", f"{args.camera}/media{i}.mp4", "-c", "copy", f"intermediate/{i}.ts"])
concat = concat[:-1]

subprocess.run(["ffmpeg", "-i", concat, "-c", "copy", output_file])