/**
 * Create a namespace for the application.
 */
var Code = {};

/**
 * Blockly's main workspace.
 * @type {Blockly.WorkspaceSvg}
 */
Code.workspace = null;


/**
 * Restore code blocks from file on backend server
 *
 */
Code.loadBlocks = function() {
  var request = $.ajax({'url': '/logics_blockly_load', dataType: 'text'});
  request.done(function(response)
  {
    var xml = Blockly.Xml.textToDom(response);
    //var workspace = Blockly.getMainWorkspace();
    Blockly.Xml.domToWorkspace(xml, Code.workspace);
  });
  request.fail(function(jqXHR, txtStat) {alert('Request failed: ' + txtStat);});
  Code.renderContent()
};


/**
 * Load blocks saved on App Engine Storage or in session/local storage.
 * @param {string} defaultXml Text representation of default blocks.
 */
Code.initBlocks = function(defaultXml) {
 if (defaultXml) {
   // Load the editor with default starting blocks.
   var xml = Blockly.Xml.textToDom(defaultXml);
   Blockly.Xml.domToWorkspace(xml, Code.workspace);
 } else {
   // Restore saved blocks in a separate thread so that subsequent
   // initialization is not affected from a failed load.
   window.setTimeout(Code.loadBlocks, 0);
 }
};


/**
 * Save XML and PYTHON code to file on backend server.
 */
Code.saveBlocks = function() {
  Code.workspace;
  var xml = Blockly.Xml.workspaceToDom(Code.workspace);
  var xmldata = Blockly.Xml.domToText(xml);
  var pycode = Blockly.Python.workspaceToCode(Code.workspace);
  $.ajax({  url: "/logics_blockly_save",
            type: "POST",
            data: {xml: xmldata, py: pycode },
            //success: function(response) {
            //    alert(response +' ?');
            //    $("#test").html(response);
            //}
        });
};


/**
 * Discard all blocks from the workspace.
 */
Code.discardBlocks = function() {
  var count = Code.workspace.getAllBlocks().length;
  if (count < 2 ||
      window.confirm(Blockly.Msg.DELETE_ALL_BLOCKS.replace('%1', count))) {
    Code.workspace.clear();
    Code.renderContent();
  }
};


/**
 * Bind a function to a button's click event.
 * On touch enabled browsers, ontouchend is treated as equivalent to onclick.
 * @param {!Element|string} el Button element or ID thereof.
 * @param {!Function} func Event handler to bind.
 */
Code.bindClick = function(el, func) {
  if (typeof el == 'string') {
    el = document.getElementById(el);
  }
  el.addEventListener('click', func, true);
  el.addEventListener('touchend', func, true);
};


/**
 * List of tab names.
 * @private
 */
Code.TABS_ = ['blocks', 'python', 'xml'];

Code.selected = 'blocks';

/**
 * Switch the visible pane when a tab is clicked.
 * @param {string} clickedName Name of tab clicked.
 */
Code.tabClick = function(clickedName) {
  // If the XML tab was open, save and render the content.
  if (document.getElementById('tab_xml').className == 'tabon') {
    var xmlTextarea = document.getElementById('content_xml');
    var xmlText = xmlTextarea.value;
    var xmlDom = null;
    try {
      xmlDom = Blockly.Xml.textToDom(xmlText);
    } catch (e) {
      var q =
          window.confirm(MSG['badXml'].replace('%1', e));
      if (!q) {
        // Leave the user on the XML tab.
        return;
      }
    }
    if (xmlDom) {
      Code.workspace.clear();
      Blockly.Xml.domToWorkspace(xmlDom, Code.workspace);
    }
  }

  if (document.getElementById('tab_blocks').className == 'tabon') {
    Code.workspace.setVisible(false);
  }
  // Deselect all tabs and hide all panes.
  for (var i = 0; i < Code.TABS_.length; i++) {
    var name = Code.TABS_[i];
    document.getElementById('tab_' + name).className = 'taboff';
    document.getElementById('content_' + name).style.visibility = 'hidden';
  }

  // Select the active tab.
  Code.selected = clickedName;
  document.getElementById('tab_' + clickedName).className = 'tabon';
  // Show the selected pane.
  document.getElementById('content_' + clickedName).style.visibility =
      'visible';
  Code.renderContent();
  if (clickedName == 'blocks') {
    Code.workspace.setVisible(true);
  }
  Blockly.svgResize(Code.workspace);
};

