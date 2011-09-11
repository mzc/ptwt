#!/usr/bin/env python

import sys
import string
import getopt
import subprocess

from secret import *
from restapi import OAuthOOB, OAuthConn
from restapi import Client

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHENTICATE_URL  = "https://api.twitter.com/oauth/authenticate"
ACCESS_TOKEN_URL  = "https://api.twitter.com/oauth/access_token"

commands = {
    'help': lambda oauth_conn, twitter, args: usage(),
    'exit': lambda oauth_conn, twitter, args: quit(),
    'quit': lambda oauth_conn, twitter, args: quit(),
    'ls'  : lambda oauth_conn, twitter, args: lists(oauth_conn, twitter, args),
    'htl' : lambda oauth_conn, twitter, args: home_timeline(oauth_conn, twitter, args),
    'utl' : lambda oauth_conn, twitter, args: user_timeline(oauth_conn, twitter, args),
    'ptl' : lambda oauth_conn, twitter, args: public_timeline(oauth_conn, twitter, args),
    'u'   : lambda oauth_conn, twitter, args: users_lookup(oauth_conn, twitter, args),
    'fr'  : lambda oauth_conn, twitter, args: friends(oauth_conn, twitter, args),
    'fo'  : lambda oauth_conn, twitter, args: followers(oauth_conn, twitter, args),
}

def usage():
    print 'usage: TODO'

def check_json_error(json):
    try:
        if json.has_key('errors'):
            return json['errors'][0]['message']
        elif json.has_key('error'):
            return json['error']
        else:
            return False
    except:
        return False

def prompt_error(json):
    error = check_json_error(json)
    if error:
        print error
        return True
    else:
        return False

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
    
def home_timeline(oauth_conn, twitter, args):
    statuses = twitter.Statuses()

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

    jsons = statuses.home_timeline(oauth_conn)
    if not prompt_error(jsons):
        print_timeline(jsons, verbose)

def user_timeline(oauth_conn, twitter, args):
    statuses = twitter.Statuses()

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
        jsons = statuses.user_timeline(oauth_conn, screen_name = screen_name)
    else:
        jsons = statuses.user_timeline(oauth_conn)

    if not prompt_error(jsons):
        print_timeline(jsons, verbose)
        
def public_timeline(oauth_conn, twitter, args):
    statuses = twitter.Statuses()
    
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

    jsons = statuses.public_timeline(oauth_conn)
    if not prompt_error(jsons):
        print_timeline(jsons, verbose)

def print_lists(jsons, verbose):
    for json in jsons:
        slug = json['slug']
        description = json['description']
        if verbose:
            print '%s: %s' % (slug, description)
        else:
            print '%s' % slug

def lists(oauth_conn, twitter, args):
    lists = twitter.Lists()

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

    if len(args) >= 2:
        # get the timeline of the specified list
        owner_screen_name, slug = args[0], args[1]
        jsons = lists.statuses(oauth_conn, owner_screen_name = owner_screen_name, slug = slug)
        if not prompt_error(jsons):
            print_timeline(jsons, verbose)
    else:
        # get all the lists of a specified user
        if args:
            screen_name = args[0]
            jsons = lists.all(oauth_conn, screen_name = screen_name)
        else:
            jsons = lists.all(oauth_conn)

        if not prompt_error(jsons):
            print_lists(jsons, verbose)
    
def print_users(jsons, verbose):
    for json in jsons:
        screen_name = json['screen_name']
        name = json['name']
        id_str = json['id_str']
        location = json['location']
        created_at = json['created_at']
        description = json['description']
        time_zone = json['time_zone']
        if verbose:
            print '%s: %s at %s (%s)' % (screen_name, name, location, time_zone)
            print '\tID: %s' % id_str
            print '\tCreated at: %s' % created_at
            print '\tDesc: %s' % description
        else:
            print '%s: %s at %s (%s)' % (screen_name, name, location, time_zone)
    
def users_lookup_by_screen_name(oauth_conn, users, args):
    screen_names = string.join(args, ',')
    jsons = users.lookup(oauth_conn, screen_name = screen_names)
    return jsons

def users_lookup_by_user_id(oauth_conn, users, args):
    user_id = string.join(args[0:100], ',') # TODO: improve it
    jsons = users.lookup(oauth_conn, user_id = user_id)
    return jsons

def users_lookup(oauth_conn, twitter, args):
    users = twitter.Users()

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
    if not args:
        usage()
        return

    jsons = users_lookup_by_screen_name(oauth_conn, users, args)
    if not prompt_error(jsons):
        print_users(jsons, verbose)

def friends(oauth_conn, twitter, args):
    friends = twitter.Friends()
    
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
        screen_names = args[0]
        users_int = friends.ids(oauth_conn, screen_name = screen_names)
    else:
        users_int = friends.ids(oauth_conn)
        
    if prompt_error(users_int):
        return

    users_string = map(str, users_int)
    
    users = twitter.Users()
    jsons = users_lookup_by_user_id(oauth_conn, users, users_string)
    if not prompt_error(jsons):
        print_users(jsons, verbose)

def followers(oauth_conn, twitter, args):
    followers = twitter.Followers()
    
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
        screen_names = args[0]
        users_int = followers.ids(oauth_conn, screen_name = screen_names)
    else:
        users_int = followers.ids(oauth_conn)

    if prompt_error(users_int):
        return

    users_string = map(str, users_int)
    
    users = twitter.Users()
    jsons = users_lookup_by_user_id(oauth_conn, users, users_string)
    if not prompt_error(jsons):
        print_users(jsons, verbose)

def interactive(oauth_conn, twitter):
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
            commands[cmd](oauth_conn, twitter, args)
        except KeyError:
            print 'Unknow command:', cmd

def one_shot(oauth_conn, twitter):
    cmd, args = sys.argv[1], sys.argv[2:]

    try:
        commands[cmd](oauth_conn, twitter, args)
    except KeyError:
        print 'Unknow command:', cmd

def authorize():
    oauth_oob = OAuthOOB(REQUEST_TOKEN_URL, AUTHENTICATE_URL, ACCESS_TOKEN_URL)
    oauth_conn = OAuthConn(CONSUMER_KEY, CONSUMER_SECRET)
    oauth_conn = oauth_oob.get_temp_credentials(oauth_conn)
    
    subprocess.call(['chromium', oauth_oob.temp_credentials_url])
    sys.stdout.write('PIN:')
    pin_code = raw_input()
    
    oauth_conn = oauth_oob.get_credentials(oauth_conn, pin_code)
    
    return oauth_conn
        
def main():
    twitter = Client('twitter')
    oauth_conn = authorize()

    if len(sys.argv) == 1:
        interactive(oauth_conn, twitter)
    else:
        one_shot(oauth_conn, twitter)
        
if __name__ == '__main__':
    main()
