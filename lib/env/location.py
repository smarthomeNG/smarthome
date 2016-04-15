
# lib/env/location.py

if sh.sun:
    sh.env.location.sunrise(sh.sun.rise().astimezone(sh.tzinfo()))
    sh.env.location.sunset(sh.sun.set().astimezone(sh.tzinfo()))

    sh.env.location.moonrise(sh.moon.rise().astimezone(sh.tzinfo()))
    sh.env.location.moonset(sh.moon.set().astimezone(sh.tzinfo()))
    sh.env.location.moonphase(sh.moon.phase())

    # setting day and night
    day = sh.sun.rise(-6).day != sh.sun.set(-6).day
    sh.env.location.day(day)
    sh.env.location.night(not day)
    
    # setting altitude/azimut
    azimut, altitude = sh.sun.pos()
    azimut = round(azimut,2)
    altitude = round(altitude,2)
    sh.env.location.azimut(azimut)
    sh.env.location.altitude(altitude)
