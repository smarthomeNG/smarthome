# lib/env/sunpos.py

import math

if sh.sun:
    # setting altitude/azimut
    # azimut, elevation = sh.sun.pos()

    # by default sh.sun.pos() will return the current position of sun in radians
    azimut_radians, elevation_radians = sh.sun.pos()

    # and it is unnecessary to calc again just for degrees:
    # azimut_degrees, elevation_degrees = sh.sun.pos(dt=time, degree=True)
    # better use this:
    azimut_degrees = math.degrees(azimut_radians)
    elevation_degrees = math.degrees(elevation_radians)

    sh.env.location.sun_position.azimut.degrees(round(azimut_degrees, 2), logic.lname)
    sh.env.location.sun_position.elevation.degrees(round(elevation_degrees, 2), logic.lname)
    sh.env.location.sun_position.azimut.radians(round(azimut_radians,2), logic.lname)
    sh.env.location.sun_position.elevation.radians(round(elevation_radians,2), logic.lname)
