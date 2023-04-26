import json
# from statistics import median_grouped
import pandas as pd
# from pyrsistent import v
import mne
import os
import time
import tqdm
import math
import numpy as np
#
import config
exp_list = config.exp_list

montage = mne.channels.read_dig_fif('../../github/EEG_notebook/data/montage.fif')
montage.ch_names = json.load(open("../../github/EEG_notebook/data/montage_ch_names.json"))
montage.dig = montage.dig[:64]
montage.ch_names = montage.ch_names[:64]

def dic_v2k(trigger2event_dict):
    re = {}
    for k,v in trigger2event_dict.items():
        re[v] = k
    return re

def load_txt(file_name):
    trigger2trigger2time = {}
    with open(file_name) as f:
        for line in f.readlines():
            t1, t2, time = line.strip().split(':')
            if t1 not in trigger2trigger2time.keys():
                trigger2trigger2time[t1] = {}
            trigger2trigger2time[t1][t2] = time
    return trigger2trigger2time

def timestamp_convert_localdate(timestamp,time_format="%Y/%m/%d %H:%M:%S"):
    timeArray = time.localtime(timestamp)
    styleTime = time.strftime(str(time_format), timeArray)
    return styleTime

def filter_255(events_from_annot):
    re = []
    for item in events_from_annot:
        if item[-1] != 255:
            re.append(item)
    return re

def load_label(file_name):
    df = pd.read_excel(file_name)
    ColNames_list = df.columns.tolist()
    score_label={}
    for i in range(len(df)):
        ten_digit = int(df['index'][i])-1
        line_score={'immersion':{},'interest':{},'arousal':{},'valance':{},'visual':{},'auditory':{}}
        for col in ColNames_list:
            if col.split('、')[0].isdigit():
                digit = int(col.split('、')[0])
            if "immersion" in col:
                line_score['immersion'][digit] = int(df[col][i])
            elif "interest" in col:
                line_score['interest'][digit] = int(df[col][i])
            elif "arousal" in col:
                line_score['arousal'][digit] = int(df[col][i])
            elif "valence" in col:
                line_score['valance'][digit] = int(df[col][i])
            elif "visual" in col:
                line_score['visual'][digit] = int(df[col][i])
            elif "auditory" in col:
                line_score['auditory'][digit] = int(df[col][i]) 


        for label_name in line_score:
            for digit in line_score[label_name]:
                index = ten_digit*10 + digit
                if index not in score_label:
                    score_label[index]={}
                score_label[index][label_name] = line_score[label_name][digit]
    
    return score_label

def is_number(s):
    try: 
        float(s)
        return True
    except ValueError: 
        pass
    try:
        import unicodedata 
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
    return False



def load_excel(file_name):
    df = pd.read_excel(file_name)
    # df.sort_values("local_time_ms", inplace = True, ignore_index=True)
    df.sort_values("local_time_ms", inplace = True)
    v2info = {}
    current_v = '-1'
    current_v_set = set()
    goon = True
    print(df.loc[2]['item_link'], df.loc[2]['item_link'].split('/')[5])
    for i in range(len(df)):
        item_id = df.loc[i]['item_id']
        if 'item_link' in df.columns:
            if '=' in df.loc[i]['item_link']:
                tmp_item_id = df.loc[i]['item_link'].split('/')[5]
            else:
                print('no = in item link')
            if tmp_item_id!=item_id:
                item_id=tmp_item_id
        if current_v != item_id:
            current_v = item_id
            if current_v in current_v_set:
                goon = False
            else:
                current_v_set.add(current_v)
                goon = True
        if goon == False:
            continue
        if not is_number(df.loc[i]['text']):
            print('comment not digit', df.loc[i]['text'])
            continue
        if isinstance(df.loc[i]['text'], str):
            print(df.loc[i]['text'])
            x=float(df.loc[i]['text'])
        else:
            x=df.loc[i]['text']
        if int(item_id) not in v2info.keys():
            v2info[int(item_id)] = {'like':int(0), 'comment_number':x, 'start_time':-1, 'skip_time':-1,'end_time':1e30,'video_duration':int(df.loc[i]['item_duration']),'video_tag':df.loc[i]['item_label']}
        if df.loc[i]['event'] == 'like':
            v2info[int(item_id)]['like'] = int(1)
            v2info[int(item_id)]['like_time'] = int(df.loc[i]['local_time_ms'])
        if not np.isnan(x) and np.isnan(v2info[int(item_id)]['comment_number']):
            v2info[int(item_id)]['comment_number'] = x
        elif df.loc[i]['event'] == 'video_play':
        # if df.loc[i]['event'] == 'video_play':
            if v2info[int(item_id)]['start_time'] != -1:
                print("rewriting error!", df.loc[i]['item_label'])
                continue
            v2info[int(item_id)]['start_time'] = df.loc[i]['local_time_ms']
        elif df.loc[i]['event'] == 'play_time':
            v2info[int(item_id)]['end_time'] = min(df.loc[i]['local_time_ms'], v2info[int(item_id)]['end_time'])
            v2info[int(item_id)]['skip_time'] = max(df.loc[i]['local_time_ms'], v2info[int(item_id)]['skip_time'])
        elif df.loc[i]['event'] == 'video_play_pause':
            v2info[int(item_id)]['end_time'] = min(df.loc[i]['local_time_ms'], v2info[int(item_id)]['end_time'])
            v2info[int(item_id)]['skip_time'] = max(df.loc[i]['local_time_ms'], v2info[int(item_id)]['skip_time'])
        elif df.loc[i]['event'] == 'click_comment_button':
            v2info[int(item_id)]['end_time'] = min(df.loc[i]['local_time_ms'], v2info[int(item_id)]['end_time'])
            v2info[int(item_id)]['skip_time'] = max(df.loc[i]['local_time_ms'], v2info[int(item_id)]['skip_time'])
    for itemid in v2info :
        v2info[itemid]['browsing_dur'] = float((v2info[itemid]['skip_time'] - v2info[itemid]['start_time'])/1000)
        
    return v2info
    
