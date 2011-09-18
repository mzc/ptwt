#!/usr/bin/env python

import sys
import os
import errno
import string
import getopt
import subprocess
try:
    import simplejson as json
except ImportError:
    import json

from restapi import OAuthOOB, OAuthConn
from restapi import Client

REQUEST_TOKEN_URL = "https://api.twitter.com/oauth/request_token"
AUTHENTICATE_URL  = "https://api.twitter.com/oauth/authenticate"
ACCESS_TOKEN_URL  = "https://api.twitter.com/oauth/access_token"
CONSUMER_KEY      = 'dB2Uh0OXgDtAxp6KHK9Q'
CONSUMER_SECRET   = 'lKcsEGOtdNolro2aWBG1zwomhftIdKiimxPTaT3nSRo'

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

prog_name = None

def usage():
    print 'usage: ' + prog_name + ' <command> [<args>]'
    print 'The commands supported are:'
    print '    help             Show this usage'
    print '    exit/quit        Quit this program'
    print '    ls  [USER]       Show user\'s list'
    print '    ls  USER LIST    Show timeline of user\'s list'
    print '    htl              Show yours home timeline'
    print '    utl [USER]       Show user\'s user timeline'
    print '    ptl              Show public timetline'
    print '    u   USER         Show user\'s personal information'
    print '    fr  [USER]       Show whom the user are following'
    print '    fo  [USER]       Show who are following the user'

def check_entity_error(entity):
    try:
        if entity.has_key('errors'):
            return entity['errors'][0]['message']
        elif entity.has_key('error'):
            return entity['error']
        else:
            return False
    except:
        return False

def prompt_error(entity):
    error = check_entity_error(entity)
    if error:
        print error
        return True
    else:
        return False

def print_timeline(entities, verbose):
    for entity in entities:
        screen_name = entity['user']['screen_name']
        name = entity['user']['name']
        text = entity['text']
        created_at = entity['created_at']
        
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

    entities = statuses.home_timeline(oauth_conn)
    if not prompt_error(entities):
        print_timeline(entities, verbose)

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
        entities = statuses.user_timeline(oauth_conn, screen_name = screen_name)
    else:
        entities = statuses.user_timeline(oauth_conn)

    if not prompt_error(entities):
        print_timeline(entities, verbose)
        
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

    entities = statuses.public_timeline(oauth_conn)
    if not prompt_error(entities):
        print_timeline(entities, verbose)

def print_lists(entities, verbose):
    for entity in entities:
        slug = entity['slug']
        description = entity['description']
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
        entities = lists.statuses(oauth_conn, owner_screen_name = owner_screen_name, slug = slug)
        if not prompt_error(entities):
            print_timeline(entities, verbose)
    else:
        # get all the lists of a specified user
        if args:
            screen_name = args[0]
            entities = lists.all(oauth_conn, screen_name = screen_name)
        else:
            entities = lists.all(oauth_conn)

        if not prompt_error(entities):
            print_lists(entities, verbose)
    
def print_users(entities, verbose):
    for entity in entities:
        screen_name = entity['screen_name']
        name = entity['name']
        id_str = entity['id_str']
        location = entity['location']
        created_at = entity['created_at']
        description = entity['description']
        time_zone = entity['time_zone']
        if verbose:
            print '%s: %s at %s (%s)' % (screen_name, name, location, time_zone)
            print '\tID: %s' % id_str
            print '\tCreated at: %s' % created_at
            print '\tDesc: %s' % description
        else:
            print '%s: %s at %s (%s)' % (screen_name, name, location, time_zone)
    
def users_lookup_by_screen_name(oauth_conn, users, args):
    screen_names = string.join(args, ',')
    entities = users.lookup(oauth_conn, screen_name = screen_names)
    return entities

def users_lookup_by_user_id(oauth_conn, users, args):
    user_id = string.join(args[0:100], ',') # TODO: improve it
    entities = users.lookup(oauth_conn, user_id = user_id)
    return entities

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

    entities = users_lookup_by_screen_name(oauth_conn, users, args)
    if not prompt_error(entities):
        print_users(entities, verbose)

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
    entities = users_lookup_by_user_id(oauth_conn, users, users_string)
    if not prompt_error(entities):
        print_users(entities, verbose)

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
    entities = users_lookup_by_user_id(oauth_conn, users, users_string)
    if not prompt_error(entities):
        print_users(entities, verbose)

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
            usage()

def one_shot(oauth_conn, twitter):
    cmd, args = sys.argv[1], sys.argv[2:]

    try:
        commands[cmd](oauth_conn, twitter, args)
    except KeyError:
        usage()

def authorize_oob():
    oauth_oob = OAuthOOB(REQUEST_TOKEN_URL, AUTHENTICATE_URL, ACCESS_TOKEN_URL)
    oauth_conn = OAuthConn(CONSUMER_KEY, CONSUMER_SECRET)

    try:
        oauth_conn = oauth_oob.get_temp_credentials(oauth_conn)
    except Exception, e:
        print e
        exit(1)
    
    subprocess.call(['chromium', oauth_oob.temp_credentials_url])
    sys.stdout.write('PIN: ')
    pin_code = raw_input()

    try:
        oauth_conn = oauth_oob.get_credentials(oauth_conn, pin_code)
    except Exception, e:
        print e
        exit(1)
    
    return oauth_conn

def authorize(settings):
    try:
        config = json.load(open(settings))
        
        consumer_key    = config['consumer_key']
        consumer_secret = config['consumer_secret']
        token_key       = config['token_key']
        token_secret    = config['token_secret']
        
        oauth_conn = OAuthConn(consumer_key, consumer_secret, token_key, token_secret)
    except Exception:
        oauth_conn = authorize_oob()
        consumer_key    = CONSUMER_KEY
        consumer_secret = CONSUMER_SECRET
        token_key       = oauth_conn.token_key
        token_secret    = oauth_conn.token_secret

        f = open(settings, 'w')
        f. write(json.dumps({ 'consumer_key'    : consumer_key,
                              'consumer_secret' : consumer_secret,
                              'token_key'       : token_key,
                              'token_secret'    : token_secret, }, indent=4))
    return oauth_conn
        
def main():
    global prog_name
    
    prog_name = sys.argv[0]
    settings_dir = os.getenv('HOME') + '/.config/ptwt/' 
    settings =  settings_dir + 'settings'
    try:
        os.stat(settings_dir)
    except OSError, e:
        if e.errno == errno.ENOENT:
            os.makedirs(settings_dir)
        else:
            sys.stderr.write('Failed to create config dir: ' + settings_dir + '\n')
            exit(1)
    
    twitter = Client('twitter')
    oauth_conn = authorize(settings)

    if len(sys.argv) == 1:
        interactive(oauth_conn, twitter)
    else:
        one_shot(oauth_conn, twitter)
        
if __name__ == '__main__':
    main()
