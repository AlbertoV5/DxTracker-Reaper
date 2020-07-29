#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
"""

from resemblyzer import VoiceEncoder
from scipy.io import wavfile
import numpy as np
import pandas as pd
from tqdm import tqdm
import configparser

def ReadAudio(filePath):
    sr, data = wavfile.read(filePath)
    audio = data/32767
    #audio = audio * (1/np.max(audio))
    return sr, audio

def Resemble(encoder, audio): # Normalize frame over file
    return encoder.embed_utterance(audio*(1/np.max(audio)))
    
def GetDxUtterance(encoder, filePath):
    sr, audio = ReadAudio(filePath)
    return Resemble(encoder, audio)

def GetGtUtteranceFrames(encoder, filePath):
    sr, audio = ReadAudio(filePath)
    hopLength, frameLength =  1, 3 #Seconds 
    hop, frame = hopLength * sr, frameLength * sr #Samples
    
    frames = [audio[(i*hop):(i*hop)+frame] for i in range(audio.size//hop)]
    print('Getting Guide Track Utterance Frames')
    return np.array([i*hopLength,Resemble(encoder, frames[i])] for i in tqdm(range(len(frames))))

def CompareUtterance(dxU, gtU, threshold = 0.91):
    scalarProduct = np.array([np.dot(dxU,gtU[i][1]) for i in tqdm(range(len(gtU)))])
    return scalarProduct[np.where(scalarProduct[:,1]>threshold)]
    
    
def Process(gtFilePath, dxFilePath, threshold = 0.9):
    sr, speaker = ReadAudio(dxFilePath)
    DX1 = Resemble(encoder, speaker) # Encode Speaker
    sr, guideTrack = ReadAudio(gtFilePath) # Read Guide Track

    hopLength, frameLength =  1, 3 #Seconds 
    hop, frame = hopLength * sr, frameLength * sr #Samples
    
    gtFrames = [guideTrack[(i*hop):(i*hop)+frame] for i in range(guideTrack.size//hop)]
    scalarProduct = np.array([[i*hopLength,np.dot(DX1, Resemble(encoder, gtFrames[i]))] for i in tqdm(range(len(gtFrames)))])
    similar = scalarProduct[np.where(scalarProduct[:,1]>threshold)]
    
    df = pd.DataFrame({'Seconds':similar[:,0], 'Score':similar[:,1]})
    df.to_csv('timestamps.csv', index = False, header = 'Seconds')

def ReaperMarkers(color, name):
    ts1 = pd.read_csv('timestamps.csv')
    sec1 = ts1['Seconds']
    
    with open("project.RPP", "r") as file:
        r = file.read()
        
    markers = ''    
    for i in sec1:
        markers += '  MARKER 1 ' + str(i) + ' ' + name + ' 0 ' + color + ' 1 B {928F1A51-EA34-874B-BC89-9F00D3638A16}\n'
    
    r = r[:-2] + markers + '\n>'
    with open("projectMarkers.RPP", "w+") as file:
        file.write(r)

rscPath = '/Users/albertovaldezquinto/Library/Application Support/REAPER/'
config = configparser.ConfigParser()
config.read(rscPath + 'dxTracker.ini')


encoder = VoiceEncoder()
DxList = GetDxUtterance(encoder, 'Soh1.wav')

Process("Source1.wav", "Soh1.wav", float(config['threshold']))

ReaperMarkers('17793279', "Dx1")

'''
scoreFrames = []
for i in tqdm(range(length//hopSize)):
    position = i * hopSize
    frame = guideTrack[position:position + frameSize]
    trackEU = encoder.embed_utterance(frame*(1/(np.max(frame))))
    scoreFrames.append([position/sr,np.dot(speaker, trackEU)])
'''