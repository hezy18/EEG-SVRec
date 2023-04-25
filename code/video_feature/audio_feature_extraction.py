# v0.1
# 提取音频并保存，生成 audio_feature.csv & tempo.json

import numpy as np
import pandas as pd
import os
import json
import os
# from pydub import AudioSegment
from tqdm import tqdm
# import logging
# logging.basicConfig(level=logging.CRITICAL)
import warnings
warnings.filterwarnings("ignore")
from tqdm import tqdm

import config
exp_list = config.exp_list
threshold = config.threshold

# os.environ["IMAGEIO_FFMPEG_EXE"] = "/Users/hezhiyu/opt/anaconda3/envs/video/lib/python3.8/site-packages/ffmpeg/"

def get_done_id_list():
    id_list=[]
    filenames = os.listdir('audio')
    for filename in filenames:
        if filename=='.DS_Store':
            continue
        # print(filename)
        id = filename.split('.')[0]
        if id!='':
            id_list.append(id)
            
    f = open('done_iids.txt', 'w') 
    for iid in id_list:
        f.writelines(str(iid)+'\n')
    f.close()
    return id_list

id_list = get_done_id_list()

def extract_audio(id):
    import moviepy.editor as mp
    my_clip = mp.VideoFileClip('douyin/'+id+'.mp4')
    my_clip.audio.write_audiofile('audio/'+id+'.mp3')


def get_audio():
    filenames = os.listdir('douyin')
    for filename in tqdm(filenames):
        print(filename)
        id = filename.split('.')[0]
        if id!='':
            if id not in id_list:
                extract_audio(id)

get_audio()

# ComParE_2016
def get_features():
    import opensmile
    smile = opensmile.Smile(
    feature_set=opensmile.FeatureSet.ComParE_2016,
    feature_level=opensmile.FeatureLevel.Functionals,
    )
    import librosa
    def get_audiofeatures(id):
        song,sr = librosa.load('audio/'+id+'.mp3',sr=None)
        y = smile.process_signal(song,sampling_rate = sr)
        y["music"] = 'audio/'+id+'.mp3'
        # print(y)
        # print(type(y)==pd.DataFrame)
        return y

    result = None
    filenames = os.listdir('audio')
    for filename in tqdm(filenames):
        # print(filename)
        id = filename.split('.')[0]
        if id!='':
            y=get_audiofeatures(id)
        if result is None:
            result = y
        else:
            result = pd.concat([result, y])
    

    result.to_csv('audio_features_emotion.csv')

get_features()

import librosa
def get_tempo_features():

    def get_tempo_audiofeatures(id):
        y,sr = librosa.load('audio/'+id+'.mp3',sr=None)
        # melspec = librosa.feature.melspectrogram(y, sr, n_fft=1024, hop_length=512, n_mels=128)
        # logmelspec = librosa.power_to_db(melspec)
        
        # temporgram = librosa.feature.tempogram(y, sr)
        # fourier_tempogram = librosa.feature.fourier_tempogram(y, sr)
        
        onset_env = librosa.onset.onset_strength(y, sr=sr, hop_length=512, aggregate=np.median)
        tempo, _ = librosa.beat.beat_track(onset_envelope=onset_env, sr=sr)
        # print('bpm',tempo)
        
        # zero_crossings = librosa.feature.zero_crossing_rate(y)
        # print('zero_crossing', sum(zero_crossings))
        
        # print(logmelspec.shape,temporgram.shape,fourier_tempogram.shape)
        return 'audio/'+id+'.mp3',tempo
        

    tempo_dict={}
    filenames = os.listdir('audio')
    for filename in tqdm(filenames):
        # print(filename)
        id = filename.split('.')[0]
        if id!='':
            music, tempo = get_tempo_audiofeatures(id)
            tempo_dict[music] = tempo
    return tempo_dict

id_tempo = get_tempo_features()

with open('tempo.json','w') as f:
    f.write(json.dumps(id_tempo))