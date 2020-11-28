#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 28 11:58:42 2020
@author: christophercree
"""

import data_sonifier as ds
import pandas as pd
import numpy as np

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
new_mid = ds.convertDataToMidi(df,
                            x = 'time_occurance',
                            y = ['col1','col2'],
                            aes=['minor triad','halfdim7'],
                            bins = 'qcut',
                            offset=[50,72],
                            programList=[82,56],
                            t_factor = 0.1)
new_mid.save('myMidi_qcut.mid')
ds.printMidi(new_mid)

#sample midi file using cut on df 
new_mid = ds.convertDataToMidi(df,
                            x = 'time_occurance',
                            y = ['col1','col2'],
                            aes=['major triad','minor triad'],
                            bins = 'cut',
                            offset=[60,70],
                            programList=[12,13],
                            t_factor = 0.1)
new_mid.save('myMidi_cut.mid')
ds.printMidi(new_mid)

new_mid = ds.convertDataToMidi(df1,
                            x = 'time_occurance',
                            duration = [10000],
                            y = ['col1'],
                            aes=[[0,6,12,18]],
                            bins = 'categorical',
                            offset=[50],
                            programList=[8],
                            t_factor = 0.1)
new_mid.save('myMidi_categorical_eqaulDuration.mid')
ds.printMidi(new_mid)

new_mid = ds.convertDataToMidi(df1,
                            x = 'time_occurance',
                            y = ['col1'],
                            aes=[[0,6,12,18]],
                            bins = 'categorical',
                            offset=[50],
                            programList=[8],
                            t_factor = 0.1)
new_mid.save('myMidi_4categorical_timeToNext.mid')
ds.printMidi(new_mid)