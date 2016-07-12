# README #

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for? ###

* Quick summary
* Version
* [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up? ###

* Summary of set up
* Configuration

1.  Amazon Machine Image (AMI): Ubuntu Server 14.04 LTS (HVM), SSD Volume Type - ami-fce3c696

2.  Instance Type: t2.micro

3.  Instance Details: default

4. Add Storage: none

5. Tag instance: Name=NetCDF_Scavenger

6. Configure Security Group: just ssh

7. Review Instance Launch : Launch! (select you public key)

8. View the instance boot and copy the public ip address

* Dependencies

Using ssh login as ubuntu user

sudo apt-get update

sudo apt-get upgrade

sudo apt-get install build-essential gfortran git libcurl4-gnutls-dev m4 python-pip python-numpy python-dev libxslt1-dev libxml2-dev libbz2-dev python-twisted python-setuptools python-pymongo grads nco cdo

sudo pip install cython parallel_sync scrapy

git clone https://github.com/RDCEP/NetCDFScavenger.git 

mv NetCDFScavenger netcdf-scavenger

cd netcdf-scavenger

Edit the file etc/profile. Check the latest available HDF5 version on https://www.hdfgroup.org/HDF5/release/obtain5.html and modify the profile file.

source etc/profile

install-deps

sudo -i

source /home/ubuntu/netcdf-scavenger/etc/profile

install-netcdf4-python

* Database configuration

If you want to install a mongodb instance on the same machine (just for testing purposes)

install-mongodb



mongo --port 27017

use admin

db.system.users.remove({})    <== removing all users

db.system.version.remove({}) <== removing current version 

db.system.version.insert({ "_id" : "authSchema", "currentVersion" : 3 })

use netcdf

db.createUser({ user: "scavenger",pwd: "Rey2015!",roles: [ { role: "userAdmin", db: "netcdf" } ]})

quit()

Restart the service

service mongod restart

exit

* How to run tests

cd $HOME/netcdf-scavenger

scrapy crawl netcdf

* Deployment instructions

mkdir $HOME/.netcdf-scavenger

cat > $HOME/.netcdf-scavenger/config.in << EOF

[mongodb]

host: 127.0.0.1

port: 27017

user: scavenger

password: Rey2015!

EOF

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact
