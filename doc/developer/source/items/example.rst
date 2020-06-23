Example for use of functions
============================

This logic uses some of the functions described above.


.. code-block:: python
   :caption:  logics/sample.py

   # getting the parent of item
   sh.item.return_parent()

   # get all children for item and log them
   for child in sh.item.return_children():
      logger.debug( ... )

   # set the item after 10 minutes to 42
   sh.item.autotimer('10m', 42)

   # disable autotimer for item
   sh.item.autotimer()

   # will in- or decrement the living room light to 100 by a stepping of ``1`` and a timedelta of ``2.5`` seconds.
   sh.living.light.fade(100, 1, 2.5)


