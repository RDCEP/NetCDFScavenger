# Scrapy settings for prism_scraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'netcdf_scraper'
BOT_VERSION = '1.0'

SPIDER_MODULES = ['netcdf_scraper.spiders']
NEWSPIDER_MODULE = 'netcdf_scraper.spiders'
USER_AGENT = '%s/%s' % (BOT_NAME, BOT_VERSION)
