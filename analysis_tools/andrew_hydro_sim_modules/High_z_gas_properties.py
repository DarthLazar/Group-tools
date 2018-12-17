import h5py, os
import numpy as np
import numpy.ma as ma

#The purpose of this program is to test the gas properties of the gas that forms stars
#in the reionization runs. The plan is to take all of the stars at z = 6 (snapshot 
#number 52) and go back in time and find the gas particles that those stars formed out of.
#Then track the properties of those gas particle back to the beginning of the simulation

snap_dir = '/gdata/rouge/agraus/reionization_runs_hi_z/fg/'

print snap_dir+'snapshot_m10b_fg_z_6_052.hdf5'

f_initial = h5py.File(snap_dir+'snapshot_m10b_fg_z_6_052.hdf5')
star_ids = f_initial['PartType4']['ParticleIDs'][:]

star_ids_sort = np.sort(star_ids)

print 'stars at z = 6: '+str(len(star_ids))

output_hdf5 = h5py.File('gas_particles.hdf5')

for snapshot_file in os.listdir('/gdata/rouge/agraus/reionization_runs_hi_z/fg/'):    

    print snapshot_file

    f_z = h5py.File(snap_dir+snapshot_file)

    'at z='+str(f_z['Header'].attrs['Redshift'])

    redshift = f_z['Header'].attrs['Redshift']

    gas_ids_at_z = f_z['PartType0']['ParticleIDs'][:]
    rho_at_z = f_z['PartType0']['Density'][:]
    EA_at_z = f_z['PartType0']['ElectronAbundance'][:]
    IE_at_z = f_z['PartType0']['InternalEnergy'][:]
    Z_at_z = f_z['PartType0']['Metallicity'][:,1] #Note that metals are an array so it doesn't really work with how the arrays are constructed
    NH_at_z = f_z['PartType0']['NeutralHydrogenAbundance'][:]

    #Now I want to sort these array BY the gas ids array

    sort_mask = np.argsort(gas_ids_at_z)
    gas_ids_sort = gas_ids_at_z[sort_mask]
    rho_sort = rho_at_z[sort_mask]
    EA_sort = EA_at_z[sort_mask]
    IE_sort = IE_at_z[sort_mask]
    Z_sort = Z_at_z[sort_mask]
    NH_sort = NH_at_z[sort_mask]
    
    star_ids_masked = ma.masked_where(np.in1d(star_ids_sort,gas_ids_sort,invert=True),star_ids_sort)
    
    ma.set_fill_value(star_ids_masked,0.0)
    
    #I stopped here: The fill value doesn't really seem to be working correcly, and when I do star_ids_masked.data
    #it doesn't really seem to be g

    gas_final = star_ids_masked.filled(0.0).astype('float64')
    rho_final = star_ids_masked.filled(0.0).astype('float64')
    EA_final = star_ids_masked.filled(0.0).astype('float64')
    IE_final = star_ids_masked.filled(0.0).astype('float64')
    Z_final = star_ids_masked.filled(0.0).astype('float64')
    NH_final = star_ids_masked.filled(0.0).astype('float64')

    gas_mask = np.in1d(gas_ids_sort,star_ids_sort) #the GAS ids which are in the star sample at this z
    rho_from_gas_mask = rho_sort[gas_mask].astype('float64') #The densities of gas particles which turn into stars by z =6
    EA_from_gas_mask = EA_sort[gas_mask].astype('float64')
    IE_from_gas_mask = IE_sort[gas_mask].astype('float64')
    Z_from_gas_mask = Z_sort[gas_mask].astype('float64')
    NH_from_gas_mask = NH_sort[gas_mask].astype('float64')

    #For some reason it is replaceing the non-zero elements with zero instead of the correct replacement
    #I think that for very low values 1e-8 or so it just replaces the element with zero.
    #looks like it's turning ANY fraction into a zero
    #Maybe try to change dtype of maksing array?

    print EA_from_gas_mask

    np.place(rho_final, rho_final!=0.0,rho_from_gas_mask)
    np.place(EA_final, EA_final!=0.0,EA_from_gas_mask)
    np.place(IE_final, IE_final!=0.0,IE_from_gas_mask)
    np.place(Z_final, Z_final!=0.0,Z_from_gas_mask)
    np.place(NH_final, NH_final!=0.0,NH_from_gas_mask)

    print EA_final

    #rho_final[(rho_final!=0.0)] = np.array(rho_from_gas_mask)
    #EA_final[EA_final!=0.0] = EA_from_gas_mask
    #IE_final[IE_final!=0.0] = IE_from_gas_mask
    #Z_final[Z_final!=0.0] = Z_from_gas_mask
    #NH_final[NH_final!=0.0] = NH_from_gas_mask

    print np.sum(EA_final!=0.0)
    print np.sum(IE_final!=0.0)
    print np.sum(Z_final!=0.0)
    print np.sum(NH_final!=0.0)

    #okay I think we just for every redshift make a group,
    #then make a subgroup at each redshift that is
    #the star ids then all of the gas properties

    group = output_hdf5.create_group(str(round(redshift,3)))
    dset_i = group.create_dataset('ids',data=star_ids_sort)
    dset_rho = group.create_dataset('rho',data=rho_final)
    dset_EA = group.create_dataset('ElectronAbundance',data=EA_final)
    dset_IE = group.create_dataset('InternalEnergy',data=IE_final)
    dset_Z = group.create_dataset('heliummassfraction',data=Z_final)
    dset_NH = group.create_dataset('NeutralHydrogenAbundance',data=NH_final)

    assert np.sum(rho_final!=0.0)==np.sum(np.in1d(star_ids_sort,gas_ids_sort))
    #Dont use Electron abundance, because some values are supposed to be zero
    #assert np.sum(EA_final!=0.0)==np.sum(np.in1d(star_ids_sort,gas_ids_sort))
    assert np.sum(IE_final!=0.0)==np.sum(np.in1d(star_ids_sort,gas_ids_sort))
    assert np.sum(Z_final!=0.0)==np.sum(np.in1d(star_ids_sort,gas_ids_sort))
    assert np.sum(NH_final!=0.0)==np.sum(np.in1d(star_ids_sort,gas_ids_sort))

output_hdf5.close()
