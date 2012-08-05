import numpy
from matplotlib import pyplot as plt
import os, shutil
import csv
import time
try:
    from jjb.chomp import chomp_betti
except ImportError:
    # use the local copy
    import chomp_betti

def plot_raw_cell( fname, **args ):
    """
    Read in an ASCII file containing raw data for a red blood cell.

    Original files contain 5000 frames. Limit the frames loaded using
    max_frames arg. Number of frames = 5000 - <max_frames>. Therefore,
    number of rows = 5 implies that the last 5 rows of fname were read
    in (eg., 4995-4999).

    NOTE: bounday matrix is hardcoded for now.
    """
    fargs = { 'savename': None,
             'skiprows': 4997,
             'bnd' : 'boundary_Nov_new110125',
             'plot' : True
             }
    fargs.update( args )
    # set max frames
    skiprows = fargs['skiprows']

    # load boundary matrix for dimensions of cell array
    bnd_arr = numpy.loadtxt( fargs['bnd'] )
    nx,ny = bnd_arr.shape
    frames = load_rbc( fname, skiprows, nx, ny )
    num_cols = len( frames ) # for subplot 

    # compute mean over all extracted frames
    avg = find_mean( frames )
    print "avg", avg

    masked = [ numpy.ma.masked_less( f, avg ) for f in frames ]
    
    # save to disk
    if fargs['savename']:
        for i in range( num_cols ):
            sname = savename + '_' + str(i)
            numpy.save( sname, frames[i] )
    # plot the frames
    if fargs['plot']:
        fig = plt.figure()
        for i in range( num_cols ):
            sax = fig.add_subplot( 2, num_cols, i+1 )
            ma = numpy.ma.masked_less_equal( frames[i], 0 )
            sax.imshow( ma )
            #sax.imshow( frames[i] )
        for i in range( num_cols ):
            sax = fig.add_subplot( 2, num_cols, 4+i )
            sax.imshow( masked[i] )
        fig.savefig( fname+'_frames'+str(num_cols)+'.png' )
        fig.show()

def load_rbc( fname, skiprows, nx, ny ):
    """
    Returns a block frames from <fname> cell data. Reshapes array
    according to boundary data determined from <bnd> arg in
    plot_raw_data().
    """
    C = numpy.loadtxt( fname, skiprows=skiprows )    
    cell_frames = [ C[i].reshape(( nx,ny )) for i in range( 5000-skiprows ) ]
    return cell_frames

def complement2npy( fname ):
    """
    Each Complement cell image is stored in a DOS file, with
    approximately 200 lines. This reads the file and converts the
    values to ints before stacking them in a numpy array.

    fname -- full path to the file
    """
    # this convert from DOS newline format ('U'==universal newline)
    reader = csv.reader( open( fname, 'rU' ), delimiter='\t' )
    lines = list( reader )
    # convert strings to ints
    rows = [ [ int( val ) for val in row[:-1] ] for row in lines[4:] ]
    try:
        return numpy.vstack( rows[4:], dtype=numpy.int )
    except ValueError:
        print "problem with rows, here are the first 10:", rows[:10]
                       
    
def extract_complement_cell( fdir ):
    """
    fdir -- directory containing the Complement cell image frames.

    Return a 3D numpy array, with the third axis corrseponding to
    time.
    """
    if not fdir.endswith( '/' ): fdir+='/'
    dlist = os.listdir( fdir )
    dlist.sort()
    all_frames = []
    print "converting frames..."
    tstart = time.time()
    for frame in dlist:
        if frame.startswith('.'): continue
        all_frames.append( complement2npy( fdir + frame ) )
    print "Took ", time.time() - tstart, "seconds for converting", \
        len( dlist ), "frames."
    return numpy.array( all_frames )
    

def make_dir( fdir ):
    """
    Try to make directory. 
    """
    try:
        os.makedirs( fdir )
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise
    
