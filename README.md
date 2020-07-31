# DxTracker for Reaper

Identify different speakers in your Reaper session using A.I. (Resemblyzer, rpp, reapy).

https://github.com/resemble-ai/Resemblyzer

![Step1](Guide/comp.jpg)

## Description

The script combines Reaper and Resemblyzer into a simple tool for identifying speakers in an audio track. It does it by getting the Embeded Utterance (EU) of each Speaker Sample and a set of EU frames for the guide track, then it compares all the Speaker's EU with each frame using scalar product in a mutually exclusive way. 

- The result is a new .RPP project with the speakers/Dx separated by tracks.
- Recommended duration for Speaker Sample is 5 to 30 seconds. 
- Supports .wav in 16, 24 bits with any common sample rate.
- Stores the Embeded Utterance Frames (EUF) of the guide track as .npy so you can run multiple threshold/Speaker Samples iterations without restarting the whole process. 

The results are great on interviews and they may vary depending on the Speaker Samples and EUF granularity config. The applications are many within the Reasemblyzer possibilities, for example, finding off-axis takes for a single Dx track based on in-axis and off-axis speaker samples for the same actor, etc.

## Installation (Anaconda Environment)

1. Install Anaconda 
2. Open Terminal and run:

`conda create -n dxt python=3.7`

`git clone https://github.com/AlbertoV5/DxTracker-Reaper.git`

`cd DxTracker-Reaper`

`conda activate dxt`

`pip install -r requirements.txt`

3. For installing the REAPER content, run: `open REAPER` and follow the Reaper installation:

## Installation (Reaper)

4. Put contents of the REAPER folder in your Reaper Media folder. (Find it with: Options > 'Show REAPER resource path in explorer/finder')
5. Add new action, 'Load Reascript' and find 'DxTracker.py' in your Reaper Media > DxTracker folder.
6. (Optional) Add it to a toolbar and use icon from the Data > toolbar_icons folder.

If you have issues adding 'DxTracker.py' as an Action, go to Preferences > Plug-ins > Reascript:

7. 'Custom path to Python dll directory': Run `conda env list` and copy the path from the new environment.

8. 'Force Reascript to use specific Python .dylib': `'libpython3.7m.dylib'`

## Configuration

You can modify some values in DxTracker.ini 

`hoplength = 1` `framelength = 3` Granularity of Embeded Utterance Frames for guide track (in seconds). The script will save different EUFrames .npy of the same guide track source for different settings.

`threshold = 0.9` The score/confidence threshold for returning a frame (ratio).

`overlapitems = True` Resultant items can overlap between different Dx tracks (based on hop and frame length).

Other variables are meant for the project data.

## How to Use

Step 1: Setup your session for Guide Track and number of speakers (4 in this case)

![Step1](Guide/step1.gif)

Step2: Cut Speaker Samples (around 10 seconds) from guide track (or other sources) and drag them to their respective Dx tracks.

![Step2](Guide/step2.gif)

Step3: Select all items to process (Speaker Samples and guide track) and run the DxTracker action.

![Step3](Guide/step3.gif)

Step4: Open Terminal and run trackdx.py in the DxTracker directory and the conda environment.

![Step4](Guide/step4.gif)

Step5: Once the script is done, open new project 'PROJECTNAME_dxtracker.RPP' in the same directory of the original project.

![Step5](Guide/step5.gif)


## Observations

The original resemblyzer demo used real time speaker identification to read an interview and plot the speaker confidence. For DxTracker, as it is designed for audio post, I changed it to what I found most efficient for Reaper, which is having items that reference the guide track file instead of something like generating new audio stems from the GT.

Everything related to Reaper and comparing Utterance is really efficient and it is done within seconds, what takes time is processing the guide track into EUFrames, and mostly depends on the Resemblyzer CPU/GPU configuration. For example, it took around 38 minutes to process a 4.3 hour, 44.1khz 16bit podcast with the hop, frame = 1, 3 setting with a 3.7 GHz Quad-Core Intel Xeon E5 CPU. Performance may vary, so go make a coffee in the meantime or watch some NBA highlights in your phone.

Luckily, there is a progress bar.
![refduration](Guide/refdur.png)

You can use Speaker Samples from different audio sources, as long as you don't move the file location around, and if you do, just re-run the DxTracker action to read the new location. Also, I have found that a threshold of around 0.92 may work best than the default 0.9 but that's what I'll be testing among other stuff.

The EUF .npy will be saved as 'SourceName_hopLength_frameLength.npy'. Maybe adding support to different item cuts of the GT as start, length in the future.

Feel free to reach out.