class Transformer:
    def __init__(self,):
        self.b = 0
        self.k = 0
    def fit(self, action, event):
        self.k = (event[1] - event[0]) / (action[1] - action[0])
        self.b = event[1] - action[1] * self.k
        return self.k, self.b
    def action2event(self,action):
        return int(self.k * action + self.b + 0.5)         
    

def find_time(start_time, time2t2t, time_stamps, txt_info):
    if start_time < time_stamps[0] or start_time > time_stamps[-1]:
        return None
    for i, time_stamp in enumerate(time_stamps):
        # mising three triggers
        if time_stamps[i+1] - time_stamp > 10000 * 3:
            return None
        if start_time >= time_stamp and start_time < time_stamps[i+1]:
            real_time = [time_stamp, time_stamps[i+1]]
            eeg_time = []
            for rtime in real_time:
                t1, t2 = time2t2t[rtime]
                eeg_time.append(txt_info[t1][t2]['eeg_time'])
            transformer = Transformer()
            transformer.fit(real_time, eeg_time)
            if abs(transformer.k - 1000) > 50:
                with open('tmp.txt','a') as f:
                    f.write(str(real_time))
                    f.write('\t')
                    f.write(str(eeg_time))
                    f.write('\t')
                    f.write(str(t1)+'\t'+str(t2))
                    f.write('\n')
                print(transformer.k)
                return None
            return transformer.action2event(start_time)

def map_info(txt_info, events_from_annot, excel_info):
    
    event_group = []
    # print(events_from_annot)
    for i in range(len(events_from_annot)):
        if i + 1 < len(events_from_annot):
            time_diff = events_from_annot[i+1][0] - events_from_annot[i][0]
            if time_diff < 1050 and time_diff > 950:
                event_group.append([events_from_annot[i][2], events_from_annot[i+1][2], events_from_annot[i+1][0]])
                if str(events_from_annot[i][2]) in txt_info.keys() and str(events_from_annot[i+1][2]) in txt_info[str(events_from_annot[i][2])].keys():
                    print(txt_info[str(events_from_annot[i][2])][str(events_from_annot[i+1][2])],str(events_from_annot[i][2]),str(events_from_annot[i+1][2]))
                    try:
                        txt_info[str(events_from_annot[i][2])][str(events_from_annot[i+1][2])] = {
                        'time': float(txt_info[str(events_from_annot[i][2])][str(events_from_annot[i+1][2])]),
                        'eeg_time': float(events_from_annot[i+1][0])
                        }
                    except:
                        continue
    
    time2t2t = {}
    for t1 in txt_info.keys():
        for t2 in txt_info[t1].keys():
            if type(txt_info[t1][t2]) == dict:
                time2t2t[txt_info[t1][t2]['time']] = [t1, t2]
    time_stamps = list(sorted([float(item) for item in time2t2t.keys()]))

    v2info = excel_info
    for v in v2info.keys():
        start_time = int(v2info[v]['start_time'] / 1e3)
        end_time = int(v2info[v]['end_time'] / 1e3)
        time_diff = int(end_time - start_time)
        eeg_time = find_time(start_time, time2t2t, time_stamps, txt_info)
        if eeg_time != None:
            v2info[v]['eeg_start_time'] = int(eeg_time)
        eeg_time = find_time(end_time, time2t2t, time_stamps, txt_info)
        if eeg_time != None:
            v2info[v]['eeg_end_time'] = int(eeg_time)
    return v2info

