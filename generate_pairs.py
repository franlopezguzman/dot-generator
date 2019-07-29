# -*- coding: utf-8 -*-
#
# @author: franlopezguzman

import numpy as np
import matplotlib.pyplot as plt
from os import mkdir
from os.path import exists
from scipy.spatial import ConvexHull
from math import *

#---------------------------------------------------------------------

def main():
    # Define parameters
    global numerositiesLeft, numerositiesRight, outData, outDir, imageFormat
    global spacingLarger, spacingSmaller, sizeLarger, sizeSmaller
    numerositiesLeft = [5,6,7,8,9,10,12,14]
    numerositiesRight = [5,6,7,8,9,10,12,14]
    spacingLarger = 1. / max(max(numerositiesLeft),max(numerositiesRight))
    spacingSmaller = spacingLarger / 4
    sizeLarger = .1
    sizeSmaller = sizeLarger / 2
    repetitions = 4
    imageFormat = 'png'
	
    #Create data array and directory
    outDir, outData = new_data(numerositiesLeft, numerositiesRight, repetitions)
    
    #Create figures for all sets
    generate_pairs(numerositiesLeft,numerositiesRight, totalRepetitions=repetitions)
    
    #Save data
    save_data(outDir, outData)
   
#---------------------------------------------------------------------
    
def generate_pairs(numerositiesLeft,numerositiesRight,totalRepetitions=2, colorLeft='#FDFF00', colorRight='#0004FA'):
    pair = -1
    for numLeft in numerositiesLeft:
        for numRight in numerositiesRight:
            if (numLeft != numRight):
                for repetition in range(totalRepetitions):
                    pair += 1
                    numMax = max(numLeft,numRight)
                    isCongruent = (repetition % 2 == 0) #alternating congruence
                    congruenceOK = False
                    congruenceIterations = 0
                    while not congruenceOK:
                        plt.close()
                        (fig, [axLeft,axRight]) = new_figure()
                        #Generate left image
                        occupiedAreaLeft = occupied_area(numLeft, numMax, isCongruent)
                        itemSizeMaxLeft, itemSizeMinLeft = item_size(numLeft, numMax, isCongruent, occupiedAreaLeft)
                        paintedAreaLeft, convexHullLeft = generate_set(
                                numLeft,occupiedAreaLeft,itemSizeMaxLeft,itemSizeMinLeft,colorLeft,axLeft)
                        #Generate right image
                        occupiedAreaRight = occupied_area(numRight, numMax, isCongruent)
                        itemSizeMaxRight, itemSizeMinRight = item_size(numRight, numMax, isCongruent, occupiedAreaRight)
                        paintedAreaRight, convexHullRight = generate_set(
                                numRight,occupiedAreaRight,itemSizeMaxRight,itemSizeMinRight,colorRight, axRight)
                        #Check if congruence is respected
                        congruenceOK = check_congruence(numLeft, paintedAreaLeft, convexHullLeft,
                                numRight, paintedAreaRight, convexHullRight, isCongruent)
                        congruenceIterations += 1
                        if (congruenceIterations == 100):
                            print('Error: congruence not respected for pair %02d %02d repetition %1d ' % (numLeft, numRight, repetition//2))
                            congruenceOK = True
                    #Save figure
                    fig.set_size_inches(18.5, 10.5)
                    plt.savefig(outDir + '%02d' % numLeft + '%02d' % numRight + 
                                '_Cong' + str(int(isCongruent)) + '_Rep' + str(repetition//2) +
                                '.' + imageFormat, format=imageFormat)
                    plt.close()
                    #Save data
                    outData[pair,0] = numLeft
                    outData[pair,1] = numRight
                    outData[pair,2] = max(numLeft,numRight) / min(numLeft,numRight) #Ratio
                    outData[pair,3] = isCongruent
                    outData[pair,4] = paintedAreaLeft
                    outData[pair,5] = paintedAreaRight
                    outData[pair,6] = convexHullLeft
                    outData[pair,7] = convexHullRight 

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
    convexHull = ConvexHull(coords)
    #Calculate painted area:
    paintedArea = pi * np.sum(radii**2)
    return (paintedArea, convexHull.volume)

#---------------------------------------------------------------------

def occupied_area(num, numMax, isCongruent=1):
    if isCongruent:
        if (num == numMax):
            occupiedArea = sqrt(spacingLarger * num)
        else:
            occupiedArea = sqrt(spacingSmaller * num)
    else:
        if (num == numMax):
            occupiedArea = sqrt(spacingSmaller * num)
        else:
            occupiedArea = sqrt(spacingLarger * num)
    return occupiedArea

#---------------------------------------------------------------------

def item_size(num, numMax, isCongruent=1, occupiedArea=1):
    if isCongruent:
        if (num == numMax):
            itemSizeMax = sqrt(sizeLarger/num)
        else:
            itemSizeMax = sqrt(sizeSmaller/num)
    else:
        if (num == numMax):
            itemSizeMax = sqrt(sizeSmaller/num)
        else:
            itemSizeMax = sqrt(sizeLarger/num)
    itemSizeMin = itemSizeMax / 2
    return (itemSizeMax, itemSizeMin)

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
    
def check_congruence(numLeft, paintedAreaLeft, convexHullLeft,
                     numRight, paintedAreaRight, convexHullRight, isCongruent):
    numMax = max(numLeft, numRight)
    if isCongruent:
        if (numLeft == numMax):
            return (paintedAreaLeft > paintedAreaRight) and (convexHullLeft > convexHullRight)
        else:
            return (paintedAreaRight > paintedAreaLeft) and (convexHullRight > convexHullLeft)
    else:
        if (numLeft == numMax):
            return (paintedAreaRight > paintedAreaLeft) and (convexHullRight > convexHullLeft)
        else:
            return (paintedAreaLeft > paintedAreaRight) and (convexHullLeft > convexHullRight)

#---------------------------------------------------------------------
    
def new_figure():
    (fig, [ax1,ax2]) = plt.subplots(1,2)
    ax1.set_xlim([0,1]); ax1.set_ylim([0,1])
    ax1.set_aspect('equal'); ax1.set_facecolor('#BEBDC2')
    ax1.set_xticks([]); ax1.set_yticks([])
    ax1.spines['top'].set_linewidth(-10); 
    ax1.spines['right'].set_linewidth(-10)
    ax1.spines['bottom'].set_linewidth(-10)
    ax1.spines['left'].set_linewidth(-10)
    ax2.set_xlim([0,1]); ax2.set_ylim([0,1])
    ax2.set_aspect('equal')
    ax2.set_facecolor('#BEBDC2')
    ax2.set_xticks([]); ax2.set_yticks([])
    ax2.spines['top'].set_linewidth(-10)
    ax2.spines['right'].set_linewidth(-10)
    ax2.spines['bottom'].set_linewidth(-10)
    ax2.spines['left'].set_linewidth(-10)
    
    return (fig, [ax1,ax2])
    
#---------------------------------------------------------------------

def new_data(numerositiesLeft, numerositiesRight, repetitions, outDir='Figuras/'):
    outData = np.zeros([len(numerositiesLeft)*len(numerositiesRight)*repetitions, 8])
    if not exists(outDir):
        mkdir(outDir)
    return outDir, outData
	
#---------------------------------------------------------------------
	
def save_data(outDir, outData):
    header = 'numLeft,numRight,ratio,isCongruent,paintedAreaLeft,paintedAreaRight,convexHullLeft,convexHullRight'
    np.savetxt(outDir+'data.csv', outData, header=header, fmt='%.3f', delimiter=',')	
	
#---------------------------------------------------------------------
	
if __name__=='__main__': main()