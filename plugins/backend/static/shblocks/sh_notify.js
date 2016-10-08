/**
 * @license
            <block type="shnotify_email"></block>
            <block type="shnotify_prowl"></block>
            <block type="shnotify_nma"></block>
            <block type="shnotify_pushbullit"></block>
 */
'use strict';
goog.provide('Blockly.Blocks.sh_logic');
goog.require('Blockly.Blocks');

/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#c2zkf2
 */
Blockly.Blocks['shnotify_email'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("eine eMail senden an")
        .appendField(new Blockly.FieldTextInput("mail@smarthome.py"), "TO")
        .appendField("mit Betreff")
        .appendField(new Blockly.FieldTextInput("Nachricht von SmartHome"), "SUBJECT")
        .appendField("und Text:");
    this.appendValueInput("TEXT")
        .setCheck("String");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};
Blockly.Python['shnotify_email'] = function(block) {
  var to = block.getFieldValue('TO');
  var subject = block.getFieldValue('SUBJECT');
  var text = Blockly.Python.valueToCode(block, 'TO', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = 'if sh.mail: sh.mail('+to+', '+subject+', '+text+')';
  return code;
};


Blockly.Blocks['shnotify_prowl'] = {
  /**
   * Block for
   */
  init: function() {
    this.setColour(340);
    this.appendDummyInput().appendField('Sende Nachricht mit PROWL:');
  },
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#ptwi98
 */
Blockly.Blocks['shnotify_nma'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("eine NMA Nachricht senden")
        .appendField("mit Betreff")
        .appendField(new Blockly.FieldTextInput("Nachricht von SmartHome"), "SUBJECT")
        .appendField("und Text:");
    this.appendValueInput("TEXT")
        .setCheck("String");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};
Blockly.Python['shnotify_nma'] = function(block) {
  var text_subject = block.getFieldValue('SUBJECT');
  var value_text = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_ATOMIC);
  // TODO: Assemble Python into code variable.
  var code = '...';
  return code;
};


/**
 * https://
 */
Blockly.Blocks['shnotify_pushbullit'] = {
  /**
   * Block for
   */
  init: function() {
    this.setColour(340);
    this.appendDummyInput().appendField('Sende Nachricht mit Pushbullit:');
  },
};

