#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 22:22:50 2020

@author: christophercree
"""
import mido as md
import pandas as pd
import numpy as np
TFACTOR = .01
TEMPO = 60600 #MAX value = 60600 ~ 990bpm 

def newMidiFile(trackNames,programList,filename=None):
    new_mid = md.MidiFile() #type 1
    i=0
    for trackName in trackNames:
        new_track = md.MidiTrack()
        
        #add meta messages
        new_track.append(md.MetaMessage('track_name',name=trackName))
        new_track.append(md.MetaMessage('set_tempo',tempo=TEMPO))
        
        #add messages
        new_track.append(md.Message('program_change',
                                    program=programList[i],
                                    channel=i+1))        
        #add track to file
        new_mid.tracks.append(new_track)
        i=i+1
        
    if filename != None:
        new_mid.save(filename)
    else: print("file not saved: filename not provided")
    return new_mid

def column_to_track(data,factoredTime,track):
    i = 0
    for value in data:
        new_msg = md.Message('note_on',
                             note = value,
                             velocity = 64,
                             time = factoredTime[i+1]-factoredTime[i]
                             )
        track.append(new_msg)
        new_msg = md.Message('note_off',
                             note = value,
                             velocity = 64,
                             time = factoredTime[i+1]-factoredTime[i]
                             )
        track.append(new_msg)
        i = i+1

def factorTime(t,t_factor): 
    df = t*t_factor
    df = df.round(decimals=0)
    #print('here')
    time = df.astype(int)
    time = time.tolist()
    return time

def convertDataToMidi(df,x='time',y=['col1'],aes=['maj'],bins='cut',offset=[60],programList=[12],t_factor=TFACTOR,lastTime='default'):
    
    new_mid = newMidiFile(trackNames=y,programList=programList)
    
    for track in new_mid.tracks:
        for msg in track:
            print(msg)
    
    time = factorTime(np.array(df[x].astype(int)),t_factor)

    if lastTime == 'default':
        time.append(int(time[-1]+(time[-1]-time[-2]))) #use the same duration of the second to last sample
    else: 
        time.append(int(time[-1]+lastTime*t_factor)) #add user defined time for last element
    
    pitchMap = getAes(aes,offset)

# =============================================================================
#     if not pitchMap:    
#         print('empty list')
#     print(pitchMap)
# =============================================================================
    
    if bins == 'qcut':
        i=0
        for col in y:
            df[col] =pd.qcut(df[col],q=len(pitchMap[i]),labels=pitchMap[i])
            i=i+1
    elif bins == 'cut':
        i=0
        for col in y:
            df[col]=pd.cut(np.array(df[col]),bins=len(pitchMap[i]),labels=pitchMap[i])
            i=i+1
    elif bins == 'categorical':
        for col in y:
            i=0
            uniqueCategories = df[col].unique()
            numCategories = len(uniqueCategories)
            print(numCategories)
            if len(pitchMap[i]) == len(uniqueCategories):#TODO change to >=
                print('Mapping', uniqueCategories, 'to pitch map', pitchMap[i])
                df[col] = df[col].cat.rename_categories(pitchMap[i])
                print('success')
            else:
                print("Error: pitchMap and number of categorical variables are not equal")
            i=i+1
    #print(df)
            
    i=0
    for track in new_mid.tracks:
        data = df[track.name]
        column_to_track(data,time,track)
        i=i+1
    return new_mid

def getAes(aesTypes,offsets):
    pitchSets = {'major triad':{0,4,7},
                 'minor triad':{0,3,7},
            'diminished triad':{0,3,6},
             'augmented triad':{0,4,8},
                        'maj7':{0,4,7,11},
                   'dominant7':{0,4,7,10},
                        'min7':{0,3,7,10},
                    'halfdim7':{0,3,6,10},
                        'dim7':{0,3,6,9},
             'wholetone scale':{0,2,4,6,8,10,12},
             'chromatic scale':{0,1,2,3,4,5,6,7,8,9,10,11,12},
                 'major scale':{0,2,4,5,7,9,11,12},
         'natural minor scale':{0,2,3,5,7,9,10,12},
        'harmonic minor scale':{0,2,3,5,7,9,11,12},
            'pentatonic scale':{0,2,5,7,9}
                }
    empty = ret = []
    i=0
    for offset in offsets:
        
        pitchSet = set(pitchSets.get(aesTypes[i],aesTypes[i]))
        print(pitchSet) #TODO fix this if user enters unknown string
        maximumPitch = max(pitchSet) #cast as set if user defined tuple
        try:
            if(offset < 0 or offset > 127-maximumPitch):
                print('offset out of range')
                ret.append(empty)
            else:
                ret.append(list(map(lambda x : x + offset, pitchSet)))
        except KeyError:
            print('aesType not found')
        i=i+1
    return ret

#Test Main
df = pd.DataFrame(np.array([[0,     5.4, 9.3], 
                            [10504, 5.5, 3.2],
                            [23293, 6.6, 11.6], 
                            [35323, 5.2, 3.4], 
                            [45029, 7.1, 9.5], 
                            [52094, 5.9, 8.3], 
                            [62098, 5.4, 4.1], 
                            [78594, 3.8, 4.2]]),
                   columns=['time', 'col1', 'col2'])

df1 = pd.DataFrame(np.array([[0,    'cat'], 
                            [10504, 'dog'],
                            [23293, 'sheep'], 
                            [35323, 'sheep'], 
                            [45029, 'cat'], 
                            [52094, 'dog'], 
                            [62098, 'dog'], 
                            [78594, 'wolf']]),
                   columns=['time', 'col1'])
df1['col1'] = df1['col1'].astype('category')

#print(df)
#print(getAes(['major triad',tuple([0,1,2,3])],[50,60]))
#print(getAes(['major scale','natural minor scale'],[50,70]))

new_mid = convertDataToMidi(df,
                            x = 'time',
                            y = ['col1','col2'],
                            aes=['dim7','maj7'],
                            bins = 'qcut',
                            offset=[60,70],
                            programList=[12,13],
                            t_factor = 0.1,
                            lastTime = 16000)
new_mid.save('myMidi_1.mid')

for track in new_mid.tracks:
    for msg in track:
        print(msg)

new_mid = convertDataToMidi(df,
                            x = 'time',
                            y = ['col1','col2'],
                            aes=[tuple([0,6,12,18]),tuple([0,6,12,18])],
                            bins = 'cut',
                            offset=[50,70],
                            programList=[12,13],
                            t_factor = 0.1,
                            lastTime = 16000)
new_mid.save('myMidi_2.mid')

for track in new_mid.tracks:
    for msg in track:
        print(msg)

new_mid = convertDataToMidi(df1,
                            x = 'time',
                            y = ['col1'],
                            aes=[tuple([0,1,12,24])],
                            bins = 'categorical',
                            offset=[50],
                            programList=[8],
                            t_factor = 0.1,
                            lastTime = 16000)
new_mid.save('myMidi_3.mid')

for track in new_mid.tracks:
    for msg in track:
        print(msg)

# =============================================================================
# message_numbers = []
# duplicates = []
# 
# for track in .tracks:
#     if len(track) in message_numbers:
#         duplicates.append(track)
#     else:
#         message_numbers.append(len(track))
# 
# for track in duplicates:
#     cv1.tracks.remove(track)
# 
# cv1.save('new_song.mid')
# =============================================================================
