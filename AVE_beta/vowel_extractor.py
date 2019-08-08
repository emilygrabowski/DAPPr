# -*- coding: utf-8 -*-
"""
Spyder Editor

File to test functionality of running a praat script from a python script
"""


#import io
#from praatio.utilities import utils

import pandas as pd
from matplotlib import pyplot as plt
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler  
import sklearn.model_selection
import numpy as np
from sklearn.feature_selection import RFE
from sklearn.svm import LinearSVC
from math import log, log10
import os
import io
import csv


#def get_contour(df,column='intensity',window=2,direction="both",trim=True):
#    targ_col = df[column].values
#    print(len(targ_col))
#    filler_front = targ_col[0]
#    filler_back = targ_col[-1]
#    targ_pre = []
#    for i in range(window):
#        targ_pre.append(filler_front)
#    targ_pre=targ_pre+list(targ_col[:-window])
#    targ_post = list(targ_col[window:])
#    
#    for i in range(window):
#        targ_post.append(filler_back)
#    #print(len(targ_pre),len(targ_post),len(targ_col))
#
#    df[column+'_pre_'+str(window)]=targ_col-targ_pre
#    df[column+'_post_'+str(window)]=targ_post-targ_col
#    if trim:
#        df=df.iloc[window:-window,]
#    return(df)
#    

###reading praat

#d = pd.read_csv('test_file/output_mamad_binary.txt',sep='\t')
#print(list(d))
#print("DONE")
#d=d.rename(str.lower, axis='columns')
#d=d.rename(str.strip, axis='columns')
#d.token=d.token.str.strip()
#print(list(d))
#d['vowel']=1
#d.loc[d.token=='','vowel'] = 0
#
#
#
#prop_v=len(d.loc[d.vowel==1])/len(d.vowel)
#prop_other=1-prop_v
#
#
###get the intensity slope-esque thing
#dmod=get_contour(d,window=2)
#
#
#print(d.mean(axis=0))
#print(d.loc[d.vowel==0,].mean(axis=0))
#print(d.loc[d.vowel==1,].mean(axis=0))


##reading vs
def preprocess_vs(infile,options=False):
    df = pd.read_csv(infile,encoding='utf-8')

    df['vowel']=1
    df.loc[df.Label=='x','vowel'] = 0
    prop_v=len(df.loc[df.vowel==1])/len(df.vowel)
    print("The proportion of vowels in this recording is ", prop_v)
    if options:
        newstr = []
        for x in df['strF0']:
            if not x==0:
                newstr.append(12* log(x / 100,2))
            else:
                newstr.append(0)
        df['strF0']=newstr
        newstr = []
        for x in df['shrF0']:
            if not x==0:
                newstr.append(12* log(x / 100,2))
            else:
                newstr.append(0)
                
        df['shrF0']=newstr
    

    X=df.iloc[:,5:28]
    y=df.iloc[:,29]
    return(df,X,y,prop_v)
def train_model(X,y,clf,param_grid,ts=.1):


    #prop_other=1-prop_v
    #
    #
    ###get the intensity slope-esque thing
    #dmod=get_contour(d,window=2)
    #
    #
    #print(d.mean(axis=0))
    #print(d.loc[d.vowel==0,].mean(axis=0))
    #print(d.loc[d.vowel==1,].mean(axis=0))
    #print(d.loc[d.vowel==0,].mean(axis=0)-d.loc[d.vowel==1,].mean(axis=0))
    #
    #d=d.loc[d.strF0!=0,]
    #noV = d.loc[d.vowel==0,]
    #V = d.loc[d.vowel==1,]
    #
    ###sample so the data are a 50/50 split (avoid frequency bias)
    #
    #nsamps= len(V.iloc[:,1])
    #
    #noV = noV.sample(nsamps)
    
    #d=pd.concat([V,noV])
    

    scaler = StandardScaler()#scale data
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=0,test_size = ts)
    scaler.fit(X_train)
    X_train = scaler.transform(X_train)
    X_test = scaler.transform(X_test)
    
    
    nfolds=4
    best=sklearn.model_selection.GridSearchCV(clf,param_grid,cv=nfolds,scoring= 'accuracy',verbose=1)
    
    fit = best.fit(X_train,y_train)
    print(fit.best_params_)
    print(fit.best_score_)
    mat = confusion_matrix(y_test,fit.predict(X_test))
    print(mat)
    return(scaler, fit.best_params_, fit.best_score_, mat,best)

