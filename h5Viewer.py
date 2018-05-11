# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

__author__  = "Stephen Terry"
__date__    = "07/19/2017"
__version__ = " Version 0.1"


import os
import sys

import h5py

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import pdb
class MainForm(QDialog):
    
    def __init__(self,parent=None):
        super(MainForm,self).__init__(parent)
        
        treeLabel = QLabel("Tree")
        self.treeWidget = QTreeWidget()
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.treeWidget.customContextMenuRequested.connect(self.vHeaderMenu)
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels(["Groups"])
        
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.treeWidget)
        self.setLayout(self.layout)
        self.setWindowTitle("H5Viewer")
        #self.setH5File()
        self.h5File = r''
        self.populateTree()
        
    def vHeaderMenu(self,position):
        
        indexes = self.treeWidget.selectedIndexes()
        
        menu = QMenu()
        submenu = QMenu("Plot")
        pltImgAction = QAction("Plot Image",self)
        pltXYAction = QAction("Plot X v Y",self)
        pltImgAction.triggered.connect(lambda: self.doNothing(val = indexes))
        pltXYAction.triggered.connect(lambda: self.doNothing(val = indexes))
        submenu.addAction(pltImgAction)
        submenu.addAction(pltXYAction)
        menu.addMenu(submenu)
        menu.exec_(self.treeWidget.viewport().mapToGlobal(position))   
        
    def doNothing(self,val = None):
        
        print("From Context menu, Index is %s" % val)
        print(val[0].data(role = Qt.DisplayRole))
        print(val[0].parent().data(role = Qt.DisplayRole))
        self.path = val[0].data(role = Qt.DisplayRole)
        while val[0].parent().data(role = Qt.DisplayRole) is not None:
            self.path = '/'+val[0].parent().data(role = Qt.DisplayRole)+'/'+self.path
            self.doNothing(val = [val[0].parent()])
            
        print(self.path)
        
    def setH5File(self,f=None):
        
        if ((f is not None) and (os.path.isfile(f))):
            self.h5File=f
        
    def populateTree(self):
        
        self.treeWidget.clear()
        self.treeWidget.setColumnCount(1)
        self.treeWidget.setHeaderLabels(["Groups"])
        self.treeWidget.setItemsExpandable(True)
       
        self.h5 = h5py.File(self.h5File,'r')
        self.treeItems = {}
        self.rootPopulated = False
        self.addBranches()
        #print "File load complete"
        
    def addBranches(self,parent="/"):
        #print "Adding branches for %s" % parent
        ## Check the root for attributes
        if not self.rootPopulated:
            self.rootPopulated = True
            ancestor = QTreeWidgetItem(self.treeWidget,[os.path.basename(self.h5File)])
            self.treeItems[os.path.basename(self.h5File)] = ancestor
            self.addAttributes(self.h5,ancestor)
            
        for k in self.h5[parent].keys():
            name = k
            
            #ancestor = self.treeItems.get(parent.split('/')[-1])
            ancestor = self.treeItems.get(parent[1:])
            if ancestor is None:
                ancestor = QTreeWidgetItem(self.treeWidget,[name])
                self.treeItems[name] = ancestor
            else:
                kitem = QTreeWidgetItem(ancestor,[name])
                self.treeItems[parent[1:]+'/'+name] = kitem
                ancestor = kitem
                
            item = self.h5[parent+'/'+k]
            ## is the item a group
            if is_group(item):
                ## Check for attributes
                self.addAttributes(item,ancestor)
                ##if it is a group, check for keys again
                self.addBranches(parent=item.name)
            ## is the item a dataset
            if is_dataset(item):
                self.addAttributes(item,ancestor)
                
    def addAttributes(self,item,ancestor):
        if hasAttrs(item):
            attrItem = QTreeWidgetItem(ancestor,['Attributes'])
            for kk in item.attrs.keys():
                kitem = QTreeWidgetItem(attrItem,[kk])
                #pdb.set_trace()
                self.treeItems[item.name[1:]+'/'+kk] = kitem
                
def hasAttrs(h):
    if h.attrs.keys() != []:
        return True
    else:
        return False
        
def is_group(h):
    return isinstance(h,h5py.Group)

def is_dataset(h):
    return isinstance(h,h5py.Dataset)
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = MainForm()
    form.show()
    app.exec_()
    
    
    
