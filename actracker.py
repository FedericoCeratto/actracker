#!/usr/bin/env python


import bottle
from argparse import ArgumentParser
from gevent import monkey; monkey.patch_all()
from setproctitle import setproctitle

from actmon import ActMon

am = None

# Webapp routes

@bottle.route('/')
@bottle.view('index')
def route_index():
    return am.summary()

@bottle.route('/history')
@bottle.view('history')
def route_history():
    return am.history()

@bottle.route('/activity')
@bottle.view('kmactivity')
def route_kmactivity():
    return am.kmactivity()

@bottle.route('/conf')
@bottle.view('conf')
def route_conf():
    return {'conf': am.conf, 'msg': ''}

@bottle.post('/conf')
@bottle.view('conf')
def route_post_conf():
    try:
        cnt = am.update_classifiers(bottle.request.forms.items())
        msg = "Saved %d classifiers" % cnt

    except Exception, e:
        msg = "Error: %s" % e

    return dict(conf=am.conf, msg=msg)



def parse_args():
    """Parse command-line options and args
    """
    ap = ArgumentParser()
    ap.add_argument('-d', '--debug', action='store_true', help='debugging mode')
    args = ap.parse_args()
    return args


def main():
    global am
    args = parse_args()

    setproctitle('actracker')

    am = ActMon(debug=args.debug)
    am.start()

    try:
        bottle.run(port=am.conf['port'], server='gevent', debug=args.debug)
    except Exception, e:
        print e
        raise

    am.save_log()
    print 'Bye'

if __name__ == '__main__':
    main()
