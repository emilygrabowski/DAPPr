
# -*- coding: utf-8 -*-

import os
import io
from praatio.utilities import utils
import platform
import pandas as pd
#from tkinter import messagebox
#from sklearn.externals import joblib
import codecs
import shutil
import chardet
import pandas as pd
import numpy as np
import platform

if platform.system() == "Darwin":
    file_sep="/"
elif platform.system()=="Windows":
    file_sep="\\"

def set_praat_path():
    if platform.system() == "Darwin":
        print("Darwin")
        praat_exe =  "/Applications/Praat.app/Contents/MacOS/Praat"
    elif platform.system() == "Windows":
        print("Windows")
        praat_exe = "C:\\Program Files\\Praat\\Praat.exe"
        
    if not os.path.isfile(praat_exe):
        messagebox.showinfo("Error",'Praat not found in default folder. Please manually enter the path')
        #inputstr = input("What is the path to your Praat application?" )
        #instr = os.path.dirname(inputstr) #if its run in an IDE need this
        #instr = inputstr
        #stripped = instr.strip("' ")
        #print(stripped)
    else:

        metafile = open("setup.txt","w")
        metafile.write(praat_exe)
        metafile.close()
        return (praat_exe)


def run_praat_script(filename,praat_exe,dname, audio_in, tg_in, pfloor, pceiling,out):
    #print(dname)
    subinfo = []
    print(audio_in,tg_in)

    subinfo.append("Sending the following information to Praat Script:\n")
    subinfo.append("\tAudio File: %s\n" % audio_in)
    subinfo.append("\tText File: %s\n" % tg_in)
    subinfo.append("\tPath-to-Praat: %s\n" % praat_exe)
    praatscriptpath = os.path.join(dname, filename)
    #print(praatscriptpath) 
    #audio_in = input("What audio file do you want to analyze? ")
    #tg_in = input("What is the matching TextGrid file? ")    
    utils.runPraatScript(praat_exe,praatscriptpath,
                         [audio_in.strip("'\ "),tg_in.strip("'\ "),pfloor,pceiling,out])
    return subinfo
def load_praat_path():
    try:
        with open('setup.txt', 'r') as f:
            first_line = f.readline()
            praat_exe = first_line
    except FileNotFoundError:
        praat_exe = set_praat_path()
    return praat_exe
    
def load_praat_default():
    print("getting defaulst")
    try:
        with open('setup.txt', 'r') as f:
            first_line = f.readline()
            praat_exe = first_line
    except FileNotFoundError:
        print(platform.system())
        if platform.system() == "Darwin":
            print("Mac Detected")
            praat_exe =  "/Applications/Praat.app/Contents/MacOS/Praat"
        elif platform.system() == "Windows":
            print("Windows Detected")
            praat_exe = "C:\\Program Files\\Praat"
    return praat_exe

    
def find_header(data):
    split_line=data[0].split()
    try:
        int(split_line[0])
    except:
        indices = {'num': 0, 'speaker':1, 'name':2,
        'pitch':3, 'time':4 }
        return indices


