========================
Multi-Instance Fähigkeit
========================

Es gibt Plugins, die so geschrieben sind, dass von ihnen mehrere Instanzen parallel geladen werden
können.

Wenn von solchen Plugins nur eine Instanz konfiguriert wird, ist nichts besonderes zu
beachten. Dann wird ein solches Plugin konfiguriert wie alle andern Plugins auch.

Wenn mehrere Instanzen eines Plugins konfiguriert werden, muss in der Konfiguration der Items
eine Information hinterlegt werden, auf welche Instanz des Plugins sich das Item bezieht. Dazu
**muss** jeder Instanz ein eindeutiger Name gegeben werden. Das erfolgt in der **../etc/plugin.yaml**
dadurch, dass jeder Instanz ein Parameter **instance** hinzugefügt wird:

.. code:: yaml

   fritzbox_1:
       plugin_name: avm
       instance: fb6360
       ...

   fritzbox_2:
       plugin_name: avm
       instance: fb7490
       ...


Außerdem muss jedem Item die Information mitgegeben werden, auf welche Instanz sich das Item bezieht:

.. code:: yaml

   wan:
       connection_status:
           type: str
           avm_data_type@fb7490: wan_connection_status


Wenn ein Item mehrere Attribute nutzt, die das Plugin zur Verfügung stellt, ist als Grundregel
jedes Attribut mit der **@<instance>** zu ergänzen.

Es kann sein, dass die Ergänzung eines einzelnen Attributes reicht. Das ist dann in der Doku
des jeweiligen Plugins beschrieben.

