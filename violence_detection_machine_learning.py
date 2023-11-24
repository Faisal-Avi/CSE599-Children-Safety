import os
import gc
import sys

import pandas as pd
import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
import seaborn as sns
import pickle

import skimage
from skimage.feature import hog, canny
from skimage.filters import sobel
from skimage import color


from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import OneHotEncoder

from keras import layers
import keras.backend as K
from keras.models import Sequential, Model
from keras.preprocessing import image
from keras.layers import Input, Dense, Activation, Dropout
from keras.layers import Flatten, BatchNormalization
from keras.layers import Convolution2D, MaxPooling2D, AveragePooling2D, GlobalAveragePooling2D 
from keras.applications.imagenet_utils import preprocess_input
from tensorflow.keras.applications.vgg19 import VGG19
from tensorflow.keras.applications import MobileNetV3Large
from tf_explain.core.activations import ExtractActivations
from tf_explain.core.grad_cam import GradCAM
from keras.utils.data_utils import get_file

from PIL import Image
from tqdm import tqdm
import random as rnd
import cv2
from keras.preprocessing.image import ImageDataGenerator
from numpy import expand_dims
from livelossplot import PlotLossesKeras

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB, GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix, accuracy_score, classification_report , precision_score, recall_score, f1_score
from sklearn.metrics import roc_curve, auc
from sklearn.metrics import RocCurveDisplay
from sklearn.preprocessing import label_binarize
from scipy import interp
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

start_date_and_time = datetime.now()
print(start_date_and_time)

main_path = "C:\\Python310\\thesis\\voilence_dataset\\"
path_violence = main_path + "violence\\"
path_non_violence = main_path + "non_violence\\"

main_df = pd.DataFrame()

#print(os.listdir(path_violence))

main_df['images'] = os.listdir(path_violence) + os.listdir(path_non_violence) 

classes = []
paths = []
for image in main_df['images']:
    class_ = image.split('_')[0]
    classes.append(class_)
    if class_ == 'V':
        paths.append(main_path+'violence\\'+image)
    else:
        paths.append(main_path+'non_violence\\'+image)
        
main_df['classes'] = classes
main_df['path'] = paths

print(type(main_df))
print(main_df.columns)

main_df.head()

main_df.isna().sum()

print('Leaves Count: ',len(main_df['classes'].value_counts()))
print(main_df['classes'].value_counts())

plot = sns.countplot(x = main_df['classes'], color = '#2596be')
sns.set(rc={'figure.figsize':(15,12)})
sns.despine()
plot.set_title('Class Distribution\n', font = 'serif', x = 0.1, y=1, fontsize = 18);
plot.set_ylabel("Count", x = 0.02, font = 'serif', fontsize = 12)
plot.set_xlabel("Leaves classes", fontsize = 15, font = 'serif')

for p in plot.patches:
    plot.annotate(format(p.get_height(), '.0f'), (p.get_x() + p.get_width() / 2, p.get_height()), 
       ha = 'center', va = 'center', xytext = (0, -20),font = 'serif', textcoords = 'offset points', size = 15)
       
plt.figure(figsize=(5,5))
class_cnt = main_df.groupby(['classes']).size().reset_index(name = 'counts')
colors = sns.color_palette('Paired')[0:9]
plt.pie(class_cnt['counts'], labels=class_cnt['classes'], colors=colors, autopct='%1.1f%%')
plt.legend(loc='upper right')
plt.show()

plt.figure(figsize = (15,12))
for idx,i in enumerate(main_df.classes.unique()):
    plt.subplot(4,7,idx+1)
    df = main_df[main_df['classes'] ==i].reset_index(drop = True)
    image_path = df.loc[rnd.randint(0, len(df))-1,'path']
    img = Image.open(image_path)
    img = img.resize((224,224))
    plt.imshow(img)
    plt.axis('off')
    plt.title(i)
plt.tight_layout()
plt.show()


def plot_species(df,image_class):
    plt.figure(figsize = (12,12))
    species_df = df[df['classes'] == image_class].reset_index(drop = True)
    plt.suptitle(image_class)
    for idx,i in enumerate(np.random.choice(species_df['path'],32)):
        plt.subplot(8,8,idx+1)
        image_path = i
        img = Image.open(image_path)
        img = img.resize((224,224))
        plt.imshow(img)
        plt.axis('off')
    plt.tight_layout()
    plt.show()
   