def import_praat(filename, sep="/t",header=[]):
    """import_praat
     This function takes as input a file that is (currently an output of
     a Praat Script which is a .txt file) and reads in the relevant
     information into a list of token objects.
                ##NOTE: I think we want to make this something that is a more flexible function,
                where the user can specify a header and separator--but that is a problem
                for another day (put in placeholing keyword arguments)"""
    print("hi")
    path = "%s" %(filename)
    if platform.system()=="Darwin":
        path="//%s" %(filename)
    print(path)
    by = min(32, os.path.getsize(path))
    raw = open(path,'rb').read(by)
    result = chardet.detect(raw)
    print(result)
    encoding = result['encoding']
    #encoding='utf-16'
    print("Detected encoding is",encoding,"Detected confidence is ",result['confidence'])


    #set up the token_list
    print(path)
    print(os.path.isfile(path))
    try:
        data = pd.read_csv(path,encoding='ascii',sep='\t',index_col=0)
    except:
        print("Character detection failed. Trying hard-coded encodings")
        try:
            data = pd.read_csv(path,encoding='ascii', sep='\t',index_col=0)
        except:
            data = pd.read_csv(path,encoding='utf-16',sep='\t',index_col=0)
    data['n']=data.index.values

    ##make a df with high level (token info) and a list of df for the pitch information.

    tokens= pd.DataFrame({'n':data.n.unique()})
    label=[]
    length=[]
    start=[]
    stop=[]
    data['first']=False
    data['last']=False
    pitch=data.reset_index()
    print(list(pitch))
    pitch['raw_Hz']=pitch[' Pitch ']
    #if platform.system()=='Windows':
    #    print(platform.system())
    #    pitch['raw_Hz']==pitch['Pitch ']
    pitch['token']=pitch[' Token ']
    #if platform.system()=='Windows':
    #    pitch['token']=pitch['Token ']

    pitch['t']=pitch[' Time ']
    data['t']=data[' Time ']
    #data['t']=data[' Time ']

    data=data.reset_index()
    for i in data.n.unique():
        mdf=data.loc[data.n==i,]
        data.loc[data.index==mdf.index.values[0],'first']=True
        data.loc[data.index==mdf.index.values[-1],'last']=True
        start.append(mdf['t'].values[0])
        stop.append(mdf['t'].values[-1])
        label.append(mdf[" Token "].values[0])
        length.append(len(mdf[" Pitch "].values))
    tokens['label']=label
    tokens['len']=length
    tokens['start']=start
    tokens['stop']=stop

    tokens['exreason']=0

    return (tokens,pitch)
#    speaker = data[1].split()[1]
#    
#    
#    token_list = TokenList(speaker)
#    current_token = Token()
#    idict = find_header(data)
#    for piece in data[1:]:
#        split_line = piece.split()
#        try:
#            if split_line[idict['num']] != current_token.number and len(split_line)==5:
#                #print(split_line[idict['num']],current_token.number)
#                previous_token = current_token #Move down the chain
#                if previous_token.number is not None:
#                    #print("appending2")
#                    token_list.list.append(previous_token)
#                token_number = split_line[idict['num']]
#                token_name = split_line[idict['name']]
#                current_token = Token(token_number, token_name)
#
#                
#            if len(split_line) == 5:
#                pitch_entry = PitchEntry(split_line[idict['pitch']], split_line[idict['time']])
#                current_token.pitch_list.append(pitch_entry)
#            else:
#                print("Import Error. Please check your Praat textgrids for newline characters in these tokens")
#                print(split_line)
#        except:
#            print('error')
#            print(split_line)
#    if current_token.number != None:
#        
#        #print("appending")
#        token_list.list.append(current_token)
#    raw_tone.close()
#    #for token in token_list.list:
#        #print(token)
#    return (token_list, path)
'''
def new_import_praat(file):
    rawdata = pd.read_csv(file, sep = "\t")
    sub = rawdata.loc[:,['Filename','seg_Start','Label'
    ,'seg_End','t_ms','sF0','pF0','shrF0']]
    token_list = []
    token_start = None
    token_number = 1
    current = None
    pitch = []
    start_points = set(sub.seg_Start)
    #print(start_points)
    for k in start_points:
        subsub = sub.loc[sub['seg_Start'] == k]
        current = Token(token_number,sub.Label[0])
        subsub['t_ms'] = subsub.t_ms.apply(lambda x:x/1000)
        current.pitch = subsub
        current.pitch_list = subsub.pF0
        token_list.append(current)
    return(token_list,file)
'''   
def write_metadata(dname, info, raw):
    
    """
    #write a function that will record metadate, coded by speaker
    """
    meta_out = os.path.join(dname,"metadata.txt")
    if os.path.isfile(meta_out):
        output_file = open(meta_out, "a")
    else:
        output_file = open(meta_out, "w")
        output_file.write("File\tSpeaker ID\tOutput ID\tDate\tTokens\tBins\t Tokens excluded/tSpeaker_Averabe\tMean_Hz (reference)\tMin_semi\tMax_semi\tRange_semi\tBin_span\tMin_Hz\tMax_Hz\tRange_Hz\n")
        
    
    #path, tokenlist,bins,threshold,exclusions,reference_tone,minimum,maximum,raw#
    #output_file = open("atlas_%s_metadata.txt" %raw, 'wb')
    #I want to add a speaker name to the metadata title using the speaker ID feature
    tab = '\t'
    for i in range(0, len(info)):
        if not isinstance(info[i],str):
            info[i] = str(info[i])
    tup = tuple(info)
    line = tab.join(tup)
    output_file.write(line +'\n')
    output_file.close()

