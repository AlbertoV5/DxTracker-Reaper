#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: albertovaldezquinto
"""
import configparser
import pandas as pd
import numpy as np
import os
import rpp
from rpp import Element

rscPath = '/Users/albertovaldezquinto/Library/Application Support/REAPER/'
eufPath = rscPath + 'dxTrackerEUF/'
pos = 'Position (s)'

info = configparser.ConfigParser()
info.read(rscPath + 'dxTracker.ini')

projPath = info['PROJECT']['path'] + '/' + info['PROJECT']['name']
gtName, gtStart = info['GT']['name'], float(info['GT']['start']) 
hop, frame = float(info['CONFIG']['hoplength']), float(info['CONFIG']['framelength'])
gtSource = info['GT']['path']

dxList = [np.array(pd.read_csv(eufPath + file)[pos]) for file in os.listdir(eufPath) if '.csv' in file]

dxIsolated = []
for i in range(len(dxList)):
    try:
        dxIsolated.append(np.setdiff1d(dxList[i],dxList[i+1]))
    except:
        dxIsolated.append(np.setdiff1d(dxList[i], dxList[i-1]))

def Sequences(data, stepsize):
    return np.split(data, np.cumsum( np.where(data[1:] - data[:-1] > stepsize) )+1)
    
with open(projPath + '.RPP', "r") as file:
    r = rpp.loads(file.read())

for dx in dxIsolated:
    #seq = Sequences(dx, frame)
    track = Element(tag = 'TRACK', attrib = [], children = [])
    for i in range(len(dx)):
        start = dx[i]
        length = frame
        try:
            if start + length > dx[i+1]:
                length = hop
        except:
            pass
        item = Element(tag = "ITEM", attrib = [], children = [
            ["POSITION", start], ["LENGTH", length], ["SOFFS", start],
            Element(tag = 'SOURCE WAVE', attrib = [], children = [['FILE', gtSource]])])
        track.insert(len(track), item)
            
    r.insert(len(r), track)
    
with open(projPath + '_.RPP', "w+") as file:
    file.write(rpp.dumps(r))


