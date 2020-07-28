#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 22:23:06 2020

@author: albertovaldezquinto
"""

from resemblyzer import VoiceEncoder, preprocess_wav, trim_long_silences
from resemblyzer import audio
from pathlib import Path
import numpy as np
import datetime
import pandas as pd


def Process(longFile, speaker):
    encoder = VoiceEncoder()
    sr = 44100
    
    interview = Path(longFile)
    iwav = preprocess_wav(interview, source_sr = sr)
    
    speaker1_path = Path(speaker)
    speaker1_wav = audio.preprocess_wav2(speaker1_path, source_sr = sr)
    
    speaker1 = encoder.embed_utterance(speaker1_wav)
    
    length = iwav.size
    hopSize = 1 * sr
    chunkSize = 2 * sr
    scoreMap = []
    
    for i in range(length//hopSize):
        start = i * hopSize
        end = start + chunkSize
        chunk = encoder.embed_utterance(trim_long_silences(iwav[start:end]))
        
        dot = np.dot(speaker1, chunk)
        scoreMap.append([start/sr,dot])
        
    scoreMap = np.array(scoreMap)
    tr = 0.90
    topIndex = np.where(scoreMap[:,1]>tr)
    top = scoreMap[topIndex]
    secPos = list(top[:,0])
    print(top)
    
    df = pd.DataFrame({'Seconds':secPos})
    df.to_csv('timestamps.csv', index = False, header = 'Seconds')


def Reaper():
    ts1 = pd.read_csv('timestamps.csv')
    sec1 = ts1['Seconds']
    name = 'Dx1'
    
    with open("project.RPP", "r") as file:
        r = file.read()
        
    markers = ''    
    for i in sec1:
        markers += '  MARKER 1 ' + str(i) + ' ' + name + ' 0 0 1 B {928F1A51-EA34-874B-BC89-9F00D3638A16}\n'
        
    r = r[:-2] + markers
    r = r + '\n>'
        
    #print(r)
    with open("projectMarkers.RPP", "w+") as file:
        file.write(r)


Process("Int01.wav", "Soh2.wav")
Reaper()
