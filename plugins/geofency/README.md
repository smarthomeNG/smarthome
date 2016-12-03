# GEOFENCY

Requirements
============

None so far

Configuration
=============

plugin.conf
-----------
<pre>
[geofency]
    class_name = Geofency
    class_path = plugins.geofency
    port = 2828                            # Which Port to run the Web Server on
    logic = geofency
</pre>

You need to create a logic that will handle your individual customization of what shoud happen when a GeoFency POST request comes in.

Example:

<pre>
if (by == "geofency"):
    if (value["device"] == "534538CC-6D456-4459-B045-0C345345309101"):
        if (value["name"] == "HOME"):
            if (value["entry"] == "1"):
                sh.Service.Monitoring.MyPresence(True)
            else:
                sh.Service.Monitoring.MyPresence(False)
</pre>
