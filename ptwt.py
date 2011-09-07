#!/usr/bin/env python

import sys
import os
import httplib2
import string

from secret import *
from restapi import OAuth_Single
from restapi import Client

conn = None

commands = {
    'help': lambda twitter, args: usage(args),
    'exit': lambda twitter, args: quit(args),
    'quit': lambda twitter, args: quit(args),
    'auth': lambda twitter, args: auth_single(args),
    'ls'  : lambda twitter, args: lists(twitter, args),
    'htl' : lambda twitter, args: home_timeline(twitter, args),
    'utl' : lambda twitter, args: user_timeline(twitter, args),
    'ptl' : lambda twitter, args: public_timeline(twitter, args),
}

def usage(args):
    print 'usage: TODO'

def print_timeline(jsons):
    for json in jsons:
        print '%s: %s' % (json['user']['screen_name'], json['text'])
    
def home_timeline(twitter, args):
    statuses = twitter.statuses()

    jsons = statuses.home_timeline(conn)
    print_timeline(jsons)

def user_timeline(twitter, args):
    statuses = twitter.statuses()

    if args:
        screen_name = args[0]
        jsons = statuses.user_timeline(conn, screen_name = screen_name)
    else:
        jsons = statuses.user_timeline(conn)
    
    print_timeline(jsons)
        
def public_timeline(twitter, args):
    statuses = twitter.statuses()
    jsons = statuses.public_timeline(conn)
    print_timeline(jsons)

def lists(twitter, args):
    lists = twitter.lists()
    
    if args:
        screen_name = args[0]
        jsons = lists.all(conn, screen_name = screen_name)
    else:
        jsons = lists.all(conn)
    
    for json in jsons:
        slug = json['slug']
        des = json['description']
        if des:
            print '%s: %s' % (slug, des)
        else:
            print '%s' % slug

def auth_single(args):
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
        auth_single(args)
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
