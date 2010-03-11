# README.markdown

This README describes how to set up your computer for developing the Pinax implementation of the Kukui Cup.  Most of the content can be found in the [Pinax documentation](http://pinaxproject.com/docs/0.7/install.html) and the [Django CAS](http://code.google.com/p/django-cas/) project page.

If you're on Windows, there's also a screencast on installing Pinax in Windows on [Beshr Kayali's blog](http://beshrkayali.com/posts/10/).

## Prerequisites
* [Python](http://www.python.org/download/) 2.5 or higher (but not Python 3).  Verify that you have it installed by typing `python` at the command prompt.  The interpreter should launch.  Close the interpreter by typing `exit()`.
* If on Mac OS X, make sure that the Apple Developer Tools are installed (which is bundled with XCode).  You can either get this from your Mac's install DVD or from Apple's [site](http://developer.apple.com/technologies/xcode.html).  Note that you need an Apple developer account (which is free) to download from Apple.
* [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL).

## Installing Pinax
* Download the latest official release from the [Pinax web site](http://pinaxproject.com/download/).
* Extract the bundle and using the terminal or a command prompt, change into the new directory.
* Run `python scripts/pinax-boot.py <path-to-virtual-env-to-create>`.  For example, if you want to install to /pinax-env, then type `python scripts/pinax-boot.py /pinax-env`.

## Obtaining the Kukui Cup Pinax source
* Getting this project requires Git.  Find a package for your operating system at the [GitHub install wiki](http://help.github.com/git-installation-redirect).
* If you wish to commit to the Kukui Cup Pinax project, you will need to create an account at [GitHub](http://github.com).  Then, you will need to set up your [SSH keys](http://help.github.com/key-setup-redirect) and your [email settings](http://help.github.com/git-email-settings/).
* Once you set those up, you should be able to check out the code by using the private url.  Type `git clone git@github.com:keokilee/kukui-cup-pinax.git` to check out the code.  This will create the new folder and download the code from the repository.

## Setting up Kukui Cup Pinax
* cd into the kukui-cup-pinax folder.
* Start the Pinax virtual environment by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Copy `settings.py.example` to `settings.py`.  This will work as is, but you might want to make a few changes to it depending on your environment.  Some things you might want to change are the database settings, timezone, and the CAS Login server.
* Type `python manage.py syncdb` to create the database.
* It will ask you if you want to create a superuser.  Say "yes".
* IMPORTANT: Use your UH username (i.e. if your UH email is "bob@hawaii.edu", use "bob" as your username).  This is so that you can authenticate via UH CAS.
* Type in a valid email address and any password you like (you probably won't use the password, but emails might be activated later).
* The database fixtures should be automatically loaded (it should say `Installed 70 objects from 1 fixture(s)`).  If they are not, type `python manage.py loaddata fixtures/*` to load the data in the fixtures folder.

## Running the server
* If the virtual environment is not already active, start it by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Type `python manage.py runserver` to start the web server.
* Open a browser and go to http://localhost:8000 to see the website.

## Troubleshooting
If you visit http://localhost:8000 and a NoneType exception appears, it is isn't your fault!  Django/Pinax has an issue with dumping and loading fixtures that depend on foreign keys.  In this case, it is the foreign key that connects the django\_generic\_flatblocks\_genericflatblock table to the django\_content\_type table.  A sample SQL script is located in `fixture_update.sql`.  You'll need to update the content type ids in the genericflatblock table to point to the correct entry in the content types table.  It is recommended that you use a GUI based database browser like the [SQLite Database Browser](http://sqlitebrowser.sourceforge.net/) for SQLite3.

Some hints:
* website\_header matches to the content type with name "title"
* website\_footer matches to the content type "text"
* website\_image matches to the content type "image"
* homepage\_tips matches to the content type "titleandtext"
 
It sucks, but there's no easy way around it.

## Running tests
While Django/Pinax has support for running tests, some of the out of the box tests fail (as of Pinax 0.7.1).  You can run the tests using `python manage.py test`.  I created my own script to only run my own tests in the system.  You can run those tests by typing `python runtests.py`.  These are the same tests that are run by our continuous integration server.

# Further documentation
For information on editing views, consult the [Editing Views wiki](http://wiki.github.com/keokilee/kukui-cup-pinax/editing-views).
