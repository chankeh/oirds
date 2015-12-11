#!/usr/bin/env python
# Used to build the training images for a labeled data set.
# each training image is white.  The polygons representing each label
# has an assigned color in the image.

#import h5py, os

import matplotlib 
matplotlib.use('Agg') 
import matplotlib.pyplot as plt
#%matplotlib inline
import lmdb
import caffe
from PIL import Image
import numpy as np

label_colors = [(0,0,0), (64,128,1),(192,0,0),(0,128,2),(0,128,3),(128,0,4)]
modes = ['VEHICLE/CAR','VEHICLE/PICK-UP','VEHICLE/TRUCK','VEHICLE/UNKNOWN','VEHICLE/VAN']
modeIndices = dict( zip( modes, [int(x) for x in range( len(modes) )] ) )
imageSizeCrop=128

def main():
    import os
    import pandas as pd
    import itertools
    import glob
    import sys
    import random
    if sys.version_info[0] < 3:
        from StringIO import StringIO
    else:
        from io import StringIO

    if len(sys.argv) < 3:
      print "Usage: ", sys.argv[0], " dataDir imageFile"
      sys.exit( 0 )


    parentDataDir = sys.argv[1]
    if parentDataDir[-1] != '/':
       parentDataDir += "/"

    runcaffe(parentDataDir, openImg(sys.argv[2]))

def runcaffe (dataDir,im):
   from caffe.proto import caffe_pb2
   blob = caffe_pb2.BlobProto()
   meandata = open(dataDir + 'train_mean.binaryproto', 'rb').read()
   blob.ParseFromString(meandata)
   meanarr = np.array(caffe.io.blobproto_to_array(blob))
   net = caffe.Net(dataDir + 'deploy.prototxt', dataDir + '/train_iter_8000.caffemodel', caffe.TEST)
   transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
   transformer.set_mean('data', meanarr[0,:])
   transformer.set_transpose('data', (2,0,1))
   ## RGB -> BGR ?
   transformer.set_channel_swap('data', (2,1,0))
   transformer.set_raw_scale('data', 255.0)
   net.blobs['data'].reshape(1,3,imageSizeCrop,imageSizeCrop)
   #out= forward_all(data=np.asarray([transformer.preprocess('data', im)]))
   net.blobs['data'].data[...] = transformer.preprocess('data', im)
   outputResult(net.forward(), transformer, net.blobs['data'].data[0])

def outputResult(out, transformer, data):
  classPerPixel = out['score'][0].argmax(axis=0)
  ima = transformer.deprocess('data', data)
  shapeIME =  (classPerPixel.shape[0],classPerPixel.shape[1])
 # print out['prob'][0].argmax(axis=1)
 # print out['prob'][0].argmax(axis=2)
  plt.subplot(1, 3, 1)
  plt.imshow(ima)

#  for x in range(0,59):
#    plt.subplot(8, 8, x+2)
#    plt.imshow(toImageArray(np.ones(shapeIME, dtype=np.uint8)*x))

  plt.subplot(1, 3, 2)
  plt.imshow(toImageArray(classPerPixel)) 

  plt.subplot(1, 3, 2)
  plt.imshow(out('score')) 
  plt.savefig('outputPlt')


def toImageArray(classPerPixel):
  ima = np.zeros((classPerPixel.shape[0], classPerPixel.shape[0], 3), dtype=np.uint8)
  for i in range(0,ima.shape[0]-1):
    for j in range(0,ima.shape[1]-1):
        ima[i,j] = label_colors[classPerPixel[i,j]%6]
  return ima
  
def openImg(imFileName):
  from PIL import Image
  return convertImg(Image.open(imFileName))
   
def convertImg (im):
   return np.array(resizeImg(im))
   #return tmp.transpose(2,0,1)

def resizeImg(im):
   wpercent = (imageSizeCrop/float(im.size[0]))
   hsize = int((float(im.size[1])*float(wpercent)))
   return im.resize((imageSizeCrop ,hsize),Image.ANTIALIAS).crop((0,0,imageSizeCrop, imageSizeCrop))


if __name__=="__main__":
    main()
