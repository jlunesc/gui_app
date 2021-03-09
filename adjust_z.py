import numpy as np

def adjustZValues(segmentation_dataFrame, z_positions_dataFrame):

    print('\n\t\tcomputing z positions... ')

    # FIRST PART: obtain the 'true z positions' from the slides collection

    # remember that z_norm = z_real_position - min(all_real_z_positions)
    z_offset = np.array(z_positions_dataFrame['z_offset'])


    # SECOND PART: adjust the z values

    # here I count the number of positions in each time point. Notice that I don't
    # care that in the segmentation data frame the initial time is t=o while in
    # the z-positions data frame the initial time is 1
    counts = np.array(segmentation_dataFrame['z'].groupby(segmentation_dataFrame['time']).count())

    # this is the vector that allows to adjust the offset
    z_increments = sum([[item] * times for (item, times) in zip(z_offset, counts)], [])

    z_adjusted_values = np.array(z_increments) + np.array(segmentation_dataFrame['z'])

    # array with the adjusted values, i.e., original z value + offset
    segmentation_dataFrame['z_adjusted'] = z_adjusted_values

    segmentation_dataFrame.rename(columns={'z': 'old_z'}, inplace=True)
    segmentation_dataFrame.rename(columns={'z_adjusted': 'z'}, inplace=True)

    return segmentation_dataFrame