import subprocess

from os.path import expanduser
from parallel_sync import wget
from netCDF4 import Dataset
import json, math, os
import posixpath
import urlparse
import tempfile
import datetime

class NetCDF2JSON(object):

    def __init__(self):
        super(NetCDF2JSON, self).__init__()

    def ifGrADS(self,filename):
        gradscheck_filename="/opt/galaxy/tools/faceit/gradscheck.gs"
        args=gradscheck_filename+" "+filename
        isGrADS=False
        p = subprocess.Popen(['grads', '-lbc', args ], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        if "[OK]" in out:
            return True
        return False

    def get(self, filename,url):

        try:
            rootgrp = Dataset(filename)
        except:
            return None

        isGrADS=False
        #isGrADS=self.ifGrADS(filename)

        if filename.startswith("http"):
            isOpenDAP=True
        else:
            isOpenDAP=False

        lon1=None
        lon2=None
        lat1=None
        lat2=None
        feature=None
        geo=False

        if geo is False:
            try:
                lon1=float(min(rootgrp.variables['lon']))
                lon2=float(max(rootgrp.variables['lon']))
                lat1=float(min(rootgrp.variables['lat']))
                lat2=float(max(rootgrp.variables['lat']))
                geo=True
            except:
                pass

        if geo is False:
            try:
                lon1=float(min(rootgrp.variables['X']))
                lon2=float(max(rootgrp.variables['X']))
                lat1=float(min(rootgrp.variables['Y']))
                lat2=float(max(rootgrp.variables['Y']))
                geo=True
            except:
                pass

        if geo is False:
            try:
                lon1=float(min(rootgrp.variables['longitude']))
                lon2=float(max(rootgrp.variables['longitude']))
                lat1=float(min(rootgrp.variables['latitude']))
                lat2=float(max(rootgrp.variables['latitude']))
                geo=True
            except:
                pass

        variables=[]
        for variable in rootgrp.variables.values():
            attributes=[]
            for attribute in variable.ncattrs():
                attributes.append({ "name": str(attribute), "value": str(variable.getncattr(attribute))} )

            dimensions=[]
            for dimension in variable.dimensions:
                dimensions.append(str(dimension))

            shapes=[]
            for shape in variable.shape:
                shapes.append(shape)

            variables.append({
                "name":str(variable.name),
                "dtype":str(variable.dtype),
                "ndim":variable.ndim,
                "shape":shapes,
                "dimensions":dimensions,
                "attributes":attributes
                })

        dimensions=[]
        for dimension in rootgrp.dimensions.values():
            dimensions.append({
                "name":str(dimension.name),
                "size":len(dimension),
                })

        attributes=[]
        for attribute in rootgrp.ncattrs():
            attributes.append({ "name": str(attribute), "value": str(rootgrp.getncattr(attribute))} )

        

        feature={
            "name":os.path.basename(filename),
            "opendap":isOpenDAP,
            "grads":isGrADS,
            "dimensions":dimensions,
            "variables":variables,
            "url": str(url),
            "date": str(datetime.datetime.utcnow()),
            "attributes": attributes
        }
        if geo is True:
            feature["loc"]={
                "type": "Polygon",
                 "coordinates": [[[lon1,lat1],[lon2,lat1],[lon2,lat2],[lon1,lat2],[lon1,lat1]]]
            }
        rootgrp.close()
        return feature

if __name__ == "__main__":
	netCDF2JSON=NetCDF2JSON()
        #response=Response("http://users.rcc.uchicago.edu/~davidkelly999/prism.2deg.tile/0021/clim_0021_0028.tile.nc4")
        filename="/home/ubuntu/clim_0021_0028.tile.nc4"
        uri="http://users.rcc.uchicago.edu/~davidkelly999/prism.2deg.tile/0021/clim_0021_0028.tile.nc4"
        item=netCDF2JSON.get(filename,uri)
	print str(item)
