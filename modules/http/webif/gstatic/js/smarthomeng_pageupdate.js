function getCookie(cname) {
  let name = cname + "=";
  let decodedCookie = decodeURIComponent(document.cookie);
  let ca = decodedCookie.split(';');
  for(let i = 0; i <ca.length; i++) {
    let c = ca[i];
    while (c.charAt(0) == ' ') {
      c = c.substring(1);
    }
    if (c.indexOf(name) == 0) {
      let result = c.substring(name.length, c.length);
      console.log("Reading cookie " + cname + " with value " + result);
      return result;
    }
  }
  return "";
}

function setCookie(cname, cvalue, exdays, path) {
  if (exdays === 0)
  {
    let expires = "expires=Thu, 01 Jan 1970 00:00:00 UTC";

    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/plugin/" + path;
    console.log("Deleting cookie " + cname + " for plugin " + path);
  }
  else
  {
    const d = new Date();
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/plugin/" + path;
    console.log("Setting cookie " + cname + " for plugin " + path + " to " + cvalue + ", all cookies " + document.cookie);
  }

}
/* setCookie('update_interval', '', 0, '');*/
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
    refresh.set_interval(update_interval, true);
    console.log("Set Refresh Interval to " + update_interval + ", active " + update_active);
  }
  else {
    refresh.stop();
  }
}

/**
 * initialize form values correctly and update active checkbox based on interval value (disabled on 0)
*/
$(window).on('load', function (e) {
  if ( document.body.contains(document.getElementById("update_active")) )
    document.getElementById("update_active").checked = window.update_active;
  if ( document.body.contains(document.getElementById("update_interval")) )
    document.getElementById("update_interval").value = window.update_interval / 1000;
  set_update_active();
  if ( document.body.contains(document.getElementById("update_interval")) ) {
    let interval_input = document.getElementById("update_interval");
    interval_input.addEventListener('input', event => {
      set_update_active();
    });
  }
});