for image_class in main_df['classes'].unique():
    plot_species(main_df , image_class)
    
widths, heights = [], []

for path in tqdm(main_df["path"]):
    width, height = Image.open(path).size
    widths.append(width)
    heights.append(height)
    
main_df["width"] = widths
main_df["height"] = heights
main_df["dimension"] = main_df["width"] * main_df["height"]

main_df.sort_values('width').head(84)
main_df.sort_values('width').tail(84)

def edges_images_gray(class_name):
    classes_df = main_df[main_df['classes'] ==  class_name].reset_index(drop = True)
    for idx,i in enumerate(np.random.choice(main_df['path'],4)):
        image = cv2.imread(i)
        gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = sobel(image)
        gray_edges=canny(gray)
        dimension = edges.shape
        fig = plt.figure(figsize=(8, 8))
        plt.suptitle(class_name)
        plt.subplot(2,2,1)
        plt.imshow(gray_edges)
        plt.subplot(2,2,2)
        plt.imshow(edges[:dimension[0],:dimension[1],0], cmap="gray")
        plt.subplot(2,2,3)
        plt.imshow(edges[:dimension[0],:dimension[1],1], cmap='gray')
        plt.subplot(2,2,4)
        plt.imshow(edges[:dimension[0],:dimension[1],2], cmap='gray')
        plt.show()
        
        
def edges_images_white(class_name):
    classes_df = main_df[main_df['classes'] ==  class_name].reset_index(drop = True)
    for idx,i in enumerate(np.random.choice(main_df['path'],4)):
        image = cv2.imread(i)
        gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        edges = sobel(image)
        gray_edges=canny(gray)
        dimension = edges.shape
        fig = plt.figure(figsize=(8, 8))
        plt.suptitle(class_name)
        plt.subplot(2,2,1)
        plt.imshow(gray_edges)
        plt.subplot(2,2,2)
        plt.imshow(edges[:dimension[0],:dimension[1],0], cmap="BuGn")
        plt.subplot(2,2,3)
        plt.imshow(edges[:dimension[0],:dimension[1],1], cmap='BuGn')
        plt.subplot(2,2,4)
        plt.imshow(edges[:dimension[0],:dimension[1],2], cmap='BuGn')
        plt.show()
        
for class_name in main_df['classes'].unique():
    edges_images_gray(class_name)
    
for class_name in main_df['classes'].unique():
    edges_images_white(class_name)
    

def corners_images_gray(class_name):
    classes_df = main_df[main_df['classes'] ==  class_name].reset_index(drop = True)
    for idx,i in enumerate(np.random.choice(main_df['path'],4)):
        image = cv2.imread(i)
        gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        corners_gray = cv2.goodFeaturesToTrack(gray, maxCorners=50, qualityLevel=0.02, minDistance=20)
        corners_gray = np.float32(corners_gray)
        for item in corners_gray:
            x, y = item[0]
            cv2.circle(image, (int(x), int(y)), 6, (0, 255, 0), -1)
        fig = plt.figure(figsize=(8, 8))
        plt.suptitle(class_name)
        plt.subplot(2,2,1)
        plt.imshow(image, cmap="BuGn")
        plt.show()
        
for class_name in main_df['classes'].unique():
    corners_images_gray(class_name)
    