###test on a different recording, same speaker
def test_model(X,y,fit,scaler,outfile):
    X = scaler.transform(X)

    fit_test  = fit.predict(X)
    if y!=None:
        mat = confusion_matrix(y,fit.predict(X))
        print(mat)
    else:
        mat = None
    X=pd.DataFrame(X)
    return(fit_test,mat)



def write_tg_from_timestamps(d,d2=None,filename=None,tgFolder=None,ntiers=2):
    tgOut = os.path.join(tgFolder, "%s.TextGrid" %filename)
    tg = io.open(tgOut, "w")
    #f = sf.SoundFile(os.path.join(dname,soundfile))
    #print('samples = {}'.format(len(f)))
    #print('sample rate = {}'.format(f.samplerate))
    #print('seconds = {}'.format(len(f) / f.samplerate))    
    d=d.reset_index()
    if d2!= None:
        d2=d2.reset_index()
    else:
        ntiers =1
    tg_start = 0
    try:
        z= max(d.stop)
    except:
        print('TextGrid error. Not enough segments found')
    tg_end = float(max(d.stop))+.5
    #print(tg_start,tg_end)
    
    # Write the header
    tg.write('File type = "ooTextFile"\nObject class = "TextGrid"\n\n')
    tg.write('xmin = %f\n' % tg_start)
    tg.write('xmax = %f\n' % tg_end)
    tg.write('tiers? <exists>\n')
    tg.write('size = %d\n' % ntiers)
    tg.write('item []:')
    
    

#        
#    nints = 1
#    nints_tokens = 1
    nints=2*d.shape[0]+1
    tiertype = 'IntervalTier'
    name = 'values'
    tg.write('\n\titem [%d]:\n' % 1)
    tg.write('\t\tclass = "%s"\n' % tiertype)
    tg.write('\t\tname = "%s"\n' % name)
    tg.write('\t\txmin = %f\n' % tg_start)
    tg.write('\t\txmax = %f\n' % tg_end)
    tg.write('\t\tintervals: size = %d' % nints)
    
    
    start_start_buffer = 0
    stop_start_buffer = .01
    
    label = ""
    n=1
    tg.write('\n\t\tintervals [%d]:\n' % n)
    tg.write('\t\t\txmin = %f\n' % start_start_buffer)
    tg.write('\t\t\txmax = %f\n' % d.start[0])
    tg.write('\t\t\ttext = "%s"' % label)
    
    for i in range(d.shape[0]-1):
        n+=1
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin = %f\n' % d.start[i])
        tg.write('\t\t\txmax = %f\n' % d.stop[i])
        tg.write('\t\t\ttext = "%s"' % 'V')
        n+=1
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin = %f\n' % d.stop[i])
        tg.write('\t\t\txmax = %f\n' % d.start[i+1])
        tg.write('\t\t\ttext = "%s"' % "")
        
    n+=1
    tg.write('\n\t\tintervals [%d]:\n' % n)
    tg.write('\t\t\txmin = %f\n' % d.start[d.shape[0]-1])
    tg.write('\t\t\txmax = %f\n' % d.stop[d.shape[0]-1])
    tg.write('\t\t\ttext = "%s"' % 'V')
    label = ""
    n+=1
    tg.write('\n\t\tintervals [%d]:\n' % n)
    tg.write('\t\t\txmin = %f\n' % d.stop[d.shape[0]-1])
    tg.write('\t\t\txmax = %f\n' % tg_end)
    tg.write('\t\t\ttext = "%s"\n' % label)
    n+=1
    
    if ntiers==2:
    
        nints=2*d2.shape[0]+1
            
        tiertype = 'IntervalTier'
        name = 'values'
        tg.write('\n\titem [%d]:\n' % 2)
        tg.write('\t\tclass = "%s"\n' % tiertype)
        tg.write('\t\tname = "%s"\n' % name)
        tg.write('\t\txmin = %f\n' % tg_start)
        tg.write('\t\txmax = %f\n' % tg_end)
        tg.write('\t\tintervals: size = %d' % nints)
        
        
        start_start_buffer = 0
        stop_start_buffer = .01
        
        label = ""
        n=1
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin = %f\n' % start_start_buffer)
        tg.write('\t\t\txmax = %f\n' % d2.start[0])
        tg.write('\t\t\ttext = "%s"' % label)
        
        for i in range(d2.shape[0]-1):
            n+=1
            tg.write('\n\t\tintervals [%d]:\n' % n)
            tg.write('\t\t\txmin = %f\n' % d2.start[i])
            tg.write('\t\t\txmax = %f\n' % d2.stop[i])
            tg.write('\t\t\ttext = "%s"' % 'V')
            n+=1
            tg.write('\n\t\tintervals [%d]:\n' % n)
            tg.write('\t\t\txmin = %f\n' % d2.stop[i])
            tg.write('\t\t\txmax = %f\n' % d2.start[i+1])
            tg.write('\t\t\ttext = "%s"' % "")
            
        n+=1
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin = %f\n' % d2.start[d2.shape[0]-1])
        tg.write('\t\t\txmax = %f\n' % d2.stop[d2.shape[0]-1])
        tg.write('\t\t\ttext = "%s"' % 'V')
        label = ""
        n+=1
        tg.write('\n\t\tintervals [%d]:\n' % n)
        tg.write('\t\t\txmin = %f\n' % d2.stop[d2.shape[0]-1])
        tg.write('\t\t\txmax = %f\n' % tg_end)
        tg.write('\t\t\ttext = "%s"\n' % label)
        n+=1
    tg.close()
    
    




