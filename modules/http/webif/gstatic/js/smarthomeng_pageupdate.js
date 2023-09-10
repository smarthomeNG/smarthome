/**
 * enables or disables the auto refresh checkbox based on form input for interval
*/
function set_update_active() {
  if (document.body.contains(document.getElementById("update_interval")) && (document.getElementById("update_interval").value.length == 0 || document.getElementById("update_interval").value == 0 || window.update_blocked == true))
  {
    $('input[name=update_active]').attr('disabled','disabled');
    document.getElementById("update_active").checked = false;
    window.update_active = false;
    $('input[name=update_active]').attr('title', 'Automatische Aktualisierung nicht möglich/deaktiviert');
  }
  else if (document.body.contains(document.getElementById("update_active")))
  {
    window.update_active = document.getElementById("update_active").checked;
    $('input[name=update_active]').removeAttr('disabled');
  }
}

/**
 * sets the update interval based on form input and setting via JS
*/
function set_update_interval() {
  if ( document.body.contains(document.getElementById("update_active")) )
    window.update_active = document.getElementById("update_active").checked;
  if ( document.body.contains(document.getElementById("update_interval")) )
    window.update_interval = document.getElementById("update_interval").value * 1000;
  if (window.update_active)
  {
    refresh.set_interval(update_interval, false);
    setCookie("update_interval", update_interval, 365, window.pluginname);
    setCookie("update_active", update_active, 365, window.pluginname);
    console.log("Set Refresh Interval to " + update_interval + ", active " + update_active);
  }
  else {
    setCookie("update_active", update_active, 365, window.pluginname);
    refresh.stop();
  }
}


/**
 * initialize form values correctly and update active checkbox based on interval value (disabled on 0)
*/
$(window).on('load', function (e) {
  //setCookie('update_interval', '', 0, window.pluginname);
  //setCookie('update_active', '', 0, window.pluginname);
  let cookie_interval = getCookie("update_interval");
  let cookie_active = getCookie("update_active");
  if (cookie_active !== "")
    window.update_active = cookie_active;
  if (cookie_interval !== "")
  {
    if (window.update_active == true)
      refresh.set_interval(cookie_interval, false);
    else
      window.update_interval = cookie_interval;
    if ( document.body.contains(document.getElementById("update_interval")) )
      document.getElementById("update_interval").value = cookie_interval;
  }

  if ( document.body.contains(document.getElementById("update_active")) )
    document.getElementById("update_active").checked = window.update_active;
  if ( document.body.contains(document.getElementById("update_interval")) )
    document.getElementById("update_interval").value = window.update_interval / 1000;
  set_update_active();
  set_update_interval();
  if ( document.body.contains(document.getElementById("update_interval")) ) {
    let interval_input = document.getElementById("update_interval");
    interval_input.addEventListener('input', event => {
      set_update_active();
    });
  }
});
