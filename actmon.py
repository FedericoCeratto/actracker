
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



class ActMon(object):

    def __init__(self):
        homedir = os.path.expanduser('~')
        self._conf_dir_name = BaseDirectory.save_config_path('actracker')
        self._log_dir_name = BaseDirectory.save_data_path('actracker')
        self._conf_fname = os.path.join(self._conf_dir_name, 'conf.json')
        self._load_conf()
        self._load_log()
        self._last_application = ('', '')

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
                'Iceweasel': [
                    ('Hacker News.*', ('reading', 'tech_read')),
                    ('Slashdot.*', ('reading', 'tech_read')),
                    ('Scribd.*', ('reading',)),
                    ('Inbox.*Gmail', ('email',)),
                ],
                'Pidgin': [],
                'Chromium': [],
                'X-terminal-emulator': [
                    ('.*packaging.* - VIM', ('packaging','vim')),
                    ('.*projects.* - VIM', ('coding','vim')),
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
        except IOError:
            d = {'au': {}, 'ad': {}}

        self._app_usage = Counter(d['au'])
        self._totcnt = sum(d['au'].values()) or 1
        self._app_usage_detail = defaultdict(Counter)
        for name, title_cnt in d['ad'].iteritems():
            self._app_usage_detail[name].update(title_cnt)

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
        while True:
            window = display.get_input_focus().focus
            application_name, title = self._get_application_name(window)
            self._last_application = (application_name, title)

            self._app_usage.update([application_name,])
            self._app_usage_detail[application_name].update([title,])

            gevent.sleep(1)
            self._totcnt += 1


    def start(self):
        """Start activity monitor greenlet
        """
        gevent.Greenlet.spawn(self._activity_monitor)

    def summary(self):
        """Generate activity summary

        :returns: dict
        """
        o = []
        tags_summary = Counter()

        for name, cnt in self._app_usage.most_common(10):
            o.append((cnt * 100.0 / self._totcnt, name, '', False))
            for title, wcnt in self._app_usage_detail[name].most_common(10):
                current = (name, title) == self._last_application
                o.append((wcnt * 100.0 / self._totcnt, '', title, current))

                tags = self._classify(name, title)
                tags_summary.update({t: wcnt for t in tags})

        ts = [(t, cnt * 100.0 / self._totcnt)
            for t, cnt in tags_summary.most_common(10)]

        return dict(app_usage=o, tags_summary=ts)
