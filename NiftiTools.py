#import os
from numpy import array, sign, int32
import numpy as np
import nibabel as nib
import math

#add comments! add docstrings!
def striprotations(InputNiiFilename, OutputNiiFilename):
    InputImageHandle = nib.load(InputNiiFilename)
    InputImageAffine = InputImageHandle.get_affine()
    InputImageHeader = InputImageHandle.get_header()
    Data = array(InputImageHandle.get_data())

    newaffine = (sign(InputImageAffine) *
               array([[InputImageHeader['pixdim'][1], 0, 0, 0],
                      [0, InputImageHeader['pixdim'][2], 0, 0],
                      [0, 0, InputImageHeader['pixdim'][3], 0],
                      [1, 1, 1, 1]]))
    newaffine += (array([[0, 0, 0, 1],
                      [0, 0, 0, 1],
                      [0, 0, 0, 1],
                      [0, 0, 0, 0]]) * InputImageAffine)


    OutputNiftiFileHandle = nib.Nifti1Image(Data, newaffine, header=InputImageHeader)
    OutputNiftiFileHandle.set_data_dtype(int32)
    OutputNiftiFileHandle.to_filename(OutputNiiFilename)

def setaffine(InputNiiFilename, OutputNiiFilename, affine, offsets):

    """
    setaffine(InputNiiFilename, OutputNiiFilename, affine)
    takes the input image, replace the affine with the 3x3 affine provided
    centers the image using the midpoint along each dimension as the new center coordinate
    returns the image
    """

    InputImageHandle = nib.load(InputNiiFilename)
    InputImageAffine = InputImageHandle.get_affine()
    InputImageHeader = InputImageHandle.get_header()
    Data = array(InputImageHandle.get_data())

    (xlen, ylen, zlen) = Data.shape
    newaffine = InputImageAffine
    newaffine[0:3, 0:3] = affine
    newaffine[0, 3] = offsets[0]
    newaffine[1, 3] = offsets[1]
    newaffine[2, 3] = offsets[2]

    OutputNiftiFileHandle = nib.Nifti1Image(Data, newaffine, header=InputImageHeader)
    OutputNiftiFileHandle.set_data_dtype(int32)
    OutputNiftiFileHandle.to_filename(OutputNiiFilename)

def growRegion(InputNiiFilename, OutputNiiFilename, voxels):
    """Makes every nonzero voxel grow into it's neighboring zero regions:
Meant to be used as a way of growing masks only..all values set to 1"""
    InputImageHandle = nib.load(InputNiiFilename)
    InputImageAffine = InputImageHandle.get_affine()
    InputImageHeader = InputImageHandle.get_header()
    Data = array(InputImageHandle.get_data())
    (xlen, ylen, zlen) = Data.shape
    for i in range(0, voxels):
        paddeddata = np.zeros((xlen + 2, ylen + 2, zlen + 2))
        paddeddata[1:xlen + 1, 1:ylen + 1, 1:zlen + 1] = Data # for 256 len, goes from 0 to 255, so padded 1 to 256 or 1 to xlen+1 (last entry not used)
        for x in range(1, xlen + 1): #last entry not evaluated and we need 256 checked
            for y in range (0, ylen + 1):
                for z in range (0, zlen + 1):
                    if paddeddata[x, y, z] == 0:
                    #+2 instead of +1 to account for funny python indexing (+1 would only get first and middle entries
                        Data[x - 1, y - 1, z - 1] = 1 if (np.abs(paddeddata[x - 1:x + 2, y - 1:y + 2, z - 1:z + 2]).sum() != 0) else 0

    OutputNiftiFileHandle = nib.Nifti1Image(Data, InputImageAffine, header=InputImageHeader)
    OutputNiftiFileHandle.set_data_dtype(int32)
    OutputNiftiFileHandle.to_filename(OutputNiiFilename)