"""
def write_excel_syllables(dname, token_list, raw=None):

###NOT IN USE

    excel_folder = os.path.join(dname,"Coarse")
    if not os.path.exists(excel_folder):
        os.mkdir(excel_folder)
    excel_out = os.path.join(excel_folder,"%s_coarse.txt" %raw)
    output_file = io.open(excel_out, "wb")
    #output_file = io.open('excel_output_syllables_%s.txt' %raw, 'wb')
    output_file.write('Token_Number\tToken\tPitch_Hz\tPitch_semi\tBin\tTime1\tTime2\tNewbin'\
                      .encode('utf-8'))
    for token in token_list.list:
        if not token.exclude:
            token.average_hz()
            tab = '\t'
            seq = (token.number, token.name, token.hz_avg, token.semi_avg,token.point_bins[0],
                   token.time_divisions[0], token.time_divisions[1], str(token.npbin1))
            #print two lines for each token
            line1 = tab.join(seq)
            output_file.write(str(line1+'\n').encode('utf-8'))
            line2 = tab.join((token.number, token.name, token.hz_avg, token.semi_avg,token.point_bins[1],
                              token.time_divisions[1], token.time_divisions[2], str(token.npbin2)))
            output_file.write(str(line2+'\n').encode('utf-8'))
            
"""          
def write_excel_bins(dname, token_list, raw=None):

    """
    write spreadsheet output by syllable
    """

    excel_folder = os.path.join(dname,"Coarse")
    if not os.path.exists(excel_folder):
        os.mkdir(excel_folder)
    excel_out = os.path.join(excel_folder,"%s_coarse.txt" %raw)
    output_file = io.open(excel_out, "wb")
    #output_file = io.open('excel_output_syllables_%s.txt' %raw, 'wb')
    output_file.write('Token_Number\tToken\tPitch_semi\tPitch_Hz\tPitch_avg\tbin\tTime1\tTime2\n'\
                      .encode('utf-8'))
    for token in token_list.list:
        if not token.exclude:
            token.average_hz()
            tab = '\t'
            for p in range(len(token.point_bins)):
                try:
                    seq = (token.number, token.name, str(token.points_semi[p]), str(token.points_freq[p]), str(token.hz_avg),str(token.point_bins[p]),
                       token.time_divisions[p], token.time_divisions[p+1])  ##take out np bin
                           #print two lines for each token
                    line = tab.join(seq)
                    output_file.write(str(line+'\n').encode('utf-8'))
                except:
                    print(token.point_bins, token.time_divisions)
            

