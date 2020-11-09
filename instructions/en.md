<span style="color: #ff0000;"><strong>Using HLC Pattern skill </span>

- "Hey snips/Alice"

then try one of the following 

- "change your LED pattern please",
- "change your h l c pattern ",
- "change your LED pattern",
- "set a new LED pattern",
- "change leds"

When asked which option to use, select one of those options by saying

(exchange # for the number of your choice)
- "option #" 
- "number #"
- "3"

<span style="color: green;">NOTE:</span> During this process Alice will action some 'sudo' commands. They are as follows:

- cp command : to copy the modified service file back to /etc/systemd/system/hermesledcontrol.service
- sudo systemctl daemon-reload
- sudo systemctl restart hermesledcontrol
   
