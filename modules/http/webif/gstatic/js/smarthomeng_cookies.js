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
      try {
        result = JSON.parse(result);
      }
      catch (e) {
      }
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
    try {
      cvalue = JSON.stringify(cvalue);
    }
    catch(e) {

    }
    d.setTime(d.getTime() + (exdays * 24 * 60 * 60 * 1000));
    let expires = "expires="+d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/plugin/" + path;
    console.log("Setting cookie " + cname + " for plugin " + path + " to " + cvalue + ", all cookies " + document.cookie);
  }

}
