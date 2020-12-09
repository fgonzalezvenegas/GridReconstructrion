# GridReconstructrion
Grid reconstruction from GIS data

Requirements:
pandas
numpy
networkx
pandapower



How to use:
1- Reconstructing grid from GIS:
 (1) Reconstructing graphs
  You should download Enedis GIS data from https://www.enedis.fr/cartographie-des-reseaux-denedis
  Use tools to select the area of interest and download Substations, MV Overhead and Underground lines and LV substations
  
  Functions from graph_reconstruction.py file allows to read, format and reconstruct the graph of Nodes and Lines.
  
 *Note: sometimes the files downloaded from enedis site appear to be corrupted and are not well read by python. 
    Open and re-save them in Excel to solve this issue
  
 (2) 'Untangling' the grid and assigning tech data:
  Run processing_grid.py. This file requires some data:
  - Annual load per IRIS
  - Load profiles
  - Technical data
  - IRIS contours (polygons)
  
  In first instance, this script will create a connected graph of Nodes and Lines based on Enedis GIS data (from (1))
  It will save files of Nodes, MV lines, and Load Nodes (i.e. LV substations)
  Alternatively, you can load a pre-processed graph data
  
  Once everything is loaded, it'll open a python screen that shows your graph data.
    Click on lines to open/close connectors and untangle the grid. When you click on lines, you get a message of distances to each substation in the console.
    Click on 'Recompute feeders' to update the view on independent feeders
    
  Once you have all untangled:
    Click on 'Reduce data and compute tech data'. This will reduce the data to only that connected to the main Substation and define the type of conductor for each line section based on expected max load.
    
  Save current data
    
  (3) Creating PandaPower grid
  Run creating_ppgrid.py
  Use data from (2) to create a PandaPower grid, add PV generators and run a timeseries.
  
  *Note: I had issues with PandaPower time series module and I created my own (see functions in ppgrid.py file).
    
