#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: albertovaldezquinto
"""
from reapy import reascript_api as reaper
import configparser
import pandas as pd
import numpy as np
import os
import rpp
from rpp import Element

class Item():
    def __init__(self, item):
        self.item = item
        self.itemLength = reaper.GetMediaItemInfo_Value(item, 'D_LENGTH')
        self.activeTake = reaper.GetActiveTake(item)
        self.source = reaper.GetMediaItemTake_Source(self.activeTake)
        self.offset = reaper.GetMediaItemTakeInfo_Value(self.activeTake, 'D_STARTOFFS')
        self.sourcePath = reaper.GetMediaSourceFileName(self.source, '',512)[1]
        self.sourceLength = reaper.GetMediaSourceLength(self.source, False)[0]
        self.sourceSR = reaper.GetMediaSourceSampleRate(self.source)
        self.itemTrack = reaper.GetMediaItem_Track(item)
        self.trackName = reaper.GetTrackName(self.itemTrack,'',512)[2]

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
        length = hop
        try:
            if start + length > dx[i+1]:
                length = frame
        except:
            pass
        item = Element(tag = "ITEM", attrib = [], children = [
            ["POSITION", start], ["LENGTH", length], ["SOFFS", start],
            Element(tag = 'SOURCE WAVE', attrib = [], children = [['FILE', gtSource]])])
        track.insert(len(track), item)
            
    r.insert(len(r), track)
    
with open(projPath + '_.RPP', "w+") as file:
    file.write(rpp.dumps(r))


'''
for i in range(len(dxList)):
    try:
        dxIsolated.append(np.setdiff1d(dxList[i],dxList[i+1]))
    except:
        dxIsolated.append(np.setdiff1d(dxList[i], dxList[i-1]))

for i in dx:
    if len(i) > 0:
        start = i[0]
        #end = i[-1] + 1
        end = i[0] + 1
        length = end - start
        print(start, end)
        item = Element(tag = "ITEM", attrib = [], children = [
            ["POSITION", start],
            ["LENGTH", length],
            ["SOFFS", start],
            Element(tag = 'SOURCE WAVE', attrib = [], children = [['FILE', gtSource]])]
            )
        track.insert(len(track), item)



if guideTrackItem.offset == start:
reaper.ShowConsoleMsg('Found the GT.')
track = guideTrackItem.itemTrack
    
items = [Item(reaper.GetSelectedMediaItems(i)) for i in range(reaper.CountSelectedMediaItems(0))]
trackNames = [item.trackName for item in items]
guideTrackItem = items[trackNames.index(gtName)]
gtSource = guideTrackItem.source


        for j in range(len(dx)-1):
            start, length = dx[j], frame
            
            if dx[j+1] - dx[j] > frame:
                item = reaper.AddMediaItemToTrack(track)
                take = reaper.AddTakeToMediaItem(item)
                reaper.SetMediaItemTake_Source(take, gtSource)
                
                reaper.SetMediaItemPosition(item, start)
                reaper.SetMediaItemLength(item, length, False)
                
                reaper.SetMediaItemInfo_Value(item, 'D_POS')
                reaper.SetMediaItemInfo_Value(item, 'D_STARTOFFS')
                reaper.SetMediaItemInfo_Value(item, 'D_LENGTH', )
            else:
                start, length = dx[i], frame
                
'''  

