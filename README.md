# DxTracker for Reaper

Identify different speakers in your Reaper session using A.I. (Resemblyzer).

https://github.com/resemble-ai/Resemblyzer

![Step1](Guide/comp.jpg)

## Description

The script combines Reaper and Resemblyzer into a simple tool for identifying speakers in an audio track. It does it by getting the Embeded Utterance (EU) of each speaker and a set of EU frames for the guide track, then it compares all speakers with each frame using scalar/dot product in a mutually exclusive way. 

- Recommended duration for Speaker Sample is 5 to 30 seconds (> 10 is best). 
- Supports .wav in 16, 24 bits for any common sample rate.
- Stores the EUF (Embeded Utterance Frames) as .npy file.

The results are great on interviews and they may vary depending on the Speaker Samples and EUF granularity config. The applications are many within the Reasemblyzer possibilities, for example, finding off-axis takes for a single Dx track based on in-axis and off-axis speaker samples for the same actor, etc.

## Installation (Anaconda Environment)

1. Install Anaconda 
2. Open Terminal and run:

`conda create -n dxt python=3.7` (change dxt for however you want to name your environment)

`git clone https://github.com/AlbertoV5/DxTracker-Reaper.git`

`cd DxTracker-Reaper`

`conda activate dxt`

`pip install -r requirements.txt`

3. For installing the REAPER content, run: `open REAPER` and follow the Reaper installation:

## Installation (Reaper)

1. Put contents of the REAPER folder in your Reaper Media folder. (Find it with: Options > 'Show REAPER resource path in explorer/finder')
2. Add new action, 'Load Reascript' and find 'DxTracker.py' in your Reaper Media > DxTracker folder.
3. (Optional) Add it to a toolbar and use icon from the Data > toolbar_icons folder.

If you have issues adding 'DxTracker.py' as an Action, go to Preferences > Reascript > Enable Python and add the environment directory and .dylib extension. 

1. Custom path to Python dll: Run `conda which` and copy the path to the environment you just created. 

2. Force Reascript to use specific Python .dylib: `libpython3.7m.dylib`

## Configuration

You can modify some values in DxTracker.ini 

`hoplength = 1` `framelength = 3` Granularity of Embeded Utterance Frames for guide track (in seconds).

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

You can use Speaker Samples from different audio sources, as long as you don't move the file location around, and if you do, just re-run the DxTracker action to read the new location. 

Feel free to reach out.
