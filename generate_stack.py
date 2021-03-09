# here I define a class for stacks with methods
# that allow us to generate stacks using 'real data' and black
# slices
import numpy as np


class ImageGenerator(object):

    def __init__(self):

        self.pz = 1.31 #todo avoid hard-coding this!

        return None


    def readImage(self,image):

        # this method first reads the image and then gives the dimensions
        # for the array stack structure in the tiff files: T,Z,C,Y,X
        self.image = image

        self.len_time = image.shape[0]
        self.len_z = image.shape[1]
        self.len_channel = image.shape[2]
        self.len_y = image.shape[3]
        self.len_x = image.shape[4]

        # having the dimensions I can already define the black
        # slide, so I do it:
        self.black_slide = np.zeros((self.len_channel, self.len_y, self.len_x), np.uint16)


    def readZPositions(self, data_frame_zPositions):

        self.intervals = data_frame_zPositions
        self.increments = np.array([int(round(item / self.pz)) for item in data_frame_zPositions['z_offset']])


    def generateNewStack(self):

        # number of slides in the new stack
        self.n_slides = \
            range(np.max(self.increments + self.len_z) - np.min(self.increments))

        hs = []
        for tp in range(self.len_time):

            # notice that a and b are the first and the last point in the interval
            # with slides with real data
            a = int(self.increments[tp])
            b = int(a + self.len_z)

            z_slide = 0

            new_stack = []

            for z in self.n_slides:

                if z not in range(a, b):
                    new_slide = self.black_slide

                else:
                    new_slide = self.image[tp][z_slide]
                    z_slide += 1 # increase the index in the z-stack of the real data

                new_stack.append(new_slide)

            hs.append(new_stack)

            print('generating {} frame of stack'.format(tp))

        self.new_image = np.array(hs)


    def printImageMetadata(self):

        print('Image features: \nnumber of channels: {} \tnumber of frames (time): {} \tz-stack size: {} '
              '\n\n'.format(self.new_image.shape[2], self.new_image.shape[0], self.new_image.shape[1]))
