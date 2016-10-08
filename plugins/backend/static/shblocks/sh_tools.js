/**
 * @license
            <block type="shtools_logger"></block>
            <block type="shtools_dewpoint"></block>
            <block type="shtools_fetchurl"></block>
 */
'use strict';
goog.provide('Blockly.Blocks.sh_tools');
goog.require('Blockly.Blocks');

/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#prgbjr
 */
Blockly.Blocks['shtools_logger'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(45);
    this.appendDummyInput()
        .appendField("schreibe ins Log");
    this.appendValueInput("LOGTEXT")
        .setCheck("String");
    this.appendDummyInput()
        .appendField("mit log-level")
        .appendField(new Blockly.FieldDropdown([["debug", "DEBUG"], ["info", "INFO"], ["warning", "WARNING"], ["error", "ERROR"], ["critical", "CRITICAL"]]), "LOGLEVEL");
    this.setInputsInline(true);
    this.setPreviousStatement(true);
    this.setNextStatement(true);
    this.setTooltip('');
  }
};
Blockly.Python['shtools_logger'] = function(block) {
  var loglevel = block.getFieldValue('LOGLEVEL').toLowerCase();
  var logtext =  Blockly.Python.valueToCode(block, 'LOGTEXT', Blockly.Python.ORDER_NONE) || '\'\'';
  var code = "logger." + loglevel + "(" + logtext + ")\n";
  return code;
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#ipzxr2
 */
Blockly.Blocks['shtools_dewpoint'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("Taupunkt bei")
    this.appendValueInput("TEMP")
        .appendField("°C Temeratur und ")
    this.appendValueInput("HUM")
        .appendField("% rel.Feuchtigkeit");
    this.setInputsInline(true);
    this.setOutput(true, "Number");
    this.setTooltip('');
  }
};
Blockly.Python['shtools_dewpoint'] = function(block) {
  var value_hum = Blockly.Python.valueToCode(block, 'HUM', Blockly.Python.ORDER_ATOMIC);
  var value_temp = Blockly.Python.valueToCode(block, 'TEMP', Blockly.Python.ORDER_ATOMIC);
  var code = 'sh.tools.dewpoint(' + value_temp + ', ' + value_hum + ')';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#onut2y
 */
Blockly.Blocks['shtools_fetchurl'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("open URL")
        .appendField(new Blockly.FieldTextInput("http://"), "URL");
    this.setInputsInline(true);
    this.setOutput(true, "String");
    this.setTooltip('');
  }
};
Blockly.Python['shtools_fetchurl'] = function(block) {
  var text_url = block.getFieldValue('URL');
  var code = 'sh.tools.fetch_url("' + text_url + '")' ;
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};

/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#eqhv9d
 */
Blockly.Blocks['shtools_fetchurl2'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("open URL")
        .appendField(new Blockly.FieldTextInput("http://"), "URL")
        .appendField(" mit username")
        .appendField(new Blockly.FieldTextInput(""), "USER")
        .appendField(": password")
        .appendField(new Blockly.FieldTextInput(""), "PASSWORD");
    this.setInputsInline(true);
    this.setOutput(true, "String");
    this.setTooltip('');
  }
};
Blockly.Python['shtools_fetchurl2'] = function(block) {
  var text_url = block.getFieldValue('URL');
  var text_user = block.getFieldValue('USER');
  var text_password = block.getFieldValue('PASSWORD');
  var code = 'sh.tools.fetch_url("' + text_url + '", "' + text_user + '", "' + text_password + '")';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};

