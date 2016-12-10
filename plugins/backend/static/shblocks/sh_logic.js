/**
 * @license
            <block type="shlogic_by"></block>
            <block type="shlogic_source"></block>
            <block type="shlogic_dest"></block>
            <block type="shlogic_trigger"></block>
 */
'use strict';
goog.provide('Blockly.Blocks.sh_logic');
goog.require('Blockly.Blocks');


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#ojesy8
 */
Blockly.Blocks['shlogic_by'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("Auslöser (trigger by)");
    this.setOutput(true);
    this.setTooltip('');
  }
};
Blockly.Python['shlogic_by'] = function(block) {
  var code = "trigger['by']";
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#p3ajqk
 */
Blockly.Blocks['shlogic_source'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("Trigger Source");
    this.setOutput(true);
    this.setTooltip('');
  }
};
Blockly.Python['shlogic_source'] = function(block) {
  var code = "trigger['source']";
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#8jdhtt
 */
Blockly.Blocks['shlogic_dest'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("Trigger Dest");
    this.setOutput(true);
    this.setTooltip('');
  }
};
Blockly.Python['shlogic_dest'] = function(block) {
  var code = "trigger['dest']";
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#umj2u6
 */
Blockly.Blocks['shlogic_value'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("Trigger Value");
    this.setOutput(true);
    this.setTooltip('');
  }
};
Blockly.Python['shlogic_value'] = function(block) {
  var code = "trigger['value']";
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#r74ibg
 */
Blockly.Blocks['shlogic_trigger'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("diese Logik auslösen um ");
    this.appendValueInput("DATETIME");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};
Blockly.Python['shlogic_trigger'] = function(block) {
  var value_datetime = Blockly.Python.valueToCode(block, 'DATETIME', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = '...';
  return code;
};

