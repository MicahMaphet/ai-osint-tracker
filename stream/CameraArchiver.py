#!.venv/bin/python3
import urllib.request
import requests
import re
import urllib
from pathlib import Path
import subprocess
import time
import os
from os import path
import time
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument('-wait', type=float, help='time in second to wait between data fetching')
parser.add_argument('camera', type=str, help='camera id, 4 numbers after GDOT in url and video player on website or url')
args = parser.parse_args()

try:
    wait_time = float(args.wait)
    print(f'waiting {wait_time} seconds between stream updating')
except:
    wait_time = 3
# playlist file directing to all of the relevant media for the camera

try:
    camera = args.camera # camera number, in GDOT-CCTV-####
    assert(int(camera) > 0 and int(camera) < 10000)
    print(camera)
    camera = f"GDOT-CCTV-{camera}"
    url = f'https://sfs-msc-pub-lq-05.navigator.dot.ga.gov/rtplive/{camera}/playlist.m3u8'
    print(url)
except:
    url = args.camera
    camera = url[url.find("/rtplive/")+len("/rtplive/"):url.find("/playlist.m3u8")]
print(camera)

# url all the media content will be found in
base_url = url[:url.rfind('/') + 1]

# create the necessary directories if they are not there
Path(f'rawmedia/{camera}/').mkdir(exist_ok=True, parents=True)
Path(f'media/{camera}/').mkdir(exist_ok=True, parents=True)

while True:
    # store all the current file ids to avoid repeats
    file_ids = [f[f.rfind('_')+1:-3] for f in os.listdir(f'rawmedia/{camera}') if path.isfile(path.join(f'rawmedia/{camera}', f))]
    # download the playlist file of that camera
    playlist = requests.get(url).text
    # download the chunklist file linked in the playlist file, the file name periodicaly changes
    file_name = re.findall(r'chunklist_w.*?\.m3u8', playlist)
    if (len(file_name) == 0):
        continue
    file_name = file_name[-1]
    chunklist_url = base_url + file_name
    chunklist = requests.get(chunklist_url).text
    # download the media files listed in the chunklist file
    media_files = re.findall(r'media_w.*?\.ts', chunklist)
    media_concat = 'concat:'

    # 
    any_new_video = False
    for media_file in reversed(media_files):
        if media_file[media_file.rfind('_')+1:-3] not in file_ids:
            any_new_video = True
            continue
    if not any_new_video:
        print(f'no new video on camera {camera} {time.ctime()}')
    for media_file in media_files:
        if not any_new_video:
            break
        if media_file[media_file.rfind('_')+1:-3] in file_ids:
            continue
        print(f'{time.ctime()}\ndownloading video clip: {media_file} from camera {camera}')
        urllib.request.urlretrieve(base_url + media_file, f'rawmedia/{camera}/{media_file}')
        # convert the media file to mp4 for viewing and simultaneously keeping track of data
        subprocess.run(['ffmpeg', '-i', 
                        f'rawmedia/{camera}/{media_file}', 
                        f'media/{camera}/media{len(os.listdir(f'media/{camera}'))}.mp4'],
                        stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    # wait a little, no need to waste data periodically fetching data that update every 4 second
    time.sleep(wait_time)
