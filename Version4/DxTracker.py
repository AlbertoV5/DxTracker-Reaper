#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Get Guide Track and Dialogue Tracks Utterance and compare to find speakers in audio
Version - 0.4

"""
import soundfile
import numpy as np
import configparser
from resemblyzer import VoiceEncoder
from tqdm import tqdm
from pathlib import Path
import rpp
from rpp import Element

rscPath = '/Users/albertovaldezquinto/Library/Application Support/REAPER/'

def ReadAudio(filePath, start, end):
    audio, sr = soundfile.read(filePath, start = start, stop = end)
    audio = audio[:,0]
    return audio, sr

def DxUtterance(encoder, dx):
    sr, start, end = int(dx['sr']), float(dx['start']), float(dx['end'])
    audio, sr = ReadAudio(dx['path'], int(start*sr), int(end*sr))
    return encoder.embed_utterance(audio*(1/np.max(audio))) #normalize frame

def GuideTrackUtteranceFrames(encoder, gt, hopLength, frameLength): # Read the guide track and separate utterance in frames
    sr, start, end = int(gt['sr']), float(gt['start']), float(gt['end'])
    hop, frame = int(hopLength * sr), int(frameLength * sr)
    audio, sr = ReadAudio(gt['path'], int(start*sr), int(end*sr)) # Read audio file    
    frames = [audio[(i*hop):(i*hop)+frame] for i in range(audio.size//hop)] # frame list to [position,utterance] array
    return np.array([[(i*hopLength) + start,encoder.embed_utterance(frames[i]*(1/np.max(frames[i])))] for i in tqdm(range(len(frames)),position = 0)])

def CompareUtterance(dxU, gtUF, threshold = 0.91): #gtUF as a [position, guide track utterance] array
    scalarProduct = np.array([ [gtUF[i][0], np.dot(dxU,gtUF[i][1])] for i in tqdm(range(len(gtUF)))])
    return scalarProduct[np.where(scalarProduct[:,1]>threshold)]

def CompareUtteranceExclusive(dxUList, gtUF, threshold = 0.9): # Compare all speakers with guide track at once
    scalarProductExclusive = []
    for i in range(len(gtUF)):
        product = [np.dot(j, gtUF[i][1]) for j in dxUList]
        higher = max(product)
        speaker = int(product.index(higher))
        scalarProductExclusive.append([gtUF[i][0], higher, speaker])
        
    scalarProductExclusive = np.array(scalarProductExclusive)
    return scalarProductExclusive[np.where(scalarProductExclusive[:,1]>threshold)]

def ReaPush(r,projPath,dx,scores,hop,frame,gtSource,trackName,trackColor):
    track = Element(tag = 'TRACK', attrib = [], children = [['NAME', trackName],['PEAKCOL',trackColor]])
    for i in range(len(dx)):
        start, length = dx[i], frame
        try:
            if start + length > dx[i+1]:
                length = hop
        except:
            pass

        item = Element(tag = "ITEM", attrib = [], children = [
            ["POSITION", start], ["LENGTH", length], ["SOFFS", start], ['NAME', int(scores[i]*100)],
            Element(tag = 'SOURCE WAVE', attrib = [], children = [['FILE', gtSource]])])
        track.insert(len(track), item)
            
    r.insert(len(r), track)

#DATA
eufPath = rscPath + 'dxTrackerEUF/'
info = configparser.ConfigParser()
info.read(rscPath + 'dxTracker.ini')

projectName, gt = info['PROJECT']['name'].split('.')[0], info['GT']
tr, hopLength, frameLength = info['CONFIG']['threshold'], info['CONFIG']['hopLength'], info['CONFIG']['frameLength']
gtUFpath = eufPath + projectName + '_' + gt['name'] + '_' + tr + '_' + hopLength + '_' + frameLength + '.npy'
projPath = info['PROJECT']['path'] + '/' + info['PROJECT']['name']
frameWP = bool(info['PUSH']['frame_when_possible'] != 'False')

#Tracks
dxList, dxc = [], 1
while True:
    try:
        dxList.append(info['DX' + str(dxc)])
    except:
        break
    dxc+=1

#Get/Read Utterance
encoder = VoiceEncoder()
speakersUtterance = [DxUtterance(encoder, i) for i in dxList]

if Path(gtUFpath).is_file():
    print('\nReading Utterance Frames from file: ' + gtUFpath)
    guideTrackUtterance = np.load(gtUFpath, allow_pickle = True) # Load .npy with name, tr, hop, frame
else:
    print('\nGetting Utterance Frames for Guide Track:', gt['name'])
    guideTrackUtterance = GuideTrackUtteranceFrames(encoder, gt, float(hopLength), float(frameLength))
    np.save(gtUFpath,guideTrackUtterance, allow_pickle = True) # Save guide track .npy with name, tr, hop, frame

#Process
resultExclusive = CompareUtteranceExclusive(speakersUtterance, guideTrackUtterance, float(tr))

print('Comparing Utterance from Speakers to Guide Track.')

with open(projPath + '.RPP', "r") as file:
    r = rpp.loads(file.read())

for i in range(len(dxList)):
    result = resultExclusive[np.where(resultExclusive[:,2] == int(i))]
    ReaPush(r, projPath, result[:,0], result[:,1], float(hopLength), float(hopLength), gt['path'], dxList[i]['name'], dxList[i]['color'])
    
with open(projPath + '_.RPP', "w+") as file:
    file.write(rpp.dumps(r))

print('Done.')



