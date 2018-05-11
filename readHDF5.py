#!/usr/bin/env python

import os
import sys
import numpy
import keyword
import h5py
import pandas
import pdb

def is_group(h):
    """This function checks whether the item under test is an H5 Group object
    
       PARAMETERS:  h: object
                       object to be tested
                       
       RETURNS:     boolean"""
       
    return isinstance(h,h5py.Group)
   
def is_dataset(h):
    """This function checks whether the item under test is an H5 Dataset object
    
       PARAMETERS:  h: object
                       object to be tested
                       
       RETURNS:     boolean"""
       
    return isinstance(h,h5py.Dataset)
   
def hasAttrs(h):
    """This function checks whether the item under test contains any attributes
    
        PARAMETERS:   h: object
                         object to be tested (H5 Group or Dataset)
                         
        RETURNS:      boolean"""

        
    if h.attrs.keys() != []:
        return True
    else:
        return False
    
class ATTRIB_OBJECT(object):
    """The ATTRIB_OBJECT class defines the methods that can be performed on the 
       attributes found in H5 Groups and Datasets"""
       
    def __call__(self):
        """This function makes the ATTRIB_OBJECT callable.  When the object is called,
           the attribute keys and values will be printed to the screen."""
           
        self.showAttributes()
        
    def setAttributes(self,item):
        """This function sets the attributes of an H5 Group or Dataset object to the 
           ATTRIB_OBJECT of the calling object.  The attributes are set in a manner so
           that they are available through dot notation
           
           PARAMETERS:  item: H5.Group or H5.Dataset
           
           RETURNS:      NONE"""
           
        for k,v in item.attrs.items():
            name = self.checkName(k)
            if type(v) == numpy.bytes_:
                setattr(self,name,v.astype(str))
            else:
                setattr(self,name,v)
            
    def showAttributes(self):
        
        """This function prints the attribute keys and values to the screen"""
        
        for k in self.__dict__.keys():
            print(k,self.__dict__[k])
            
    def isEmpty(self):
        
        if len(self.__dict__.keys()) == 0:
            return True
        else:
            return False
            
    def checkName(self,name):
        """This function check for valid attribute names.  Names are compared
           against Python keywords and to make sure they do not begin with a 
           number.  The default is to prepend an underscore (_) to names that
           violate python naming conventions.
           
           PARAMETERS:  name: string
                           the string to be tested
                           
           RETURNS:   name: string
                          the corrected name"""
                          
        if name in keyword.kwlist:
            name = "_" + name
            
        if name[0].isdigit():
            name = "_" + name
            
        name = name.replace(' ', '_')
        name = name.replace('-', '_')
        name = name.replace('#', '_')
        name = name.replace('.', '_')
            
        return name
            
class GROUP_OBJECT(object):
    """The GROUP_OBJECT class defines the methods that can be performed on the
       H5 Group objects found in an H5 file."""
       
    def __init__(self,parent="/"):
        self.parent = parent
        self.attributes = ATTRIB_OBJECT()
        
    def showAttributes(self):
        
        self.attributes()
        
class DATASET_OBJECT(object):
    """The DATASET_OBJECT class defines the methods that can be performed on the 
       H5 Dataset objects found in an H5 file."""
       
    def __init__(self,h5,parent="/"):
        self._h5 = h5
        self.parent = parent
        self.attributes = ATTRIB_OBJECT()
        self.data = None
        self.path = None
        
    def shape(self):
        
        return self._h5[self.path].shape
    
    def size(self):
        
        return self._h5[self.path].size
    
    def getType(self):
        
        if self.data is None:
            return type(self._h5[self.path].value)
        else:
            return type(self.data)
        
    def getDType(self):
        
        if self.data is None:
            return self._h5[self.path].value.dtype
        else:
            return self.data.dtype
    
    def setData(self):
        
        if self.data is None:
            self.data = self._h5[self.path].value
            
    def delData(self):
        
        self.data = None
        
    def showAttributes(self):
        
        self.attributes()
        
    def showAsDataFrame(self):
        """This functino will show the dataset object as a pandas dataframe."""
        
        y = getattr(self,"data",None)
        if y is not None:
            try:
                df = pandas.DataFrame(self.data)
                print(df)
            except:
                print("Error: Cannot show dataset as a DataFrame object")
        else:
            print("Dataset object has no data.  Try .setData()")
                
    def setAsDataFrame(self):
        """This function will set the dataset object as a pandas dataframe."""
        
        y = getattr(self,"data",None)
        if y is not None:
            try:
                df = pandas.DataFrame(self.data)
                setattr(self,"data",df)
            except:
                print("Error: Cannot set dataset as DataFrame object")
        else:
            print("Dataset object has no data. Try .setData()")
            
