#!/usr/bin/env python


import bottle
from gevent import monkey; monkey.patch_all()
from setproctitle import setproctitle

from actmon import ActMon

am = None

# Webapp routes

@bottle.route('/')
@bottle.view('index')
def route_index():

    return am.summary()

@bottle.route('/conf')
@bottle.view('conf')
def route_conf():

    return am.summary()


def main():

    setproctitle('actracker')
    #from trayicon import create_tray_icon
    #create_tray_icon()

    global am
    am = ActMon()
    am.start()

    try:
        bottle.run(port=am.conf['port'], server='gevent')
    except Exception, e:
        print e
        raise

    am.save_log()
    print 'Bye'

if __name__ == '__main__':
    main()
