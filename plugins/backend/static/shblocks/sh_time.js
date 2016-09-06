/**
 * @license
            <block type="shtime_now"></block>
            <block type="shtime_time"></block>
            <block type="shtime_sun"></block>
            <block type="shtime_moon"></block>
            <block type="shtime_auto"></block>
 */
'use strict';
goog.provide('Blockly.Blocks.sh_logic');
goog.require('Blockly.Blocks');


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#dngzfj
 */
Blockly.Blocks['shtime_now'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField("Zeit: jetzt");
    this.setInputsInline(true);
    this.setOutput(true, "DateTime");
    this.setTooltip('');
  }
};
Blockly.Python['shtime_now'] = function(block) {
  var code = 'sh.now()';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#rvch7e
 */
Blockly.Blocks['shtime_time'] = {
  init: function() {
    var hh_mmValidator = function(text) {
          if(text === null) {
            return null;
          }
          text = text.replace(/O/ig, '0');
          text = text.replace(/,/g, ':');
          var hh_mm = text.split(':');
          if (hh_mm.length !== 2) {
            return null;
          }
          return String('00'+hh_mm[0]).slice(-2) + ':' + String('00'+hh_mm[1]).slice(-2);
    };
    this.setHelpUrl('http://www.example.com/');
    this.setColour(210);
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput("12:00", hh_mmValidator ), "TIME")
        .appendField("Uhr");
    this.setInputsInline(true);
    this.setOutput(true, "DateTime");
    this.setTooltip('');
  }
};

Blockly.Python['shtime_time'] = function(block) {
  var text_time = block.getFieldValue('TIME');
  var code = 'datetime.strptime("'+text_time+'", "%H:%M")';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};


/**
 * https://blockly-demo.appspot.com/static/demos/blockfactory/index.html#5yobn6
 */
Blockly.Blocks['shtime_sunpos'] = {
  init: function() {
    this.setHelpUrl('http://www.example.com/');
    this.setColour(300);
    this.appendValueInput("DELTA")
        .appendField(new Blockly.FieldDropdown([["Azimut Winkel des Sonnenstands", "0"],
                                                ["Altitude Winkel des Sonnenstands", "1"]]),
                                                 "AA")
        .appendField(new Blockly.FieldDropdown([["+", "+"],
                                                ["-", "-"]]), "PM");
    this.appendDummyInput()
        .appendField("Minuten");
    this.setInputsInline(true);
    this.setOutput(true, "Number");
    this.setTooltip('');
  }
};
Blockly.Python['shtime_sunpos'] = function(block) {
  var delta = Blockly.Python.valueToCode(block, 'DELTA', Blockly.Python.ORDER_ATOMIC);
  var aa = block.getFieldValue('AA');
  var pm = block.getFieldValue('PM');
  if (delta === '') { pm = ''; };
  var code = 'sh.sun.pos('+pm+delta+')['+aa+']';
  // TODO: Change ORDER_NONE to the correct strength.
  return [code, Blockly.Python.ORDER_NONE];
};



Blockly.Blocks['shtime_moon'] = {
  /**
   * Block for
   */
  init: function() {
    this.setColour(340);
    this.appendDummyInput().appendField('Mond:');
  },
};

Blockly.Blocks['shtime_auto'] = {
  /**
   * Block for
   */
  init: function() {
    this.setColour(340);
    this.appendDummyInput().appendField('Autotimer:');
  },
};

