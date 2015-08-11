# udacity-item-catalog
Item Catalog (Udacity)
by Adland Lee

This application provides a list of items within a variety of categories and
integrates third party user registration and authentication.

This product demonstrates a CRUD web application, OAuth integration, and security
measures to address CSRF.


## System Requirements

* Vagrant https://www.vagrantup.com
* VirtualBox https://www.virtualbox.org
* this repo

## Software version requirements

* Flask == 0.10.1
* SQLAlchemy == 0.8.4
* bleach == 1.4.1
* oauth2client == 1.4.11
* requests == 2.2.1
* httplib2 == 0.9.1

## Running the Demo

In the vagrant directory, start the instance:

    vagrant up

Login to the instance:

    vagrant ssh

Change to the project directory and run the test suite

    cd /vagrant/catalog
    python project.py

The default running project can be accessed via the local web browser at:

    localhost:5000

## Reference

* [API](vagrant/catalog/API.md)