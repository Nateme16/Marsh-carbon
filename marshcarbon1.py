# -*- coding: utf-8 -*-
"""
Blue Carbon Tool 1

Created on Thu Mar 24 14:18:36 2016

@author: Nate Merrill
"""
# This tool takes the view extent, clips the changes for upland conversion 
#step one is to go open MarshMigration.mxd and zoom into extent you want, save and close!
#then run this

import sys, os
import arcpy
from arcpy import env
import numpy as np

arcpy.env.workspace = r"L:\Public\Marsh Migration Values\Tooltest"
arcpy.env.overwriteOutput = True

landuse= r"L:\Public\Marsh Migration Values\RI\rilu0304n\rilu0304.shp"

slamm5= r"L:\Public\Marsh Migration Values\RI\SLAMM15\SLAMM_RI_5ft_SLR.shp"

#pre-split Slamm5 results by attribute in Arcmap to new, pers or loss, learn to code?
new= r"L:\Public\Marsh Migration Values\RI\SLAMM15\slamm5_RI_new.shp"
pers= r"L:\Public\Marsh Migration Values\RI\SLAMM15\slamm5_RI_pers.shp"
loss= r"L:\Public\Marsh Migration Values\RI\SLAMM15\slamm5_RI_loss.shp"

wetlandsinv=r"L:\Public\Marsh Migration Values\RI\wetlands93\wetlands93.shp"

#gets spatial extent from map view area
mxd = arcpy.mapping.MapDocument(r"L:\Public\Marsh Migration Values\MarshMigration.mxd")
df = arcpy.mapping.ListDataFrames(mxd)[0]
dfAsFeature = arcpy.Polygon(arcpy.Array([df.extent.lowerLeft,df.extent.lowerRight,df.extent.upperRight,df.extent.upperLeft]), df.spatialReference)

#clip all input layers by extent
landclip=arcpy.Clip_analysis(landuse,dfAsFeature,"landuseclip")
newclip = arcpy.Clip_analysis(new, dfAsFeature, "newclip")
persclip = arcpy.Clip_analysis(pers, dfAsFeature, "persclip")
lossclip = arcpy.Clip_analysis(loss, dfAsFeature, "loss")
wetclip = arcpy.Clip_analysis(wetlandsinv, dfAsFeature, "wetclip")

#Clip wetlands inventory layer for persistent and lost wetland types by SLAMM
pers_wet=arcpy.Clip_analysis(wetclip, persclip, "pers_wet")
loss_wet=arcpy.Clip_analysis(wetclip, lossclip, "loss_wet")

#clip out wetlands inventory area from LU layer 
arcpy.Erase_analysis(landclip,wetclip,"land_lesswet")

#clip out new wetland area replacing wetlandinv and lU classes
LUandwet=arcpy.Merge_management([landclip,wetclip],"LUandwet")
new_wetreplace= arcpy.Clip_analysis("LUandwet.shp",new,"new_wetreplace") #dont know why this needed .shp

#re-calculate areas in square meters and adds it as new field
arcpy.AddField_management(loss_wet,"Shape_area", "DOUBLE")
arcpy.AddField_management(pers_wet,"Shape_area", "DOUBLE")
arcpy.AddField_management(new_wetreplace,"Shape_area", "DOUBLE")
arcpy.AddField_management(newclip,"Shape_area", "DOUBLE")

exp="!SHAPE.AREA@SQUAREMETERS!"
arcpy.CalculateField_management(loss_wet, "Shape_area", exp, "PYTHON_9.3")
arcpy.CalculateField_management(pers_wet, "Shape_area", exp, "PYTHON_9.3")
arcpy.CalculateField_management(new_wetreplace, "Shape_area", exp, "PYTHON_9.3")
arcpy.CalculateField_management(newclip, "Shape_area", exp, "PYTHON_9.3")


#Get the areas from the layers

loss_area = arcpy.da.TableToNumPyArray(loss_wet,("DESCRIPTIO","Shape_area"))
uq=np.unique(loss_area['DESCRIPTIO'])
area=np.zeros([len(uq),1])
i=0
for x in np.nditer(uq):
     c=np.where(loss_area['DESCRIPTIO']==str(x))
     area[i,0]=(sum(loss_area['Shape_area'][c]))
     i=i+1
lost_area_bytype=np.column_stack((uq,area))


pers_area = arcpy.da.TableToNumPyArray(pers_wet,("DESCRIPTIO","Shape_area"))
uq=np.unique(pers_area['DESCRIPTIO'])
area=np.zeros([len(uq),1])
i=0
for x in np.nditer(uq):
     c=np.where(pers_area['DESCRIPTIO']==str(x))
     area[i,0]=(sum(pers_area['Shape_area'][c]))
     i=i+1
pers_area_bytype=np.column_stack((uq,area))

new_wetreplace_area = arcpy.da.TableToNumPyArray(new_wetreplace,("DESCRIPTIO","Shape_area"))
uq=np.unique(new_wetreplace_area['DESCRIPTIO'])
area=np.zeros([len(uq),1])
i=0
for x in np.nditer(uq):
     c=np.where(new_wetreplace_area['DESCRIPTIO']==str(x))
     area[i,0]=(sum(new_wetreplace_area['Shape_area'][c]))
     i=i+1
new_wetreplace_area_bytype=np.column_stack((uq,area))

newclip_area = arcpy.da.TableToNumPyArray(newclip,("final_clas","Shape_area")) #this one does not have DESCRIPTIO field, only final_clas
uq=np.unique(newclip_area['final_clas'])
area=np.zeros([len(uq),1])
i=0
for x in np.nditer(uq):
     c=np.where(newclip_area['final_clas']==str(x))
     area[i,0]=(sum(newclip_area['Shape_area'][c]))
     i=i+1
newclip_area_bytype=np.column_stack((uq,area))