def extract_frames( fname, bnd ):
    """
    Each line of fname contains a raveled matrix. Read each line,
    reshape it based on array stored in <bnd> file. Save to file.
    """
    if os.uname()[0] == 'Linux':
        savefunc = numpy.save
    elif os.uname()[0] == 'Darwin':
        # why the !@$# doesn't Mac save readable .npy files??
        savefunc = numpy.savetxt
    fh = open( fname, 'r' )
    bnd_arr = numpy.loadtxt( bnd )
    nx, ny = bnd_arr.shape
    bnd_arr = bnd_arr.ravel()
    # save files in a special folder
    part = fname.rpartition( '/' )
    cell_name = part[-1]
    # find the subfolder name from the beginning of the cell
    # name. subfolder must have been created already.
    subfolder = cell_name.partition( '-' )[0]
    savedir = part[0] + '/' + 'frames/' + subfolder +'/'

    make_dir( savedir )
    # print 'savedir', savedir
     
    # loop over lines in <fname> and save each as nx x ny array
    #k = 0. 
    fromstring = numpy.fromstring
    for k, line in enumerate( fh.readlines() ):
        arr = fromstring( line, sep='\t' )
        # remove boundary
        arr = bnd_arr * arr
        arr.resize( (nx,ny) )
        #numpy.save( savedir + cell_name + '_' + str(k), arr )
        savefunc( savedir + cell_name + '_' + str(k), arr )

def frames2png( fdir ):
    """
    Convert matrices in directory <fdir> to images.
    """
    dlist = os.listdir( fdir )
    dlist = [ f for f in dlist if f.endswith('npy') ]
    fig = plt.figure()
    ax = fig.gca()
    ax.hold( False )
    for f in dlist:
        arr = numpy.load( fdir + f )
        ma = numpy.ma.masked_less_equal( arr, 0 )
        ax.imshow( ma )
        # strip the .npy off
        fig.savefig( fdir + f[:-3] + 'png' )
        ax.clear()

def thresh2png( fdir, value ):
    """
    Convert thresholded matrices in directory <fdir> to images.
    """
    dlist = os.listdir( fdir )
    thresh = 'thresh'+str(value)
    dlist = [ f for f in dlist if f.endswith('npy') and thresh in f ]
    fig = plt.figure()
    ax = fig.gca()
    ax.hold( False )
    for f in dlist:
        arr = numpy.load( fdir + f )
        #ma = numpy.ma.masked_less_equal( arr, 0 )
        ax.imshow( arr )
        # strip the .npy off
        fig.savefig( fdir + f[:-3] + 'png' )
        ax.clear()

def threshold_frame( arr, pct ):
    """
    Threshold an cell array at <pct>*mean. <pct> should be entered as
    a decimals (eg., 100% = 1.0).

    1 if > <pct>*mean
    0 if <= <pct>*mean
    """
    # mask the array as a percent of the mean (excluding al zeros first)
    ma = numpy.ma.masked_less_equal( arr, 0 )
    return numpy.ma.masked_less_equal( arr, pct*ma.mean() )

def threshold_all( fdir, pct ):
    """
    Threshold all RBC images in directory <fdir>. The originals are
    stored in NPY files. Save the thresholded arrays at them as
    boolean arrays after masking.
    """
    dlist = os.listdir( fdir )
    dlist = [ f for f in dlist if f.endswith('npy') and 'thresh' not in f ]
    for f in dlist:
        arr = numpy.load( fdir + f )
        #thresh = threshold_frame( arr, pct )
        # mask the array as a percent of the mean (excluding al zeros first)
        thresh = numpy.ma.masked_less_equal( arr, 0 )
        thresh = numpy.ma.masked_less_equal( arr, pct*thresh.mean() )
        numpy.save( fdir + f[:-4] +'_thresh'+str(pct)+'.npy', thresh.mask )

def thresh2cub( fdir, value ):
    """
    Convert thresholded image matrices to Chomp CUB format.
    """
    dlist = os.listdir( fdir )
    thresh = 'thresh'+str(value)
    dlist = [ f for f in dlist if f.endswith('npy') and thresh in f ]
    for f in dlist:
        savename = fdir + f[:-3] + 'cub'
        arr = numpy.load( fdir + f )
        c = arr.astype( 'uint' )
        # where the masked matrix is False (==0)
        w = numpy.where( c==0 )
        # zip locations of thresholded values to get coords (2D)
        z = zip( w[0], w[1] )
        coords = [ str(x)+'\n' for x in z ]
        with open( savename, 'w' ) as fh:
            fh.writelines( coords )
 
