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

sudo apt-get install build-essential gfortran git libcurl4-gnutls-dev m4 python-pip python-numpy python-dev libxslt1-dev libxml2-dev libbz2-dev python-twisted python-setuptools python-pymongo

sudo pip install cython parallel_sync scrapy

git clone https://montella@bitbucket.org/montella/netcdf-scavenger.git 

cd netcdf-scavenger

source etc/profile

install-deps

sudo -i

source /home/ubuntu/netcdf-scavenger/etc/profile

install-netcdf4-python

* Database configuration
If you want to install a mongodb instance on the same machine (just for testing purposes)

install-mongoldb

service mongod stop

mongod --port 27017 --dbpath /var/lib/mongodb/

From another shell on the same machine

mongo --port 27017

use admin

db.createUser({ user: "admin",pwd: "abc123",roles: [ { role: "userAdminAnyDatabase", db: "admin" } ]})

db.createUser({ user: "scavenger",pwd: "Rey2015!",roles: [ { role: "userAdmin", db: "netcdf" } ]})

quit()

Hit CTRL-C to stop the mongod service

Restart the service with auth

mongod --auth --port 27017 --dbpath /var/lib/mongodb/

From another shell on the same machine

mongo --port 27017 -u "admin" -p "abc123" --authenticationDatabase "admin"

quit()

mongo --port 27017 -u "scavenger" -p "Rey2015!" --authenticationDatabase "admin"

use netcdf

quit()

Hit CTRL-C to stop the mongod service

Restart the service

service mongod start

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
