# README.markdown

This README describes how to set up your computer for developing the Pinax implementation of the Kukui Cup.  Most of the content can be found in the [Pinax documentation](http://pinaxproject.com/docs/0.7/install.html) and the [Django CAS](http://code.google.com/p/django-cas/) project page.

## Prerequisites
* Make sure you can type `python` on the command line to start the interpreter (type `exit()` to close the interpreter).  If you do not have [Python](http://www.python.org/download/) 2.5 or higher (but not Python 3), install it.
* If on Mac OS X, make sure that the Apple developer tools are installed (which includes XCode).  This is required to get gcc installed.
* Install the [Python Image Library](http://www.pythonware.com/products/pil/) (PIL).

## Installing Pinax
* Download the latest official release from the [Pinax web site](http://pinaxproject.com/download/).
* Extract the bundle and using the terminal or a command prompt, change into the new directory.
* Run `python scripts/pinax-boot.py <path-to-virtual-env-to-create>`.  For example, if you want to install to /pinax-env, then type `python scripts/pinax-boot.py /pinax-env`.

## Installing Django CAS
* Download the latest official release from the [Django CAS](http://code.google.com/p/django-cas/) project page.
* Extract the bundle and change into the Django CAS directory.
* Run `python setup.py install` to install Django CAS to your PYTHONPATH.

## Obtaining the Kukui Cup Pinax source
* Getting this project requires Git.  Find a package for your operating system at the [GitHub install wiki](http://help.github.com/git-installation-redirect).
* If you wish to commit to the Kukui Cup Pinax project, you will need to create an account at [GitHub](http://github.com).  Then, you will need to set up your [SSH keys](http://help.github.com/key-setup-redirect) and your [email settings](http://help.github.com/git-email-settings/).
* Once you set those up, you should be able to check out the code by typing `git clone git@github.com:keokilee/kukui-cup-pinax.git`.  This will create the new folder and download the code from the repository.

## Setting up Kukui Cup Pinax
* cd into the kukui-cup-pinax folder.
* Start the Pinax virtual environment by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Copy `settings.py.example` to `settings.py`.  This will work as is, but you might want to make a few changes to it depending on your environment.  Some things you might want to change are the database settings, timezone, and the CAS Login server.
* Type `python manage.py syncdb` to create the database.
* It will ask you if you want to create a superuser.  Say "yes".
* IMPORTANT: Use your UH username (i.e. if your UH email is "bob@hawaii.edu", use "bob" as your username).  This is so that you can authenticate via UH CAS.
* Type in a valid email address and any password you like (you probably won't use the password, but emails might be activated later).
* After the tables are created, type `python manage.py loaddata fixtures/*` to load the data in the fixtures folder.

## Running the server
* If the virtual environment is not already active, start it by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Type `python manage.py runserver` to start the web server.
* Open a browser and go to http://localhost:8000 to see the website.
 
## Running tests
While Django/Pinax has support for running tests, some of the out of the box tests fail (as of Pinax 0.7.1).  You can run the tests using `python manage.py test`.  I created my own script to only run my own tests in the system.  You can run those tests by typing `python runtests.py`.

## Modifying templates