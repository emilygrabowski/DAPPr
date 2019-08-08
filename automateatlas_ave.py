#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 18:21:44 2018

@author: emilygrabowski
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb 19 18:14:01 2017

@author: emilygrabowski

Script to run ATLAS analysis. Requires as input a list of parameters. 
"""
#from sklearn.externals import joblib
version = "0.1.5"
import os
import re
from praatio.utilities import utils
import pandas as pd
import sys
import chardet
from tkinter import messagebox
import ntpath
import shutil
from math import log, log10
import numpy as np
import platform

#from sklearn.preprocessing import StandardScaler  
#from sklearn.neural_network import MLPClassifier


#from Praatio import tgio, utils
import atlasutilities

import AVEbeta
from dhstage02 import alphadh
from dhstage02 import handle_undefineds2
#from sklearn.externals import joblib
if getattr(sys, 'frozen',False):
    dname = os.path.dirname(sys.executable)
elif __file__:
    dname = os.path.dirname(os.path.abspath(__file__))
if platform.system() == "Darwin":
    file_sep="/"
elif platform.system()=="Windows":
    file_sep="\\"

def automate(args):
    
    logfile = open(os.path.join(dname,'log.txt'),'w')
    logfile.write('root folder is: %s' %dname)
    logfile.write("\nRunning ATLAS with the following arguments:\n")
    for a in args:
        logfile.write('\t%s\n' %str(a))
    
    if not os.path.exists(os.path.join(dname,'Data')):
        os.mkdir(os.path.join(dname,'Data'))
    """
    Fully automated script used to run with output from a GUI
    """
    #print('automation began', args)
    #(audiofile, textfile, outputfile, 
    #binvar, und, dh, praat, speakerid, 
    #outputid, sylout, elanout, excelout, metaout)
    audio_in=args[0]
    txt_in=args[1]
    file_out=args[2]
    numbins=args[3]
    sex=args[4]
    undefined='exclude'
    #dh=args[5]
    dh='auto'
    praat_path=args[6]
    speaker_id=args[7]
    #output_id=args[8]

    tritone = args[9]
    prevsp = args[10]
    custom_low=args[11]
    custom_high=args[12]

    
    
    
    ###basically we need a function that will set up the speaker data--
    ###let's put this in atlas utilities--or at least build parts there
    
    
    ##decide if we should use the db or if this is an independent job
    ##decide if we should use the db or if this is an independent job

    (spath,speaker,db)=atlasutilities.get_sp_db(dname,speaker_id,'',prevsp,'None')
    if file_out=='':
        ofile=spath
    else:
        ofile=file_out
    
    ##get the list of files to run.
    if audio_in[-1]=='/':
        d=True
        runlist=[]
        for f in os.listdir(audio_in):
            if f[-4:]=='.wav' or f[-4:]=='.WAV':
                runlist.append(''.join((audio_in,f)))
            
    else:
        runlist=[audio_in]
    
    recidlist=[]
    all_pitch=pd.DataFrame({'recid':[],'pitch':[]})
    for audio_in in runlist:
    ##check if it a wav file or a directory
    ###do this later. first I will focus on making the whole thing work up to the update phase
    
    
    ##make a log file to record the statistics, warnings, etc, from the run
    
    ##Run the Praat Path##
    
    
    ##do this for each file
    
        faudio=audio_in
        print("debugging mode")
        ftxt=audio_in[:-4]+'.TextGrid'
        print(ftxt)
        print(os.path.exists(ftxt))
        if not os.path.exists(ftxt):
            ave_status = AVEbeta.test_ave(faudio,dname)
            #ave_status = "filler"
            print(ave_status)
            if ave_status:
                print("Vowel extraction successful, saving TextGrid")
            else:
                print("Vowel extraction unsuccessful, skipping file")
        recid=ntpath.basename(faudio).split('.')[0]
        if not os.path.exists(ftxt):
            print("No vowels found by automatic methods. Skipping file" )
            continue
        print('starting')
        if sex=="m":
            low_pitch_limit=70
            high_pitch_limit=250
        elif sex=="f":
            low_pitch_limit=100
            high_pitch_limit=300
        else:
            low_pitch_limit=custom_low
            high_pitch_limit=custom_high
        print(low_pitch_limit, high_pitch_limit)
        
        info = atlasutilities.run_praat_script("atlas_script_optimize.praat", praat_path, 
                                        dname, faudio, ftxt,low_pitch_limit,high_pitch_limit, 'praat')
        for i in info:
            logfile.write(i)
            
        ##Import the results from the Praat Script##
        
        
        #try:
        inter = os.path.join(dname, "praat.txt")
        print(inter)
        print(os.path.isfile(inter))
        print("before")
        (tokens,pitch) = atlasutilities.import_praat(inter.strip(file_sep))
        print(spath)
        print("tokens",tokens)
        print(inter)
        print(os.path.join(spath,'extractedpitch',''.join((recid,'.txt'))))
        #import the data/ create the necessary structures
        shutil.copy(inter,os.path.join(spath,'extractedpitch',''.join((recid,'.txt'))))
        #except FileNotFoundError:
        #    print("praat not working")
        #    logfile.write("file not found. please try again\n")
        print('hu')
        threshold=.4
        (warnings,tokens,pitch,og) = handle_undefineds2(undefined, tokens,pitch,threshold)
        (tokens,pitch) = alphadh('auto', tokens,pitch,1.2,.8)
        print('done')
        #merge
        og['dh']=False
        for t in pitch.loc[pitch['dh']==True,'t'].tolist():
            og.loc[og['t']==t,'dh']=True
        pitch=pitch.loc[pitch['dh']==False]
        print('dh done')
        (tokens,pitch,og) = atlasutilities.find_outliers(tokens,pitch,og,threshold,3) #exclusion threshold set at 4
        
        (S,n) = atlasutilities.calculate_reference(pitch)
        print(S,n)
        mean=S/n
        alg='praat'
        if recid in speaker['file'].tolist():
            speaker.loc[speaker['file']==recid,'alg']=alg
            speaker.loc[speaker['file']==recid,'n']=n
            speaker.loc[speaker['file']==recid,'mean']=mean
        
        else:
            data={'file':recid,'alg':alg,'mean':mean,'n':n}
            speaker=speaker.append(data,ignore_index=True)
        
        print('cleaning complete')    
        
        

            
        speaker.to_csv(os.path.join(spath,'data.txt'))
        
    
        if not os.path.exists(os.path.join(spath,'pitch')):
            os.mkdir(os.path.join(spath,'pitch'))
        if not os.path.exists(os.path.join(spath,'tokens')):
            os.mkdir(os.path.join(spath,'tokens'))
        new=pd.DataFrame({'pitch':pitch['raw_Hz']})
        new['recid']=recid
        if len(all_pitch['recid'].tolist())!=0:
            old=all_pitch.loc[(all_pitch['recid']!=recid),]
        else:
            old=all_pitch
        all_pitch=pd.concat([old,new])

        pitch.to_csv(os.path.join(spath,'pitch',''.join((recid,'.txt'))),encoding='utf-8')
        all_pitch.to_csv(os.path.join(spath,'all_pitch.txt'))

        tokens.to_csv(os.path.join(spath,'tokens',''.join((recid,'.txt'))),encoding='utf-8')
        recidlist.append(recid)
        
        #loop through the vials
        
    ##start new loop for main analysis
    #    ##
    #
    all_pitch=pd.read_csv(os.path.join(spath,'all_pitch.txt'),engine="python")
        
    for recid in recidlist:
        raw=recid+str(numbins)
        #refp=sum(speaker['n']*speaker['mean'])/sum(speaker.n)

        pitch_path=os.path.join(spath,'pitch',''.join((recid,'.txt')))
        

        token_path=os.path.join(spath,'tokens',''.join((recid,'.txt')))

        pitch=pd.read_csv(pitch_path,encoding='utf-8')
        if db:
            refp=np.percentile(all_pitch['pitch'],50)
        else:
            refp = np.percentile(pitch['raw_Hz'],50)
        print("median used in final:")
        print(refp)
        tokens=pd.read_csv(token_path,encoding='utf-8')
        plist=pitch['raw_Hz'].tolist()
        p=[12* log(x / refp,2) for x in plist]
        pitch['semi']=p
        allplist=all_pitch['pitch'].tolist()
        ap=[12*log(x/refp,2) for x in allplist]
        all_pitch['semi']=ap
        bmin=np.percentile(ap,1)
        bmax=np.percentile(ap,99)
        all_pitch.to_csv(os.path.join(spath,'all_pitch.txt'))

        if int(tritone)==2:
            quants=[.25,.75]
        elif int(tritone)==3:
            quants=[.2,.5,.8]
    
        
        (bmin,bmax,bspan,pitch) = atlasutilities.assign_bins(pitch,numbins,bmin,bmax)
        
        tokens=atlasutilities.get_vals_to_bin(tokens,pitch,quants)
        
        if int(tritone)==2:
        
            tokens[['b1','b2']] = tokens['b_b'].str.split(',',expand=True)
            tokens[['t1','t2']] = tokens['b_t'].str.split(',',expand=True)
            tokens[['v1','v2']] = tokens['b_v'].str.split(',',expand=True)
        elif int(tritone)==3:
            tokens[['b1','b2','b3']] = tokens['b_b'].str.split(',',expand=True)
            tokens[['t1','t2','t3']] = tokens['b_t'].str.split(',',expand=True)
            tokens[['v1','v2','v3']] = tokens['b_v'].str.split(',',expand=True)
        tgFolder = os.path.join(ofile, ''.join(("Token_output",file_sep)))
        if not os.path.exists(tgFolder):
            os.mkdir(tgFolder)
        file_out=''.join((tgFolder,raw,'.txt'))
        tokens.to_csv(file_out,sep='\t')
        
        
        pFolder = os.path.join(ofile, ''.join(("Pitch_output",file_sep)))
        if not os.path.exists(pFolder):
            os.mkdir(pFolder)
        file_out=''.join((pFolder,raw,'.txt'))
        pitch.to_csv(file_out,sep='\t')
        
        
#        tFolder = os.path.join(ofile, "troubleshooting/")
#        if not os.path.exists(tFolder):
#            os.mkdir(tFolder)
#        file_out=''.join((tFolder,raw,'.txt'))
#        og.to_csv(file_out,sep='\t')
        
        atlasutilities.write_tg(ofile,tokens,pitch,raw)

        
        #logfile.write("Writing every sample to an output file...\n")
        #atlasutilities.write_entrywise_results(file_out, token_list, raw)
        
        #if elan == '1':
        #    logfile.write("Writing ELAN-compatible output...\n")
        #    atlasutilities.write_bins_for_elan(file_out, token_list, raw)
        #
        #if syl == '1':
        #    logfile.write("Writing 20/80 phonetic output...\n")
        #    atlasutilities.write_excel_bins(file_out, token_list, raw)
        #
        #if excel == '1':
        #    logfile.write("Writing every sample to an output file...\n")
        #    atlasutilities.write_entrywise_results(file_out, token_list, raw)
        #    
        #if meta == '1':
        #    logfile.write("Writing metadata output...\n")
        #    range_semi= maximum-minimum
        #    range_hz = max_hz-min_hz
        #    i=datetime.datetime.now()
        #    date = "%s/%s/%s" % (i.day, i.month, i.year)
        #    atlasutilities.write_metadata(file_out,[audio_in, speaker_id, output_id, date, len(token_list.list),
        #                                    numbins,
        #                                    excluded, refp, minimum,
        #                                    maximum, range_semi, bin_span, min_hz,
        #                                    max_hz, range_hz], raw)
        #atlasutilities.write_for_graphing(file_out, token_list, raw)
        #atlasutilities.write_tg(file_out,token_list,raw,ntiers =2)
        #logfile.write("ATLAS has concluded.")
        #logfile.close()
    messagebox.showinfo("Status","ATLAS analysis is complete")
        #
        #print("ATLAS ANALYSIS COMPLETE")
        ###test automate atlas
        #

#args=['/Users/emilygrabowski/Dropbox/ATLAS/Test_files/Seenku/bC.WAV', '/Users/emilygrabowski/Dropbox/ATLAS/Test_files/Seenku/bC.TextGrid', '/Users/emilygrabowski/Documents/GitHub/ATLAS/test_env', 8, 'smooth', 'auto', '/Applications/Praat.app/Contents/MacOS/Praat', speakerid, outputid, '1', '1', '1', '1', '2', prevspeaker]

