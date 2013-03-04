
from pyRBC import rbc_histogram as rh
from matplotlib import pyplot as plt
import numpy as np

"""
This module is just for convenience. For manipulating plots (labels,
legends, etc) without having to tweak the original code in
rbc_histogram.py.
"""

def plot_hist( old, new ):
    """
    new : list of lists holding normalized birth times for generators.

    old : (same)
    """
    out = rh.plot_hist_birth_times( old, new )

    fig = out[0]
    ax = fig.gca()
    ax.set_xlabel( "First birth times (normalized) of midrange generators" )

    plt.show()

    return fig

def concat_birth_times( bt, thresh, num_bts=1 ):

    cells = bt[ thresh ]   # all midrange gens, (birth, death) for each cell
    #cvals = cells.values() # just grab all values, so 11 or 13 lists of 5000 lists

    birth_times = {}
    # extract all i'th generators
    for n in range( num_bts ):
        bt_n = []
        for cell in cells.values():
            for frame in cell:
                # graph i'th birth time from frame
                try:
                    bt_n.append( frame[n][0] )
                # for the random frame with very few midrange gens
                except:
                    pass 
        birth_times[n] = bt_n 

    return birth_times
 
