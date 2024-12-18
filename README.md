# [EEGSVRec: An EEG Dataset with User Multidimensional Affective Engagement Labels in Short Video Recommendation](https://dl.acm.org/doi/pdf/10.1145/3626772.3657890)


The paper has been accepted by SIGIR 2024.

Quick Links: [🗃️Dataset](#Dataset) |
[🛠️Code](#Code) |
[📭Citation](#Citation) |

# Dataset

## Statistics

User ID: 30 users. min=(0)1, max=30

Item ID: 2684 items. min=0, max=2683

Number of Interactions: 3657

**<span style="color:red; font-weight:bold;">NEWS</span>**: We have updated EEG's DE features as of 2024.12.18! In this version, the "key" has been changed from "the interaction idx" to "item_id."


## Behavior and MAES

The data is organized in the form of the JSON object.

Path = "./data/metadata/{user_id}_behavior_MAES.json"

The key of the top-level dictionary in the JSON object is "item_id" (the specific id of the video).

For each interaction(user_id,item_id), fields:
*  "start_time", "end_time": the start and end time of viewing video (timestamp)
*  "eeg_start_time", "eeg_end_time": the EEG time aligned with start and end time
*  "like", "like_time": like or not; if like, the timestamp of liking
*  "video_duration": duration of the video (in seconds)
*  "immersion", "interest", "valence", "arousal", "visual", "auditory": MAES (1-5)
*  "session_id", "video_order": the order of session and video, specifically
*  "video_tag": encoded video tag
*  "session_mode": personalized / randomized / non-personalized / mixed
*  "preference": if session_mode = mixed, recommendation / random


## EEG data

The data is preprocessed and in the form of .cnt

The method of data alignment of .cnt is at "./code/EEG_feature/part1_preprocess_for_resource.py"

The EEG data can be accessed at [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/d/84caed5b9fac4816a1ba/)

**Noticing:**

1. The complete EEG cleaned data is about 62G (35G after compression) 

2. We also provide the DE feature of EEG per second.

3. The preprocessed data, which is used to run the baseline (it is normalized and calculated as the average of seconds), is provided at '/data/EEG_data/EEG_DE_avg'.


## Partcipants

The basic information of the participants

Path = "./data/participant.csv"

Fields: iid, age, gender, usage (using year of short video app he/she employed, 1: never, 2: under 6 months, 3: 6-12 months, 4: 1-2 years, 5: over 2 years)


## Video features

The features of the videos

Path = "./data/video_features/video_features.csv", "./data/video_features/video_ComParE-example.csv"

The full file of video_ComParE is at [Tsinghua Cloud](https://cloud.tsinghua.edu.cn/d/84caed5b9fac4816a1ba/)


## Instruction

Path = "./instruction.md"


# Code

The codes of video and EEG feature extraction


# Citation
If you use our dataset, code or find MicroLens useful in your work, please cite our paper as:

```bib
@article{zhang2024eeg,
  title={EEG-SVRec: An EEG Dataset with User Multidimensional Affective Engagement Labels in Short Video Recommendation},
  author={Zhang, Shaorun and He, Zhiyu and Ye, Ziyi and Sun, Peijie and Ai, Qingyao and Zhang, Min and Liu, Yiqun},
  journal={arXiv preprint arXiv:2404.01008},
  year={2024}
}
```

> :warning: **Caution**: It's prohibited to privately modify the dataset and then offer secondary downloads. If you've made alterations to the dataset in your work, you are encouraged to open-source the data processing code, so others can benefit from your methods. Or notify us of your new dataset so we can put it on this Github with your paper.

If you have any question, please contact us.