def find_mean( frames ):
    return numpy.mean( [ f.mean() for f in frames] )

def run_chomp( fdir, value ):
    """
    """
    # grab CUB files
    dlist = os.listdir( fdir )
    thresh = 'thresh'+str( value )
    dlist = [ f for f in dlist if f.endswith('cub') and thresh in f ]
    for f in dlist:
        savename = fdir + 'chomp/' + f[:-4] 
        chomp_betti.run_chomp( fdir + f, savename+'.cbetti' )
        chomp_betti.extract_betti( savename )

def rename_cub_files( fdir, val ):
    """
    chomp cannot deal with two 'dots' in a file name. 
    """
    dlist = os.listdir( fdir )
    ending = str( val ) + 'cub'
    dlist = [ f for f in dlist if f.endswith( ending ) ]
    newlist = []
    for f in dlist:
        part = f.partition( '.' )
        newf = part[0] + part[-1]
        # x = f.rstrip('cub')
        #newf = x + '.cub'
        shutil.move( fdir + f, fdir + newf )
    

def plot_betti( barr, cell=1, savedir=None, dim=0, fig=None,
               total_cells=2, color='b', showplot=False, save=False, **args):
    """
    Plot betti numbers for each frame for a cell. Obtain a time series
    (time=frame number)
    """
    fargs = {'alpha' : 1.0,
             'lw' : 1.0
             }
    fargs.update( args )
    if fig is None:
        fig = plt.figure()
    ax = fig.gca()
    #ax = fig.add_subplot(total_cells, 1, cell_num+1)
    
    data = barr[:,dim,:]
    ax.plot( data[1], '-', **fargs )
    # record title and some stats
    # ax.set_title(  'Betti numbers for cell '+str(cell)+\
    #              ' (mean='+str( round(data[1].mean()) )+')' )
    ax.set_xlabel( 'Frame', fontsize=20 )
    ax.set_ylabel( r'$\beta_{'+str(dim)+'}$', fontsize=20 )
    if save==True:
        if savedir == None:
            fname = './figures_raw/betti_frames_H'+str(dim)+'_cell'+str(cell)+'.png'
        else:
            fname = savedir + '/betti_frames_H'+str(dim)+'_cell'+str(cell)+'.png'
        fig.savefig( fname )
    if showplot:
        fig.show()

def read_betti_dir( fdir, val ):
    """
    Read all .betti files in a directory and sort them for time series analysis.
    """
    dlist = os.listdir( fdir )
    # focus on one threshold value
    ending = str( val ) + '.betti'
    betti_list = [ f for f in dlist if f.endswith( ending ) ]

    betti_dict = dir_hash( betti_list )
    frames = betti_dict.keys()
    frames.sort()
    # keep the frame numbers organized in a dict ?
    #betti = {}
    # nah, just list them, but append them in frame order
    betti_arr = []
    for i in frames:
        b = betti_dict[i]
        bnums = numpy.loadtxt( fdir+b, dtype=numpy.uint8 )
        betti_arr.append( bnums )
    betti_arr = numpy.asarray( betti_arr )
    return betti_arr.T

def dir_hash( dlist ):
    """
    """
    files= {}
    for filename in dlist: 
        basename, extension = filename.split('.')
        # filename: new/old, prefix==id, frame number, threshold value
        celltype, prefix, frame, thresh = basename.split('_')
        files[ int( frame ) ] = filename
    return files

def fft_filter( fdir, bnd, modes ):
    """
    Call fft_image.run_fft_filter()

    fdir : directory containing image frames

    bnd : path to boundary file

    modes : percentage of Fourier modes to use for low pass filter (0,1)
    """
    fft_image.run_fft_filter( fdir, bnd, modes )