def sift_images_gray(class_name):
    classes_df = main_df[main_df['classes'] ==  class_name].reset_index(drop = True)
    for idx,i in enumerate(np.random.choice(main_df['path'],4)):
        image = cv2.imread(i)
        gray=cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        sift = cv2.SIFT_create()
        kp, des = sift.detectAndCompute(gray, None)
        kp_img = cv2.drawKeypoints(image, kp, None, color=(0, 255, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        fig = plt.figure(figsize=(8, 8))
        plt.suptitle(class_name)
        plt.subplot(2,2,1)
        plt.imshow(kp_img, cmap="viridis")
        plt.show()
        
for class_name in main_df['classes'].unique():
    sift_images_gray(class_name)
'''   

Xtrain, Xtest, ytrain, ytest = train_test_split(main_df[['path', 'classes']], main_df[['classes']], test_size=0.2, random_state=42)

print(Xtrain)
print(Xtest)
print(ytrain)
print(ytest)

# Decision Tree 
descision_tree_model = DecisionTreeClassifier()
descision_tree_model.fit(Xtrain,ytrain)
prediction_dt = descision_tree_model.predict(Xtest)
print('Decision Tree Accuracy Score:',round(accuracy_score(ytest,prediction_dt)*100),'%')
print('Decision Tree Precision Score:',round(precision_score(ytest,prediction_dt,average='micro')*100),'%')
print('Decision Tree Recall Score:',round(recall_score(ytest,prediction_dt,average='micro')*100),'%')
print('Decision Tree F1 Score:',round(f1_score(ytest,prediction_dt,average='micro')*100),'%')   

#ValueError: could not convert string to float: 'C:\\Python310\\thesis\\voilence_dataset\\violence\\V_173.mp4_frame1.jpg'

#-----------------------------------------------

X = main_df.loc[:, main_df.columns != 'classes']
y = main_df.loc[:, main_df.columns == 'classes']

print('Faisal')
print(X)
print(y)


X_train, X_val, y_train, y_val = train_test_split(main_df[['path', 'classes']], main_df[['classes']], test_size=0.2, random_state=42)

print(Xtrain)
print(Xtest)
print(ytrain)
print(ytest)

# Decision Tree 
descision_tree_model = DecisionTreeClassifier()
descision_tree_model.fit(Xtrain,ytrain)
prediction_dt = descision_tree_model.predict(Xtest)
print('Decision Tree Accuracy Score:',round(accuracy_score(ytest,prediction_dt)*100),'%')
print('Decision Tree Precision Score:',round(precision_score(ytest,prediction_dt,average='micro')*100),'%')
print('Decision Tree Recall Score:',round(recall_score(ytest,prediction_dt,average='micro')*100),'%')
print('Decision Tree F1 Score:',round(f1_score(ytest,prediction_dt,average='micro')*100),'%')

# Naive Bayes
multinomial_naive_bayes = GaussianNB()
multinomial_naive_bayes.fit(Xtrain,ytrain)
prediction_naive = multinomial_naive_bayes.predict(Xtest)
print('Naive Bayes Accuracy Score:',round(accuracy_score(ytest,prediction_naive)*100),'%')
print('Naive Bayes Precision Score:',round(precision_score(ytest,prediction_naive,average='micro')*100),'%')
print('Naive Bayes Recall Score:',round(recall_score(ytest,prediction_naive,average='micro')*100),'%')
print('Naive Bayes F1 Score:',round(f1_score(ytest,prediction_naive,average='micro')*100),'%')

# Logistic Regression
Logistic_model = LogisticRegression(C=1000)
Logistic_model.fit(Xtrain,ytrain)
prediction_Logistic = Logistic_model.predict(Xtest)
print('Logistic Regression Accuracy Score:',round(accuracy_score(ytest,prediction_Logistic)*100),'%')
print('Logistic Regression Precision Score:',round(precision_score(ytest,prediction_Logistic,average='micro')*100),'%')
print('Logistic Regression Recall Score:',round(recall_score(ytest,prediction_Logistic,average='micro')*100),'%')
print('Logistic Regression F1 Score:',round(f1_score(ytest,prediction_Logistic,average='micro')*100),'%')

# Random Forest
Random_forest_model = RandomForestClassifier(class_weight='balanced')
Random_forest_model.fit(Xtrain,ytrain)
prediction_Random_forest_model = Random_forest_model.predict(Xtest)
print('Random Forest Accuracy Score:',round(accuracy_score(ytest,prediction_Random_forest_model)*100),'%')
print('Random Forest Precision Score:',round(precision_score(ytest,prediction_Random_forest_model,average='micro')*100),'%')
print('Random Forest Recall Score:',round(recall_score(ytest,prediction_Random_forest_model,average='micro')*100),'%')
print('Random Forest F1 Score:',round(f1_score(ytest,prediction_Random_forest_model,average='micro')*100),'%')

# SVM Classifier
support_vector_model = SVC()
support_vector_model.fit(Xtrain,ytrain)
prediction_svm = support_vector_model.predict(Xtest)
print('Support Vector Machine Accuracy Score:',round(accuracy_score(ytest,prediction_svm)*100),'%')
print('Support Vector Machine Precision Score:',round(precision_score(ytest,prediction_svm,average='micro')*100),'%')
print('Support Vector Machine Recall Score:',round(recall_score(ytest,prediction_svm,average='micro')*100),'%')
print('Support Vector Machine F1 Score:',round(f1_score(ytest,prediction_svm,average='micro')*100),'%')
'''
end_date_and_time = datetime.now()
print(end_date_and_time)
print(1)
