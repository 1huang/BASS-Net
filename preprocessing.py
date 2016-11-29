import scipy.io
import numpy as np
from random import shuffle
import scipy.ndimage
import os

##loading images for input and target image
import scipy.io as io
input_mat = io.loadmat('../data/Salinas.mat')['salinas']
target_mat = io.loadmat('../data/Salinas_gt.mat')['salinas_gt']

PATCH_SIZE = 3
HEIGHT = input_mat.shape[0]
WIDTH = input_mat.shape[1]
BAND = input_mat.shape[2]
CLASSES = [] 
COUNT = 200 #Number of patches of each class
OUTPUT_CLASSES = 16

input_mat = input_mat.astype(float)
input_mat -= np.min(input_mat)
input_mat /= np.max(input_mat)

MEAN_ARRAY = np.ndarray(shape=(BAND,),dtype=float)
new_input_mat = []
input_mat = np.transpose(input_mat,(2,0,1))
print(input_mat.shape)
for i in range(BAND):
    MEAN_ARRAY[i] = np.mean(input_mat[i,:,:])
    try:
        new_input_mat.append(np.pad(input_mat[i,:,:],PATCH_SIZE/2,'constant',constant_values = 0))
    except:
        new_input_mat = input_mat
    
print np.array(new_input_mat).shape

input_mat = np.array(new_input_mat)

def Patch(height_index,width_index):
    """
    Returns a mean-normalized patch, the top left corner of which 
    is at (height_index, width_index)
    
    Inputs: 
    height_index - row index of the top left corner of the image patch
    width_index - column index of the top left corner of the image patch
    
    Outputs:
    mean_normalized_patch - mean normalized patch of size (PATCH_SIZE, PATCH_SIZE) 
    whose top left corner is at (height_index, width_index)
    """
#     transpose_array = np.transpose(input_mat,(2,0,1))
    transpose_array = input_mat
#     print input_mat.shape
    height_slice = slice(height_index, height_index+PATCH_SIZE)
    width_slice = slice(width_index, width_index+PATCH_SIZE)
    patch = transpose_array[:, height_slice, width_slice]
    mean_normalized_patch = []
    for i in range(patch.shape[0]):
        mean_normalized_patch.append(patch[i] - MEAN_ARRAY[i]) 
    
    return np.array(mean_normalized_patch)

for i in range(OUTPUT_CLASSES):
    CLASSES.append([])
count = 0
image = []
image_label = []
for i in range(HEIGHT):
    for j in range(WIDTH):
        curr_inp = Patch(i,j)
        curr_tar = target_mat[i , j]
        image.append(curr_inp)
        image_label.append(curr_tar)
        if(curr_tar!=0): #Ignore patches with unknown landcover type for the central pixel
            CLASSES[curr_tar-1].append(curr_inp)
            count += 1
print count

image = np.array(image)
image_label = np.array(image_label)
for i in range(11):
    start = i*20000
    if i == 10:
        end = image.shape[0]
    else:
        end = (i+1)*20000
    image_mat = {}
    image_mat["image_patch"] = image[start:end]
    image_mat["labels"] = image_label[start:end]
    print end
#     print image_label.shape
    file_name = "Salinas_patch_image" + str(i) + ".mat"
    scipy.io.savemat(file_name, image_mat)

TRAIN_PATCH,TRAIN_LABELS,TEST_PATCH,TEST_LABELS,VAL_PATCH, VAL_LABELS = [],[],[],[],[],[]
FULL_TRAIN_PATCH = []
FULL_TRAIN_LABELS = []
train_idx = 175
count = 0
for i, data in enumerate(CLASSES):
    shuffle(data)
#     FULL_TRAIN_PATCH += data[:200]
#     FULL_TRAIN_LABELS += [count]*200
    TRAIN_PATCH += data[:train_idx]
    TRAIN_LABELS += [count]*train_idx
    VAL_PATCH += data[train_idx:200]
    VAL_LABELS += [count]*(200-train_idx)
    TEST_PATCH += data[200:]
    TEST_LABELS += [count]*(len(data) - 200)
    count += 1

FULL_TRAIN_LABELS = TRAIN_LABELS + VAL_LABELS
FULL_TRAIN_PATCH = TRAIN_PATCH + VAL_PATCH

TRAIN_LABELS = np.array(TRAIN_LABELS)
TRAIN_PATCH = np.array(TRAIN_PATCH)
TEST_PATCH = np.array(TEST_PATCH)
TEST_LABELS = np.array(TEST_LABELS)
VAL_PATCH = np.array(VAL_PATCH)
VAL_LABELS = np.array(VAL_LABELS)
FULL_TRAIN_LABELS = np.array(FULL_TRAIN_LABELS)
FULL_TRAIN_PATCH = np.array(FULL_TRAIN_PATCH)

train_idx = range(len(TRAIN_PATCH))
shuffle(train_idx)
TRAIN_PATCH = TRAIN_PATCH[train_idx]
TRAIN_LABELS = TRAIN_LABELS[train_idx]
test_idx = range(len(TEST_PATCH))
TEST_PATCH = TEST_PATCH[test_idx]
TEST_LABELS = TEST_LABELS[test_idx]
val_idx = range(len(VAL_PATCH))
shuffle(val_idx)
VAL_PATCH = VAL_PATCH[val_idx]
VAL_LABELS = VAL_LABELS[val_idx]
full_train_idx = shuffle(range(len(FULL_TRAIN_PATCH)))
FULL_TRAIN_PATCH = FULL_TRAIN_PATCH[full_train_idx]
FULL_TRAIN_LABELS = FULL_TRAIN_LABELS[full_train_idx]

train = {}
train["train_patch"] = TRAIN_PATCH
train["train_labels"] = TRAIN_LABELS
scipy.io.savemat("../data/Salinas_Train_patch_" + str(PATCH_SIZE) + ".mat", train)


test = {}
test["test_patch"] = TEST_PATCH
test["test_labels"] = TEST_LABELS
scipy.io.savemat("../data/Salinas_Test_patch_" + str(PATCH_SIZE) + ".mat", test)

val = {}
val["val_patch"] = VAL_PATCH
val["val_labels"] = VAL_LABELS
scipy.io.savemat("../data/Salinas_Val_patch_" + str(PATCH_SIZE) + ".mat", val)

full_train = {}
full_train["train_patch"] = FULL_TRAIN_PATCH
full_train["train_labels"] = FULL_TRAIN_LABELS
scipy.io.savemat("../data/Salinas_Full_Train_patch_" + str(PATCH_SIZE) + ".mat", full_train)


