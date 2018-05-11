#!/usr/bin/env python

import os
import sys

import h5py

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *


class MainForm(QDialog):
    
    def __init__(self,parent=None):
        super(MainForm,self).__init__(parent)
        
        treeLabel = QLabel("Tree")
        self.treeWidget = QTreeWidget()
        self.treeWidget.setContextMenuPolicy(Qt.CustomContextMenu)
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

        
    def addBranches(self,parent="/"):
        ## Check the root for attributes
        if not self.rootPopulated:
            self.rootPopulated = True
            ancestor = QTreeWidgetItem(self.treeWidget,[os.path.basename(self.h5File)])
            self.treeItems[os.path.basename(self.h5File)] = ancestor
            self.addAttributes(self.h5,ancestor)
            
        for k in self.h5[parent].keys():
            name = k
            
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
    
    
    
