# Script for ioBroker for monitoring Zehnder Comfoair q-Series

Thanks to Dirk Paessler and the Team of PRTG. i found their implementation for monitoring Zehnder Comfoair q-Series Ventilation Systems and adapted it for ioBroker.

It makes use of the Open Source library PyComfoConnect found here: https://github.com/michaelarnauts/comfoconnect 

One requirement is to install this library.

In ioBroker i use the Adapter Simple RESTful API to write the values into the database.



The py-script needs to run on somewhere in the network. I am running it on the ioBroker-Server itself. 

I am using Cron and run it every 5 minutes. I added a value "last update", that is not really necessary as ioBroker has a compareable value itself. The script also writes all values to a file zehnder.json. I use that also for debugging.



I am trying to add the Counter that shows the next "programm-switch", but until now i wasn't able to figure out what type of values is delivered from the comfoair Q.



To use it, you have to enter the following values:

- comfoconnect_ip: IP of comfoconnect lan-c
- comfoconnect_pin: PIN of comfoconnect lan-c
- ioBroker: IP-Address:port of ioBroker
- if you want another path inside ioBroker you should also change dp 



As last point, i am not an experienced coder, so this could be done much better and more effective. also error handling is... well basically it shows the error if one occurs...

Feel free to improve it and share it with the community.



Currently it is not possible to do write/set-operations.



It is only tested on comfoair q 350. 