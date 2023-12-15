# Misc Options Calculators

## Running

Use a web server (eg nginx) with *siteroot* as the sites root, then use reverse proxy to use the Flask webserver in *flaskserv* for requests to /script/\*.py, which must of course be started beforehand.
This can be done with the *waitress-serve* command. See the appropriate Flask docs for more.
