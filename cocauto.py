# -*- coding: utf-8 -*-
# sudo pip install pyvbox
# from https://gist.github.com/thuandt/e9cf284d7eb2d61dd99a

from time import sleep
import virtualbox

genymotion_vm_name = "Samsung Galaxy S3 - 4.3 - API 18 - 720x1280"

vbox = virtualbox.VirtualBox()
genymotion_vm = vbox.find_machine(genymotion_vm_name)
genymotion_session = genymotion_vm.create_session()

while True:
    genymotion_session.console.mouse.put_mouse_event_absolute(360,223,0,0,0)
    genymotion_session.console.mouse.put_mouse_event_absolute(360,223,0,0,1)
    genymotion_session.console.mouse.put_mouse_event_absolute(360,223,0,0,0)
    print "click"
    sleep(60)
