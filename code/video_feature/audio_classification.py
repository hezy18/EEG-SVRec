# v0.1
# 遍历audio文件夹下的音频
# 生成music_label.json，'music_label_logits.csv'
# merge得到'music_merge_label.json'，为'Speech','Music','Others'三类

def get_class():
    sample_rate =16000
    import pandas as pd

    def get_audio(id):
        import librosa
        y,sr = librosa.load('audio/'+id+'.mp3',sr=sample_rate)
        print(y)
        print(sr)
        return 'audio/'+id+'.mp3', y, sr

    from transformers import ASTFeatureExtractor, ASTForAudioClassification
    from datasets import load_dataset
    import torch
    feature_extractor = ASTFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")
    model = ASTForAudioClassification.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")

    def classification(music_array):
        # from transformers import AutoFeatureExtractor, AutoModelForAudioClassification

        # extractor = AutoFeatureExtractor.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")

        # model = AutoModelForAudioClassification.from_pretrained("MIT/ast-finetuned-audioset-10-10-0.4593")
        
        # audio file is decoded on the fly
        inputs = feature_extractor(music_array, sampling_rate=sample_rate, return_tensors="pt")

        with torch.no_grad():
            logits = model(**inputs).logits

        predicted_class_ids = torch.argmax(logits, dim=-1).item()
        predicted_label = model.config.id2label[predicted_class_ids]
        
        print(predicted_label)
        
        logits_list = logits[0].tolist()
        return logits_list, predicted_label

    import os
    from tqdm import tqdm
    label_dict={}
    filenames = os.listdir('audio')

    label_list=[]
    id2label = model.config.id2label
    for i in range(526):
        label_list.append(id2label[i])
    label_list.append("music_id")
        
    data = pd.DataFrame([label_list])
    for filename in tqdm(filenames):
        print(filename)
        id = filename.split('.')[0]
        if id!='':
            music_id, music_array, sr = get_audio(id)
            logits_list, label = classification(music_array)
            logits_list.append(music_id)
            label_dict[music_id] = label
            
            df = pd.DataFrame([logits_list])
            data = data.append(df)

    import json
    with open('music_label.json','w') as f:
        f.write(json.dumps(label_dict))

    data.to_csv('music_label_logits.csv')

get_class()

def modify_class():
    import pandas as pd
    df = pd.read_csv('music_label_logits.csv')
    logits_array = df.values
    
    import json
    with open('music_label.json', 'r') as f:
        label_dict = json.load(f)
    
    # 统计label涵盖内容和数目
    label_count={}
    for id in label_dict:
        label = label_dict[id]
        if label not in label_count:
            label_count[label]=0
            # 查看特殊label及对应的audio id
        if label!='Speech' and label!='Music':
            print(label,id)
        label_count[label]+=1
        
    print(label_count)
    
    # 进行类别merge：speech,music,其他
    music_label_list=['Music', 'Chant','Harmonica','Harp','Bass drum']
    speech_label_list=['Speech', 'Speech synthesizer']
    merge_id_label={}
    for id in label_dict:
        label = label_dict[id]
        if label in music_label_list:
            merge_label='Music'
        elif label in speech_label_list:
            merge_label='Speech'
        else:
            merge_label='Others'
        merge_id_label[id]=merge_label
    with open('music_merge_label.json','w') as f:
        f.write(json.dumps(merge_id_label))
    
    #统计merge后label涵盖内容和数目   
    merge_label_count={}
    for id in merge_id_label:
        label = merge_id_label[id]
        if label not in merge_label_count:
            merge_label_count[label]=0
        merge_label_count[label]+=1
        
    print(merge_label_count)
    
    #TODO:挑出同时有Music和Speech的audio

modify_class()