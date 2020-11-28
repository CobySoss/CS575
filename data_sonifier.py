#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 17 22:22:50 2020
@author: christophercree
"""
import mido as md
import pandas as pd
import numpy as np

TFACTOR = .01 #DEFAULT
TEMPO = 60600 #MAX value = 60600 ~ 990bpm 

def printMidi(midiFile):
    for track in midiFile.tracks:
        for msg in track:
            print(msg)

def newMidiFile(trackNames,programList,filename=None):
    new_mid = md.MidiFile() #type 1

    for i in range(len(trackNames)):
        new_track = md.MidiTrack() #create new track
        #add meta messages
        new_track.append(md.MetaMessage('track_name',name=trackNames[i]))
        new_track.append(md.MetaMessage('set_tempo',tempo=TEMPO))
        
        #add messages
        new_track.append(md.Message('program_change',
                                    program=programList[i],
                                    channel=1))        
        #add track to file
        new_mid.tracks.append(new_track)
        
    if filename != None:
        new_mid.save(filename)
    else: print("file not saved: filename not provided")
    return new_mid

def column_to_track(pitches,durations,track):
    for i in range(len(pitches)):
        track.append(md.Message('note_on', note=pitches[i],
                             velocity=64, time=0))
        track.append(md.Message('note_off', note=pitches[i],
                             velocity=64, time=durations[i]))

def factorTime(time,t_factor):
    for t in time:
        int(round(t*t_factor))
    return time

def calculateEventDuration(t,d,t_factor):
    durations = [int(round(value*t_factor, 0)) for value in d]
    #print(duration)
        
    #only one duration provided for more than one time
    if 1 == len(d) and 1 < len(t):
        value = d[0]*t_factor
        durations = [value] * len(t)
        #print(duration)
    
    #no duration provided use "duration = time to next event" method
    elif 0 == len(d): 
        for i in range(len(t)-1):
            durations.append((t[i+1]-t[i])*t_factor)
        mean = sum(durations) / len(durations)
        durations.append(mean) #add value to end of list for nth duration    
    elif len(d) != len(t):
        print('duration list provided does not contain the same number of values as time_occurance')
    else:
        print('should not be here')
        
    durations = [int(round(num, 0)) for num in durations]
    return durations   

def getAes(aesTypes,offsets):
    pitchSets = {'major triad':tuple([0,4,7]),
                 'minor triad':tuple([0,3,7]),
            'diminished triad':tuple([0,3,6]),
             'augmented triad':tuple([0,4,8]),
                        'maj7':tuple([0,4,7,11]),
                   'dominant7':tuple([0,4,7,10]),
                        'min7':tuple([0,3,7,10]),
                    'halfdim7':tuple([0,3,6,10]),
                        'dim7':tuple([0,3,6,9]),
             'wholetone scale':tuple([0,2,4,6,8,10,12]),
             'chromatic scale':tuple([0,1,2,3,4,5,6,7,8,9,10,11,12]),
                 'major scale':tuple([0,2,4,5,7,9,11,12]),
         'natural minor scale':tuple([0,2,3,5,7,9,10,12]),
        'harmonic minor scale':tuple([0,2,3,5,7,9,11,12]),
            'pentatonic scale':tuple([0,2,5,7,9])
                }
    empty = ret = []

    for i in range(len(aesTypes)):
        try:
            if isinstance(aesTypes[i],str):
                pitchSet = pitchSets.get(aesTypes[i])
            elif isinstance(aesTypes[i],list):
                pitchSet = tuple(aesTypes[i])
    
            maximumPitch = max(pitchSet)

            if(offsets[i] < 0 or offsets[i] > 127-maximumPitch):
                print('offset', i, 'out of range')
                ret.append(empty)
            else:
                ret.append(list(map(lambda x : x + offsets[i], pitchSet)))
        except TypeError:
            print('aesType not found')
            ret.append(empty)
    return ret

# =============================================================================
# df = time series data for sonification
# x = df column name of time_occurance data. Data type is integer to repesent
#     some unit of time such as: milliseonds, seconds, days, years etc, where
#     the values start at zero and are strictly monotonically increasing.
# duration = [] default parameter. An empty list results in durations 
#            being derived from time_occurnace data, such that the duration of
#            each element is equal to the time to the next event. The last 
#            duration is set arbitraily to the mean duration of the series.
#          = [value] a list with a single value results in all elements given a
#            duration equal to this value.
#          = [1,...,n] a list of n values, one for each n rows in df
# y = list of 1 to n df column name(s)
# aes = a list of n objects for each element in y. These can be keywords 
#       represeting common musical sets such as triads, 7th chords, scales, or 
#       these can be user defined lists for mapping i.e. [0,6] is a tritone.
# bins = one of three keywords 'cut', 'qcut', 'categorical' to define how
#        all columns in y are mapped to each cooresponding pitch set provided 
#        in aes. For example, if aes = 'major triad' the set has three elements
#        [0,4,7] the data will be binned into three groups. Bining by 'cut' and 
#        'qcut' uses the number of elements in the cooresponding aes. 
#        For categorical binning the user much select or provide an aes that 
#        contains the same number unique categories.
# offset = A list of n offsets for each column in y. The offset maps the aes to
#        MIDI notes (musical pitches, low to high) between 0-127. The largest 
#        valid value is 127 - max(aes) for each aes.
# program list = A list of MIDI programs (insturments). Each column in y is 
#                assigned to a MIDI track and with the corresponding program
# t_factor = time factor, to scale (speed up or slow down) x and duration.                
# =============================================================================
def convertDataToMidi(df,x='time_occurance',duration=[],
                         y=['col1'],aes=['maj'],bins='cut',
                         offset=[60],programList=[12],t_factor=TFACTOR):
    
    new_mid = newMidiFile(trackNames=y,programList=programList)
    #printMidi(new_mid)
    
    factoredTime = factorTime(df[x],t_factor)
    eventDuration = calculateEventDuration(factoredTime,duration,t_factor)
    pitchMap = getAes(aes,offset)
    
    if bins == 'qcut':
        i=0
        for col in y:
            df[col]=pd.qcut(df[col],q=len(pitchMap[i]),labels=pitchMap[i])
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
            
    for track in new_mid.tracks:
        data = df[track.name]
        column_to_track(data,eventDuration,track)
    return new_mid

#Test Main

#sample data set
df = pd.DataFrame(np.array([[0,     5.4, 9.3], 
                            [10504, 5.5, 3.2],
                            [23293, 6.6, 11.6], 
                            [35323, 5.2, 3.4], 
                            [45029, 7.1, 9.5], 
                            [52094, 5.9, 8.3], 
                            [62098, 5.4, 4.1], 
                            [78594, 3.8, 4.2]]),
                   columns=['time_occurance', 'col1', 'col2'])
df['time_occurance'] = df["time_occurance"].astype(int)

#sample data set with categorical variable
df1 = pd.DataFrame(np.array([[0,     'cat'], 
                            [10504, 'dog'],
                            [23293, 'sheep'], 
                            [35323, 'sheep'], 
                            [45029, 'cat'], 
                            [52094, 'dog'], 
                            [62098, 'dog'], 
                            [78594, 'wolf']]),
                   columns=['time_occurance', 'col1'])
df1['time_occurance'] = df1["time_occurance"].astype(int)
df1['col1'] = df1['col1'].astype('category')

#sample midi file using qcut on df 
new_mid = convertDataToMidi(df,
                            x = 'time_occurance',
                            y = ['col1','col2'],
                            aes=['minor triad','halfdim7'],
                            bins = 'qcut',
                            offset=[50,72],
                            programList=[82,56],
                            t_factor = 0.1)
new_mid.save('myMidi_qcut.mid')
printMidi(new_mid)

#sample midi file using cut on df 
new_mid = convertDataToMidi(df,
                            x = 'time_occurance',
                            y = ['col1','col2'],
                            aes=['major triad','minor triad'],
                            bins = 'cut',
                            offset=[60,70],
                            programList=[12,13],
                            t_factor = 0.1)
new_mid.save('myMidi_cut.mid')
printMidi(new_mid)

new_mid = convertDataToMidi(df1,
                            x = 'time_occurance',
                            duration = [10000],
                            y = ['col1'],
                            aes=[[0,6,12,18]],
                            bins = 'categorical',
                            offset=[50],
                            programList=[8],
                            t_factor = 0.1)
new_mid.save('myMidi_categorical_eqaulDuration.mid')
printMidi(new_mid)

new_mid = convertDataToMidi(df1,
                            x = 'time_occurance',
                            y = ['col1'],
                            aes=[[0,6,12,18]],
                            bins = 'categorical',
                            offset=[50],
                            programList=[8],
                            t_factor = 0.1)
new_mid.save('myMidi_4categorical_timeToNext.mid')
printMidi(new_mid)
