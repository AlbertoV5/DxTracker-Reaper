# DxTracker for Reaper (using Resemblyzer)

## Description:

Find speakers in audio file using A.I. (Resemblyzer) and update your Reaper session.
https://github.com/resemble-ai/Resemblyzer

## Requirements:
- SoundFile==0.10.2
- numpy==1.18.5
- tqdm==4.47.0
- Resemblyzer==0.1.1.dev0
- reapy==0.0
- rpp==0.4

## How to Use:
1. Put contents of DxTracker in your Reaper Media folder.
2. Add new action 'DxTracker.py'
3. Select items for dx tracking (at least 2, guide track and one > 5 sec. sample of speakers)
4. Run track.py, it generates a new project in the same location with new audio tracks.

