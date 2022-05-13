How to Update Blockly with latest files
=======================================

It is possible to download a whole zip directory from github at https://github.com/google/blockly/zipball/master

From the content of the zip directory only a few files are needed for operation:

* blockly_compressed.js
* blocks_compressed.js
* python_compressed.js
* demos/code/style.css
* msg/js/de.js
* msg/js/en.js
* msg/js/fr.js  ...  and other languages as well if needed
* LICENSE
* README.md

need to be put directly and plain into ``plugins/blockly/webif/static/blockly`` directory

The ``media`` directory needs to be copied in full to the same directory