class READ_H5_FILE(object):
    
    def __init__(self,filename):
        
        ## Verify the file exists
        if not os.path.isfile(filename):
            sys.stdout.write("ERROR: %s does not exist!\n" % filename)
            sys.exit(1)
            
        self.filename = filename
        self.h5 = h5py.File(self.filename,'r')
        self.dataItems = {}
        
        self.assignRoot()
        self.findChildren()
        self.buildStruct()
        
        #pdb.set_trace()
        
    def checkName(self,name):
        """This function check for valid attribute names.  Names are compared
           against Python keywords and to make sure they do not begin with a 
           number.  The default is to prepend an underscore (_) to names that
           violate python naming conventions.
           
           PARAMETERS:  name: string
                           the string to be tested
                           
           RETURNS:   name: string
                          the corrected name"""
                          
        if len(name) != 0:
            if name in keyword.kwlist:
                name = "_" + name
            
            if name[0].isdigit():
                name = "_" + name
            
        name = name.replace(' ', '_')
        name = name.replace('-', '_')
        name = name.replace('#', '_')
        name = name.replace('.', '_')
            
        return name
    
    def assignRoot(self):
        """This function checks the root H5 Group for attributes.  If found, the
           atrributes are set to the root attribute of the READ_H5_FILE object."""
           
        self.root = GROUP_OBJECT()
        if hasAttrs(self.h5):
            self.root.attributes.setAttributes(self.h5)
            
    def findChildren(self,parent="/"):
        """This function loops through the keys of an H5 Group.  The function is
           called recursively if H5 Groups are found to be children of H5 Groups.
           If the key is found to be ab H5 Group or Dataset object, it is checked
           for attributes and if found the attributes are assigned to the object.
           Keys and values are stored internally in the dataItems dict so that 
           they can be assigned as attributes later.
           
           PARAMETERS:    parent: string
                              The Group of the H5 file to be checked for children"""
                              
        for k in self.h5[parent].keys():
            #pdb.set_trace()
            name = self.checkName(k)
            item = self.h5[parent+'/'+k]
            if is_group(item):
                temp = GROUP_OBJECT(parent=item.parent.name[1:])
                if hasAttrs(item):
                    temp.attributes.setAttributes(item)
                    
                self.dataItems[name] = temp
                self.findChildren(parent=item.name)

                if self.checkName(item.parent.name[1:]) in self.dataItems.keys():  
                    y = getattr(self.dataItems[self.checkName(item.parent.name[1:])],name,None)
                    if y is not None:
                        print("WARNING: Attribute %s already exists!  Modifying name...\n" % name)
                        self.findAvailableName(item,name,temp)
                    else:
                        setattr(self.dataItems[self.checkName(item.parent.name[1:])],name,temp)
                        self.dataItems.pop(name)
                        
            if is_dataset(item):
                temp = DATASET_OBJECT(self.h5,parent=item.parent.name[1:])
                #pdb.set_trace()
                if hasAttrs(item):
                    temp.attributes.setAttributes(item)
                ## Need to modify this for lazy reading
                temp.path = item.name
                
                if self.checkName(item.parent.name[1:]) in self.dataItems.keys():
                    setattr(self.dataItems[self.checkName(item.parent.name[1:])],name,temp)
                elif self.checkName(item.parent.name[1:].split('/')[-1]) in self.dataItems.keys():
                    setattr(self.dataItems[self.checkName(item.parent.name[1:].split('/')[-1])],name,temp)
                else:
                    self.dataItems[name] = temp
                    
    def findAvailableName(self,item,name,temp):
        """This function modifies the name of an attribute to guarantee that names
           are unique within an H5 Group object.
           
           PARAMETERS:    item: H5 Group Object
                               the H5 Group object that has a conflicting name
                               
           RETURNS:       NONE"""
           
        avail = False
        counter = 0
        
        while not avail:
            counter += 1
            newName = name + "_" + str(counter).zfill(2)
            y = getattr(self.dataItems[item.parent.name[1:]],newName,None)
            if y is None:
                avail = True
                setattr(self.dataItems[item.parent.name[1:]],newName,temp)
                print("Name %s modified to %s\n" % (name,newName))
                self.dataItems.pop(item.name[1:])
                
    def buildStruct(self):
        """This function assigns the objects in the dataItems dict to the 
           READ_H5_FILE objectas attributes so that they are available through
           dot notation."""
           
        for k in self.dataItems.keys():
            setattr(self,k,self.dataItems[k])
            
    def dump(self,item=None,level=0):
        """This function will print the READ_H5_FILE Object attributes to the
           screen in a tree format.
           
           PARAMETERS:   item: object
                           the object to recursively search for attributes
                           
           RETURNS:      NONE"""
           
        if item is None:
            item = self
        for attr in dir(item):
            val = getattr(item,attr)
            if isinstance(val,GROUP_OBJECT):
                if level == 0:
                    print(attr + "(GROUP Object)")
                else:
                    print('|' + level*'-',attr + "(GROUP Object)")
                self.dump(item=val,level = level+1)
            if isinstance(val,DATASET_OBJECT):
                if level == 0:
                    print(attr + "(DATASET Object), DataType: " +
                          str(val.getType())[str(val.getDType()).find("'")+1:-2])
                else:
                    print(level*''+'|'+level*'-',attr + "(DATASET Object), DataType: " +
                          str(val.getType())[str(val.getDType()).find("'")+1:-2])
                self.dump(item=val,level = level+1)
            if isinstance(val,ATTRIB_OBJECT):
                if not val.isEmpty():
                    print(level*' '+'|'+level*'-',attr + "(ATTRIB object)")
                
            