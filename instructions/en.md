## Using HLC Pattern skill

### OPTION 1
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

### OPTION 2


try asking 

- "hey snips/alice"

- "change LEDs to google"
- "change LED pattern to alexa"

The Pattern options are :

- google
- alexa
- projectalice
- pgas
- kiboost


#### NOTE FOR WHEN USING THIS METHOD:
Due to the weird naming of the last two options try pronouncing it like the following 

(note the spaces)

- p g a s
- k i boost

Also some ASR's like pocketsphinx don't like the word LEDs. So a good default utternce, 
(but a little less natural), would be 

- "change alice lights to google"

or

- "change alice lights"

#### NOTE:
During this process Alice will action some 'sudo' commands. They are as follows:

- cp command : to copy the modified service file back to /etc/systemd/system/hermesledcontrol.service
- sudo systemctl daemon-reload
- sudo systemctl restart hermesledcontrol
   