if __name__ == "__main__":

    have_pp = False
    try:
        import pp
        have_pp = True
    except ImportError:
        print "Could not import pp. Will proceed the serial way..."

    # new_fdir = '/data/jberwald/wyss/data/Cells_Jesse/New/frames/'
    # old_fdir = '/data/jberwald/wyss/data/Cells_Jesse/Old/frames/'
    new_fdir = '/sciclone/home04/jberwald/data10/jberwald/wyss/data/Cells_Jesse/New/frames/'
    old_fdir = '/sciclone/home04/jberwald/data10/jberwald/wyss/data/Cells_Jesse/Old/frames/'
    new_cells = [ 'new_110125/', 'new_130125/', 'new_140125/', 'new_40125/', 'new_50125/' ]
    old_cells = [ 'old_100125/', 'old_120125/', 'old_50125/', 'old_90125/' ]

    # Mac testing environment
    # new_fdir = '/data/jberwald/rbc/New/frames/'
    # #    old_fdir = '/data/jberwald/wyss/data/Cells_Jesse/Old/frames/'
    # new_cells = ['new_140125']

    sval = '125'

    # read all betti files from all experiments
    # new_arrs = {}
    # old_arrs = {}
    # for cell in new_dirs:
    #     betti_files = new_fdir + cell + 'chomp/'
    #     new_arrs[ betti_files ] = read_betti_dir( betti_files, sval )
    #     #new_arrs.append( read_betti_dir( betti_files ) )
    # for cell in old_dirs:
    #     betti_files = old_fdir + cell + 'chomp/'
    #     old_arrs[ betti_files ] = read_betti_dir( betti_files, sval )
        #old_arrs.append( read_betti_dir( betti_files ) )
    
    # split a giant cell file containing 5000 frames into individual files. 
    # cell_name = '/data/jberwald/wyss/data/Cells_Jesse/Old/old_50125-concatenated-ASCII'
    # bnd_name = '/data/jberwald/wyss/data/Cells_Jesse/Old/boundary_Nov_old50125'
    # extract_frames( cell_name, bnd_name )

    val =0.75
    sval = '075'
    #what_to_run = 'chomp'

    # set proper directories depending on cells (old? new?)
    fdir = new_fdir
    cell_dirs = new_cells
    # run stuff in parallel on all available processors
    if have_pp:
        # create a pool of workers. Default is to use all cpu's
        pool = pp.Server()
        jobs = []
        depmods = ( 'shutil', 'chomp_betti', 'numpy', 'os', 'fft_image' )
        # distribute jobs to the pool of workers
        for task in [ 'fft' ]: #'2cub', 'chomp' ]:
            for cell in cell_dirs:
                cub_files = fdir + cell
                if task=='threshold':
                    print "thresholding... "
                    print cub_files
                    jobs.append( pool.submit( threshold_all,
                                              args=( cub_files, val ),
                                              modules=depmods ) )
                elif task=='fft':
                    # run each cell in parallel, looping over a range
                    # of values for fourier modes
                    filters = numpy.linspace( 0, 1, 21 )
                    for r in filters:
                        # find the proper boundary file
                        idx = fdir.find( 'frames' )
                        bnd_file = fdir[:idx] + 'boundary_Nov_'+cell[:3]+cell[4:]
                        # just in case
                        bnd_file = bnd_file.rstrip( '/' )
                        print "performing low pass filter using r=", str( r )
                        print "frames", cub_files
                        print "boundary", bnd_file
                        jobs.append( pool.submit( fft_filter,
                                                  args=( cub_files, bnd_file, r ),
                                                  modules=depmods ) )
                        print ""
                elif task=='2cub':
                    print "converting to cubes... "
                    print cub_files
                    jobs.append( pool.submit( thresh2cub,
                                              args=( cub_files, val ),
                                              modules=depmods ) )
                elif task=='chomp':
                    print "chomping..."
                    print cub_files
                    rename_cub_files( cub_files, val )
                    jobs.append( pool.submit( run_chomp,
                                              args=( cub_files, sval ),
                                              modules=depmods ) )
                else:
                    print "What are we running? Unrecognized task:", task
            pool.wait()
        pool.print_stats()
        pool.destroy()

    # else:
    # for cell in cell_dirs:
    #     threshold_all( fdir, pct=val )
    #     cub_files = fdir + cell
    #     #run_chomp( cub_files, val )
    
    # str_values = [ '1.0' ]
    # for c in cell_dirs:
    #     thresh2cub( fdir, sval )
        
    
    # #values = [ '09', '10', '12']
 

#    rename_cub_files( fdir )
