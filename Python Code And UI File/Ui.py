# -*- coding: utf-8 -*-
# coding=utf8
import sys
from PyQt5 import  QtGui,QtCore,QtWidgets
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import  QApplication,QMainWindow,QPushButton,QListWidget,QMessageBox,QCheckBox,QComboBox,QLineEdit , QPlainTextEdit ,QFileDialog
from PyQt5.uic import loadUi
import imutils
import Panorama as pn
import cv2

class Window(QMainWindow):

    def __init__(self):
        super(Window, self).__init__()
        loadUi('interface.ui',self) ## load file .ui
        self.setWindowTitle("Panorama") ## set the tile
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.image_list_filename = []

        #   Slots :
        self.bt_image.clicked.connect(self.on_bt_image_clicked)
        self.bt_panorama.clicked.connect(self.on_bt_panorama_clicked)
        self.bt_view.clicked.connect(self.on_bt_view_clicked)
        self.bt_reset.clicked.connect(self.on_bt_reset_clicked)

    @pyqtSlot()

    def on_bt_image_clicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        files, _ = QFileDialog.getOpenFileNames(self, "QFileDialog.getOpenFileNames()", "Choose Files",
                                                "All Files (*)", options=options)
        if len(files)!=0:
            self.list_image.addItems(files)
        for i in range(len(files)):
            self.image_list_filename.append(files[i])

        print(self.image_list_filename)



    def on_bt_panorama_clicked(self):

       imgs = []

       for i in self.image_list_filename:
           temp = cv2.imread(i)
           temp = imutils.resize(temp, width=400,height=400)
           imgs.append(temp)

       if len(imgs)!=0:
           result = pn.stitch(imgs)
           result = imutils.resize(result, width=800, height=800)
           cv2.imshow("Panorama",result)


       else:
           QMessageBox.about(self, 'Panorama', "Không tìm thấy file ảnh!")

    def on_bt_view_clicked(self):

        for i in self.image_list_filename:
            img = cv2.imread(i)
            img = imutils.resize(img,width=400,height=400)
            cv2.imshow(i,img)

    def on_bt_reset_clicked(self):
        self.list_image.clear()
        self.image_list_filename = []


app = QApplication(sys.argv)
GUI = Window()
GUI.show()

sys.exit(app.exec_())