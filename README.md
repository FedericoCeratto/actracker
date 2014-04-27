actracker
=========

A simple user activity tracker.

Based on the ideas around [Quantified self](https://en.wikipedia.org/wiki/Quantified_Self), it tracks what you are doing based on:

* Focused windows
* Keyboard and mouse activity

Actracker tries to classify what you are doing (e.g. reading, coding, and so on) based on user-configurable rules.

It provides a graphical history of your computer usage in the last weeks or months.


Installation
------------

Use virtualenv on package-based Linux distributions! [Learn why](http://workaround.org/easy-install-debian)

    $ pip install actracker

Usage
-----

Run actracker as:

    $ ./actracker.py

And open in your browser:
http://127.0.0.1:8080

You can create or edit classification rules at:
http://127.0.0.1:8080/conf

To change the port number edit:
    ~/.config/actracker/conf.json
