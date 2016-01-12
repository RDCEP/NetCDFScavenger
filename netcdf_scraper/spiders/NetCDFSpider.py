import subprocess

from os.path import expanduser
from parallel_sync import wget
from netCDF4 import Dataset
import json, math, os
import posixpath
import urlparse
import tempfile
import datetime

from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, Response
from netcdf_scraper.items import NetCDFScraperItem

from pymongo import MongoClient
from pymongo.errors import PyMongoError

import ConfigParser

class NetCDFSpider(CrawlSpider):
    name = 'netcdf'
    allowed_domains = ['.edu','.gov','opendap.org']
    start_urls = [
        'http://www.unidata.ucar.edu/software/netcdf/examples/files.html',
        'http://docs.opendap.org/index.php/Dataset_List',
        'http://gcmd.gsfc.nasa.gov/KeywordSearch/Home.do?Portal=dods',
        'http://users.rcc.uchicago.edu/~davidkelly999/',
        'http://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/',
    ]

    rules = (
        Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//a',)), callback="parse_items", follow= True),
    )

    def __init__(self):
        super(NetCDFSpider, self).__init__()
        home = expanduser("~")
        self.config = ConfigParser.ConfigParser()
        self.config.read(home+"/.netcdf-scavenger/config.ini")
        self.mongodb_url="mongodb://"+self.configSectionMap("mongodb")['host']+":"+self.configSectionMap("mongodb")['port']+"/"


    def parse_items(self, response):
        # Create an item
        item = NetCDFScraperItem()

        # Populate it
        item["url"] = response.url
        item["date"] = str(datetime.datetime.utcnow())
        item["status"] = "UNKWN"

        if response.url.endswith(".nc4") or response.url.endswith(".nc") or response.url.endswith("dods"):
            stored_item=None
            # Try to check if this url has been visided using mongodb
            client = MongoClient(self.mongodb_url)
            if client.netcdf.authenticate(user, password) is True:
                db = client.netcdf
                items = db.items
		stored_item=items.find_one({"url": response.url })
            else:
                print "No MongoDb authentication"
            client.close()

            if stored_item is not None:
                # Now a very trivial beahviour
                # It should be smarter
                item["status"] = "ASTRD"
                return item

	    downloaded=False
	    tempdir=""
	    filename=""

            # Check if it is served by an opendap server
            try:
		# The netcdf file is hosted by a opendap server
		# There is non need to download it
            	rootgrp = Dataset(response.url)
                rootgrp.close()
                filename=response.url
            except:
		# Unfortunatly the netcdf have to be downloaded
            	tempdir=tempfile._get_default_tempdir()+"/"+next(tempfile._get_candidate_names())
            	path = urlparse.urlsplit(response.url).path
            	filename =tempdir+"/"+posixpath.basename(path)
            	wget.download(tempdir,response.url)
		downloaded=True
	    # Get the feature 
            feature=self.get_item_info(filename, response.url)

	    # Remove the downloaed file and directory if needed
            if downloaded is True:
            	os.remove(filename)
		os.rmdir(tempdir)

            # Check if the feature is valid
            if feature is not None:
                #print json.dumps(feature,None,"\t")

	        # Try to save the item in mongodb
                client = MongoClient(mongodb_url)
                if client.netcdf.authenticate(user, password) is True:
		    db = client.netcdf
		    items = db.items
		    item_id = items.insert_one(feature).inserted_id
                    item["status"] = "NEWFT"
                else:
                    print "No MongoDb authentication"
	        client.close()

	# Return the item
        return item

    def get_item_info(self, filename,url):
        gradscheck_filename="/opt/galaxy/tools/faceit/gradscheck.gs"
        try:
            rootgrp = Dataset(filename)
        except:
            return None

        args=gradscheck_filename+" "+filename
        isGrADS=False
        #print "[--"+args
        #try:
        p = subprocess.Popen(['grads', '-lbc', args ], stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out, err = p.communicate()
        if "[OK]" in out:
            isGrADS=True
        #except:
        #    pass
        #print "--]"
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
                #"unlimited":dimension.is_unlimited()
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

    def configSectionMap(self,section):
        dict1 = {}
        options = self.config.options(section)
        for option in options:
            try:
                dict1[option] = self.config.get(section, option)
                if dict1[option] == -1:
                    print("skip: %s" % option)
            except:
                print("exception on %s!" % option)
                dict1[option] = None
        return dict1

if __name__ == "__main__":
	netcdfSpider=NetCDFSpider()
        #response=Response("http://users.rcc.uchicago.edu/~davidkelly999/prism.2deg.tile/0021/clim_0021_0028.tile.nc4")
        response=Response("http://users.rcc.uchicago.edu/~davidkelly999/gsde.2deg.tile/0066/soil_0066_0055.tile.nc4")
        response=Response("http://iridl.ldeo.columbia.edu/SOURCES/.ECOSYSTEMS/.Matthews/dods")
        item=netcdfSpider.parse_items(response);
	print str(item)
