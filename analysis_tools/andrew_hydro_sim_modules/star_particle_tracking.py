#I'm writing this because I don't understand how Andrew W program works
#so I'm making my own.
#
#This is in principle simple (at least it will be at first)
#
#take in a list of star particle ids (or a file with the ids) and then
#a list of snapshots and track the positions of the particles back in
#time.
#
#This will work like a merger tree, but much simpler
#

import h5py, sys, re
import numpy as np

def track_particles(z0_snap,snapshot_numbers,star_list=None,snap_loc='./'):
    #first check if the input ids are an array or a file

    snap_num = re.split('_|\.',z0_snap)[-2]

    output_hdf5 = h5py.File('star_tracking.hdf5','w')

    f_zero = h5py.File(snap_loc+z0_snap)

    h = f_zero['Header'].attrs['HubbleParam']

    ids_zero = f_zero['PartType4']['ParticleIDs'][:]
    coords_zero = f_zero['PartType4']['Coordinates'][:]/h

    #This will check to see if you gave it a file or just a list
    if type(star_list)==str:
        star_ids = np.loadtxt(star_list)
        assert a.ndim==1 , 'The array is not 1d'
    elif type(star_list)==list or type(star_list)==np.ndarray:
        star_ids = star_list
    else:
        print('The ids were None or in an unrecognized format, so I will use everything:')
        star_ids = ids_zero

    selected_ids = ids_zero[(star_ids==ids_zero)]
    selected_coords = coords_zero[(star_ids==ids_zero)]
    
    group = output_hdf5.create_group('snapshot_'+snap_num)
    dset_i = group.create_dataset('ids',data=selected_ids)
    dset_c = group.create_dataset('coordinates',data=selected_coords)

    for snap_id in snapshot_numbers:
        #This is going to assume that the snapshot file names are the same
        #differing only by the snapshot number

        print 'running for snapshot {}'.format(snap_id)

        snap_file = z0_snap.replace(str(snap_num),str(snap_id))

        f_snap = h5py.File(snap_loc+snap_file)
        a_scale = f_snap['Header'].attrs['Time'] #scale factor

        #I need to check if the snap actually has stars in it or else it will 
        #give an error when trying to grab the data
        if 'PartType4' in f_snap:
            f_coords = f_snap['PartType4']['Coordinates'][:]*a_scale/h #remember units are comoving/h
            f_ids = f_snap['PartType4']['ParticleIDs'][:]

            #now I need to correlate the ids from z=0 to this snapshot
            particle_correlate = (selected_ids==f_ids)

            step_ids = f_ids[particle_correlate]
            step_coords = f_coords[particle_correlate]
        
        else:
            step_ids = []
            step_coords = []

        group = output_hdf5.create_group('snapshot_'+snap_id)
        dset_i = group.create_dataset('ids',data=step_ids)
        dset_c = group.create_dataset('coordinates',data=step_coords)

    output_hdf5.close()
    
        