##first, clean up results--if the two surrounding numbers are different from the one in the middle, change it
###do this for up to 10 items.
def make_tg_autovowels(d,outfile,outdir,threshold=10,groundtruth=True):
    
    d['test']=d['pred']
#    d['diff'] = (d.pred != d.pred.shift()).astype(int)
#    d.ix[0,'diff'] = 0
    sl = d['test'][d['test'].diff() != 0].index.values
    targ_ind=[]
    for i in range(len(sl)-1):
        if sl[i+1]-sl[i]>threshold:
            targ_ind.append(sl[i])
            
    #print(d.loc[targ_ind,'test'])
    
    start=[]
    stop=[]
    val=[]
    for i in range(len(targ_ind)-1):
        ind=targ_ind[i]
        nextind=targ_ind[i+1]
        j=1
        while d.loc[ind,'pred']==d.loc[nextind,'pred']:
            #print(j)
            #print(d.loc[ind,'pred'],d.loc[nextind,'pred'])
            #print(nextind)
            j+=1
            m = i+j
            #print(m,len(targ_ind))
            if m==len(targ_ind):
                #print("stop")
                break
            else:
                nextind = targ_ind[m]
            #print(len(targ_ind)-1)
        #input("Press Enter to continue...")
    
        #print(ind,nextind)
        start.append(d.loc[ind,'time'])
        stop.append(d.loc[nextind,'time'])
        val.append(d.loc[ind,'pred'])
    
        
    ##make dataframe with start and stop times for the indices:
    newdf = pd.DataFrame({'start':start,'stop':stop,'val':val})
    
    newdf = newdf.drop_duplicates(subset = 'stop', keep = 'first')
    
    vonly= newdf.loc[newdf['val']==1,]
    

    
    
    ##now do the same thing for the data
    ##Now, make a new data frame with start and stop times for the target intervals
    if groundtruth==True:
        sl = d['vowel'].diff()[d['vowel'].diff() != 0].index.values
        #print(d.loc[sl,'test'])
        targ_ind=[]
        for i in range(len(sl)-1):
            if sl[i+1]-sl[i]>20:
                targ_ind.append(sl[i])
                
        #print(d.loc[targ_ind,'vowel'])
        
        start=[]
        stop=[]
        val=[]
        for i in range(len(targ_ind)-1):
            ind=targ_ind[i]
            nextind=targ_ind[i+1]
            j=1
            while d.loc[ind,'vowel']==d.loc[nextind,'vowel']:
                #print(j)
                #print(d.loc[ind,'vowel'],d.loc[nextind,'vowel'])
                #print(nextind)
                j+=1
                m = i+j
                #print(m,len(targ_ind))
                if m==len(targ_ind):
                    #print("stop")
                    break
                else:
                    nextind = targ_ind[m]
                print(len(targ_ind)-1)
            #input("Press Enter to continue...")
        
            #print(ind,nextind)
            start.append(d.loc[ind,'time'])
            stop.append(d.loc[nextind,'time'])
            val.append(d.loc[ind,'vowel'])
        
            
        ##make dataframe with start and stop times for the indices:
        newdf = pd.DataFrame({'start':start,'stop':stop,'val':val})
        
        newdf = newdf.drop_duplicates(subset = 'stop', keep = 'first')
        true= newdf.loc[newdf['val']==1,]
        
        #true['start']=true['start']/1000
        #true['stop']=true['stop']/1000
        true=true.reset_index()
    else:
        true=None
    vonly=vonly.reset_index()
    if groundtruth:
        ntiers=2
    else:
        ntiers=1
    write_tg_from_timestamps(vonly,true,outfile,outdir,ntiers=ntiers)
    return(vonly,true)
    
    
