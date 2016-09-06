/**
 * @license
 * Visual Blocks Editor for smarthome.py
 *
 * Copyright 2015 Dirk Wallmeier
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

/**
 * @fileoverview Variable blocks for Blockly.
 * @author DW
 */
'use strict';

goog.provide('Blockly.Blocks.sh_items');

goog.require('Blockly.Blocks');



Blockly.Blocks['sh_item'] = {
  /**
   * Block for item
   * @this Blockly.Block
   */
  init: function() {
    var itemlist = new Blockly.FieldTextInput('0');
    itemlist.setVisible(false);
    var dropdown = new Blockly.FieldDropdown( function () {
                              var il = new Array();
                              il = itemlist.getValue();
                              if (il != '0') { il = eval("(function(){return " + il + ";})()");};
                              return il;
                             } );
    this.setColour(340);
    this.appendDummyInput()
        .appendField(itemlist, 'ITEMLIST')
        .appendField('Item')
        .appendField(dropdown, 'ITEM');
    this.setOutput(true, "SHITEM");
    this.setTooltip('Gibt ein Item Objekt zurück.');
  },
};

Blockly.Python['sh_item'] = function(block) {
  // Variable getter.
  var code = 'sh.' + block.getFieldValue('ITEM');
  return [code, Blockly.Python.ORDER_ATOMIC];
};

Blockly.Blocks['sh_item_get'] = {
  /**
   * Block for item getter. -> this is a "Sensor"
   * @this Blockly.Block
   */
    init: function() {
        this.setHelpUrl('');
        this.setColour(260);
        this.appendValueInput("ITEMOBJECT")
            .setCheck("SHITEM")
            .appendField("Wert von");
        this.setInputsInline(true);
        this.setOutput(true);
        this.setTooltip('Gibt den Wert des Items zurück.');
    }
};

Blockly.Python['sh_item_get'] = function(block) {
    var itemobj = Blockly.Python.valueToCode(block, 'ITEMOBJECT', Blockly.Python.ORDER_ATOMIC) || 'item';
    var code = itemobj + '()';
    return [code, Blockly.Python.ORDER_NONE];
};


Blockly.Blocks['sh_item_set'] = {
  /**
   * Block for item setter.
   * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#7wv5ve
   */
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(260);
    this.appendValueInput("ITEMOJECT")
        .setCheck("SHITEM")
        .appendField("setze");
    this.appendValueInput("VALUE")
        .appendField("auf den Wert");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};

Blockly.Python['sh_item_set'] = function(block) {
  var itemoject = Blockly.Python.valueToCode(block, 'ITEMOJECT', Blockly.Python.ORDER_ATOMIC) || 'item';
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_ATOMIC) || '0';
  // TODO: Assemble Python into code variable.
  //var code = '...';
  var code = itemoject + '(' + value + ')\n';
  return code;
};



