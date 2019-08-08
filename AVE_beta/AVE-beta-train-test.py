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
import pandas as pd
import pickle as pkl
from sklearn.neural_network import MLPClassifier

##simplify
traindir = sys.argv[1]
testdir = sys.argv[2]
#traindir = "/Users/emilygrabowski/Desktop/ave-beta-data/train/"
#testdir = "/Users/emilygrabowski/Desktop/ave-beta-data/test/"

flist = os.listdir(testdir)
alpha = [10]
hls= [(40,5)]
rs= [1]
threshold_list = [.02]
smoothing_threshold = [8]
solver=['lbfgs']
param_grid = {"alpha":alpha,"hidden_layer_sizes":hls,"random_state":rs,'solver':solver}
clf = MLPClassifier()

use_intensity = True
use_pitch= False

training_list = os.listdir(traindir)
test_list = os.listdir(testdir)
    
print("Number of test files:",len(test_list),"Number of training files:",len(training_list))

#preprocess the files
Xlist = []
ylist = []
ex = []
training_length = 0.0
for f in training_list:
    t = f.split('.')
    if t[1] == 'wav':
    
    #print(f)
        trainfile = os.path.join(traindir,t[0])
        try:
            #get the spectral coefficients and make a training matrix
            Xs,ys,merged,length = AVEutils.preprocess_spec(trainfile,intensity=use_intensity,pitch=use_pitch)
            training_length = training_length + float(length)
            Xlist.append(Xs)
            ylist.append(ys)
            
    
        except:
            print("Error processing file",f,"Excluding from analysis")
            ex.append(f)
X =pd.concat(Xlist)
y =pd.concat(ylist)

#train a model and scaler using the MLP classifier
(scaler, best_params, best_score, mat,best) = vowel_extractor.train_model(X,y,clf,param_grid)

#save the model output
pkl.dump( scaler,open( "scaler.p", "wb" ) )
pkl.dump( best, open("model.p", "wb" ) )


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
            #print(length)
            result_file = t[0]
            fit_test,mat=vowel_extractor.test_model(X_test,y_test,best,scaler,"%s.csv" %(result_file))
            merged['pred']=fit_test
            #merged.to_csv("%s.csv" %(result_file))
            for s in smoothing_threshold:
                acc_list = []
                cov_list = []
                (vonly,true) = vowel_extractor.make_tg_autovowels(merged,result_file,testdir,threshold=s,groundtruth = False)
        except:
            print("Error in importing:",f)

print('amount of training_data', training_length)
print('amount of test', test_amount)


    

