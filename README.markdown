# README.markdown

This README describes how to set up your computer for developing the Pinax implementation of the Kukui Cup.  Most of the content can be found in the [Pinax documentation](http://pinaxproject.com/docs/0.7/install.html) and the [Django CAS](http://code.google.com/p/django-cas/) project page.

## Prerequisites
* Install [Python](http://www.python.org/download/) 2.5 or higher (but not Python 3).  Make sure you can type `python` on the command line to start the interpreter (type `exit()` to close the interpreter).
* Install the [Python Image Library](http://www.pythonware.com/products/pil/) (PIL)
* If on OS X, make sure that the Apple developer tools are installed (which includes XCode).

## Installing Pinax
* Download the latest official release from the [Pinax web site](http://pinaxproject.com/download/).
* Extract the bundle and using the terminal or a command prompt, change into the new directory.
* Run `python scripts/pinax-boot.py <path-to-virtual-env-to-create>`.  For example, if you want to install to /pinax-env, then type `python scripts/pinax-boot.py /pinax-env`.

## Installing Django CAS
* Download the latest official release from the [Django CAS](http://code.google.com/p/django-cas/) project page.
* Extract the bundle and change into the Django CAS directory.
* Run `python setup.py install` to install Django CAS to your PYTHONPATH.

## Obtaining the Kukui Cup Pinax source
* Getting this project requires Git.  Find a package for your operating system at the [Git download page](http://git-scm.com/download).
* Once Git is installed, cd into the directory that will hold the code.
* Type `git clone git@github.com:keokilee/kukui-cup-pinax.git` to create a folder called "kukui-cup-pinax" and download the files.

## Running the server for the first time
* cd into the kukui-cup-pinax folder.
* Start the Pinax virtual environment by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Type `python manage.py syncdb` to create the Sqlite database.
* It will ask you if you want to create a superuser.  Say "yes".
* IMPORTANT: Use your UH username (i.e. if your UH email is "bob@hawaii.edu", use "bob" as your username).  This is required so that you can authenticate via UH CAS.
* Type in a valid email address and any password you like (you probably won't use the password, but emails might be activated later).
* After the tables are created, type `python manage.py loaddata fixtures/*` to load the data in the fixtures folder.
* Type `python manage.py runserver` to start the web server.
* Open a browser and go to http://localhost:8000 to see the website.
 
# Modifying templates