def performance_metric(vonly,true,threshold):
    
    ntotal = vonly.shape[0]
    nsuccessful = 0

    
    for index,row in vonly.iterrows():
        start = row['start']
        stop = row['stop']
        d = true.iloc[(true['start']-start).abs().argsort()[0]]
        start2=d['start']
        stop2=d['stop']

        if (abs(start2-start) <threshold) & (abs(stop2-stop) <threshold):
            nsuccessful = nsuccessful+1
            
    
    acc = nsuccessful/ntotal
    
    
    ntotal = true.shape[0]

    nsuccessful= 0
    
    for index,row in true.iterrows():
        start = row['start']
        stop = row['stop']
        d = vonly.iloc[(vonly['start']-start).abs().argsort()[0]]
        start2=d['start']
        stop2=d['stop']

        if (abs(start2-start) <threshold) & (abs(stop2-stop) <threshold):
            nsuccessful = nsuccessful+1
            
    
    cov = nsuccessful/ntotal
    return(acc,cov)




##FOR SVC
#param_grid = {'random_state':[0], 'tol':[1e-5]}
#clf = LinearSVC()
#
#
#
###continue
#training_data = 'training_data.csv'
#test_data= 'test_new_speaker.csv'
#result_file = 'mamadouAudio1_auto'
#
#
#(d,X,y,prop_v)=preprocess(training_data)
#(d_test,X_test,y_test,prop_v_test)=preprocess(test_data)
#
#
#
#(scaler, best_params, best_score, mat,best) = train_model(X,y,clf,param_grid)
#fit_test=test_model(X_test,y_test,best,"%s.csv" %(result_file))
##
#d_test['pred']=fit_test
#d_test.to_csv("%s.csv" %(result_file))
#gt=True
#print("smoothing")
#for s in smoothing_threshold:
#    acc_list = []
#    cov_list = []
#    (vonly,true) = make_tg_autovowels(d_test,result_file,"/Users/emilygrabowski/Dropbox/Emily/AVE",threshold=s,groundtruth = gt)
#    if gt:
#        f= open('modelcomparison.csv','a',newline='')
#        wr = csv.writer(f, quoting=csv.QUOTE_ALL)
#        for t in threshold_list:
#            (acc,cov) = performance_metric(vonly,true,t)
#            acc_list.append(acc)
#            cov_list.append(cov)
#        arglist = [training_data,test_data,result_file,best_params,best_score,s] + acc_list + cov_list
#
#    wr.writerow(arglist)   
#print(acc_list,cov_list)
#f.close()




