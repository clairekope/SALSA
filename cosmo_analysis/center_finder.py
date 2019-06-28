import yt
import numpy as np
from sys import argv
from pathlib import Path

#
#Find the center and orientation of galaxy
#return center coordinates and normal vector
#

def find_center(ds_fname, tracking_dir=None, save_data=True, max_field=None):
    """
    Use to retrieve the center of galaxy

    Parameters:
        ds_fname : string: path to dataset containing galaxy
        tracking_dir : string: path to directory contianing tracking files
                    if set to None, defaults to ds_path/../../track_files
        save_data : bool : write data to file? defaults to True
        max_field : string : field name. finds maximum of that field and sets
                    that to be the center. If None, will try to retrieve the center
                    from files in track_files directory

    Returns:
        center : yt array : the center of galaxy in units of code_length
        normal_vector : yt array : vector pointing along the axis of rotation
                        of the galaxy. (units are dimensionless)
    """
    ds = yt.load(ds_fname)

    if max_field is not None:
        #let max field be center of gal
        v, center = ds.find_max(max_field)
        n_vec = find_normal_vector(ds, center)
    else:
        #get directory where tracker files are kept
        sfname = ds_fname.split('/')
        if tracking_dir is None:
            tracking_dir = '/'.join(sfname[:-2]) + '/track_files'

        try:
            #check if kept center and normal_vector in center_normal_track.dat
            center_norm_file = tracking_dir + '/center_normal_track.dat'

            center, n_vec = search_center_norm(center_norm_file, sfname[-1])

            #check if center was found
            if center is None:
                raise RuntimeError("could not find {} in {}" \
                                        .format(sfname[-1], center_norm_file))
            else:
                center = ds.arr(center, 'code_length')
                n_vec = ds.arr(n_vec, 'dimensionless')
        #catch if file or entry not found
        except (FileNotFoundError, RuntimeError):
            #check for center in center_track file
            try:
                #return center of track with nearest redshift to dataset's
                center_file = tracking_dir + '/center_track.dat'
                f = np.loadtxt(center_file, skiprows=2, usecols=(0, 1, 2, 3))
                indx = np.abs(f[:, 0] - ds.current_redshift).argmin()
                center = ds.arr(f[indx, 1:], 'code_length')

                #compute normal vec from center
                n_vec = find_normal_vector(ds, center)
                
                if save_data:
                    #write center and norm to file
                    w = open(center_norm_file, 'a')
                    write_str = "{:s} {:f} ".format(sfname[-1], ds.current_redshift)
                    write_str += ' '.join(str(x) for x in center.value) + ' '
                    write_str += ' '.join(str(x) for x in n_vec.value)

                    w.write(write_str + '\n')
                    w.close()

            except OSError:
                raise RuntimeError("Need {} to exist, otherwise set max_field to define center"\
                                        .format(tracking_dir + '/center_track.dat'))

    return center, n_vec

def search_center_norm(file, ds_name):
    """
    Tries to find the center and normal vector from the file

    Parameters:
        file : string: path to file with center and normal information
                formatted as ds_name redshift center(x, y, z) n_vec(x, y, z)
        ds_name : string: name of the dataset i.e. RD0036, DD0075

    Returns:
        center : list/array floats: coordinates to center of galaxy
        n_vec : list/array floats: vector pointing along axis of rotation

        NOTE: Both return NoneType if entry not found in file
    """
    center = None
    n_vec = None

    #read through file
    f = open(file, 'r')
    for line in f:
        sline = line.split()
        #check line is not empty
        if len(sline) ==0:
            continue

        #check dataset name. return center and n_vector
        if ds_name == sline[0]:
            #convert to floats then stop reading file
            center = [ float(val) for val in sline[2:5] ]
            n_vec = [ float(val) for val in sline[5:8] ]
            break

    f.close()
    return center, n_vec

def find_normal_vector(ds, center):
    """
    Finds normal vector given dataset and center of galaxy

    Parameters:
        ds : yt loaded dataset
        center : array: coordinates to center of galaxy in cod_lenght units
    Returns:
        normal_vector : yt array: dimensionless normal vector pointing in the
                        direction of the axis of rotation of given center
    """

    #create sphere inside disk of galaxy
    sph_gal = ds.sphere(center, (20, 'kpc'))

    #compute the bulk velocity
    bulk_velocity = sph_gal.quantities.bulk_velocity(use_particles=False)
    sph_gal.set_field_parameter(("bulk_velocity"), bulk_velocity)

    #compute angular momentum vector normalize it
    axis_rot = sph_gal.quantities.angular_momentum_vector()
    normal_vector = axis_rot/(np.linalg.norm(axis_rot) * axis_rot.unit_array)

    return normal_vector
if __name__ == '__main__':
    ds_filename = argv[1]
    c, n = find_center(ds_filename)

    print("x, y, z")
    print(f"{c[0]}, {c[1]}, {c[2]}")
    print(f"{n[0]}, {n[1]}, {n[2]}")