def write_bins_for_elan(dname, token_list, raw=None):
    
    """
    output format for ELAN compatibility
    """
    
    elan_folder = os.path.join(dname,"ELAN")
    if not os.path.exists(elan_folder):
        os.mkdir(elan_folder)
    elan_out = os.path.join(elan_folder,"%s_ELAN.txt" %raw)
    output_file = open(elan_out, "w")
    
    excluded = 0
    for token in token_list.list:
        tab = '\t'
        if not token.exclude:
            for i in range(len(token.point_bins)):
                if i != len(token.point_bins) or len(token.point_bins)==1:
                    '''
                    if token.point_bins[i] == token.point_bins[i+1]:
                        try:
                            line = tab.join((str(token.point_bins[i]),
                                             str(token.time_divisions[i]),
                                             str(token.time_divisions[i+2])))
                            output_file.write(str(line)+"\n")
                            i += 2
                        except:
                            print(token.time_divisions)
                else:
                    line = tab.join((str(token.point_bins[i]),
                                     str(token.time_divisions[i]),
                                     str(token.time_divisions[i+1])))
                    '''
                line = tab.join((str(token.point_bins[i]),
                                 str(token.time_divisions[i]),
                                 str(token.time_divisions[i+1])))
                output_file.write(str(line)+"\n")
                i+=1
        if token.exclude:
            excluded += 1
    return excluded


def write_entrywise_results(dname, token_list, raw=None):
    
    """
    write simple spreadsheet results
    """
    xcel_folder = os.path.join(dname,"Detailed")
    if not os.path.exists(xcel_folder):
        os.mkdir(xcel_folder)
    xcel_out = os.path.join(xcel_folder,"%s_detailed.txt" %raw)
    output_file = io.open(xcel_out, "wb")
    output_file.write('Token_Number\tToken\tPitch_Hz\tPitch_Semitones\tBin\tOutlier\tTime\n'\
                      .encode('utf-8'))
    for token in token_list.list:
        if not token.exclude:
            for i in range(len(token.pitch_list_clean)):
                entry = token.pitch_list_clean[i]
                thru = float(i + 1.0) /(len(token.pitch_list_clean))
                tab = '\t'
                line = (token.number, token.name, str(entry.frequency_hz),
                     str(entry.frequency_semi), str(entry.bin),
                     str(entry.outlier), str(entry.time), str(entry.npbin) + str(thru))
                fullline = str(tab.join(line)+'\n')
                output_file.write(fullline.encode('utf-8'))
    output_file.close()
    
def write_for_graphing(dname, token_list, raw=None):
    """Write results that are easy to graph"""
    graphingFolder = os.path.join(dname, "for_graphing")
    if not os.path.exists(graphingFolder):
        os.mkdir(graphingFolder)
    graphOut = os.path.join(graphingFolder, "for_graphing_%s.txt" %raw)
    output_file = io.open(graphOut, "wb")
    for token in token_list.list:
        if not token.exclude:
            tab = '\t'
            line1 = (token.name, token.name)
            full1 = str(tab.join(line1)+'\t')
            output_file.write(full1.encode('utf-8'))
    output_file.write('\n'.encode('utf-8'))
    for token in token_list.list:
        if not token.exclude:
            for b in token.point_bins:
                output_file.write(str(b).encode('utf-8'))
                output_file.write('\t'.encode('utf-8'))

    output_file.close()
    

def write_tg(dname,token_list,pitch_list,raw = None,ntiers = 2):
    print("writing textgrid...")
    #for dname put the spath(for now),token_list is the tokens df
    tgFolder = os.path.join(dname, "TextGrids")
    if not os.path.exists(tgFolder):
        os.mkdir(tgFolder)
    tgOut = os.path.join(tgFolder, "%s_annotated.TextGrid" %raw)
    tg = io.open(tgOut, "w")
    #tl = token_list.loc[token_list['exclude']==False]
    tl=token_list
    tl=tl.reset_index()
    tg_end = float(max(tl['stop']))+.25 #pad the end time by a quarter second
    #print(tg_end)
    tg_start = 0
    #print(tg_start,tg_end)
    # Write the header
    tg.write('File type = "ooTextFile"\nObject class = "TextGrid"\n\n')
    tg.write('xmin = %f\n' % tg_start)
    tg.write('xmax = %f\n' % tg_end)
    tg.write('tiers? <exists>\n')
    tg.write('size = %d\n' % ntiers)
    tg.write('item []:')
    
    
    if ntiers == 2:
        num_bintier =2
        num_tokentier=1
    else:
        num_bintier = 1
        
    nints = 1
    nints_tokens = 1
    for t in range(len(tl['label'].tolist())):
        nints_tokens +=1
        token=tl.iloc[t]
        if token['exclude']==True:
            #print('excluded')
            nints+=1
        else:
            #print(token['exclude'],token['b_t'])
            for b in range(len(token['b_t'].split(','))):
                nints+=1
        nints_tokens += 1
        nints+=1
    #print(nints, nints_tokens)
    if ntiers == 2:
    
        tiertype = 'IntervalTier'
        name = 'tokens'
        tg.write('\n\titem [%d]:\n' % num_tokentier)
        tg.write('\t\tclass = "%s"\n' % tiertype)
        tg.write('\t\tname = "%s"\n' %name)
        tg.write('\t\txmin = %f\n' % tg_start)
        tg.write('\t\txmax = %f\n' % tg_end)
        tg.write('\t\tintervals: size = %d' % nints_tokens)
        n = 1
        #make a start buffer
        start_start_buffer = 0
        stop_start_buffer = None
        k = 0
        stop_start_buffer= float(tl.iloc[0]['start'])
