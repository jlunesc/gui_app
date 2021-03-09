import numpy as np
import bioformats, javabridge


def readZPositions(stk_files):

    # the only entry parameter for this function is a list with
    # the stk files

    print('\n\t\treading z-values... ')
    javabridge.start_vm(class_path=bioformats.JARS)

    zs = [] # array with z-positions
    ts = [] # array with time point (got from data files)

    print('starting loop...')

    for file_path in stk_files:

        print('reading file: {}'.format(file_path))

        md = bioformats.get_omexml_metadata(file_path)
        ome = bioformats.OMEXML(md)

        # create an instance of an image to read z-position
        zp = ome.image().Pixels.Plane().get_PositionZ()


        time = int(file_path[:-4].split('t')[- 1])

        zs.append(zp)
        ts.append(time)

    z_offsets = np.array([item - min(np.array(zs)) for item in zs])

    javabridge.kill_vm()

    return np.array(zs), np.array(ts), z_offsets
