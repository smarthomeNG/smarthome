:tocdepth: 3

Pushbullet
==========

Requirements
------------

Python libraries
~~~~~~~~~~~~~~~~

-  requests - `install
   instructions <http://docs.python-requests.org/en/latest/user/install/#install>`__
-  magic - `install
   instructions <https://github.com/ahupp/python-magic>`__

Other
~~~~~

-  Pushbullet API-KEY - get it from
   `**here** <http://www.pushbullet.com/>`__ for free

--------------

What's new?
-----------

**2015-11-17**:

-  Added "delete" function
-  Changed any push function to return the pushbullet service result
   object
-  Changed Logging to "warning"

**2014-08-26**:

-  Added support for eMail-Addresses as deviceId
-  Updated README.md with instructions "How to get your deviceId"
-  Added usage example to send a note to a specific device

**2014-06-17**:

-  **New python library dependecy: "magic" (see requirements section
   above)**
-  Updated to pushbullet `api v2 <http://www.pushbullet.com/api>`__,
   including new file handling
-  New *(optional)* "body" parameters for link and file pushes

**2014-05-16**:

-  Initial version

--------------

Configuration
-------------

plugin.conf
~~~~~~~~~~~

.. raw:: html

   <pre>
   [pushbullet]
       class_name = Pushbullet
       class_path = plugins.pushbullet
   #   deviceid = <your-default-device-id>
   #   apikey = <your-api-key>
   </pre>

Description of the attributes:

-  **apikey**: set api-key globally so you do not have to set it in the
   function calls
-  **deviceid**: set deviceid globally so it will be used as defaul
   target, you can override this on each call

--------------

How to get your deviceId
------------------------

| 1) Use your browser to log into your account on
  http://www.pushbullet.com
| 2) Select your desired target device
| 3) Copy the last part of the browser url (behind the "device\_iden=")
  into your clipboard.
| 4) Paste it to your plugin.conf or your api call.

--------------

Functions
---------

| *Pass a 'deviceid' if no set globally or if you want to send to
  another device.*
| *Add 'apikey' if not set globally.*

sh.pushbullet.note(title, body [, deviceid] [, apikey])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send a note to your device.

Parameters
^^^^^^^^^^

-  **title**: The title of the note
-  **body**: The note's body

Example
^^^^^^^

.. raw:: html

   <pre>
   #send simple note to default device
   sh.pushbullet.note("Note to myself.", "Call my mother.")

   #send simple note to device with id: x28d7AJFx13
   sh.pushbullet.note("Note to myself.", "Call my mother.", "x28d7AJFx13")

   #send simple note to user with email: teddy.tester@testing.de
   sh.pushbullet.note("Note to myself.", "Call my mother.", "teddy.tester@testing.de")
   </pre>

--------------

sh.pushbullet.link(title, url [, deviceid] [, apikey] [, body])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send a link to your device.

Parameters:
^^^^^^^^^^^

-  **title**: The title of the page linked to
-  **url**: The link url
-  (optional) **body**: An optional message

Example
^^^^^^^

.. raw:: html

   <pre>
   # send link to device with id: x28d7AJFx13
   #
   sh.pushbullet.link("Pushbullet", "http://www.pushbullet.com", "x28d7AJFx13", body="Try this cool service.")
   </pre>

--------------

sh.pushbullet.address(name, address [, deviceid] [, apikey])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send a address to your device.

Parameters:
^^^^^^^^^^^

-  **name**: The name of the place at the address
-  **address**: The full address or Google Maps query

Example
^^^^^^^

.. raw:: html

   <pre>
   # send address of "Eifel Tower" to default device
   sh.pushbullet.address("Eifel Tower", "https://www.google.com/maps/place/Eiffelturm/@48.85837,2.294481,17z/data=!3m1!4b1!4m2!3m1!1s0x47e66e2964e34e2d:0x8ddca9ee380ef7e0")
   </pre>

--------------

sh.pushbullet.list(title, title [, deviceid] [, apikey])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send a list of items to your device.

Parameters:
^^^^^^^^^^^

-  **title**: The title of the list
-  **items**: The list items

Example
^^^^^^^

.. raw:: html

   <pre>
   #send a shopping list to default device
   sh.pushbullet.list("Shopping list", ["Milk", "Eggs", "Salt"])
   </pre>

--------------

sh.pushbullet.file(filepath [, deviceid] [, apikey] [, body])
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Send a file to your device.

Parameters:
^^^^^^^^^^^

-  **filepath**: absolute path to the file to push
-  (optional) **body**: An optional message

Example
^^^^^^^

.. raw:: html

   <pre>
   #send smarthome log file to default device
   sh.pushbullet.file("/usr/local/smarthome/var/log/smarthome.log", body="Take a look at this log-file")
   </pre>

--------------

sh.pushbullet.delete(pushid)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Delete the push with the given id.

Parameters:
^^^^^^^^^^^

-  pushid: id of of the push to delete

Example
^^^^^^^

.. raw:: html

   <pre>
   #send a push and delete it afterwards
   result = sh.pushbullet.note("Note to myself.", "Call my mother.")
   sh.pushbullet.delete(result['iden'])
   </pre>
