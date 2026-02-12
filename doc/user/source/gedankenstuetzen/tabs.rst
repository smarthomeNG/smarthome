
.. index:: Doku Erstellung; Verwendung von Tabs

===================
Verwendung von Tabs
===================

.. note::

    Diese Information dient nur als Hilfestellung für die Erstellung von Dokumentationsseiten


Es gibt die Möglichkeit in der Dokumentation Tabs zu nutzen ähnlich wie auch im Webinterface der Plugins.
Das bietet sich für voneinander unabhängige Varianten an. Beispielsweise in der Referenz beim
Standardattribut ``crontab`` werden Tabs für die verschiedenen Parametersätze genutzt.
Für Python 3.13 ist sphinx_design anstelle von sphinx_tabs notwendig. Die Syntax hat sich
daher auch entsprechend geändert.
"Header" ist nun tab-set anstelle von tabs. Und einzelne Tabs heißen nicht mehr tab, sondern tab-item.

.. tab-set::

    .. tab-item:: Tab A

        Hier kann ein beliebiger Text für Tab A stehen oder aber Code-Beispiele


    .. tab-item:: Tab B

        Hier kann ein beliebiger Text für Tab B stehen oder aber Code-Beispiele

    .. tab-item:: Tab C

        Hier kann ein beliebiger Text für Tab C stehen oder aber Code-Beispiele

Oder beispielsweise auch verschiedene Varianten von Betriebssystemen

.. tab-set::

    .. tab-item:: Linux (Posix)

        Hier kann ein beliebiger Text für Linux stehen oder aber Code-Beispiele


    .. tab-item:: BSD Unix (Mac OS)

        Hier kann ein beliebiger Text für BSD Unix stehen oder aber Code-Beispiele

    .. tab-item:: Windows

        Hier kann ein beliebiger Text für Windows stehen oder aber Code-Beispiele
