# README.markdown

## Milestone 2.5

## CHANGELOG
* Milestone 2.5
 * Added commitments and activities to the user profile.
 * Added commitments and activities to the admin interface.
 * Added [Windmill](http://getwindmill.com) tests.
 * Added admin tab for users with admin permissions.
 * Customized profile and avatar templates for consistency.


This README describes how to set up your computer for developing the [Pinax implementation](http://github.com/keokilee/kukui-cup-pinax) of the [Kukui Cup](http://code.google.com/p/kukui-cup/).  Most of the content can be found in the [Pinax documentation](http://pinaxproject.com/docs/0.7/install.html) and the [Django CAS](http://code.google.com/p/django-cas/) project page.

If you're on Windows, there's also a screencast on installing Pinax in Windows on [Beshr Kayali's blog](http://beshrkayali.com/posts/10/).  Note that you can ignore the section adding/removing Genshi.

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
* It is recommended that you also configure Git so that it handles line endings from Windows users correctly. See [Dealing With Line Endings](http://help.github.com/dealing-with-lineendings/).
* If you only wish to download the source, you can check out using the read-only URL.  Type `git clone git://github.com/keokilee/kukui-cup-pinax.git` to get the source.
* If you wish to commit to the Kukui Cup Pinax project, you will need to create an account at [GitHub](http://github.com).  Then, you will need to set up your [SSH keys](http://help.github.com/key-setup-redirect) and your [email settings](http://help.github.com/git-email-settings/).
* Once those are set up, send me your Git username so that you can be added as a collaborator.
* When you are added as a collaborator, you should be able to check out the code by using the private url.  Type `git clone git@github.com:keokilee/kukui-cup-pinax.git` to check out the code.  This will create the new folder and download the code from the repository.

## Setting up Kukui Cup Pinax
* cd into the kukui-cup-pinax folder.
* Start the Pinax virtual environment by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Copy `settings.py.example` to `settings.py`.  This will work as is, but you might want to make a few changes to it depending on your environment.  Some things you might want to change are the database settings, timezone, and the CAS Login server.
* Type `python manage.py syncdb` to create the database.
* It will ask you if you want to create a superuser.  Say "yes".
* IMPORTANT: Use your UH username (i.e. if your UH email is "bob@hawaii.edu", use "bob" as your username).  This is so that you can authenticate via UH CAS.
* Type in a valid email address and any password you like (you probably won't use the password, but emails might be activated later).
* The database fixtures should be automatically loaded (it should say `Installed 70 objects from 1 fixture(s)`).  If they are not, type `python manage.py loaddata fixtures/initial_data.json` to load the data in the fixtures folder.

## Running the server
* If the virtual environment is not already active, start it by typing `source <path-to-created-virtual-env>/bin/activate` or `<path-to-created-virtual-env>\Scripts\activate.bat` on Windows.
* Type `python manage.py runserver` to start the web server.
* Open a browser and go to http://localhost:8000 to see the website.

## OPTIONAL: Install Windmill
Windmill is an Python app that will run tests within the browser.  The runtests.py script will work without it, but is useful if you're developing functionality and want to test it on the browser side.  Integrating it is very simple.  To install the application, download it from their [website](http://www.getwindmill.com/) and follow their installation [wiki](http://wiki.github.com/windmill/windmill/installing).  Once installed, running `python runtests.py` will run all of the available unit tests and Windmill tests.

## Troubleshooting
If you visit http://localhost:8000 and a NoneType exception appears, it is isn't your fault!  Django/Pinax has an issue with dumping and loading fixtures that depend on foreign keys.  In this case, it is the foreign key that connects the django\_generic\_flatblocks\_genericflatblock table to the django\_content\_type table.  I have created a backup of my contenttypes data that can be used to reload it.  But first, you need to delete the contents of the contenttypes database.

Here's a way to do this using the Python shell:

1. Type `python manage.py shell` to start the shell.
2. Import the ContentType model by typing `from django.contrib.contenttypes.models import ContentType`.
3. Type the following command: `map(lambda c: c.delete(), ContentType.objects.all())`.  What this does is that it loads all of the objects from the database and deletes each one.
4. Exit the python shell (type `exit()`) and reload the fixtures with `python manage.py loaddata fixtures/*`.

You should see something similar to this:

<pre>
<code>
(pinax-env)gelee-macbook-pro:kukui-cup-pinax gelee$ python manage.py shell
Python 2.6.1 (r261:67515, Jul  7 2009, 23:51:51) 
[GCC 4.2.1 (Apple Inc. build 5646)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from django.contrib.contenttypes.models import ContentType
>>> map(lambda c: c.delete(), ContentType.objects.all())
[None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None]
>>> exit()
(pinax-env)gelee-macbook-pro:kukui-cup-pinax gelee$ python manage.py loaddata fixtures/*
Installing json fixture 'fixtures/contenttypes_backup' from absolute path.
Installing json fixture 'fixtures/initial_data' from absolute path.
Installed 109 object(s) from 2 fixture(s)
(pinax-env)gelee-macbook-pro:kukui-cup-pinax gelee$
</code>
</pre>

## Running tests
While Django/Pinax has support for running tests, some of the out of the box tests fail (as of Pinax 0.7.1).  You can run the tests using `python manage.py test`.  I created my own script to only run my own tests in the system.  You can run those tests by typing `python runtests.py`.  These are the same tests that are run by our continuous integration server.

## Further documentation
For information on editing views, consult the [Editing Views wiki](http://wiki.github.com/keokilee/kukui-cup-pinax/editing-views).
