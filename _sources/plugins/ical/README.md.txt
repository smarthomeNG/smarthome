# iCal

## Changelog
1.5.4:
- added parameter handle_login to control logging of calendar uri login data.

1.5.3:
- fixed conversion from calendar defined timezones in smarthomeNG configured timezone.

1.5.2:
- Use domain name as filename if no alias is defined
- Parse calendars in plugin.yaml more robust

1.5.1:
- Fix reading offline files and line breaks
- Updated code
- using network library instead of fetch_url to download online calendars into var/ical
- possibility to disable https verification when using online calendars
- user documentation
- updated plugin.yaml
- new parameters: directory and timeout to configure download of online calendars
- implement a "prio" attribute to choose which information in an entry should be used
