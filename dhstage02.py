#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 11 12:54:10 2017

@author: emilygrabowski

a short script to check by hand the ratios between the pitches of each token, 
and then print the ratios, for us to compare to the other outputs
"""
import os
from time import sleep
import atlasutilities
from praatio.utilities import utils
#import matplotlib
#matplotlib.use('TkAGG')
#import matplotlib.pyplot as plt
#matplotlib.use('TkAGG')

import re
#import ggplot
abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
praatEXE = atlasutilities.load_praat_path()

def handle_undefineds2(method, token_list,pitch_list,threshold):
    token_list['exclude']=False
    token_list['nund']=0
    pitch_list['und']=False

    warnings = []
    warnings.append("\nBeginning undefined analysis. Method for dealing with undefineds is %s\n" %method)
    if method == 'ignore':
        pass
    else:
        if method=='exclude':
            for i in set(pitch_list['n'].tolist()):
                mdf=pitch_list.loc[pitch_list['n']==i]
                mdf['und']=False
    
                maxin=len(mdf['raw_Hz'].values)-1
                und_i=mdf.index[mdf['raw_Hz'] == 0].tolist()
                if len(und_i)/(maxin+1)>threshold:
                    token_list.loc[i-1,'exclude']=True
                    token_list.loc[i-1,'exreason']='nund'
    
                for j in und_i:
                    mdf.loc[j,'und']=True
    
                    if j==0 or j==maxin or set(range(j,maxin)).issubset(und_i) or set(range(0,j)).issubset(und_i): 
                        pass
                    else:
                        token_list.loc[i-1,'exclude']=True
                        token_list.loc[i-1,'exreason']='mund'
                        warnings.append("Whole token excluded")
                try:
                    token_list.loc[i-1,'nund']=len(und_i)
                except:
                    print(i,type(i))
                pitch_list.loc[pitch_list['n']==i,'und']=mdf['und'].tolist()
        else:
            warnings.append("Undefined method")
    og_p=pitch_list
    #clean up the pitch list
    ex=set(token_list.loc[token_list['exclude']==True]['n'])
    pitch_list=pitch_list.loc[~pitch_list['n'].isin(ex)]
    pitch_list=pitch_list.loc[pitch_list['und']==False]

    return(warnings,token_list,pitch_list,og_p)



def alphadh(method, token_list,pitch_list,threshold1,threshold2):
    pitch_list['dh']=False
    ##get first and last
    for i in pitch_list.n.unique():
        mdf=pitch_list.loc[pitch_list.n==i,]

        pitch_list.loc[pitch_list.index==mdf.index.values[0],'first']=True
        pitch_list.loc[pitch_list.index==mdf.index.values[-1],'last']=True
    
    if method=='auto':
        #for i in range(pitch_list):
        p=pitch_list['raw_Hz'].tolist()
        f=p[1:]+[p[-1]]
        pr=[p[0]]+p[:-1]
        pitch_list['foll_Hz']=f
        pitch_list['prev_Hz']=pr
        pitch_list['prev_prop']=pitch_list['raw_Hz']/pitch_list['prev_Hz']
        pitch_list['foll_prop']=pitch_list['raw_Hz']/pitch_list['foll_Hz']
        
        pitch_list.loc[((pitch_list['prev_prop']>= threshold1)|(pitch_list['prev_prop']<=threshold2))&(pitch_list['first']==False)&(pitch_list['last']==False),'dh']=True
        pitch_list.loc[((pitch_list['foll_prop']>= threshold1)|(pitch_list['foll_prop']<=threshold2))&(pitch_list['first']==False)&(pitch_list['last']==False),'dh']=True
        
        dh_i=set(pitch_list[pitch_list['dh'] == True].n.values)
        token_list.loc[token_list['n'].isin(dh_i),'exclude']=True
        token_list.loc[token_list['n'].isin(dh_i),'exreason']='dh'
    

    return(token_list,pitch_list)
    


