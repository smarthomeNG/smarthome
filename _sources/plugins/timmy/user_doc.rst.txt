
timmy
=====

Timmy ist ein Plugin, das die Definition von separaten Ein- und Ausschaltverzögerungen, sowie Blinkmuster ermöglicht. Die Blinkmuster können z.B. als visuelle Rückmeldungsfunktion verwendet werden.

Anforderungen
-------------
Das Plugin funktioniert ab Python 3.6, ansonsten existieren keine Anforderungen


Konfiguration
-------------

plugin.yaml
~~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


items.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


logic.yaml
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Funktionen
~~~~~~~~~~

Bitte die Dokumentation lesen, die aus den Metadaten der plugin.yaml erzeugt wurde.


Beispiele
---------

.. code-block:: yaml
   :linenos:

    some_lamp:
        type: bool

        blinker:
            type: bool
            timmy_blink_target: ..
            timmy_blink_loops: 3

        blinker_2:
            type: bool
            timmy_blink_target: ..
            timmy_blink_loops: 3
            timmy_blink_cycles: [.3,.3]
            timmy_blink_pattern: [True,False]



.. code-block:: yaml
   :linenos:

    temperature:
        type: num

        sun_protect_needed:
            type: bool
            eval: sh...self() > sh..defined_limit()
            eval_trigger:
                - ..self
                - .defined_limit
            timmy_delay_target_item: .post_hysteresis
            timmy_delay_off_delay_seconds: 1800
            timmy_delay_on_delay_seconds: 300

            defined_limit:
                type: num

            post_hysteresis:
                type: bool

Web Interface
-------------

Dieses Plugin hat kein WebInterface.
