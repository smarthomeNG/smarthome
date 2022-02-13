
.. index:: Logiken; Standardparameter
.. index:: Standardparameter; Logiken


Standardparameter
=================

Die folgenden Parameter können für eine Logik in der Konfigurationsdatei im Verzeichnis ../etc angegeben werden.

+------------------+-----------------------------------------------------------------------------------------------+
| **Parameter**    | **Beschreibung**                                                                              |
+==================+===============================================================================================+
| filename         | Dateiname des Logik-Codes. Diese Datei muss im Verzeichnis **../logics**  liegen. Dieser      |
|                  | Parameter muss angegeben werden.                                                              |
+------------------+-----------------------------------------------------------------------------------------------+
| watch_item       | **Optional**: String oder Liste von Strings, die jeweils einen Item-Pfad repräsentieren.      |
|                  | Eine Veränderung eines der hier aufgeführten Items führt dazu, dass die Logik ausgeführt      |
|                  | wird. Details dazu stehen :ref:`hier <logik_parameter_watch_item>` .                          |
+------------------+-----------------------------------------------------------------------------------------------+
| crontab          | **Optional**: String oder Liste von Strings, die einen crontab Eintrag darstellen. Der Syntax |
|                  | des Parameters entspricht dem Syntax des **crontab** Attributes von Items. Details dazu       |
|                  | stehen :ref:`hier <logik_parameter_crontab>` .                                                |
+------------------+-----------------------------------------------------------------------------------------------+
| cycle            | **Optional**: Angabe einer Zykluszeit, die angibt, in welchem Zeitabstand die Logik           |
|                  | periodisch ausgelöst werden soll. Der Syntax des Parameters entspricht dem Syntax des         |
|                  | **cycle** Attributes von Items. Details dazu stehen                                           |
|                  | :ref:`hier <logik_parameter_cycle>` .                                                         |
+------------------+-----------------------------------------------------------------------------------------------+
| prio             | **Optional**: Angabe einer Priorität für die Logik. Die Priorität kommt nur bei Logiken zum   |
|                  | Einsatz, die ein Schedule haben, bei denen also der Paramter **crontab** oder **cycle**       |
|                  | angegeben wurde. Die Priorität sollte zwischen **1** und **5** liegen. Falls der Parameter    |
|                  | nicht angegeben wird, wird die Standardpriorität **3** verwendet.                             |
+------------------+-----------------------------------------------------------------------------------------------+
| visu_acl         | **Optional**: Dieser Parameter wird durch das Plugin **visu_websocket**                       |
|                  | implementiert. Wenn dieser Parameter auf **True** gesetzt wird, kann die Logik                |
|                  | von einer Visualisierung aus (z.B. smartVISU) ausgelöst werden.                               |
+------------------+-----------------------------------------------------------------------------------------------+
| enabled          | **Optional**: ``enabled`` kann auf ``False`` gesetzt werden um die Ausführung der Logik       |
|                  | auszusetzen. Der Ausführungsstatus der Logik kann über das CLI-Plugin oder das Admin          |
|                  | Interface gesetzt werden.                                                                     |
+------------------+-----------------------------------------------------------------------------------------------+
| <user_parameter> | **Optional**: Es können weitere Parameter definiert werden, diese können aus der              |
|                  | Logik heraus abgefragt werden und haben sonst keine Funktion.                                 |
+------------------+-----------------------------------------------------------------------------------------------+

Falls keiner der optionalen Parameter **crontab**, **watch_item** oder **cycle** angegeben wird, wird
die Logik nicht automatisiert ausgeführt. Sie kann dann nur aus Plugins oder (falls konfiguriert) über
eine Visualisierung ausgelöst werden.