def map_label(label_info, v2info):
    for v in v2info:
        if 'idx' not in v2info[v].keys():
            continue
        number = int(v2info[v]['comment_number'])
        if number not in label_info:
            continue
        for label_name in label_info[number]:
            v2info[v][label_name] = label_info[number][label_name]

    return v2info



if __name__ == '__main__':
    for exp_name in tqdm.tqdm(exp_list):
        print(f'-----------------------------preprocessing data of exp {exp_name}-------------------------------')
        # file_name = '../data/eeg_marco/' + exp_name + '_data_0404_marco2.cnt'
        file_name = '../data/eeg/' + exp_name + '_data.cnt'
        raw = mne.io.read_raw_cnt(file_name, preload=True, verbose='WARNING')

        tmp_file_name = '../data/eeg_marco/' + exp_name + '_1_data.cnt'
        if os.path.exists(tmp_file_name):
            raw_0 = mne.io.read_raw_cnt(tmp_file_name, preload=True, verbose='WARNING')
            raw.append(raw_0)
        print(raw.info)
        
        channels = ["FP1", "FPZ", "FP2", "AF3", "AF4", "F7", "F5", "F3", "F1", "FZ", "F2", "F4", "F6", "F8", "FT7", "FC5", "FC3", "FC1", "FCZ", "FC2", "FC4", "FC6", "FT8", "T7", "C5", "C3", "C1", "CZ", "C2", "C4", "C6", "T8", "TP7", "CP5", "CP3", "CP1", "CPZ", "CP2", "CP4", "CP6", "TP8", "P7", "P5", "P3", "P1", "PZ", "P2", "P4", "P6", "P8", "PO7", "PO5", "PO3", "POZ", "PO4", "PO6", "PO8", "CB1", "O1", "OZ", "O2", "CB2"]
        raw.pick_channels(channels)
        

        events_from_annot, event_dict = mne.events_from_annotations(raw, verbose='WARNING')

        event2trigger_dic = dic_v2k(event_dict)
        for idx in range(len(events_from_annot)):
            events_from_annot[idx][2] = event2trigger_dic[events_from_annot[idx][2]]
        
        eeg_data = raw.get_data()
        events_from_annot = filter_255(events_from_annot)

        txt_info = load_txt('../data/info/'+exp_name+'_ts.txt')
        excel_info = load_excel('../data/info/'+exp_name+'_log.xlsx')
        label_info = load_label('../data/info/'+exp_name+'_label.xlsx')
        
        idx2eeg = {}
        idx = 0
        v2info = map_info(txt_info, events_from_annot, excel_info)

        for v in v2info.keys():
            v2info[v]['start_time'] = int(v2info[v]['start_time'])
            v2info[v]['end_time'] = int(v2info[v]['end_time'])
            v2info[v]['skip_time'] = int(v2info[v]['skip_time'])
            if 'eeg_start_time' not in v2info[v].keys() or 'eeg_end_time' not in v2info[v].keys():
                continue
            if v2info[v]['eeg_end_time'] - v2info[v]['eeg_start_time'] < 0:
                print('error',v)
                continue
            
            if np.isnan(v2info[v]['comment_number']):
                continue
            # print(v2info[v]['comment_number'],type(v2info[v]['comment_number']))

            time_diff = min(v2info[v]['eeg_end_time'] - v2info[v]['eeg_start_time'], 60 * 1000)
            idx2eeg[idx] = eeg_data[:,v2info[v]['eeg_start_time']:v2info[v]['eeg_start_time']+time_diff].tolist()
            v2info[v]['idx'] = int(idx)
            idx += 1
        
        v2info = map_label(label_info, v2info)
        
        json.dump(v2info, open(f'../data/raw/' + exp_name + '_v2info_add_vab_label.json','w',encoding='utf-8'),ensure_ascii=False)
        json.dump(idx2eeg, open(f'../data/raw/' + exp_name + '_idx2eeg.json','w'))



