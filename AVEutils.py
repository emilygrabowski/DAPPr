#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 14 20:11:16 2018

@author: emilygrabowski

Parselmouth
"""

import parselmouth
#import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import textgrid
import decimal
#import vowel_extractor
#import python_speech_features
#
#import pandas as pd
#from matplotlib import pyplot as plt
#from sklearn.neural_network import MLPClassifier
#from sklearn.metrics import confusion_matrix
#from sklearn.model_selection import train_test_split
#from sklearn.preprocessing import StandardScaler  
#from sklearn.neighbors import typedefs
#
#import sklearn.model_selection
#import numpy as np
#from sklearn.feature_selection import RFE
#from sklearn.svm import LinearSVC
#from math import log, log10
#import os
#import scipy.io.wavfile as wav
#import io
#
#import csv
def ms_to_s(x):
    return(x/1000)

def extend_ts(ts):
    timelist = []
    labellist = []
        
    for index, row in ts.iterrows():
        time = row.start
        while time<=row.stop:
            timelist.append(time)
            labellist.append(row.label)
            time = float(time) + .001
    ts = pd.DataFrame({"time":timelist,"label":labellist})
    return(ts)
#plt.figure()
#plt.plot(snd.xs(), snd.values.T)
#plt.xlim([snd.xmin, snd.xmax])
#plt.xlabel("time [s]")
#plt.ylabel("amplitude")
#plt.show() # or plt.savefig("sound.png"), or plt.savefig("sound.pdf")

def tg_to_times(file,extended=False,tier=0):

    tg= textgrid.TextGrid()
    tg.read(file)

    #print(tg)
    #print(tg[0][1].minTime)
    #print(tg[0][1].maxTime)
    #print(tg[0][1].mark)
    
    start = []
    stop = []
    label = []
    
    for interval in tg[tier]:
        start.append(interval.minTime)
        stop.append(interval.maxTime)
        label.append(interval.mark)
    
    
    ts = pd.DataFrame({"start":start,"stop":stop,"label":label})
    
    
    if extended:
        timelist = []
        labellist = []
        
        for index, row in ts.iterrows():
            time = row.start
            while time<=row.stop:
                timelist.append(time)
                labellist.append(row.label)
                time = time + decimal.Decimal('.001')
        ts = pd.DataFrame({"time":timelist,"label":labellist})
        ts['time']=ts['time'].apply(float)

    return(ts)

#def draw_spectrogram(spectrogram, dynamic_range=70):
#    X, Y = spectrogram.x_grid(), spectrogram.y_grid()
#    sg_db = 10 * np.log10(spectrogram.values)
#    plt.pcolormesh(X, Y, sg_db, vmin=sg_db.max() - dynamic_range, cmap='afmhot')
#    plt.ylim([spectrogram.ymin, spectrogram.ymax])
#    plt.xlabel("time [s]")
#    plt.ylabel("frequency [Hz]")

def to_st(x,refp):
    return(12* log(x / refp,2))
    
    
def norm_sub_mean(x,mean):
    return(x-mean)
    
def parselmouth_to_df(obj,pitch=False):
    if pitch:
        d = np.array(obj.selected_array['frequency'])
    else:
    
        d=np.array(obj.values)
    df = pd.DataFrame(d.transpose())
    time = obj.x_grid()
    #print(time)
    
    df['time'] =time[:-1]
    df['time'] = round(df['time'],3)
    df['time']=df['time'].apply(float)
    return(df)
def preprocess_spec(file,tg=True,intensity = False, pitch = False,method = 'spectro'):
    #sfile='.'.join((file,'wav'))
    sfile = file
    snd = parselmouth.Sound(sfile)
    if method =='spectro':
        
        spectrogram = snd.to_spectrogram(window_length=0.005, maximum_frequency=6000)
        df = parselmouth_to_df(spectrogram)

    elif method =='mfcc':
        #(rate,sig) = wav.read(sfile)
        #mfcc_feat = python_speech_features.mfcc(sig,rate, winlen = .005,nfft = 600)
        #df = pd.DataFrame(mfcc_feat)
        #time = df.index
        #df['time'] = time/rate
        #print(mfcc_feat.xgrid())
        #df = parselmouth_to_df(mfcc_feat)
        
        ##try to use parselmouth
        mfcc_p = snd.to_mfcc()
        #print(mfcc_p)
        mfcc_p = mfcc_p.to_matrix()
        df = parselmouth_to_df(mfcc_p)
        #print(list(df))
        #print(df)
   
    #print(list(df))

    #save = df
    length = max(df['time'])
    #intensitydf = None
    #pitchdf = None
    if intensity: 
        intensity = snd.to_intensity()
        intensitydf = parselmouth_to_df(intensity)
        intensitydf['stop']=intensitydf['time']
        intensitydf['start'] =intensitydf['time'].shift()
        intensitydf['label'] = intensitydf[0]
        intensitydf=intensitydf.iloc[1:,:]
        mean = sum(intensitydf.loc[intensitydf['label']!=0,'label'])/len(intensitydf.loc[intensitydf['label']!=0,'label'])

        intensitydf.loc[intensitydf['label']!=0,'label'] = [norm_sub_mean(x,mean) for x in intensitydf['label'] if not x==0 ]

        intensitydf = extend_ts(intensitydf)
        # print(df['time'])
        # print(intensitydf['time'])
        intensitydf['time']=round(intensitydf['time'],3)
        intensitydf.rename(columns={'label':'int'}, inplace=True)
        df = df.merge(intensitydf,'inner',on = 'time')
        

    if pitch: 
        pitch = snd.to_pitch()
        #print(sum(pitch.selected_array['frequency']!=0)/len(pitch.selected_array['frequency']))
        pitchdf = parselmouth_to_df(pitch,pitch=True)
        pitchdf['stop']=pitchdf['time']
        pitchdf['start'] =pitchdf['time'].shift()
        pitchdf['label'] = pitchdf.iloc[:,0]
        pitchdf=pitchdf.iloc[1:,:]
        #print(pitchdf)
        #print(list(pitchdf))
        refp = sum(pitchdf.loc[pitchdf['label']!=0,'label'])/len(pitchdf.loc[pitchdf['label']!=0,'label'])
        pitchdf.loc[pitchdf['label']!=0,'label'] = [to_st(x,refp) for x in pitchdf['label'] if not x==0 ]
        pitchdf = extend_ts(pitchdf)
        pitchdf.rename(columns={'label':'f0'}, inplace=True)

        # print(df['time'])
        # print(intensitydf['time'])
        pitchdf['time']=round(pitchdf['time'],3)
        df = df.merge(pitchdf,'inner',on = 'time')

    
    #intensityobj = parselmouth_to_array(intensity)
    # pitchobj = parselmouth_to_array(pitch)
#    plt.figure()
#    draw_spectrogram(spectrogram)
#    plt.xlim([snd.xmin, snd.xmax])
#    plt.show() # or plt.savefig("spectrogram.pdf")
    if tg:
        tfile='.'.join((file,'TextGrid'))
        ts = tg_to_times(tfile,extended=True)
        ts['vowel'] = 0
        ts.loc[ts.label=='v','vowel'] = 1
        ts.loc[ts.label=='V','vowel'] = 1

        ts['time']=round(ts['time'],3)
        merged = df.merge(ts,'inner',on='time')
        X = merged
        # print(list(X))
        X=X.drop('vowel',axis = 1)
        X=X.drop('label',axis = 1)
        X=X.drop('time',axis = 1)
        y= merged['vowel']
    else:
        X = df
        #print(list(X))
        merged = X
        X=X.drop('time',axis = 1)
        y = None
    return(X,y,merged,length)
#X,y = preprocess_spec("/Users/emilygrabowski/Dropbox/Emily/AVE/train_file/Export_seenku_mamad_Audio2_binary")

#training_data = 'training_data.csv'
#td=pd.read_csv(training_data)
#td['vowel']=1
#td.loc[td.Label=='x','vowel'] = 0
#td['time']=round(td['t_ms']/1000,4)
#df['time']=round(df['time'],3)
#merged = df.merge(td,'inner',on='time')
#d['time'] = d

#X=pd.concat([merged.iloc[:,:278],merged.iloc[:,285:307]], axis=1)
# X=merged.iloc[:,285:307]

