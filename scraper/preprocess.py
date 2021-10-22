import os
from joblib import Parallel, delayed
from os.path import join
from pathlib import Path

import scraper
import re
import subprocess
import num2words
import pydub
from pydub import AudioSegment
import logging

logger = logging.getLogger()
logging.basicConfig(level="INFO", format="%(levelname)s: %(filename)s: %(message)s")


AUDIO_EXTENSION = 'mp3'
READ_FILE_THREADS = 1
path = '../data/TedSrt'
split = 'train'

src_path = 'data'


def clean_text(text):
    '''
    Text processing to clean text before saving as label
    to lowercase, convert years to words, convert digits to words, remove symbols
    '''
    text = text.lower().strip('\n')
    text = re.sub(r'[^\w\s]', ' ', text)
    text = ' '.join([num2words.num2words(i, to='year') if (i.isdigit() & (len(i) == 4)) else i for i in text.split()]) # year to words
    text = ' '.join([num2words.num2words(i) if i.isdigit() else i for i in text.split()]) # num to words
    text = re.sub(' +', ' ', text) # remove redundant spaces
    text = text.replace('-', ' ')
    return text

def to_ms(string):
    '''
    Convert string '00:00:00,000' to milliseconds
    to be used for audio slicing
    '''
    string = string.replace(',','')
    hour, minute, second = string.split(':')
    second = int(second)
    second += int(hour) * 3600 * 1000
    second += int(minute) * 60 * 1000
    second = second
    return second

def txt_to_trans(txt_file, file_name, text_processing=clean_text):
    '''
    Convert txt file to transcript format ready to be read into Dataset
    lines formatted as 'filename-idx text_label'
    return lines and time_slices
    '''
    file = open(txt_file, 'r')
    lines = file.readlines()
    file.close()
    
    transcript = []
    time_slices = []

    for i in range(len(lines)):
        idx = re.search('^[\d]+$', lines[i].strip('\ufeff'))
        if idx:
            idx = idx[0]
            time_frame = re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2},[0-9]{3}', lines[i+1])
            if time_frame:
                start, end = to_ms(time_frame[0]), to_ms(time_frame[1])
                time_slices.append((idx, (start, end)))

                text = lines[i+2]
                text = text_processing(text)
                new_line = f"{file_name}-{idx} {text}"
                transcript.append(new_line)
                
    return transcript, time_slices

def save_trans(transcript, output_path):
    '''
    save transcript to output_path
    '''
    if not os.path.exists(os.path.dirname(output_path)):
        os.makedirs(os.path.dirname(output_path))

        with open(output_path, 'w+') as f:
            for line in transcript:
                f.write(f"{line}\n")
            f.close()

def convert(src_path=src_path):
    folder_list = os.listdir(src_path)
    for idx, curr_folder in enumerate(folder_list):
        file_name = str(idx) #save the transcript as idx, can be changed to folder name
        output_path = join(path, split, file_name)
        txt_output_path = join(output_path, file_name + '.trans.txt')
        
        # text
        logging.info(f"{idx}. Creating transcript for {curr_folder}...")
        txt_path = list(Path(join(src_path, curr_folder)).rglob('*.txt'))[0]
        transcript, time_slices = txt_to_trans(txt_path, file_name)
        save_trans(transcript, txt_output_path)
        
        # audio
        logging.info(f"{idx}. Slicing audio for {curr_folder}...")
        audio_path = list(Path(join(src_path, curr_folder)).rglob('*.' + AUDIO_EXTENSION))[0]
        audio_file = AudioSegment.from_file(audio_path, AUDIO_EXTENSION)
        for idx, time_slice in time_slices:
            audio_slice = audio_file[time_slice[0]:time_slice[1]]
            audio_output_path = join(output_path, f"{file_name}-{idx}.{AUDIO_EXTENSION}")
            audio_slice.export(audio_output_path, format=AUDIO_EXTENSION)

def main():
    scraper.main()
    convert(src_path)



if __name__ == "__main__":
    main()