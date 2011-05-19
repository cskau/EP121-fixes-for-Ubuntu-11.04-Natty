#!/usr/bin/env python

import os, sys, xaut, threading # time
from struct import *


active, orientation, keyboard = True, True, True


codetbl={0:'X',1:'Y',4:'ScanCode',40:'Misc(Multi?)',330:'Touch',325:'ToolFinger'}
typetbl={0:'Report Sync',1:'Key',2:'Relative?',3:'Absolute',4:'Misc'}

def printEv(evtimestamp,evtimestamp2,evtype,evcode,evvalue):
    if evtype == 0:
        print "Event: time %f, -------------- Report Sync ------------" % (evtimestamp)
    print "Event: time %f, type %i (%s), code %i (%s), value %i" % (evtimestamp,evtype,typetbl[evtype],evcode,codetbl[evcode],evvalue)



class WMIListener(threading.Thread):
    
    def __init__ (self):
        super(WMIListener, self).__init__()
        self._stop = threading.Event()
    
    def stop(self):
        self._stop.set()
    
    def stopped(self):
        return self._stop.isSet()
    
    def run(self):
        global active, orientation#, keyboard
        pipe = open('/dev/input/by-path/platform-eeepc-wmi-event','r')
        while True:
            evtimestamp,evtimestamp2,evtype,evcode,evvalue = unpack('qdhhi', pipe.read(24))
            if evtype == 4 and evcode == 4 and evvalue == 0xf7: # keyboard button
                None
                #keyboard = not keyboard # toggle keyboard
            elif evtype == 4 and evcode == 4 and evvalue == 0xf6: # screen button
                active = not active # toggle touch
            elif evtype == 4 and evcode == 4 and evvalue == 0xf5: # orientation lock
                orientation = not orientation # toggle flip
                if orientation:
                    os.system('xrandr -o normal && xinput set-prop "Wacom ISDv4 90 Pen stylus" "Wacom Rotation" 0')
                else:
                    os.system('xrandr -o left && xinput set-prop "Wacom ISDv4 90 Pen stylus" "Wacom Rotation" 1')

wmil = WMIListener()
wmil.start()


pipe = open('/dev/input/by-id/usb-eGalax_eMPIA_Technology_Inc._PCAP_MultiTouch_Controller-event-mouse','r')

mouse = xaut.mouse()
disp = xaut.display()

dw,dh = disp.w(),disp.h()
tw,th = 32767,32767

# default is 10, but for some reason this bugs up movement of 1,1 pixel
mouse.move_delay(0)

xys = [[mouse.x(),mouse.y()],[-1,-1]] # multitouch is really "dualtouch"
touch = [0,0]
i = 0
scrolled = False
touch_tmp,xys_tmpx,xys_tmpy = 0,0,0

while True:
    try:
        data = pipe.read(24)
    except KeyboardInterrupt:
        wmil.stop()
        sys.exit(1)
    
    evtimestamp,evtimestamp2,evtype,evcode,evvalue = unpack('qdhhi',data)
    
    if not active:
        continue
    
    if evtype == 0: # Report Sync
        
        def convert_xy(xys_tmpx,xys_tmpy):
            if orientation:
                return ( int((float(xys_tmpx)/tw)*dw), int((float(xys_tmpy)/th)*dh) )
            return ( dh-int((float(xys_tmpy)/th)*dh), int((float(xys_tmpx)/tw)*dw) )
        
        def update_mouse(xys_newx,xys_newy):
            xys[i][0], xys[i][1] = xys_newx, xys_newy
            #assert xys[0][0]<=dw and xys[0][1] <= dh, ""
            mouse.move( xys[0][0], xys[0][1] )
        
        xys_newx,xys_newy = convert_xy(xys_tmpx,xys_tmpy)
        
        if i == 1 and touch[0] == 1 and touch[1] == 0 and touch_tmp == 1:
            scrolled = False
        if i == 1 and touch[0] == 1 and touch[1] == 1:
            if touch_tmp == 0 and not scrolled:
                mouse.click(3) # right click
                touch[i] = touch_tmp
                continue
            mouse.btn_up(1)
            if xys[i][1] > xys_newy+5:
                scrolled = True
                mouse.click(4) # scroll down
            elif xys[i][1] < xys_newy-5:
                scrolled = True
                mouse.click(5) # scroll up
            update_mouse(xys_newx,xys_newy)
            touch[i] = touch_tmp
            continue
        
        update_mouse(xys_newx,xys_newy)
        
        if i == 0:
            if touch[1] == 0:
                if touch[0] == 1 and touch_tmp == 0:
                    mouse.btn_up(1)
                elif touch[0] == 0 and touch_tmp == 1:
                    mouse.btn_down(1) # left down
        
        touch[i] = touch_tmp
        
    elif evtype == 1: # Key
        if evcode == 330:
            touch_tmp = evvalue
    elif evtype == 3: # Absolute
        touch_tmp = 1 # we're not explicitely told :(
        if evcode == 0: # X
            xys_tmpx = evvalue
        elif evcode == 1: # Y
            xys_tmpy = evvalue
        elif evcode == 40: # Which multitouch point are we getting info on?
            i = evvalue
