# EEG-SVRec
An EEG Dataset with User Multidimensional Affective Engagement Labels in Short Video Recommendation

## Data Organization

### Behavior and MAES
The data is organized in the form of dictionary
Path = "./data/metadata/{uid}_behavior_MAES.json"
For each interaction(uid,iid),
Fields:
*  "start_time", "end_time": the start and end time of viewing video (timestamp)
*  "eeg_start_time", "eeg_end_time": the EEG time aligned with start and end time
*  "like", "like_time": like or not; if like, the timestamp of liking
*  "video_duration": duration of the video (in seconds)
*  "immersion", "interest", "valence", "arousal", "visual", "auditory": MAES (1-5)
*  "session_id", "video_order": the order of session and video, specifically
*  "video_tag": encoded video tag
*  "session_mode": personalized / randomized / non-personalized / mixed
*  "preference": if session_mode = mixed, recommendation / random

### EEG data
The data is preprocessed and in the form of .cnt
The EEG data can be accessed at {link}

### Partcipant
The basic information of the participants
Path = "./data/participant.csv"
Fields: iid, age, gender, usage (Years of the use of short video)

### Video features
The features of the videos
Path = "./data/video_features/video_features.csv", "./data/video_features/video_ComParE-example.csv"
The full file of video_ComParE is at {link}

## Codes
The code of video and EEG features extraction

## Instructions
