/**
 * enables or disables the auto refresh checkbox based on form input for interval
*/
function set_update_active() {
  if(document.getElementById("update_interval").value.length == 0 || document.getElementById("update_interval").value == 0)
  {
    $('input[name=update_active]').attr('disabled','disabled');
    document.getElementById("update_active").checked = false;
    window.update_active = false;
  }
  else
  {
    window.update_active = document.getElementById("update_active").checked;
    $('input[name=update_active]').removeAttr('disabled');
  }
}

/**
 * sets the update interval based on form input and setting via JS
*/
function set_update_interval() {
  window.update_active = document.getElementById("update_active").checked;
  window.update_interval = document.getElementById("update_interval").value * 1000;
  if (window.update_active)
  {
    refresh.set_interval(update_interval, false);
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
  document.getElementById("update_interval").value = window.update_interval / 1000;
  document.getElementById("update_active").checked = window.update_active;
  set_update_active();
  let interval_input = document.getElementById("update_interval");
  interval_input.addEventListener('input', event => {
    set_update_active();
  });
});
