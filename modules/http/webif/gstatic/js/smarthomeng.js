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

    function sanitize(text, spaces=false, quotes=false, entities=true, trim=true, normalize=true) {
      text = text.toString();
      if (spaces) text = text.replace(/\s\s+/g, ' ');
      if (quotes) text = text.replaceAll('"', '&quot;');
      if (entities) text = text.replace(/[\u00A0-\u9999]/g, function(i) { return '&#'+i.charCodeAt(0)+';'; });
      if (trim) text = text.trim();
      if (normalize) text = text.normalize("NFKC");
      return text;
    }

    if (typeof text == 'undefined') {
      console.log("Text for id " + id + " is undefined. Doing nothing.");
      return;
    }
    text = text.toString();
    if (table_id == null) {
      element = $("#" + $.escapeSelector(id));
      if (highlight > 0) {
        let old_text = sanitize($('#' + $.escapeSelector(id)).text(), true);
        let alternative_old_text = sanitize(old_text, false, true);
        let new_content = (old_text !== sanitize(text)) && (alternative_old_text !== sanitize(text));
        // compare old value of cell with new one and highlight
        if (old_text != "..." && new_content) {
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
          // fix HTML entities and quotation
          let old_text = sanitize($('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).data(), true);
          let alternative_old_text = sanitize(old_text, false, true);
          let new_content = (old_text !== sanitize(text)) && (alternative_old_text !== sanitize(text));

          if (highlight > 0) {
            element = $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).node();
            // compare old value of cell with new one and highlight
            if (old_text != "..." && new_content) {
              startAnimation($('#' + $.escapeSelector(id)), highlight);
            }
          }
          // update datatable cell
          if (new_content) {
            $('#' + table_id).DataTable().cell( $('#' + $.escapeSelector(id)) ).data(text);
            console.log("Redrawing table because new cell data found: " + text + " for id " + id + ", old text: " + old_text);
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
function shngGetUpdatedData(dataSet=null, update_params=null) {
    if (dataSet == null) dataSet = window.dataSet;
    if (update_params == null) update_params = window.update_params;
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
      console.log("Running page update.");
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
 * calculates the optimal width of the headtable if no min-width css attribute is defined
 */
function calculateHeadtable() {
  // try to get min-width from style attribute. If not available, calculate it
  let headminwidth = parseFloat($( "#webif-headtable > table:first" ).css('min-width'));
  if (headminwidth > 0)
  {
    console.log("Min-width " + headminwidth + "px of headtable (responsive)");
    return;
  }
  let arrOfTable1=[], i=0, x=0, y=0, columnWidth={};
  let table_margins = parseFloat($('#webif-headtable').css('padding-right')) + parseFloat($('#webif-headtable').css('padding-left')) + parseFloat($('#webif-headtable').css('margin-right')) + parseFloat($('#webif-headtable').css('margin-left'));
  // iterate through all tr and td and wrap content into a span to calculate it's width
  $('#webif-headtable tr').each(function() {
    rowWidth = 0;
    $(this).children('td').each(function() {
      let calcVal = '<span id="webif-head-span-' + (x + 1) + '-' + (y + 1) + '">'+ $(this).html()+'</span>';
      $(this).html(calcVal);
      let margins = parseFloat($(this).css('padding-right')) + parseFloat($(this).css('padding-left')) + parseFloat($(this).css('margin-right')) + parseFloat($(this).css('margin-left'));
      mWid = $(this).children('span:first').outerWidth() + margins;
      rowWidth += mWid;
      let current_mWid = columnWidth[y];
      if (isNaN(current_mWid)) current_mWid = 0;
      columnWidth[y] = Math.max.apply(Math, [mWid, current_mWid]);
      arrOfTable1.push(mWid);
      //console.log(columnWidth);
      y++;
    });
    x++;
    y = 0;
  });
  // iterate through all td to add a min-width style attribute
  $('#webif-headtable td').each(function() {
   $(this).css("min-width",arrOfTable1[i]+"px");
   i++;
  });
  function sum( obj ) {
    var sum = 0;
    for( var el in obj ) {
      if( obj.hasOwnProperty( el ) ) {
        sum += parseFloat( obj[el] );
      }
    }
    return sum;
  }
  let tableMinWidth = sum(columnWidth) + table_margins;

  console.log("Setting min-width " + tableMinWidth + "px for headtable (responsive)");
  // set the table min-width based on row with the highest width value
  $( "#webif-headtable > table:first" ).css("min-width",tableMinWidth+"px");
}


/**
 * make the top navigation bar as responsive as possible
 */
function responsiveHeader() {
  // remove the display:none attribute to show the element on the page after everything else is rendered

  // calculate different relevant element width values
  let width = $( "#webif-toprow" ).outerWidth(true) - parseFloat($( "#webif-top" ).css('padding-left'))  - parseFloat($( "#webif-top" ).css('padding-right'));
  let headminwidth = parseFloat($( "#webif-headtable > table:first" ).css('min-width'), 10);
  let headwidth = parseFloat($( "#webif-headtable" ).width());
  let buttonsrow = $( "#webif-allbuttons" ).outerWidth(true) + $( "#webif-custombuttons" ).outerWidth(true);
  if (isNaN(buttonsrow)) buttonsrow = 0;
  let buttonswidth = $( "#webif-custombuttons" ).width() + $( "#webif-autorefresh" ).width() + $( "#webif-reload_orig" ).width() + $( "#webif-close_orig" ).width() + $( "#webif-seconds_orig" ).width() + 82;
  if (isNaN(buttonswidth)) buttonswidth = 0;
  let logowidth = $( "#webif-pluginlogo" ).outerWidth(true);
  let infowidth = $( "#webif-plugininfo" ).outerWidth(true);
  //let total = width - headwidth - infowidth - logowidth;
  // calculate table width based on button width or table min-width
  let tablewidth = Math.max.apply(Math, [headminwidth, buttonsrow])
  //console.log("Widthes " + width + "-" + headminwidth + "-" + infowidth + "-" + logowidth + " table " + tablewidth + " buttonrow " + buttonsrow);
  // disable logo and info and fully expand the table
  if (width - infowidth - tablewidth <= 0) {
    $( "#webif-plugininfo" ).css("display", "none");
    $( "#webif-pluginlogo" ).css("display", "none");
    $( "#webif-headtable" ).attr('class', 'col-sm-12');
  }
  // disable logo and expand table a bit
  else if (width - tablewidth - infowidth - logowidth - 35  <= 0) {
    $( "#webif-pluginlogo" ).css("display", "none");
    $( "#webif-plugininfo" ).css("display", "");
    $( "#webif-headtable" ).attr('class', 'col-sm-9');
  }
  else {
    // show all elements as in the beginning
    $( "#webif-plugininfo" ).css("display", "");
    $( "#webif-pluginlogo" ).css("display", "");
    $( "#webif-headtable" ).attr('class', 'col-sm-7');
  }
  headwidth = $( "#webif-headtable" ).width();
  // minimize auto-refresh elements if necessary
  if (headwidth - buttonswidth <= 0) {
    $( "#webif-seconds" ).text(" s");
    $( "#webif-reload" ).text("");
    $( "#webif-close" ).text("");
  }
  else {
    // revert auto-refresh elements
    $( "#webif-seconds" ).text($( "#webif-seconds_orig" ).text());
    $( "#webif-reload" ).text($( "#webif-reload_orig" ).text());
    $( "#webif-close" ).text($( "#webif-close_orig" ).text());
  }
  // adjust height of top element based on height of table and other elements
  let headheight = $( "#webif-navbar" ).outerHeight(true);
  $('#webif-lowercontent').css('margin', headheight+'px auto 0');
  $('#webif-tabs').css('top', headheight+'px');
  let topheight = headheight + $( "#webif-tabs" ).outerHeight(true);
  $('#resize_wrapper').css('top', topheight+'px');
  $.fn.dataTable.tables({ visible: true, api: true }).fixedHeader.headerOffset( topheight );
}

function initHeader() {
  $( "#webif-navbar" ).show();
  calculateHeadtable();
  responsiveHeader();
}
//const resizeObserver = new ResizeObserver(entries => responsiveHeader() );
addEventListener('DOMContentLoaded', initHeader, false);

addEventListener('resize', responsiveHeader, false);

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
      name: false,
      cb : function(){},
      start : function(cb,iv,sd,rp){
          var elm = this;
          clearInterval(this.timeout);
          this.running = true;
          if(cb) {this.cb = cb; this.name = cb.toString().match(/{([^}]+)}/)[1].replace(/\r?\n|\r/g, "").replace(';', '').replace(/\s\s+/g, '')};
          if(iv) this.iv = iv;
          if(rp != null) this.rp = rp;
          if(sd) elm.execute(elm);
					if(iv != 0)
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
					console.log("Stopping timer " + this.name + " because stop command received");
      },
      update : function(params){
          for (key in params)
            if(params[key] != null) window[key] = params[key];
          document.getElementById("update_active").checked = window.update_active;
          document.getElementById("update_interval").value = window.update_interval / 1000;
          console.log("Updating timer " + this.name + " with params: " + JSON.stringify(params) + " interval is " + window.update_interval + ", active " + window.update_active);
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
							console.log("Stopping timer " + this.name + " because interval is set to " + iv);
							this.stop();
						}
					else
						{
            	this.start(false,iv,sd);
							console.log("Starting timer " + this.name + " with interval " + iv + " instatrigger " + sd);
						}
      }
  };
  return timer;
}
