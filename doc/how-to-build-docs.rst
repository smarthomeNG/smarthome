SmartHomeNG Documentation
=========================

This directory contains the documentation. It is in German and will at some time be multilingual, at least translated into English.

The user documentation (master language 'de') is going to be stored in ``doc/user``


How to build the documentation
==============================

Currently only the generation of html is configured. There are sections in the makefile
which also offer other targets but they are not working right now.
(Feel free to improve that!)

At first you need to satisfy the needed modules described in requirements.txt.
You can install them at once with either:

.. code-block:: bash

  sudo pip3 install requirements.txt

If you are using **virtualenv** or **pyenv** you might first checkout your environment and choose a different way.

Then you simply copy two files (**build_doc.sh** and **remove_built_files.sh**) from the doc directory to an
empty directory on your system and start the shell script build_doc by typing './build_doc.sh'

To build the documentation, start the script with (``./build_doc.sh``)

The build process will create a directory named **work**.

You will find your newly created files in ``doc/user/build/html`` in the **work** dirctory.
Your starting point is index.html

If you want to make updates to the documentation, make changes to the files in the **work** directory.
When you start build_doc.sh again, the script will use the files in the **work** directory.

Do get your changes to github do the following:

- start the script **./remove_built_files.sh** to remove the created built files that should not be checked in
- copy the directory **source** from ``work/doc/user`` to your local github environment (replacing the existing **source** directory, not merging it)
- commit your changes

Afterwards you can delete the directory **work**.
