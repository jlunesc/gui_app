import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSlot
import numpy as np
import pandas as pd
import warnings
from skimage import io
import tifffile

from generate_stack import ImageGenerator as jc_imGen
from get_z_positions import readZPositions as jc_zRead
from adjust_z import adjustZValues as jc_zAdj

class App(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'managing data frames from segmentation'
        self.left = 10
        self.top = 10
        self.width = 500
        self.height = 500

        self.pz = 1.33

        # positions for the buttons
        self.x1=10
        self.x2=350
        self.y1=15
        self.y_separation=25
        self.x3=90
        self.y2=120
        self.y_separation_2=30
        self.y3=250

        self.home()

    def home(self):

        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        self.label = QtWidgets.QLabel('1. Import files',self)
        self.label.move(self.x1,self.y1)

        # button to load the data frame
        self.buttonFunction('load df','must select a txt file',self.x2,self.y1+self.y_separation*1.-5,self.loadDataFrame)

        label_load_df = QtWidgets.QLabel('import your data frame from the segmentation (.txt)',self)
        label_load_df.move(self.x1,self.y1+self.y_separation*1.)

        # button to load the image
        self.buttonFunction('load image','must select a tif file',self.x2,self.y1+self.y_separation*2.-5,self.loadStack)

        label_load_tif = QtWidgets.QLabel('import your stack file (.tif)',self)
        label_load_tif.move(self.x1,self.y1+self.y_separation*2.)

        # button to load the folder to compute positions
        self.buttonFunction('load files','folder with .stks',self.x2,self.y1+self.y_separation*3.-5,self.loadStkFiles)

        label_load_tif = QtWidgets.QLabel('load folder with stks',self)
        label_load_tif.move(self.x1,self.y1+self.y_separation*3.)

        # appling filters
        label = QtWidgets.QLabel('2. Assign filters for the data frame',self)
        label.move(self.x1,self.y2)

        # volume
        self.textbox_volume = QtWidgets.QLineEdit(self)
        self.textbox_volume.move(self.x1,self.y2+self.y_separation_2*1.)
        self.textbox_volume.resize(50,20)

        self.buttonFunction('volume','apply volume filter',self.x3,self.y2+self.y_separation_2*1.-5,self.volumeThreshold)

        # ato
        self.textbox_ato = QtWidgets.QLineEdit(self)
        self.textbox_ato.move(self.x1,self.y2+self.y_separation_2*2.)
        self.textbox_ato.resize(50,20)

        self.buttonFunction('ato','apply ato filter',self.x3,self.y2+self.y_separation_2*2.-5,self.atoThreshold)

        # bool
        self.textbox_bool = QtWidgets.QLineEdit(self)
        self.textbox_bool.move(self.x1,self.y2+self.y_separation_2*3.)
        self.textbox_bool.resize(50,20)

        self.buttonFunction('bool','the cells excluded will be those with different boolean value to \nthat '
                                   'introduced (e.g., introduce 2 not to exclude any cell)',self.x3,self.y2+self.y_separation_2*3.-5,self.boolThreshold)

        label = QtWidgets.QLabel('3. Make different computations',self)
        label.move(self.x1,self.y3)

        # button for computing z positions
        self.buttonFunction('compute-z','make sure you upload before the file from which you \ncan compute the z '
                                        'positions at every time point',self.x2+40,self.y3+self.y_separation*1.-5,self.getZValues)

        # button for computing z positions
        self.buttonFunction('load-z','click this in case you already computed z-positions before '
                                     '',self.x2-40,self.y3+self.y_separation*1.-5,self.loadZPositions)


        label_get_z = QtWidgets.QLabel('compute the new z-positions (if you want)',self)
        label_get_z.move(self.x1,self.y3+self.y_separation*1.)

        # button for generating the new data frame
        self.buttonFunction('gen z-stack','make sure you have compute before the z-positions and that \nyou have '
                                          'uploaded the image .tif',self.x2, self.y3+self.y_separation*2.-5,self.generateZStack)

        label_gen_z_stack = QtWidgets.QLabel('generate z-stack frame with adjusted z values',self)
        label_gen_z_stack.move(self.x1,self.y3+self.y_separation*2.)

        # button for saving the dafa frame
        self.buttonFunction('save csv','csv file to be use in TrackMate, Mastodon, etc',self.x2,400,self.saveCsv)

        label_save_csv = QtWidgets.QLabel('save csv for tracking',self)
        label_save_csv.move(self.x1,405)

        # exit button
        self.buttonFunction('close','get the hell outta here!!',self.x2,435,self.close)

        self.show()


    def buttonFunction(self,message,tip_message,x,y,function):

        button = QtWidgets.QPushButton(message,self)
        button.setToolTip(tip_message)
        button.move(x,y)
        button.clicked.connect(function)


    @pyqtSlot()
    def generateZStack(self):

        if not hasattr(self,'stack'):

            print('-- you need to read the image first!')


        if not hasattr(self,'z_positions'):

            print('-- you need to compute z positions first!')


        if hasattr(self,'stack') and hasattr(self,'z_positions'):


            if not self.stack.shape[0] == len(self.z_positions['t'].unique()):

                print('stack and data frames dont have the same length... \nnumber of stacks: '
                        '{}\nnumber of time points: {}'.format(self.stack.shape[0],len(self.z_positions['t'].unique())))


            else:

                print('\n\t\tgenerating new stack... \n')

                n_stack = jc_imGen()
                n_stack.readImage(self.stack) # read image
                n_stack.readZPositions(self.z_positions) # read data frame with z-positions
                n_stack.generateNewStack()

                self.new_stack = n_stack.new_image

                n_stack.printImageMetadata()

                # tifffile.imsave(self.path_stack.split('.')[0]+'_resized.tif', self.new_stack,
                #                 metadata={'axes': 'TCZYX'})

                io.imsave(self.path_stack.split('.')[0]+'_resized.tif', np.array(self.new_stack))

                print('\n{} saved correctly!!'.format(self.path_stack.split('.')[0]+'_resized.tif'))


    @pyqtSlot()
    def loadStkFiles(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        files, _ = QtWidgets.QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "",
                                                "All Files (*);;Python Files (*.py)", options=options)
        self.stk_files=files

        print('there are {} files selected'.format(len(files)))


    @pyqtSlot()
    def volumeThreshold(self):

        self.thres_vol = float(self.textbox_volume.text())

        print('volume threshold is: {}'.format(self.thres_vol))


    @pyqtSlot()
    def atoThreshold(self):

        self.thres_ato = float(self.textbox_ato.text())

        print('ato threshold is: {}'.format(self.thres_ato))


    @pyqtSlot()
    def boolThreshold(self):

        self.value_bool = float(self.textbox_bool.text())

        print('bool threshold is: {}'.format(self.value_bool))


    @pyqtSlot()
    def loadStack(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"load stack", "",
                                                            "All Files (*);;Python Files (*.py)", options=options)

        if fileName.split('.')[-1] == 'tif':

            self.path_stack=fileName
            self.stack = io.imread(self.path_stack)

            print('{} loaded correctly!!'.format(self.path_stack))

        else:

            warnings.warn("the input file is not a tif file")


    @pyqtSlot()
    def loadDataFrame(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"load segmentation-DF", "",
                                                            "All Files (*);;Python Files (*.py)", options=options)

        if fileName.split('.')[-1] == 'txt':

            self.path_txt=fileName
            self.readDataFrame()
            self.path_df=fileName.split('.')[0]

            print('{} loaded correctly!!'.format(self.path_txt))


        else:

            warnings.warn("the input file is not a txt file")


    @pyqtSlot()
    def saveCsv(self):

        if not hasattr(self, 'df_txt'):

            print('-- you need to upload a data frame from segmentation at least!')


        else:

            self.df_export = self.df_txt

            #apply filters first
            if hasattr(self,'thres_vol'):

                self.df_export=self.df_txt[self.df_txt['volume']>=self.thres_vol]


            if hasattr(self,'thres_ato'):

                self.df_export=self.df_export[self.df_export['channel_2']>=self.thres_ato]


            if hasattr(self,'value_bool'):

                self.df_export = self.df_export[self.df_export['bool']!=self.value_bool]


            if hasattr(self,'z_positions'):

                self.df_export = jc_zAdj(self.df_export, self.z_positions)


            self.df_export.to_csv(self.path_df+'.csv')
            print('\n-- data frame for segmentation saved in:\n\n{}'.format(self.path_df+'.csv'))


    def readDataFrame(self):

        self.df_txt=pd.read_csv(self.path_txt, sep='\t',header=None)
        if len(self.df_txt.columns) == 8:
            self.df_txt.columns = ['time','x','y','z','volume','bool','channel_1','channel_2']
        elif len(self.df_txt.columns) == 9:
            self.df_txt.columns = ['time', 'x', 'y', 'z', 'volume', 'bool', 'channel_1', 'channel_2', 'channel_3']
        self.df_txt.reset_index(level=0, inplace=True)
        self.df_txt.drop(self.df_txt.columns[0], axis=1)


    def getZValues(self):

        if hasattr(self,'stk_files'):

            df = pd.DataFrame()
            df['z'], df['t'], df['z_offset'] = jc_zRead(self.stk_files)
            df = df.sort_values(by=['t'])

            self.z_positions = df

            # To save the data frame with z positions is necessary to have
            # uploaded first a txt data frame
            if hasattr(self, 'path_df'):

                self.z_positions.to_csv(self.path_df + '_zpositions.csv')


    def loadZPositions(self):

        options = QtWidgets.QFileDialog.Options()
        options |= QtWidgets.QFileDialog.DontUseNativeDialog
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self,"load z-positions", "",
                                                            "All Files (*);;Python Files (*.py)", options=options)

        if not '.csv' in fileName:

            print('no (or wrong) z positions were loaded')


        else:

            self.z_positions=pd.read_csv(fileName)

            print('\nthis is the file that you uploaded: \n\n{}'.format(fileName))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
