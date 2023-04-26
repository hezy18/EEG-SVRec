import tqdm
import numpy as np
from scipy.integrate import simps
import math
import os
import json
from sklearn import preprocessing

import config
exp_list = config.exp_list

FREQ_BANDS = {
    "delta": [0.5, 4],   # 1-3 
    "theta": [4, 8],     # 4-7
    "alpha": [8, 13],    # 8-12
    "beta": [13, 30],    # 13-30
    "gamma": [25,50]
}

def bandpower(data, sf, band, method='welch', window_sec=None, relative=False):
    from scipy.signal import welch
    from mne.time_frequency import psd_array_multitaper

    band = np.asarray(band)
    low, high = band
    print(low,high)

    # Compute the modified periodogram (Welch)
    if method == 'welch':
        if window_sec is not None:
            nperseg = window_sec * sf
        else:
            nperseg = (2 / low) * sf

        freqs, psd = welch(data, sf, nperseg=nperseg)

    elif method == 'multitaper':
        psd, freqs = psd_array_multitaper(data, sf, adaptive=True,
                                          normalization='full', verbose=0)

    # Frequency resolution
    freq_res = freqs[1] - freqs[0]

    # Find index of band in frequency vector
    idx_band = np.logical_and(freqs >= low, freqs <= high)

    # Integral approximation of the spectrum using parabola (Simpson's rule)
    bp = simps(psd[idx_band], dx=freq_res)

    if relative:
        bp /= simps(psd, dx=freq_res)
    return bp

def get_bp(idx2eeg, out_path):
    print('extracting bp')
    # idx2de = {}
    idx_long = {}
    j=0
    de_list_all=[]
    for idx in idx2eeg.keys():
        eeg = np.array(idx2eeg[idx])
        # print(eeg.shape)
        de_list = []
        for i in range(int(eeg.shape[1]/1000)):
            fs = 1000
            tmp_data = eeg[:, i * 1000 : i * 1000 + 1000]
            tmp_fs = []
            tmp_fs_line = []
            for channel_id in range(tmp_data.shape[0]):
                tmp_feature = []
                for band_item in FREQ_BANDS.values():
                    bp = math.log(bandpower(tmp_data[channel_id], fs, band_item))
                    tmp_feature.append(bp)
                    tmp_fs_line.append(bp)
                tmp_fs.append(tmp_feature)
            de_list.append(tmp_fs)
            de_list_all.append(tmp_fs_line)
        # idx2de[idx] = de_list
        idx_long[idx] = len(de_list)
        # print(len(de_list_all))
        j+=1
    print(j)
    print(len(de_list_all),len(de_list_all[0]))
    de_all = np.array(de_list_all)
    print(de_all.shape)
    min_max_scaler = preprocessing.MinMaxScaler()
    nor_de = min_max_scaler.fit_transform(de_all)
    print(nor_de)
    idx2de_nor_avg={}
    start=0
    print(idx_long[61])
    for idx in idx_long:
        my_long = idx_long[idx]
        de = nor_de[start:start+my_long,:]
        print('de',my_long, de.shape)
        tmp_fs = []
        for channel_id in range(tmp_data.shape[0]):
            tmp_feature = []
            i=0
            for band_item in FREQ_BANDS.values():
                # print(channel_id*5+i)
                tmp_feature.append(np.mean(de[:,channel_id*5+i]))
                i+=1
            tmp_fs.append(tmp_feature)
        idx2de_nor_avg[idx] = tmp_fs
        start+=my_long
    json.dump(idx2de_nor_avg, open(out_path, 'w'))
    
if __name__ == '__main__':
    for exp_name in tqdm.tqdm(exp_list):
        print(f'-----------------------------feature extraction of exp {exp_name}-------------------------------')
        idx2eeg = json.load(open(f'../data/raw/' + exp_name + '_idx2eeg.json'))
        get_bp(idx2eeg, f'../data/raw/' + exp_name + '_idx2de_nor_avg.json')