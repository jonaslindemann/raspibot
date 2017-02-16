
from inputs import get_gamepad

x = 0
y = 0

while 1:
    events = get_gamepad()
    for event in events:
        #print(event.ev_type, event.code, event.state)
        
        if event.ev_type == "Absolute":
            if event.code == "ABS_Y":
                y = event.state/32768
                
            if event.code == "ABS_X":
                x = event.state/32768      
                
        print(x, y)