############
Requirements
############

********
Hardware
********

Any machine running with a x86 or x64 CPU should be fine as well as those with
an ARM CPU like Raspberry.
Among the hardware commonly used there are found

- Raspberry 1, Raspberry 2, Raspberry 3 (the latter one is **strongly recommended** due to better hardware)
  The majority of users utilize this hardware, see `questionnaire <https://knx-user-forum.de/forum/supportforen/smarthome-py/1112952-welche-hardware-nutzt-ihr-f%C3%BCr-euer-smarthomeng>`_
- Intel NUC (recommended for stability and speed, although more power needed. Supports normal SATA drives which is an advantage over SD-cards)
- ODroid
- Banana Pi
- Beagle Bone
- Virtual machine hosted on e.g. a NAS at home
- Docker

****************
Operating System
****************

Any Linux or Unix System with shell access to install the requirements and SmartHomeNG should be fine.
SmartHomeNG is at least tested on Raspbian and Debian Stretch (amd64)

If using a hardware platform without buffered real time clock it is mandatory to have a NTP daemon running to get time via internet.
Otherwise SmartHomeNG will not start due to missing time information.

Some libraries within SmartHomeNG still use functions depending on Unix flavour.
