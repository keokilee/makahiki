# README.md

## Introduction

This README describes how to set up your computer for developing the [Pinax implementation](http://github.com/keokilee/makahiki) of the [Kukui Cup](http://code.google.com/p/kukui-cup/).  Most of the content can be found in the [Pinax documentation](http://pinaxproject.com/docs/0.7/install.html) and the [Django CAS](http://code.google.com/p/django-cas/) project page.

## Prerequisites
* [Python](http://www.python.org/download/) 2.5 or higher (but not Python 3).  On Windows machines, it is recommended that you use the 32 bit version, as using the 64 bit version appears to have issues.  Verify that you have it installed by typing `python` at the command prompt.  The interpreter should launch.  Close the interpreter by typing `exit()`.
* If on Mac OS X, make sure that the Apple Developer Tools are installed (which is bundled with XCode).  You can either get this from your Mac's install DVD or from Apple's [site](http://developer.apple.com/technologies/xcode.html).  Note that you need an Apple developer account (which is free) to download from Apple.
* [Python Imaging Library](http://www.pythonware.com/products/pil/) (PIL).

## Installing Pinax
* Download the latest official release from the [Pinax web site](http://pinaxproject.com/download/).
* Extract the bundle and using the terminal or a command prompt, change into the new directory.
* Run `python scripts/pinax-boot.py <path-to-virtual-env-to-create>`.  For example, if you want to install to /pinax-env, then type `python scripts/pinax-boot.py /pinax-env`.
* TROUBLESHOOTING: On Mac OS X Snow Leopard, you may see an issue where the virtual environment fails to install.  One way to avoid this is to use the [virtualenvwrapper](http://www.doughellmann.com/docs/virtualenvwrapper/).  Follow the steps in the introduction and make a virtualenv for Pinax (i.e. `mkvirtualenv pinax-env`). You may also want to define $WORKON_HOME to your shell startup file in addition to adding the virtualenv startup script. Then, you can go back to the pinax folder you downloaded and type `python scripts/pinax-boot.py $WORKON_HOME/pinax-env` to install Pinax into the virtual environment.

## Obtaining the Kukui Cup Pinax source
* Getting this project requires Git.  Find a package for your operating system at the [GitHub install wiki](http://help.github.com/git-installation-redirect).
* It is recommended that you also configure Git so that it handles line endings from Windows users correctly. See [Dealing With Line Endings](http://help.github.com/dealing-with-lineendings/).
* If you only wish to download the source, you can check out using the read-only URL.  Type `git clone git://github.com/keokilee/makahiki.git` to get the source.
* If you wish to commit to the Kukui Cup Pinax project, you will need to create an account at [GitHub](http://github.com).  Then, you will need to set up your [SSH keys](http://help.github.com/key-setup-redirect) and your [email settings](http://help.github.com/git-email-settings/).
* Once those are set up, send me your Git username so that you can be added as a collaborator.
* When you are added as a collaborator, you should be able to check out the code by using the private url.  Type `git clone git@github.com:keokilee/makahiki.git` to check out the code.  This will create the new folder and download the code from the repository.

## Grabbing External Dependencies
The following steps are to download additional libraries and upgrade some of the default ones.

* cd into the makahiki folder.
* Start the Pinax virtual environment by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.  If you used virtualenvwrapper, then you can just use `workon <pinax-environment-name>`.
* Check if you have pip installed by typing `pip help`.  If it works, great.  Otherwise, type `easy_install pip` to install it.
* Type `pip install -r requirements.pip` from the application root.  This will load the dependencies in requirements.pip.

## Setting up Kukui Cup Pinax
* cd into the makahiki folder.
* Start the Pinax virtual environment by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.  If you used virtualenvwrapper, then you can just use `workon <pinax-environment-name>`.
* Copy `settings.py.example` to `settings.py`.  This will work as is, but you might want to make a few changes to it depending on your environment.  Some things you might want to change are the database settings, timezone, and the CAS Login server.
* Type `python manage.py syncdb` to create the database.
* It will ask you if you want to create a superuser.  Say "yes".
* IMPORTANT: Use your CAS username as your username.  This is so that you can authenticate via the CAS login server.
* Type in a valid email address and any password you like (you probably won't use the password, but emails might be activated later).
* NOTE: syncdb may fail at this point because some apps depend on tables that are not loaded until the next step.
* Run `python manage.py migrate` to sync the migrations.
* To load some sample data into the application, type `python manage.py loaddata fixtures/base_data.json`.

## Running the server
* If the virtual environment is not already active, start it by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Type `python manage.py runserver` to start the web server.
* Open a browser and go to http://localhost:8000 to see the website.

## Adding Facebook Integration
The Javascript required to log in to Facebook is included in this application.  However, you will need to apply for your own application on Facebook at their [Developer Site](http://developers.facebook.com/).  Once this is done, it is recommended that you create a `local_settings.py` file and add the settings below.  Otherwise, you can also add these to `settings.py` directly.

<pre>
<code>
FACEBOOK_APP_ID = '&lt;APP_ID&gt;'
FACEBOOK_API_KEY = '&lt;API_KEY&gt;'
FACEBOOK_SECRET_KEY = '&lt;SECRET_KEY&gt;'
</code>
</pre>

These can be found in your application's page within the Facebook Developer page.

## Troubleshooting
If you visit http://localhost:8000 and a NoneType exception appears, it is isn't your fault!  Django/Pinax has an issue with dumping and loading fixtures that depend on foreign keys.  In this case, it is the foreign key that connects the django\_generic\_flatblocks\_genericflatblock table to the django\_content\_type table.  There are several ways of fixing this.

The most straightforward way to fix this is to use [SQLite Database Browser](http://sqlitebrowser.sourceforge.net/) to update the tables.  Open the database file (by default, it is "dev.db") and browse the data of the "django\_generic\_flatblocks\_genericflatblock" table.  Note the values of the website header field (which is of type "title"), the website footer field (type "text"), the website image field (type "image"), and the homepage\_content\_1 field (type "titleandtext"). Next, browse the contents of the "django\_content\_type" table.  Find the app_label "gblocks" and the names "title", "text", "image", and "titleandtext".  What you need to do is execute SQL to update the entries in the "django\_generic\_flatblocks\_genericflatblock" table.  An example statement is:

`UPDATE django_generic_flatblocks_genericflatblock SET content_type_id=<value in django_content_type> WHERE content_type_id=<value in django_generic_flatblocks_genericflatblock>;`

## Running tests
While Django/Pinax has support for running tests, some of the out of the box tests fail (as of Pinax 0.7.1).  You can run the tests using `python manage.py test`.  I created my own script to only run my own tests in the system.  You can run those tests by typing `python runtests.py`.  These are the same tests that are run by our continuous integration server.

## Other resources

Here are some online Python books that may be helpful when learning the language.

* [Dive Into Python](http://diveintopython.org/)
* [Learn Python the Hard Way](http://learnpythonthehardway.org/index) (more geared toward people new to coding)

The following tutorials may be helpful when learning about Django and the various packages used by the system.

* [Django Tutorial](http://docs.djangoproject.com/en/dev/intro/tutorial01/)
* [South Tutorial](http://south.aeracode.org/docs/tutorial/part1.html)

## Further documentation
For information on editing views, consult the [Editing Views wiki](http://wiki.github.com/keokilee/makahiki/editing-views).
