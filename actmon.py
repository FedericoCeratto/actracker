
from collections import Counter, defaultdict
from datetime import datetime
import Xlib.display
import gevent
import json
import string
import os
import os.path
import re
from xdg import BaseDirectory
from time import time
import ctypes

UPDATE_INTERVAL = 1
ACTIVITY_SLOT_SIZE = 10  #ms

class XScreenSaverInfo( ctypes.Structure):
  """ typedef struct { ... } XScreenSaverInfo; """
  _fields_ = [('window',      ctypes.c_ulong), # screen saver window
              ('state',       ctypes.c_int),   # off,on,disabled
              ('kind',        ctypes.c_int),   # blanked,internal,external
              ('since',       ctypes.c_ulong), # milliseconds
              ('idle',        ctypes.c_ulong), # milliseconds
              ('event_mask',  ctypes.c_ulong)] # events

class ActMon(object):

    def __init__(self, debug=False):
        homedir = os.path.expanduser('~')
        self._conf_dir_name = BaseDirectory.save_config_path('actracker')
        self._log_dir_name = BaseDirectory.save_data_path('actracker')
        self._conf_fname = os.path.join(self._conf_dir_name, 'conf.json')
        self._load_conf()
        self._load_log()
        self._last_application = ('', '')
        self.activity_counter = {}
        self._current_day = datetime.now().day
        self.debug = debug

    def _load_conf(self):
        """Load configuration from disk
        """
        print "Reading conf %s" % self._conf_fname
        try:
            with open(self._conf_fname) as f:
                self.conf = json.load(f)
        except IOError:
            print "Conf file not found."
            self._create_conf_dir()

    def _create_conf_dir(self):
        """Create configuration directory, generate default conf
        """
        if not os.path.isdir(self._conf_dir_name):
            print "Creating conf dir %s" % self._conf_dir_name
            os.mkdir(self._conf_dir_name)

        self.conf = {
            'port': 8000,
            'classifiers': {
                'Firefox': [
                    ('Hacker News.*', ('reading')),
                ],
                'Pidgin': [],
                'Chromium': [],
                'X-terminal-emulator': [
                    ('.* - VIM', ('vim',)),
                ],
            },
        }
        self._save_conf()


    def _save_conf(self):
        """Save configuration to disk
        """
        tmpfn = "%s.tmp" % self._conf_fname
        with open(tmpfn, 'w') as f:
            json.dump(self.conf, f, indent=1)

        os.rename(tmpfn, self._conf_fname)

    def _create_empty_log(self):
        self._app_usage = Counter()
        self._totcnt = 1
        self._app_usage_detail = defaultdict(Counter)

    def _load_log(self):
        """Load statistics from disk
        """
        now = datetime.now()
        fname = "%s.log" % now.strftime('%Y-%m-%d')
        fn = os.path.join(self._conf_dir_name, fname)
        try:
            print "Loading ", fn
            with open(fn) as f:
                d = json.load(f)

            print "Log loaded from %s" % fn
            self._app_usage = Counter(d['au'])
            self._totcnt = sum(d['au'].values()) or 1
            self._app_usage_detail = defaultdict(Counter)
            for name, title_cnt in d['ad'].iteritems():
                self._app_usage_detail[name].update(title_cnt)

        except IOError:
            self._create_empty_log()


    def save_log(self):
        """Save statistics to disk
        """
        now = datetime.now()
        fname = "%s.log" % now.strftime('%Y-%m-%d')
        fn = os.path.join(self._conf_dir_name, fname)
        tmp_fn = "%s.tmp" % fn

        print "Writing %s" % fn
        d = {'au': self._app_usage, 'ad': self._app_usage_detail}
        try:
            with open(tmp_fn, 'w') as f:
                json.dump(d, f)

            os.rename(tmp_fn, fn)
        except Exception, e:
            print("Exception %s while saving" % e)


    @classmethod
    def _get_application_name(self, window):
        while True:
            if isinstance(window, int):
                return 'Unknown', 'Unknown'

            wmclass = window.get_wm_class()
            if not wmclass:
                window = window.query_tree().parent # walk up
                continue

            title = window.get_wm_name()
            if not title:
                window = window.query_tree().parent # walk up
                continue

            application_name = wmclass[1]
            title = filter(lambda x: x in string.printable, title)
            return application_name, title

    def _classify(self, application_name, title):
        """Classify an activity using regexps. If no classifier is matched,
        'other' is returned.

        :returns: list - one or more tags
        """
        try:
            classifiers = self.conf['classifiers'][application_name]
        except KeyError:
            return ('other', )

        for regex, tags in classifiers:
            if re.match(regex, title):
                return tags

        return ('other', )


    def _activity_monitor(self):
        """Sample user activity
        """
        display = Xlib.display.Display()
        km_mon = self._keyboard_mouse_activity_monitor()

        while True:
            gevent.sleep(UPDATE_INTERVAL)
            #gevent.Timeout(UPDATE_INTERVAL).start()
            #try:
            #    gevent.sleep(UPDATE_INTERVAL * 2)
            #except gevent.Timeout, t:
            #    pass
            if self._day_has_changed():
                self.save_log()
                self._create_empty_log()


            window = display.get_input_focus().focus
            application_name, title = self._get_application_name(window)
            self._last_application = (application_name, title)

            activity_ms = next(km_mon)

            if activity_ms and activity_ms < 20:
                # Do not count if the user has been idle for > 20 seconds
                self._app_usage.update([application_name,])
                self._app_usage_detail[application_name].update([title,])
                self._totcnt += 1

                self._update_km_activity(activity_ms)


    def _update_km_activity(self, ms):
        slot = int(ms * 1000 / ACTIVITY_SLOT_SIZE)
        try:
            self.activity_counter[slot] += 1
        except KeyError:
            print 'filling slots'
            self.activity_counter[slot] = 1
            for s in xrange(slot):
                if s not in self.activity_counter:
                    self.activity_counter[s] = 0


    def _keyboard_mouse_activity_monitor(self):
        """Monitor keyboard and mouse for user activity
        """

        previous_activity_time = None
        xlib = ctypes.cdll.LoadLibrary('libX11.so.6')
        dpy = xlib.XOpenDisplay(os.environ['DISPLAY'])
        root = xlib.XDefaultRootWindow(dpy)
        xss = ctypes.cdll.LoadLibrary('libXss.so.1')
        xss.XScreenSaverAllocInfo.restype = ctypes.POINTER(XScreenSaverInfo)

        while True:
            xss_info = xss.XScreenSaverAllocInfo()
            xss.XScreenSaverQueryInfo(dpy, root, xss_info)
            ms = xss_info.contents.idle

            last_activity_time = time() - ms / 1000.0

            if previous_activity_time is None:
                previous_activity_time = last_activity_time
                yield None

            else:
                delta = last_activity_time - previous_activity_time
                if delta < 0.001:
                    print 'no activity', last_activity_time, previous_activity_time, delta
                    yield None

                else:
                    print 'activity detected:', last_activity_time, previous_activity_time, delta
                    yield delta
                    previous_activity_time = last_activity_time

    def _day_has_changed(self):
        day = datetime.now().day
        if day == self._current_day:
            return False

        self._current_day = day
        return True



    def start(self):
        """Start activity monitor greenlet
        """
        gevent.Greenlet.spawn(self._activity_monitor)


    # Webapp methods
    def summary(self):
        """Generate activity summary.

        :returns: dict
        """
        o = []
        tags_summary = Counter()

        for name, cnt in self._app_usage.most_common(10):
            o.append((cnt * 100.0 / self._totcnt, name, '', False, []))
            for title, wcnt in self._app_usage_detail[name].most_common(10):
                current = (name, title) == self._last_application

                tags = self._classify(name, title)
                tags_summary.update({t: wcnt for t in tags})

                o.append((wcnt * 100.0 / self._totcnt, '', title, current, tags))

        ts = [(t, cnt * 100.0 / self._totcnt)
            for t, cnt in tags_summary.most_common(10)]

        return dict(app_usage=o, tags_summary=ts, tot_cnt=self._totcnt)

    def history(self, start=None, end=None):
        """Generate activity history charts.

        :returns: dict
        """
        self.save_log()
        days = []
        tag_names = set()
        fnames = [f for f in os.listdir(self._conf_dir_name) if f.endswith('.log')]
        fnames = sorted(fnames)
        for fn in fnames:
            if not fn.endswith('.log'):
                continue

            fn = os.path.join(self._conf_dir_name, fn)
            try:
                with open(fn) as f:
                    d = json.load(f)

                print "Log loaded from %s" % fn
            except IOError, e:
                print e #FIXME
                continue

            tags_summary = Counter()
            ad = d['ad']
            for name in ad:
                for title, wcnt in ad[name].iteritems():
                    tags = self._classify(name, title)
                    tags_summary.update({t: wcnt for t in tags})
                    tag_names.update(tags)

            days.append((fn, tags_summary))

        return dict(days=days, tags=sorted(tag_names))

    def kmactivity(self):
        out = []
        max_val = max(self.activity_counter.itervalues())
        for x in sorted(self.activity_counter):
            out.append((x * ACTIVITY_SLOT_SIZE, self.activity_counter[x]))

        return dict(act=out, max_val=max_val)

    def update_classifiers(self, form):
        """
        """
        classifiers = {}
        cnt = 0
        form = sorted(form)
        while form:
            application_name = form.pop(0)[1].strip()
            regex = form.pop(0)[1]
            tags = form.pop(0)[1].strip()

            if not application_name:
                continue

            try:
                re.compile(regex)
            except Exception, e:
                raise Exception("Unable to compile regexp %r for %r" % (regex, application_name))

            tags = [t.strip() for t in tags.split(',')] or ['other', ]

            if application_name not in classifiers:
                classifiers[application_name] = []

            classifiers[application_name].append((regex, tags))
            cnt += 1

        self.conf['classifiers'] = classifiers
        self._save_conf()

        return cnt
