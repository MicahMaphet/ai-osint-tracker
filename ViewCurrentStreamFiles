#!.venv/bin/python3
import requests
import argparse
import re
import time

parser = argparse.ArgumentParser()

parser.add_argument('camera', help='camera id, 4 numbers after GDOT in url and video player on website')

args = parser.parse_args()

base_url = \
    f'https://sfs-msc-pub-lq-05.navigator.dot.ga.gov/rtplive/GDOT-CCTV-{args.camera}/'
url = base_url + 'playlist.m3u8'
print(time.ctime())
print(f'master playlist file:\n{url}')
chunklist_file_name = re.findall(r'chunklist.*?\.m3u8', requests.get(url).text)[-1]
chunklist_url = base_url + chunklist_file_name
print(f'which linked to:\n{chunklist_file_name}')
file_names = re.findall(r'media_w.*?\.ts', requests.get(chunklist_url).text)
print(f'which linked to files:\n{file_names}')

