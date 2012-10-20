"""
    
Module for assorted post processing of RBCs (Perseus Output)
created by kel 5/23/2012

    
    New Cells: 110125, 130125, 140125, 40125, 50125
    Old Cells: 100125, 120125, 50125, 90125
"""

import numpy
import matplotlib
import matplotlib.pyplot as plt
import re
import os
import rbc_current as rc

def plot_diagram (persFile, lb=0, ub=2, out_type='bin',rmv='Y', dpi=80, fontsize=20):
    """
    Plot persistence diagram for data in persFile. If rmv=='Y', remove
    the infinite generator (though this doesn't seem to be working).
    """
    with open(persFile, 'r') as fh:
        s = fh.read()
    fh.close()
    s = s.split('\n')#seperate gens
    s.remove('') #remove blank lines
#    goodGens = rc . get_gens_sigma(persFile,lb,ub)
#    goodGens = rc . get_gens_bin (persFile)
    goodGens = rc . get_outlier_gens (persFile, lb, ub, 
                                      out_type, rmv, '')
    ggList = zip(*goodGens)
    x = []
    y = []
    maxLevel = str(int(s[-1].split(' ')[-1])+1)
    for i in xrange(len(s)):
        birth,death = s[i].split(' ')
        if int(birth) == -1:
            birth = maxLevel
        if int(death) == -1:
            death = maxLevel
        if not (int(birth),int(death)) in goodGens:
            x.append( int(birth) )
            y.append( int(death) )
    fig = plt.figure( dpi=dpi )
    ax = fig.gca()
    ax.scatter( x, y,c='b',marker='o',lw=.1)
    ax.scatter( ggList[0], ggList[-1],c='r',marker='o',lw=.1)
    line = [0, int(maxLevel)]
    ax.plot(line, line, 'g-')
    ax.set_xlim( [0, max( x )+10] )
    ax.set_ylim( [0, max( y )+20] )
    ax.set_xlabel( r'birth', fontsize=fontsize )
    ax.set_ylabel( r'death', fontsize=fontsize )
    xticks = [ int( tk ) for tk in ax.get_xticks() ]
    yticks = [ int( tk ) for tk in ax.get_yticks() ]
    ax.set_xticklabels( xticks, fontsize=fontsize )
    ax.set_yticklabels( yticks, fontsize=fontsize )
    fig.show()
    return fig

def plot_diagram_std (persFile, fontsize=20):
    with open(persFile, 'r') as fh:
        s = fh.read()
    fh.close()
    s = s.split('\n')#seperate gens
    s.remove('') #remove blank lines
    x = []
    y = []
    maxLevel = str(int(s[-1].split(' ')[-1])+1)
    for i in xrange(len(s)):
        birth,death = s[i].split(' ')
        if int(birth) == -1:
            birth = maxLevel
        if int(death) == -1:
            death = maxLevel
        x.append( int(birth) )
        y.append( int(death) )
    # now make the figure
    fig = plt.figure( dpi=160 )
    ax = fig.gca()
    ax.scatter( x, y,c='b',marker='o',lw=.1)
    line = [0, int(maxLevel)]
    ax.plot(line, line, 'g-')

    # set yaxis lims
    ax.set_xlim( [0, max( line )] )
    ax.set_ylim( [0, max( y )+10] )
    
    fig.show()
    return fig

def plot_diagram_regions( persFile, lines=[], fontsize=20, zoom=False ):
    """
    persFile -- path to perseus persistence diagram text file

    lines  -- list of ints indicating region-separating h/vlines.

    ** NOTE ** The plot attributes are specifically for cell new11.
    """
    with open(persFile, 'r') as fh:
        s = fh.read()
    fh.close()
    s = s.split('\n')#seperate gens
    s.remove('') #remove blank lines
    x = []
    y = []
    maxLevel = str(int(s[-1].split(' ')[-1])+1)
    for i in xrange(len(s)):
        birth,death = s[i].split(' ')
        if int(birth) == -1:
            birth = maxLevel
        if int(death) == -1:
            death = maxLevel
        x.append( int(birth) )
        y.append( int(death) )
    # now make the figure
    fig = plt.figure( dpi=160, frameon=False )
    ax = fig.gca()
    ax.scatter( x, y,c='b',marker='o',lw=.1)
    line = [0, int(maxLevel)]
    ax.plot(line, line, 'g-')
    if not lines:
        xticks = [0,500,1000,1500,2000,2500] 
        yticks = [0,500,1000,1500,2000,2500]
    else:
        xticks = [0,500,1500,2000,2500] + lines
        yticks = [0,500,1500,2000,2500] + lines
    xticks.sort()
    yticks.sort()
    xticks_str = [ str( t ) for t in xticks ]
    yticks_str = [ str( t ) for t in yticks ]
    ax.set_xticks( xticks )
    ax.set_yticks( yticks )
    ax.set_xticklabels( xticks_str, fontsize=fontsize )
    ax.set_yticklabels( yticks_str, fontsize=fontsize )
    if lines:
        for line in lines:
            ax.hlines( line, 0, line, linestyles='dashed' ) ## jjb ***** this is _specifically_ for new11, frame 2000
            ax.vlines( line, line, 3000, linestyles='dashed' )
    if zoom:
        ax.set_xlim( (lines[0]-200, lines[0]+200) )
        ax.set_ylim( (lines[0]-200, lines[0]+200) )
        ax.set_autoscale_on( False )
    else:
        ax.set_xlim( [0, max( x )+10] )
        ax.set_ylim( [0, max( y )+20] )
    #ax.set_title( 'Persistence Diagram', fontsize=fontsize+4 )
    #ax.set_xlabel( 'birth', fontsize=fontsize )
    #ax.set_ylabel( 'death', fontsize=fontsize )
    fig.show()
    return fig

    
