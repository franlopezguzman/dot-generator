#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# @author: franlopezguzman

import numpy as np
import matplotlib.pyplot as plt
from os import mkdir
from os.path import exists
from scipy.spatial import ConvexHull
from math import sqrt, pi

def main():
    # Define parameters
    numerosities = [1,2,3,4,5,6,7,8,9]
    spacing = .5
    size = .05
    
    testDir = 'test'
    testRepetitions = 1000
    
    #Create figures for test data
    print('Creating test images...')
    generate_dots(numerosities, spacing, size, mainDir=testDir, totalRepetitions=testRepetitions)
    
#---------------------------------------------------------------------

def generate_dots(numerosities, spacing, size, totalRepetitions=10, mainDir='Figuras/',
                  color='#FDFF00', figSizePixels=96, imageFormat='png'):
    if not exists(mainDir):
        mkdir(mainDir)
    for numerosity in numerosities:
        outDir = mainDir+'/'+str(numerosity)+'/'
        outData = new_data(totalRepetitions, outDir=outDir)
        for repetition in range(totalRepetitions):
            plt.close()
            (fig, ax) = new_figure()
            #Generate left image
            occupiedArea = sqrt(spacing * numerosity)
            itemSizeMax = sqrt(size / numerosity)
            itemSizeMin = itemSizeMax / 4
            paintedArea, convexHull = generate_set(numerosity,occupiedArea,itemSizeMax,itemSizeMin,color,ax)
            #Save figure
            fig.set_size_inches(figSizePixels/96, figSizePixels/96)
            plt.savefig(outDir + '%02d' % numerosity + '_' + str(repetition) +
                        '.' + imageFormat, format=imageFormat)
            plt.close()
            #Save data
            outData[repetition,0] = numerosity
            outData[repetition,1] = paintedArea
            outData[repetition,2] = convexHull
        save_data(outDir, outData)
        print('Numerosity %d finished' % numerosity)
        

#---------------------------------------------------------------------

def generate_set(numerosity,occupiedArea=1,itemSizeMax=.1,itemSizeMin=.025,color='#0004FA', ax='None'):
    #Create a vector with the radii of all the dots
    radii = itemSizeMin + (itemSizeMax-itemSizeMin) * np.random.rand(numerosity,1)
    radii = -np.sort(-radii, axis=0)
    #Create an array for the coordinates
    coords = np.zeros([numerosity,2])
    #Create a figure
    if (ax == 'None'):
        fig, ax = new_figure()
    #Define the coordinates for the dots so that they fall inside the occupied are and don't supperpose
    for i in range(numerosity):
        available = False
        plotError = False
        setIterations = 0
        while (not available):
            coords[i,0] = np.random.rand(1)
            coords[i,1] = np.random.rand(1)
            available = is_available(i,radii,coords,occupiedArea)
            setIterations += 1
            if setIterations == 1000:
                plotError = True
                break
        if (not plotError):
            circle = plt.Circle((coords[i,0],coords[i,1]), radii[i],color=color)
            ax.add_artist(circle)
        else:
            circle = plt.Circle((coords[i,0],coords[i,1]), radii[i],color='white')
            ax.add_artist(circle)
            break       
    #Calculate convex hull:
    try:
        convexHull = ConvexHull(coords).volume
    except:
        convexHull = 0.
    #Calculate painted area:
    paintedArea = pi * np.sum(radii**2)
    return (paintedArea, convexHull)

#---------------------------------------------------------------------
    
def is_available(i,radii,coords,occupiedArea=1):
    posX = ((coords[i,0])-radii[i]>.05) and (coords[i,0]+radii[i]<.95) 
    posY = ((coords[i,1])-radii[i]>.05) and (coords[i,1]+radii[i]<.95)
    available = posX and posY  #Avoid dots on borders
    if (not available):
        return available
    for j in range(i):
        distDots = sqrt((coords[i,0]-coords[j,0])**2 + (coords[i,1]-coords[j,1])**2)
        position = distDots > (radii[i]+radii[j])*1.1 #Avoid superposition
        area = distDots < sqrt(occupiedArea) #Dots fall inside occupied area
        available = available and position and area
        if (not available):
            break
    return available

#---------------------------------------------------------------------
    
def new_figure():
    (fig, ax) = plt.subplots()
    ax.set_xlim([0,1]); ax.set_ylim([0,1])
    ax.set_aspect('equal'); ax.set_facecolor('#BEBDC2')
    ax.set_xticks([]); ax.set_yticks([])
    #ax.spines['top'].set_linewidth(-10); 
    #ax.spines['right'].set_linewidth(-10)
    #ax.spines['bottom'].set_linewidth(-10)
    #ax.spines['left'].set_linewidth(-10)
    
    return (fig, ax)
    
#---------------------------------------------------------------------

def new_data(repetitions, outDir='Figuras/'):
    outData = np.zeros([repetitions, 3])
    if not exists(outDir):
        mkdir(outDir)
    return outData
	
#---------------------------------------------------------------------
	
def save_data(outDir, outData):
    header = 'numerosity,painted_area,convex_hull'
    np.savetxt(outDir+'data.csv', outData, header=header, fmt='%.3f', delimiter=',')
	
#---------------------------------------------------------------------
    
if __name__ == '__main__': main()
