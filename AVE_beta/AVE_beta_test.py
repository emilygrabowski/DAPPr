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
import pickle as pkl
#from sklearn.neural_network import MLPClassifier

##simplify
testdir = sys.argv[1]
#traindir = "/Users/emilygrabowski/Desktop/ave-beta-data/train/"
#testdir = "/Users/emilygrabowski/Desktop/ave-beta-data/test/"

flist = os.listdir(testdir)
smoothing_threshold = [8]


use_intensity = True
use_pitch= False

test_list = os.listdir(testdir)
    
print("Number of test files:",len(test_list))


scaler = pkl.load( open( "scaler-general.p", "rb" ) )
best = pkl.load( open("model-general.p", "rb" ) )


#now process and predict the test data.
meta_acclist = []
meta_covlist = []
meta_matlist =[]
test_amount = 0.0
for f in test_list:
    
    t = f.split('.')
    if t[1] == 'wav':
        try:
            testfile = os.path.join(testdir,t[0])
            X_test,y_test,merged,length = AVEutils.preprocess_spec(testfile,intensity=use_intensity,pitch=use_pitch,tg = False)
            test_amount = float(test_amount)+length
            result_file = t[0]
            fit_test,mat=vowel_extractor.test_model(X_test,y_test,best,scaler,"%s.csv" %(result_file))
            merged['pred']=fit_test
            #smerged.to_csv("%s.csv" %(result_file))
            for s in smoothing_threshold:
                acc_list = []
                cov_list = []
                (vonly,true) = vowel_extractor.make_tg_autovowels(merged,result_file,testdir,threshold=s,groundtruth = False)
        except:
            print("Error in importing:",f)

#print('amount of training_data', training_length)
print('amount of test', test_amount)


    

