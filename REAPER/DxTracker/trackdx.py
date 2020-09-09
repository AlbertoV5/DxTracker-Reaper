#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DxTracker 0.1

Obtain Frames for Embeddings of Utterance for Guide Track and Dx Tracks

dx = dialogue
gt = guide track
EU = embeddings of utterance

Author: Alberto Valdez
av5sound.com
"""
import soundfile
import numpy as np
import configparser
from resemblyzer import VoiceEncoder, trim_long_silences, normalize_volume
from tqdm import tqdm
from pathlib import Path
import rpp
from rpp import Element
import os

rscPath = Path(os.getcwd())

def ReadAudio(filePath, start, end):
    audio, sr = soundfile.read(filePath, start = start, stop = end)
    try:
        if len(audio[0]) == 2: #Stereo sum to mono
            audio = audio[:,0] + audio[:,1] / len(audio[0])
    except:
        print("Mono file")
    return audio, sr

def Normalized(array):
    return array * (1/np.max(array))
    
def DxUtterance(encoder, dx):
    sr, start, end = int(dx['sr']), float(dx['start']), float(dx['end'])
    audio, sr = ReadAudio(dx['path'], int(start*sr), int(end*sr))
    return encoder.embed_utterance(trim_long_silences(normalize_volume(audio,0))) #normalize frame

def GuideTrackUtteranceFrames(encoder, gt, hopLength, frameLength): # separate gt in frames and then get utterance for .npy
    sr, start, end = int(gt['sr']), float(gt['start']), float(gt['end'])
    hop, frame = int(hopLength * sr), int(frameLength * sr)
    audio, sr = ReadAudio(gt['path'], int(start*sr), int(end*sr))
    frames = [audio[(i*hop):(i*hop)+frame] for i in range(audio.size//hop)] # frame list to [position,utterance] array
    return np.array(
        [[(i*hopLength) + start, encoder.embed_utterance(normalize_volume(frames[i],0))]
        for i in tqdm(range(len(frames)),position = 0)
        if np.max(frames[i]) > 0])

def CompareUtteranceExclusive(dxUE, gtUEF, threshold = 0.9): # Compare all speakers with guide track at once
    scalarProduct = []
    for i in range(len(gtUEF)):
        product = [np.dot(j, gtUEF[i][1]) for j in dxUE] #scalar product for all the speakers
        higher = max(product)        
        scalarProduct.append([gtUEF[i][0], higher, int(product.index(higher))]) # append position, scalar, speaker
    
    scalarProduct = np.array(scalarProduct)        
    threshold = np.max(scalarProduct[:,1]) * threshold
    return scalarProduct[np.where(scalarProduct[:,1]>threshold)] #pass only scalars > threshold

def ReaPush(project,result,hop,frame,gtSource,dxTrack): #Create many items, current implementation, clunky
    pos, sco = result[:,0], result[:,1]
    
    splitIndex = np.where(np.diff(pos) > hop)[0] + 1
    positions, scores = np.split(pos, splitIndex), np.split(sco, splitIndex)
    
    track = Element(tag = 'TRACK', attrib = [], children = [
        ['NAME', dxTrack['name']],['PEAKCOL', dxTrack['color']]])
    
    for i in range(len(positions)):
        start, length = positions[i][0], positions[i][-1] + frame - positions[i][0]
        score = sum(scores[i])/len(scores[i])
        try:
            if start + length > positions[i+1][0]:
                length = positions[i][-1] + hop - start
        except:
            pass
        item = Element(tag = "ITEM", attrib = [], children = [
            ["POSITION", start], ["LENGTH", length], ["SOFFS", start], 
            ['NAME', str(i).zfill(4) + '_' + str(dxTrack['name'] + '_' + str(int(score*1000)/1000))],
            Element(tag = 'SOURCE WAVE', attrib = [], children = [['FILE', gtSource]])])
        
        track.insert(len(track), item)
            
    project.insert(len(r), track)

#DATA
eufPath = rscPath / 'euframes'
info = configparser.ConfigParser()
info.read(rscPath / 'dxTracker.ini')

projectPath, projectName = Path(info['PROJECT']['path']), info['PROJECT']['name']
projectFile = projectPath / projectName
outputFile = projectPath / ((projectName).split('.')[0] + '_dxtracker.RPP')

config, guideTrack = info['CONFIG'], info['GT']
tr, hop, frame = config['threshold'], config['hopLength'], config['frameLength']
    
euFramesFile = eufPath / str(guideTrack['sourcename'] + '_' + hop + '_' + frame + '.npy')

dxList, dxc = [], 1
while True:
    try:
        dxList.append(info['DX' + str(dxc)])
    except:
        break
    dxc+=1


#Get/Read Utterance
encoder = VoiceEncoder()
print('Getting Speaker (Dx) Utterance...')
speakersUtterance = [DxUtterance(encoder, i) for i in dxList]
print('Done.')
if Path(euFramesFile).is_file():
    print('\nReading Utterance Frames from file:', euFramesFile)
    guideTrackUtterance = np.load(euFramesFile, allow_pickle = True) # Load .npy with name, hop, frame
else:
    print('\nGetting Utterance Frames for:', euFramesFile)
    guideTrackUtterance = GuideTrackUtteranceFrames(encoder, guideTrack, float(hop), float(frame))
    np.save(euFramesFile,guideTrackUtterance, allow_pickle = True) # Save guide track .npy with name, hop, frame

#Process
print('\nComparing Utterance from Speakers to Guide Track...')
resultExclusive = CompareUtteranceExclusive(speakersUtterance, guideTrackUtterance, float(tr))

if config['overlapitems'] == 'True':
    duration = frame
else:
    duration = hop

with open(projectFile, "r") as file:
    r = rpp.loads(file.read())

for i in range(len(dxList)):
    result = resultExclusive[np.where(resultExclusive[:,2] == int(i))]
    ReaPush(r, result, float(hop), float(duration), guideTrack['path'], dxList[i])
    
with open(outputFile, "w+") as file:
    file.write(rpp.dumps(r))

print('\nDone.')

try:
    os.system('cd /')
    os.system('open ' + str(outputFile).replace(' ', '\\ '))
except:
    pass
