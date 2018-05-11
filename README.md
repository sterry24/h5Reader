# h5Reader
Small python tools for reading and viewing data in an HDF5 data format.<br>


#### readHDF5.py
This program will lazily read in all data in an HDF5 file.<br>
Groups and Datasets are accessible through dot notation.<br>
Attributes can be printed as key,value pairs with .attributes() or .showAttributes()<br>
Attributes are also accessible through dot notation (.attributes.KEYNAME will return VALUE for KEYNAME)

##### Functions
GROUP OBJECTS:<br>
   - .showAttributes(): prints out all attributes attached to the group object
   
DATASET OBJECTS:<br>
   - .shape(): prints the shape of the dataset object<br>
   - .size(): prints the size of the dataset object<br>
   - .getType(): prints the data type of the data in the dataset<br>
   - .getDType(): prints the dtype of the data in the dataset (for numpy arrays)<br>
   - .setData(): this function will access the data in the HDF5 file and store it to the DATASET.data attribute.<br>
                 the DATASET.data attribute will return NONE until setData() is called
   - .delData():  this function will set the DATASET.data attribute to None<br>
   - .showAttributes(): prints out all the attributes attached to the dataset object<br>
   - .showAsDataFrame(): this function will attempt to show the dataset object as a pandas DataFrame object<br>
                  If not possible, will print an error message<br>
   - .saveAsDataFrame():  this function will attempt to save the dataset object as a pandas DataFrame to the DATASET.data attribute<br>
                  If not possible, will print an error message<br>

ATTRIBUTE OBJECTS:<br>
   - .showAttributes(): prints out all the attributes<br>
   
Dump the contents of the HDF5 file to the screen in a tree-like format with .dump()
     - This will dump the entire content of the file
     - Can provide a specific GROUP OBJECT to dump only on that GROUP (.dump(.GROUPNAME))<br>
     
     EXAMPLE: h5 = readHDF5File.READ_H5_FILE(filename)<br>
              h5.dump() ## dumps the contents of the entire file to screen<br>
              h5.dump(h5.GROUPNAME) ## Dumps the contents of the GROUPNAME to the screen<br>
