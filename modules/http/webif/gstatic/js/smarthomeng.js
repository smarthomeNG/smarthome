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
          if (highlight > 0) {
            old_text = $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).data();
            element = $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).node();
            // compare old value of cell with new one and highlight
            if (old_text != "..." && old_text != text) {
              startAnimation($('#' + $.escapeSelector(id)), highlight);
            }
          }
          // update datatable cell
          $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).data(text);
        }
      }
      catch (e) {
        console.log("Problem setting cell with id " + id + " of table " + table_id + ". Error: " + e);
      }
    }
}


/**
 * fires an ajax request to get actual data from the plugin
 * @param {string} optional name of dataset to get. Only needed, if the webinterface gets multiple different datasets from the plugin
 */
function shngGetUpdatedData(dataSet=null) {
    if (dataSet) {
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
            console.warn("Error - while getting updated data for dataSet :"+dataSet)
        }
    });
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