#        while stop_start_buffer == None:
#            try:
#                stop_start_buffer = float(pitch_list.loc[pitch_list['token']==k]['t'].tolist()[0])
#            except IndexError:
#                if k == len(tl.list):
#                    stop_start_buffer = tg_end
#                else:
#                    k+=1
        #print(start_start_buffer,stop_start_buffer,"start_buffer")
        #print('\a')
        label = ""
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin= %f\n' % start_start_buffer)
        tg.write('\t\t\txmax= %f\n' % stop_start_buffer)
        tg.write('\t\t\ttext= "%s"' % label)
        n+=1
        
        
        
        for index,row in tl.iterrows():
            
            start = row['start']
            stop = row['stop']          

            label = row['label']
            #print(start,stop,label)
            tg.write('\n\t\tintervals [%d]:\n' % n)
            tg.write('\t\t\txmin= %f\n' % start)
            tg.write('\t\t\txmax= %f\n' % stop)
            tg.write('\t\t\ttext= "%s"' % label.encode('utf-16'))
            n+=1
            #pad with an empty token
            start_buffer = row['stop']
            #print(index,len(tl['label']))
            if index==len(tl['label'])-1:
                stop_buffer=tg_end
            else:
                stop_buffer = tl.iloc[index+1]['start']
            #print(start_buffer,stop_buffer,'buffer')
            label = ""
            tg.write('\n\t\tintervals [%d]:\n' % n)
            tg.write('\t\t\txmin= %f\n' % start_buffer)
            tg.write('\t\t\txmax= %f\n' % stop_buffer)
            tg.write('\t\t\ttext= "%s"' % label)
            n+=1
    print("finished first tg")
    tiertype = 'IntervalTier'
    name = 'bins'
    tg.write('\n\titem [%d]:\n' % num_bintier)
    tg.write('\t\tclass = "%s"\n' % tiertype)
    tg.write('\t\tname = "%s"\n' %name)
    tg.write('\t\txmin = %f\n' % tg_start)
    tg.write('\t\txmax = %f\n' % tg_end)
    tg.write('\t\tintervals: size = %d' % nints)

    n = 1
    #make a start buffer
    start_buffer = 0
    stop_buffer = tl.iloc[0]['start']
    #print(start,stop,'start/stop for tier2')
    label = ""
    tg.write('\n\t\tintervals [%d]:\n' % n)
    tg.write('\t\t\txmin= %f\n' % start_buffer)
    tg.write('\t\t\txmax= %f\n' % stop_buffer)
    tg.write('\t\t\ttext= "%s"' % label)
    n+=1
        
    n = 1
    for index,row in tl.iterrows():
        if row['exclude']==True:
            start=[row['start']]
            stop=[row['stop']]
            vals=['X']

        else:
            nmeas=len(row['b_t'].split(','))
            span=row['stop']-row['start']
            tspan=span/nmeas
            #print(nmeas,span)
            vals=row['b_b'].split(',')
            start=[]
            stop=[]
            for i in range(len(vals)):

                if i==0:
                    start.append(row['start'])
                else:
                    start.append(stop[i-1])
                if i==len(row['b_t'].split(',')):
                    stop.append(row['stop'])
                else:
                    stop.append(row['start']+(i+1)*tspan)

            #print(start,stop)
            #print(start,stop,vals[i]) 
        for i in range(len(vals)):
                tg.write('\n\t\tintervals [%d]:\n' % n)
                tg.write('\t\t\txmin= %s\n' % start[i])
                tg.write('\t\t\txmax= %s\n'% stop[i])
                tg.write('\t\t\ttext= "%s"\n' % str(vals[i]))
                n+=1
        #pad with an empty token
        start_buffer = stop[-1]
        if index==len(tl['label'])-1:
            stop_buffer=tg_end
        else:
            stop_buffer = tl.iloc[index+1]['start']
        
                
        #print(start_buffer,stop_buffer,'buffer')
        label = ""
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin= %s\n' % start_buffer)
        tg.write('\t\t\txmax= %s\n' % stop_buffer)
        tg.write('\t\t\ttext= "%s"' % label)
        n+=1
    print("wrote second tg")

    #print(nints)
    tg.close()

