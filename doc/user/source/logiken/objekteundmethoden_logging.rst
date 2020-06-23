
.. index:: Logiken; Logging
.. index:: Logging; Logiken

.. role:: bluesup
.. role:: redsup


Logging in Logiken :redsup:`Neu`
================================

Logiken verfügen über einen vordefinierten Logger. Dieser Logger ist im ``logic`` Objekt hinterlegt und kann
z.B. über

.. code-block:: python

    logic.logger.info("Logtext")

angesprochen werden. Die Ausgabe und er Loglevel können in ../etc/logging.yaml konfiguriert werden:

.. code-block:: yaml

   loggers:

       # ==============================
       # Loggers for SmartHomeNG logics
       # ------------------------------
       logics:
           handlers: [shng_details_file]
           level: WARNING

       logics.<name der Logik>:
           handlers: [q21]
           level: INFO


Wobei der Logger **logics** den Loglevel und Handler für alle Logiken festlegt, für die keine besonderen
Konfigurationen vorgenommen werden.

**logics.<name der Logik>** Legt den Loglevel und den Handler für eine einzelne Logik fest.

.. note::

    In SmartHomeNG v1.7.1 und davor, gab es diesen vordefinierten Logger noch nicht,
    so dass in den Logiken der ein Logger explizit definiert werden musste:

    .. code-block:: python

        import logging
        logger = logging.getLogger(__name__)

        ...

        logger.info("Logtext")


