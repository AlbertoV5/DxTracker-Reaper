#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 22:23:06 2020

@author: albertovaldezquinto
"""

from resemblyzer import VoiceEncoder
from scipy.io import wavfile
import numpy as np
import pandas as pd
#from pathlib import Path
#from resemblyzer import audio
#from resemblyzer import VoiceEncoder, preprocess_wav, trim_long_silences

def Process(longFile, speaker, tr = 0.9):
    encoder = VoiceEncoder()
    
    audioFile = wavfile.read(longFile)
    sr, track = audioFile[0], audioFile[1]/32767
    track = track * (1 / np.max(track))

    #interview = Path(longFile)
    #sr = 44100
    #track = preprocess_wav(interview, source_sr = sr)

    print('Track was read.')
    #speaker1_path = Path(speaker)
    #speaker1_wav = audio.preprocess_wav2(speaker1_path, source_sr = sr)
    spk = wavfile.read(speaker)
    speaker1_wav = spk[1]/32767
    speaker1_wav = speaker1_wav * (1/np.max(speaker1_wav))
    
    speaker1 = encoder.embed_utterance(speaker1_wav)
    
    length = track.size
    hopSize = 1 * sr
    chunkSize = 3 * sr
    
    scoreMap = []
    print('Processing...')
    for i in range(length//hopSize):
        start = i * hopSize
        end = start + chunkSize
        #trackEU = encoder.embed_utterance(trim_long_silences(track[start:end]))
        chunk = track[start:end]
        trackEU = encoder.embed_utterance(chunk*(1/(np.max(chunk))))
        scoreMap.append([start/sr,np.dot(speaker1, trackEU)])
        
    print('Done.')
    scoreMap = np.array(scoreMap)
    topIndex = np.where(scoreMap[:,1]>tr)
    top = scoreMap[topIndex]
    secPos = list(top[:,0])
    print(secPos)
    
    df = pd.DataFrame({'Seconds':secPos, 'Score':top[:,1]})
    df.to_csv('timestamps.csv', index = False, header = 'Seconds')

def ReaperMarkers(color):
    ts1 = pd.read_csv('timestamps.csv')
    sec1 = ts1['Seconds']
    name = 'Dx1'
    
    with open("project.RPP", "r") as file:
        r = file.read()
        
    markers = ''    
    for i in sec1:
        markers += '  MARKER 1 ' + str(i) + ' ' + name + ' 0 ' + color + ' 1 B {928F1A51-EA34-874B-BC89-9F00D3638A16}\n'
        
    r = r[:-2] + markers
    r = r + '\n>'
        
    #print(r)
    with open("projectMarkers.RPP", "w+") as file:
        file.write(r)

Process("Int01.wav", "Soh1.wav", tr = 0.90)
#Process("Int01.wav", "Joe1.wav", tr = 0.90)
ReaperMarkers('17793279')
#ReaperMarkers('17924098.0')

