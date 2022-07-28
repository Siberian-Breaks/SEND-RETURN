from asyncio import sleep
import requests
import json
import argparse
import csv
import pandas as pd
import time
import os
import shutil
import subprocess
from glob import glob


# Find all 
PATH = os.getcwd()
EXT = "*.csv"
all_csv_files = [file
                 for path, subdir, files in os.walk(PATH)
                 for file in glob(os.path.join(path, EXT))]
print(all_csv_files)

# Combine all csv files into one
df = pd.concat([pd.read_csv(f) for f in all_csv_files])
df.to_csv('lyrical_data.csv', index=False)

# Gather all mp3 files in subdirectories
MP3PATH = os.getcwd()
MP3EXT = "*.mp3"
all_mp3_files = [file
                 for path, subdir, files in os.walk(MP3PATH)
                 for file in glob(os.path.join(path, MP3EXT))]
print(all_mp3_files)

# Move compiled csv file to root directory
os.rename('lyrical_data.csv', '../lyrical_data.csv')

# Move all mp3 files to a new directory
if not os.path.exists('../mp3_files/'):
    os.mkdir('../mp3_files/')
for file in all_mp3_files:
    print(file)
    shutil.copy(file, '../mp3_files/')
