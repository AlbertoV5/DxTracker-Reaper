#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get Guide Track and Dialogue Tracks Utterance and compare to find speakers in audio
"""

import soundfile
import numpy as np
import pandas as pd
import configparser
from resemblyzer import VoiceEncoder
from tqdm import tqdm
from pathlib import Path

def ReadAudio(filePath, start, end):
    audio, sr = soundfile.read(filePath, start = start, stop = end)
    audio = audio[:,0]
    return audio, sr

def DxUtterance(encoder, dx):
    sr, start, end = int(dx['sr']), float(dx['start']), float(dx['end'])
    audio, sr = ReadAudio(dx['path'], int(start*sr), int(end*sr))
    return encoder.embed_utterance(audio*(1/np.max(audio))) #normalize frame

def GuideTrackUtteranceFrames(encoder, gt, hopLength, frameLength):
    sr, start, end = int(gt['sr']), float(gt['start']), float(gt['end'])
    audio, sr = ReadAudio(gt['path'], int(start*sr), int(end*sr))
    hop, frame = int(hopLength * sr), int(frameLength * sr) #Samples
    
    frames = [audio[(i*hop):(i*hop)+frame] for i in range(audio.size//hop)] # frame list to [position,utterance] array
    return np.array([[(i*hopLength) + start,encoder.embed_utterance(frames[i]*(1/np.max(frames[i])))] for i in tqdm(range(len(frames)),position = 0)])

def CompareUtterance(dxU, gtUF, threshold = 0.91):
    scalarProduct = np.array([[gtUF[i][0], np.dot(dxU,gtUF[i][1])] for i in tqdm(range(len(gtUF)))])
    return scalarProduct[np.where(scalarProduct[:,1]>threshold)]
    
def ReaperMarkers(color, name, csvName):
    ts1 = pd.read_csv(csvName)
    sec1 = ts1['Position (s)']
    
    with open("project.RPP", "r") as file:
        r = file.read()
    markers = ''    
    for i in sec1:
        markers += '  MARKER 1 ' + str(i) + ' ' + name + ' 0 ' + color + ' 1 B {928F1A51-EA34-874B-BC89-9F00D3638A16}\n'
    r = r[:-2] + markers + '\n>'
    with open("projectMarkers.RPP", "w+") as file:  
        file.write(r)

#DATA
rscPath = '/Users/albertovaldezquinto/Library/Application Support/REAPER/'
eufPath = rscPath + 'dxTrackerEUF/'
#Config
info = configparser.ConfigParser()
info.read(rscPath + 'dxTracker.ini')
projectName = info['PROJECT']['name'].split('.')[0]
tr = info['CONFIG']['threshold']
hopLength = info['CONFIG']['hopLength']
frameLength = info['CONFIG']['frameLength']
#Tracks
gt = info['GT']
dxList, dxc = [],1
while True:
    try:
        dxList.append(info['DX' + str(dxc)])
    except:
        break
    dxc+=1

#Get Utterance
encoder = VoiceEncoder()
speakersUtterance = [DxUtterance(encoder, i) for i in dxList]

gtUFpath = eufPath + projectName + '_' + gt['name'] + '_' + tr + '_' + hopLength + '_' + frameLength + '.npy'
if Path(gtUFpath).is_file():
    print('\nReading Utterance Frames from file: ' + gtUFpath)
    guideTrackUtterance = np.load(gtUFpath, allow_pickle = True)
    print('Done.')
else:
    print('\nGetting Utterance Frames for Guide Track:')
    guideTrackUtterance = GuideTrackUtteranceFrames(encoder, gt, float(hopLength), float(frameLength))
    #Save .npy
    np.save(gtUFpath,guideTrackUtterance, allow_pickle = True)

#Scalar Product for Similarity Score of each Speaker
for i in range(len(dxList)):
    result = CompareUtterance(speakersUtterance[i], guideTrackUtterance, float(tr))
    
    csvName = eufPath + projectName + '_' + dxList[i]['name'] + '_' + tr + '_' + hopLength + '_' + frameLength + '.csv'
    df = pd.DataFrame({'Position (s)':result[:,0], 'Score':result[:,1]})
    df.to_csv(csvName, index = False)

    #ReaperMarkers('17793279', dxList[i]['name'], csvName)
    
print()
print('Done comparing Utterance from Speakers to Guide Track.')