/**
 * Populate the currently selected pane with content generated from the blocks.
 */
Code.renderContent = function() {
  var content = document.getElementById('content_' + Code.selected);
  // Initialize the pane.
  if (content.id == 'content_xml') {
    var xmlTextarea = document.getElementById('content_xml');
    var xmlDom = Blockly.Xml.workspaceToDom(Code.workspace);
    var xmlText = Blockly.Xml.domToPrettyText(xmlDom);
    xmlTextarea.value = xmlText;
    xmlTextarea.focus();
  } else if (content.id == 'content_python') {
    code = Blockly.Python.workspaceToCode(Code.workspace);
    content.textContent = code;
    if (typeof prettyPrintOne == 'function') {
      code = content.innerHTML;
      code = prettyPrintOne(code, 'py');
      content.innerHTML = code;
    }
  }
};


/**
 * Compute the absolute coordinates and dimensions of an HTML element.
 * @param {!Element} element Element to match.
 * @return {!Object} Contains height, width, x, and y properties.
 * @private
 */
Code.getBBox_ = function(element) {
  var height = element.offsetHeight;
  var width = element.offsetWidth;
  var x = 0;
  var y = 0;
  do {
    x += element.offsetLeft;
    y += element.offsetTop;
    element = element.offsetParent;
  } while (element);
  return {
    height: height,
    width: width,
    x: x,
    y: y
  };
};


/**
 * Initialize Blockly.  Called on page load.
 */
Code.init = function() {
  //Code.initLanguage();

  //var rtl = Code.isRtl();
  var container = document.getElementById('content_area');
  var onresize = function(e) {
    var bBox = Code.getBBox_(container);
    for (var i = 0; i < Code.TABS_.length; i++) {
      var el = document.getElementById('content_' + Code.TABS_[i]);
      el.style.top = bBox.y + 'px';
      el.style.left = bBox.x + 'px';
      // Height and width need to be set, read back, then set again to
      // compensate for scrollbars.
      el.style.height = bBox.height + 'px';
      el.style.height = (2 * bBox.height - el.offsetHeight) + 'px';
      el.style.width = bBox.width + 'px';
      el.style.width = (2 * bBox.width - el.offsetWidth) + 'px';
    }
    // Make the 'Blocks' tab line up with the toolbox.
    if (Code.workspace && Code.workspace.toolbox_.width) {
      document.getElementById('tab_blocks').style.minWidth =
          (Code.workspace.toolbox_.width ) + 'px';
          // Account for the 19 pixel margin and on each side.
    }
  };
  window.addEventListener('resize', onresize, false);

  // Interpolate translated messages into toolbox.
  //var toolboxText = document.getElementById('toolbox').outerHTML;
  //toolboxText = toolboxText.replace(/{(\w+)}/g,
  //    function(m, p1) {return MSG[p1]});
  //var toolboxXml = Blockly.Xml.textToDom(toolboxText);

  var toolboxXml = Blockly.Xml.textToDom(document.getElementById('toolbox').outerHTML);

  Code.workspace = Blockly.inject('content_blocks',
      {grid:
          {spacing: 25,
           length: 3,
           colour: '#ccc',
           snap: true},
       media: '../static/blockly/media/',
       //rtl: rtl,
       toolbox: toolboxXml,
       zoom:
           {controls: true,
            wheel: true}
      });

  // Add to reserved word list: Local variables in execution environment (runJS)
  // and the infinite loop detection function.
  //Blockly.JavaScript.addReservedWords('code,timeouts,checkTimeout');

  Code.initBlocks('');

  //if ('BlocklyStorage' in window) {
  //  // Hook a save function onto unload.
  //  BlocklyStorage.backupOnUnload(Code.workspace);
  //}

  Code.tabClick(Code.selected);

  for (var i = 0; i < Code.TABS_.length; i++) {
    var name = Code.TABS_[i];
    Code.bindClick('tab_' + name,
        function(name_) {return function() {Code.tabClick(name_);};}(name));
  }
  onresize();
  Blockly.svgResize(Code.workspace);

  // Lazy-load the syntax-highlighting.
  window.setTimeout(Code.importPrettify, 1);
};

window.addEventListener('load', Code.init);