def get_db(dname,cols,name):
    dbpath=os.path.join(dname,'.'.join((name,'txt')))
    print(dbpath)
    if os.path.exists(dbpath):
        speakers=pd.read_csv(dbpath)
    else:
        print("initializing...")
        testdict={}
        for c in cols:
            testdict.update({c:[]})
        speakers=pd.DataFrame.from_dict(testdict)
        speakers.to_csv(dbpath)
        
    return speakers


def getprevsp(dname,newval,newcond,retrval,retrcond,targval):
    db=get_db(dname,['speaker','mean','files','n','sum'])
    (index,new)=get_db_index(db,newval,newcond,retrval,retrcond)
    print(index)
    print(new)
    if new:
        db = db.append({'speaker':index,'mean':0,'files':[],'n':0,'sum':0}, ignore_index=True)
        V=0
        n=0
        files=[]
    elif index !='':
        V=db.loc['speaker'==index,targval]
        files=db.loc['speaker'==index,'files']
        n=db.loc['speaker'==index,'n']

    else:
        V=0
        n=0
        files=None
    return (V,n,files,index,db)
    
def get_sp_db(dname,addval,addcond,retrval,retrcond):
    
    if addval == addcond and retrval==retrcond:
        print('no db use')
        sp='temp'
        spath=os.path.join(dname,'Data',sp)
        if not os.path.exists(spath):
            os.mkdir(spath)
            os.mkdir(os.path.join(spath,'extractedpitch'))
        #speakers='temp'
        db=False
    else:
        db=True

        if retrval!=retrcond:
            print('prev index')
            sp=retrval
        elif addval!=addcond:
            print('adding new speaker')
            sp=addval

        
        else:
            print("Error: Speaker Selection failed")
        
        spath=os.path.join(dname,'Data',sp)
        if not os.path.exists(spath):
            print("makingdir")
            os.mkdir(spath)
            os.mkdir(os.path.join(spath,'extractedpitch'))
    speakers = get_db(spath,['file','n','mean','alg'],'data')

    return(spath,speakers,db)

    
#def add_db_entry(db,info):
#    db = db.append(info, ignore_index=True)



# def update_db(,info):
#    '''Get a value from a db or add a row to the db based on the values
#    '''
#    if addval == addcond and retrval==retrcond:
#        print('no db use')
#        r=0
#    else:
#
#        if retrval!=retrcond:
#            print('retrieving information from db...')
#        elif addval!=addcond:
#            print('adding new speaker')
#            db_add_row(db,info)
#        
#        else:
#            print("Error: Speaker Selection failed")
#
#
#def add_row(db)

