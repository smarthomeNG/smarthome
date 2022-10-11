function resizeCodeMirror(codeMirrorInstance, bottomSpace) {
    if (!codeMirrorInstance.getOption("fullScreen")) {
        var browserHeight = $( window ).height();
        offsetTop = $('.CodeMirror').offset().top;
        codeMirrorInstance.getScrollerElement().style.maxHeight = ((-1)*(offsetTop) - bottomSpace + browserHeight)+ 'px';
        codeMirrorInstance.refresh();
    }
}


/**********************************************************************
 * following scripts are for usage in webinterfaces of plugins.
 */


/**
 * sends a request to the specified url from a form. this will change the window location.
 * @param {string} path the path to send the post request to
 * @param {object} params the paramiters to add to the url
 * @param {string} [method=post] the method to use on the form
 */

function shngPost(path, params, method='post') {

  // The rest of this code assumes you are not using a library.
  // It can be made less wordy if you use one.
  const form = document.createElement('form');
  form.method = method;
  form.action = path;

  for (const key in params) {
    if (params.hasOwnProperty(key)) {
      const hiddenField = document.createElement('input');
      hiddenField.type = 'hidden';
      hiddenField.name = key;
      hiddenField.value = params[key];

      form.appendChild(hiddenField);
    }
  }

  document.body.appendChild(form);
  form.submit();
}

/**
 * Creates a highlight effect by transitioning from one CSS class to another.
 * Needs jquery ui effect "switchClass"
 * @param {string} $element dom element
 * @param {string} highlight duration of effect (fade off)
 */
 function startAnimation($element, highlight) {
    $element.stop(true, false);
    $element.css({ 'background-color' : '' });
    $element.switchClass("shng_effect_standard", "shng_effect_highlight", highlight*10)
       .delay(highlight*20).switchClass("shng_effect_highlight", "shng_effect_standard", highlight*1000, 'easeInOutQuad');
    $element.promise().done( function() {
      $element.removeClass('shng_effect_standard');$element.removeClass('shng_effect_highlight');
    });
 }

 /**
  * inserts text into a dom element. To be used for ajax updates
  * @param {string} id of the dom element
  * @param {string} text to insert
  */
function shngInsertText (id, text, table_id=null, highlight=0) {
    if (table_id == null) {
      element = $("#" + $.escapeSelector(id));
      if (highlight > 0) {
        old_text = $('#' + $.escapeSelector(id)).text();
        // compare old value of cell with new one and highlight
        if (old_text != "..." && old_text != text) {
          startAnimation(element, highlight);
        }
      }
      // update HTML element
      element.html(text);
    }
    else {
      try {
        // check if cell id exists on current page
        test = $('#' + table_id).DataTable().cell( $("#" + $.escapeSelector(id)), { page:'current'}).data();
        if ( test ) {
          old_text = $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).data();
          if (highlight > 0) {

            element = $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).node();
            // compare old value of cell with new one and highlight
            if (old_text != "..." && old_text != text) {
              startAnimation($('#' + $.escapeSelector(id)), highlight);
            }
          }
          // update datatable cell
          $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).data(text);
          if (old_text != text) {
            console.log("Redrawing table because new cell data found: " + text);
            $('#' + table_id).DataTable().draw(false);
          }
        }
      }
      catch (e) {
        console.warn("Problem setting cell with id " + id + " of table " + table_id + ". Error: " + e);
      }
    }
}


/**
 * fires an ajax request to get actual data from the plugin
 * @param {string} optional name of dataset to get. Only needed, if the webinterface gets multiple different datasets from the plugin
 */
function shngGetUpdatedData(dataSet=null) {
    if (dataSet) {
      if (update_params) {
        console.log("Running page update with dataSet: " + dataSet + " and params: " + update_params);
        $.ajax({
            url: "get_data.html",
            type: "GET",
            data: { dataSet : dataSet, params: update_params
                  },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                    handleUpdatedData(response, dataSet, update_params);
            },
            error: function () {
                console.warn("Error - while getting updated data for dataSet: "+dataSet)
            }
        });
      } else {
        console.log("Running page update with dataSet: " + dataSet);
        $.ajax({
            url: "get_data.html",
            type: "GET",
            data: { dataSet : dataSet
                  },
            contentType: "application/json; charset=utf-8",
            success: function (response) {
                    handleUpdatedData(response, dataSet);
            },
            error: function () {
                console.warn("Error - while getting updated data for dataSet: "+dataSet)
            }
        });
      }
    } else {
    $.ajax({
        url: "get_data.html",
        type: "GET",
        contentType: "application/json; charset=utf-8",
        success: function (response) {
                handleUpdatedData(response);
        },
        error: function () {
            console.warn("Error - while getting updated data")
        }
    });
    }
}


/**
 * replaces the body attribs onload approach. The major difference is that all parameters like activate
 * autorefresh and refreshrate can be changed by scripts and forms, etc. It's based on:
 * https://stackoverflow.com/questions/30725455/change-setinterval-value-dynamically
 * start parameters: function, interval, start directly, repeat
 * set_interval parameters: interval, start directly
*/

function timer() {
  var timer = {
      running: false,
      iv: 0,
      timeout: false,
      rp: false,
      cb : function(){},
      start : function(cb,iv,sd,rp){
          var elm = this;
          clearInterval(this.timeout);
          this.running = true;
          if(cb) this.cb = cb;
          if(iv) this.iv = iv;
          if(rp != null) this.rp = rp;
          if(sd) elm.execute(elm);
					if(iv <= 0)
						console.log("Initializing timer " + this.timeout + ", but not running because interval is 0");
					else
          	this.timeout = setTimeout(function(){elm.execute(elm)}, this.iv);
      },
      execute : function(e){
          if(!e.running) return false;
          e.cb();
          if(this.rp)
            e.start();
          else {
            this.running = false;
            clearInterval(this.timeout);
            clearTimeout(this.timeout);
          }
      },
      stop : function(){
          this.running = false;
					console.log("Stopping timer " + this.timeout + " because stop command received");
      },
      update : function(params){
          for (key in params)
            if(params[key] != null) window[key] = params[key];
          console.log("Updating timer method with: " + JSON.stringify(params));
          document.getElementById("update_active").checked = window.update_active;
          document.getElementById("update_interval").value = window.update_interval / 1000;
          if (window.update_interval > 0 && window.update_active == true)
          {
            window.refresh.set_interval(window.update_interval, true);
          }
          else
          {
            window.refresh.stop();
            document.getElementById("update_active").checked = false;
          }
      },
      set_interval : function(iv,sd){
          clearInterval(this.timeout);
					if (iv == 0)
						{
							console.log("Stopping timer " + this.timeout + " because interval is set to " + iv);
							this.stop();
						}
					else
						{
            	this.start(false,iv,sd);
							// console.log("Starting timer " + this.timeout + " with interval " + iv + " instatrigger " + sd);
						}
      }
  };
  return timer;
}
