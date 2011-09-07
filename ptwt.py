#!/usr/bin/env python

import sys
import os
import httplib2
import string
import getopt

from secret import *
from restapi import OAuth_Single
from restapi import Client

conn = None

commands = {
    'help': lambda twitter, args: usage(),
    'exit': lambda twitter, args: quit(),
    'quit': lambda twitter, args: quit(),
    'auth': lambda twitter, args: auth_single(),
    'ls'  : lambda twitter, args: lists(twitter, args),
    'htl' : lambda twitter, args: home_timeline(twitter, args),
    'utl' : lambda twitter, args: user_timeline(twitter, args),
    'ptl' : lambda twitter, args: public_timeline(twitter, args),
}

def usage():
    print 'usage: TODO'

def print_timeline(jsons, verbose):
    for json in jsons:
        screen_name = json['user']['screen_name']
        name = json['user']['name']
        text = json['text']
        created_at = json['created_at']
        
        if verbose:
            print '%s: %s at \'%s\'' % (screen_name, name, created_at)
            print '%s' % text
            print
        else:
            print '%s: %s' % (screen_name, text)
    
def home_timeline(twitter, args):
    statuses = twitter.statuses()

    try:
        opts, args = getopt.getopt(args, 'v')
    except getopt.GetoptError:
        usage()
        return

    verbose = False
    for o, a in opts:
        if o == '-v':
            verbose = True
        else:
            assert False, 'unexcepted option'

    jsons = statuses.home_timeline(conn)
    print_timeline(jsons, verbose)

def user_timeline(twitter, args):
    statuses = twitter.statuses()

    try:
        opts, args = getopt.getopt(args, 'v')
    except getopt.GetoptError:
        usage()
        return

    verbose = False
    for o, a in opts:
        if o == '-v':
            verbose = True
        else:
            assert False, 'unexcepted option'

    if args:
        screen_name = args[0]
        jsons = statuses.user_timeline(conn, screen_name = screen_name)
    else:
        jsons = statuses.user_timeline(conn)
    
    print_timeline(jsons, verbose)
        
def public_timeline(twitter, args):
    statuses = twitter.statuses()
    
    try:
        opts, args = getopt.getopt(args, 'v')
    except getopt.GetoptError:
        usage()
        return

    verbose = False
    for o, a in opts:
        if o == '-v':
            verbose = True
        else:
            assert False, 'unexcepted option'

    jsons = statuses.public_timeline(conn)
    print_timeline(jsons, verbose)

def lists(twitter, args):
    lists = twitter.lists()

    try:
        opts, args = getopt.getopt(args, 'v')
    except getopt.GetoptError:
        usage()
        return

    verbose = False
    for o, a in opts:
        if o == '-v':
            verbose = True
        else:
            assert False, 'unexcepted option'
    
    if args:
        screen_name = args[0]
        jsons = lists.all(conn, screen_name = screen_name)
    else:
        jsons = lists.all(conn)
    
    for json in jsons:
        slug = json['slug']
        des = json['description']
        if verbose:
            print '%s: \"%s\"' % (slug, des)
        else:
            print '%s' % slug

def auth_single():
    global conn
    try:
        conn = OAuth_Single(CONSUMER_KEY, CONSUMER_SECRET, TOKEN_KEY, TOKEN_SECRET)
    except Exception:
        print 'Failed'

def interactive(twitter):
    while True:
        sys.stdout.write('>>> ')
        try:
            cmd_args = string.split(raw_input())
        except:
            print
            return

        if not cmd_args:
            continue
        
        cmd, args = cmd_args[0], cmd_args[1:]
        try:
            commands[cmd](twitter, args)
        except KeyError:
            print 'Unknow command:', cmd

def one_shot(twitter):
    cmd, args = sys.argv[1], sys.argv[2:]

    try:
        auth_single()
        commands[cmd](twitter, args)
    except KeyError:
        print 'Unknow command:', cmd
        
def main():
    twitter = Client('twitter')

    if len(sys.argv) == 1:
        interactive(twitter)
    else:
        one_shot(twitter)
        
if __name__ == '__main__':
    main()