####DRIVER CODE
#abspath = os.path.abspath(__file__)
#dname = os.path.dirname(abspath)
#write_tg(dname,token_list,raw = 'test',ntiers =2)

def find_outliers(token_list,pitch_list,og,threshold=1,ob=2.5):
    pitch_list['outlier']=False
    freq=pitch_list['raw_Hz'].tolist()
    med=np.median(freq)
    std=np.std(freq)
    lower=med-ob*std
    upper=med+ob*std
    print(lower, upper)
    pitch_list.loc[(pitch_list['raw_Hz']>upper)|(pitch_list['raw_Hz']<lower),'outlier']=True
    
                   
    pitch_list.loc[(pitch_list['und']==True)|(pitch_list['dh']==True),'outlier']=True
    for k in set(token_list.loc[token_list['exclude']==True]['n'].tolist()):
        mdf=pitch_list.loc[pitch_list['n']==k]
        length=token_list.loc[token_list['n']==k,'len'].tolist()[0]
        nout=len(mdf.loc[mdf['outlier']==True]['n'].tolist())
        prop=nout/length
        if prop>threshold:
            token_list.loc[token_list['n']==k,'exclude']==True
    
    og['otherout']=False
    for t in pitch_list.loc[pitch_list['outlier']==True,'t'].tolist():
        og.loc[og['t']==t,'otherout']=True
    ex=set(token_list.loc[token_list['exclude']==True]['n'])
    
    pitch_list=pitch_list.loc[~pitch_list['n'].isin(ex)]
        
    return(token_list,pitch_list,og)


def calculate_reference(pitch_list):
    S=sum(pitch_list['raw_Hz'].tolist())
    n=len(pitch_list['n'].tolist())
    return (S,n)

def get_vals_to_bin(token_list,pitch_list,quants):
    token_list['b_v']=None
    token_list['b_t']=None
    token_list['b_b']=None
    token_list['b_r']=None


    quants=[q*100 for q in quants]

    for n in set(pitch_list['n'].tolist()):
        bin_t=[]
        bin_v=[]
        bin_b=[]
        bin_r=[]

        mdf=pitch_list.loc[pitch_list['n']==n]
        for q in quants:
            j=np.percentile(mdf['t'],q,interpolation='nearest')
            bin_t.append(str(j))
            bin_v.append(str(mdf.loc[mdf['t']==j,'semi'].tolist()[0]))
            bin_b.append(str(mdf.loc[mdf['t']==j,'bin'].tolist()[0]))
            bin_r.append(str(mdf.loc[mdf['t']==j,'raw_Hz'].tolist()[0]))

        token_list.at[token_list['n']==n,'b_v']=','.join(bin_v)
        token_list.at[token_list['n']==n,'b_t']=','.join(bin_t)
        token_list.at[token_list['n']==n,'b_b']=','.join(bin_b)
        token_list.at[token_list['n']==n,'b_r']=','.join(bin_r)


        #token_list.loc[token_list['n']==n,'b_v']=bin_v
        #token_list.loc[token_list['n']==n,'b_t']=bin_t
    return(token_list)

def assign_bins(pitch_list,nbins,bmin,bmax):
    pitch_list['bin']=None
    freq=pitch_list['semi']
    brange=bmax-bmin
    bspan=brange/nbins
    print(bmax,bmin,brange,bspan)
    
    
    ##now assign the bins
    pitch_list.loc[pitch_list['semi']>bmax,'bin']=nbins
    pitch_list.loc[pitch_list['semi']<bmin,'bin']=1
    p=pitch_list.loc[(pitch_list['semi']>bmin)&(pitch_list['semi']<bmax)]['semi'].tolist()
    b=[int((x-bmin)/(bspan))+1 for x in p]
    pitch_list.loc[(pitch_list['semi']>bmin)&(pitch_list['semi']<bmax),'bin']=b
    
    
    return (bmin,bmax,bspan,pitch_list)
