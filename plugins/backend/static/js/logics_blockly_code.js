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
 * List of tab names.
 * @private
 */
Code.TABS_ = ['blocks', 'python'];

Code.selected = 'blocks';



/**
 * Restore code blocks from file on backend server
 *
 */
Code.loadBlocks = function() {
  var request = $.ajax({'url': '/logics_blockly_load', dataType: 'text'});
  // we get the XML representation of all the blockly logics from the backend
  request.done(function(response)
  {
  	//alert('Request success: ' + response);
    var xml = Blockly.Xml.textToDom(response);
    Blockly.Xml.domToWorkspace(xml, Code.workspace);
    //Code.workspace.clear();
    Code.renderContent()
  });
  request.fail(function(jqXHR, txtStat) 
  {alert('Request failed: ' + txtStat);});
};


/**
 * Populate the Python pane with content generated from the blocks, when selected.
 */
Code.renderContent = function() {
	//if (Code.selected == 'python') {
		var content = document.getElementById('content_python');
		pycode = Blockly.Python.workspaceToCode(Code.workspace);
		content.textContent = pycode;
		if (typeof prettyPrintOne == 'function') {
		  pycode = content.innerHTML;
		  pycode = prettyPrintOne(pycode, 'py', true);
		  content.innerHTML = pycode;
		}
	//}
};


/**
 * Save XML and PYTHON code to file on backend server.
 */
Code.saveBlocks = function() {
  //Code.workspace;
  var pycode = Blockly.Python.workspaceToCode(Code.workspace);
  var xmldom = Blockly.Xml.workspaceToDom(Code.workspace);
  var xmltxt = Blockly.Xml.domToText(xmldom);
  $.ajax({  url: "/logics_blockly_save",
            type: "POST",
            data: {xml: xmltxt, py: pycode },
            success: function(response) {
            //    alert(response +' ?');
            //    $("#test").html(response);
            }
        });
};


/**
 * Discard all blocks from the workspace.
 */
Code.discardBlocks = function() {
	/**
	var count = Code.workspace.getAllBlocks().length;
	if (count < 2 ||
	  	window.confirm(Blockly.Msg.DELETE_ALL_BLOCKS.replace('%1', count))) **/ {
		Code.workspace.clear();
		Code.renderContent(); // ?
	}
};


/**
 * Initialize Blockly.  Called on page load.
 */
Code.init = function() {

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
	
	var toolboxtxt = document.getElementById('toolbox').outerHTML;
	var toolboxXml = Blockly.Xml.textToDom(toolboxtxt);
	
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
	
	//window.setTimeout(Code.loadBlocks, 0);
	Code.loadBlocks();
	
	Code.tabClick(Code.selected);
	
	Code.bindClick('tab_blocks', function(name_) {return function() {Code.tabClick(name_);};}('blocks'));
	Code.bindClick('tab_python', function(name_) {return function() {Code.tabClick(name_);};}('python'));
	
	onresize();
	Blockly.svgResize(Code.workspace);
	
	// Lazy-load the syntax-highlighting.
	Code.importPrettify();
	window.setTimeout(Code.importPrettify, 1);
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
 * Switch the visible pane when a tab is clicked.
 * @param {string} clickedName Name of tab clicked.
 */
Code.tabClick = function(clickedName) {

  if (document.getElementById('tab_blocks').className == 'tabon') {
    Code.workspace.setVisible(false);
  }

  if (clickedName == 'blocks') {
	document.getElementById('tab_python').className = 'taboff';
	document.getElementById('tab_blocks').className = 'tabon';
	document.getElementById('content_python').style.visibility = 'hidden';
	document.getElementById('content_blocks').style.visibility = 'visible';
    Code.workspace.setVisible(true);
  } else {
	document.getElementById('tab_blocks').className = 'taboff';
	document.getElementById('tab_python').className = 'tabon';
	document.getElementById('content_blocks').style.visibility = 'hidden';
	document.getElementById('content_python').style.visibility = 'visible';
  }

  Code.renderContent();
  Blockly.svgResize(Code.workspace);
};

/**
 * Load the Prettify CSS and JavaScript.
 */
Code.importPrettify = function() {
  //<link rel="stylesheet" href="../prettify.css">
  //<script src="../prettify.js"></script>
  var link = document.createElement('link');
  link.setAttribute('rel', 'stylesheet');
  link.setAttribute('href', '../static/js/google-prettify/prettify.css');
  document.head.appendChild(link);
  var script = document.createElement('script');
  script.setAttribute('src', '../static/js/google-prettify/prettify.js');
  document.head.appendChild(script);
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
 *  Init on window load
 * */
window.addEventListener('load', Code.init);

