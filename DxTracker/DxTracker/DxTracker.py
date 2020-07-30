#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@author: albertovaldezquinto
"""
from reapy import reascript_api as reaper
import configparser

rscPath = reaper.GetResourcePath() + '/DxTracker/'

smi = reaper.CountSelectedMediaItems(0)
projPath = reaper.GetProjectPath('',512)[0]
selItems = []
projectName = reaper.GetProjectName(0, '', 512)[1]
    
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
        self.trackColor = reaper.GetTrackColor(self.itemTrack)
    
if smi > 1:
    items = [Item(reaper.GetSelectedMediaItem(0,i)) for i in range(smi)]
    lengths = [i.itemLength for i in items]
    maxLengthIndex = lengths.index(max(lengths))
    gt = items[maxLengthIndex]
    items.pop(maxLengthIndex)
    
    gtData = [gt.trackName, gt.sourcePath, gt.offset, gt.offset+gt.itemLength, gt.sourceSR]
    dxData = [[i.trackName, i.sourcePath, i.offset, i.offset + i.itemLength, i.sourceSR, i.trackColor] for i in items]
    
    config = configparser.ConfigParser()
    config.read(rscPath + 'dxTracker.ini')
    
    config['PROJECT'] = {'name':projectName.split('.')[0],'path':projPath}
    
    config['GT'] = {'name':gt.trackName,'path':gt.sourcePath,'start':gt.offset,'end':gt.offset + gt.itemLength,'sr':gt.sourceSR}
                        
    for i in range(len(dxData)):
        config['DX' + str(i+1)] = {'name':dxData[i][0],'path':dxData[i][1],
                                   'start':dxData[i][2],'end':dxData[i][3],'sr':dxData[i][4],
                                   'color':dxData[i][5]}
                         
    with open(rscPath + 'dxTracker.ini', 'w+') as configFile:
        config.write(configFile)
    
    reaper.ShowMessageBox('Done', 'DxTracker', 0)
        
else:
    reaper.ShowMessageBox('Not enough items selected', 'DxTracker', 0)