#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os.path


class LogAnalyzer():
    """ Parses and summarizes nginx logfiles """

    def __init__(self, content, topcount=5):
        """ Initializing """
        self.summary = {
            "requests": {},
            "ips": {},
            "useragents": {}
        }

        self.topcount = topcount

        self.content = content

    def analyze(self):
        """ Reads and splits the access-log into our dictionary """
        lines = self.content.split("\n")
        loglist = []

        for s in lines:
            line = s.strip()
            if len(line) == 0: continue
            tmp = line.split(' ')
            ip = tmp[0]

            #not the finest way...get indices of double quotes
            doublequotes = LogAnalyzer.find_chars(line, '"')

            #get the starting/ending indices of request & useragents by their quotes
            request_start = doublequotes[0]+1
            request_end = doublequotes[1]
            useragent_start = doublequotes[4]+1
            useragent_end = doublequotes[5]

            request = line[request_start:request_end]
            useragent = line[useragent_start:useragent_end]

            #writing a dictionary per line into a list...huh...dunno
            loglist.append({
                "ip": ip,
                "request": request,
                "useragent": useragent
            })

        self.summarize(loglist)

    def summarize(self, cols):
        """ count occurences """
        for col in cols:
            if not col['request'] in self.summary['requests']:
                self.summary['requests'][col['request']] = 0
            self.summary['requests'][col['request']] += 1

            if not col['ip'] in self.summary['ips']:
                self.summary['ips'][col['ip']] = 0
            self.summary['ips'][col['ip']] += 1

            if not col['useragent'] in self.summary['useragents']:
                self.summary['useragents'][col['useragent']] = 0
            self.summary['useragents'][col['useragent']] += 1

    @staticmethod
    def find_chars(string, char):
        """ returns a list of all indices of char inside string """
        return [i for i, ltr in enumerate(string) if ltr == char]

