#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr  6 09:02:37 2019

@author: emilygrabowski

Script to run AVE using the pretrained model. 

Input: List of files or file paths (if the files are not in the working directory)
Output: TextGrid files for each input .wav file indicating where the model predicts there to be vowels. 
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 17 12:05:36 2018

@author: emilygrabowski
"""
import sys
import AVEutils
import os
import vowel_extractor
#import pandas as pd
#from sklearn.preprocessing import StandardScaler  
#from sklearn.neural_network import MLPClassifier
import pickle as pkl
#from sklearn.neural_network import MLPClassifier

##simplify
#testdir = sys.argv[1]

def test_ave(testfile,dname):

    success = False
    testdir = os.path.dirname(testfile)
#traindir = "/Users/emilygrabowski/Desktop/ave-beta-data/train/"
#testdir = "/Users/emilygrabowski/Desktop/ave-beta-data/test/"

#flist = os.listdir(testdir)
    flist = [testfile]
    smoothing_threshold = [4]
    
    
    use_intensity = True
    use_pitch= False
    
    #test_list = os.listdir(testdir)
    test_list = [testfile]   
    print("Number of test files:",len(test_list))
    
    scalerf = os.path.join(dname, "scaler-general.p")
    bestf = os.path.join(dname, "model-general.p")

    scaler = pkl.load( open( scalerf, "rb" ) )
    best = pkl.load( open(bestf, "rb" ) )
    
    
    #now process and predict the test data.
    meta_acclist = []
    meta_covlist = []
    meta_matlist =[]
    test_amount = 0.0
    for f in test_list:
        
        t = f.split('.')
        if t[1] == 'wav':
           
            try:
                #testfile = os.path.join(testdir,t[0])
                X_test,y_test,merged,length = AVEutils.preprocess_spec(testfile,intensity=use_intensity,pitch=use_pitch,tg = False)
                test_amount = float(test_amount)+length
                result_file = t[0]
                fit_test,mat=vowel_extractor.test_model(X_test,y_test,best,scaler,"%s.csv" %(result_file))
                merged['pred']=fit_test
                #smerged.to_csv("%s.csv" %(result_file))
            except:
                print("Error in importing:",f)
                
            try:
                for s in smoothing_threshold:
                    acc_list = []
                    cov_list = []
                    (vonly,true) = vowel_extractor.make_tg_autovowels(merged,result_file,testdir,threshold=s,groundtruth = False)
                    success=True
            except:
                print("No vowels found for:",f)
    
    #print('amount of training_data', training_length)
    print('amount of test', test_amount)
    
    return(success)
 #driver code   
#test('/Users/emilygrabowski/Desktop/UCLA_vqp_original/Mandarin_Audio/F1/F1_01_a.wav')
 ##beta a cleaner (to take out all but the frame sentences)
 

 
