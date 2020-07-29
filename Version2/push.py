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

projPath, projName = info['PROJECT']['path'] + '/' + info['PROJECT']['name'], info['PROJECT']['name']
gtName, gtStart, gtSource = info['GT']['name'], float(info['GT']['start']) , info['GT']['path']
hop, frame = float(info['CONFIG']['hoplength']), float(info['CONFIG']['framelength'])
frame_when_possible = bool(info['PUSH']['frame_when_possible'] != 'False')

dxList = [np.array(pd.read_csv(eufPath + file)[pos]) for file in os.listdir(eufPath) if '.csv' in file and info['PROJECT']['name'] in file]

dxIsolated = []

# 1 Speakers
if len(dxList) == 1:
    dxIsolated = dxList

# 2 Speakers
if len(dxList) == 2:
    dx0 = np.setdiff1d(dxList[0],dxList[1])
    dx1 = np.setdiff1d(dxList[1], dxList[0])
    
    dxIsolated = [dx0,dx1]
    
# 3 Speakers
if len(dxList) == 3:
    dx0 = np.setdiff1d(dxList[0],dxList[1])
    dx0 = np.setdiff1d(dx0,dxList[2])

    dx1 = np.setdiff1d(dxList[1],dxList[0])
    dx1 = np.setdiff1d(dx1,dxList[2])
    
    dx2 = np.setdiff1d(dxList[2],dxList[0])
    dx2 = np.setdiff1d(dx2,dxList[1])
    
    dxIsolated = [dx0,dx1,dx2]
    dx0 = np.setdiff1d(dxList[0],dxList[1])
    dx0 = np.setdiff1d(dx0,dxList[2])
    dx0 = np.setdiff1d(dx0,dxList[3])

    dx1 = np.setdiff1d(dxList[1],dxList[0])
    dx1 = np.setdiff1d(dx1,dxList[2])
    dx1 = np.setdiff1d(dx1,dxList[3])
    
    dx2 = np.setdiff1d(dxList[2],dxList[0])
    dx2 = np.setdiff1d(dx2,dxList[1])
    dx2 = np.setdiff1d(dx2,dxList[1])
    
    dxIsolated = [dx0,dx1,dx2]
        
with open(projPath + '.RPP', "r") as file:
    r = rpp.loads(file.read())

for dx in dxList:
    track = Element(tag = 'TRACK', attrib = [], children = [['NAME', 'Dx']])
    for i in range(len(dx)):
        start = dx[i]
        if frame_when_possible:
            length = frame
            try:
                if start + length > dx[i+1]:
                    length = hop
            except:
                pass
        else:
            length = hop

        item = Element(tag = "ITEM", attrib = [], children = [
            ["POSITION", start], ["LENGTH", length], ["SOFFS", start],
            Element(tag = 'SOURCE WAVE', attrib = [], children = [['FILE', gtSource]])])
        track.insert(len(track), item)
            
    r.insert(len(r), track)
    
with open(projPath + '_.RPP', "w+") as file:
    file.write(rpp.dumps(r))


