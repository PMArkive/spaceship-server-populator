#!/usr/bin/python3
import sys
# https://github.com/Yepoleb/python-a2s
import a2s
import time
import socket

# list of servers. no shit
serverlist = [
    "mge.sappho.io:27015",
    "elo1.sappho.io:27115",
    "elo2.sappho.io:27215",
    "elo3.sappho.io:27615",
    "dm.sappho.io:27315",
    "dm.sappho.io:27415",
    "dm.sappho.io:28315",
    "dm.sappho.io:28415",
    "dm.sappho.io:27515",
    "dm.sappho.io:28215",
    "bb1.sappho.io:27715",
    "ulti.sappho.io:27815",
    "pub.sappho.io:27915",
    "jump.sappho.io:28015",
]

# oh man this is so ugly but i'd rather do this in python than php
# we just readfile with php and this just becomes a table
# because i don't know php and i dont want to fuck with it any more than i have to
template_string = (
"""
<div class="centerTable">
    <h3 style="margin: 5px">There are <span style="color:#ff85d5">{}</span> players across <span style="color:#ff85d5">{}</span> servers!</h3>
    <div class="serverDiv" style="">
        <table class="servers">
        <tbody>
            <tr>
                <th>Players</th>
                <th>Connect Link</th>
                <th>Server Name</th>
                <th class="mapHeading">Current Map</th>
            </tr>
            {}
        </tbody>
        </table>
    </div>
</div>
""")

final_string = ''

totalplayers = 0
totalservers = 0

# also ugly don't look at me
full    = 'server_full'
notfull = 'server_notfull'
empty   = 'server_empty'
error   = 'server_error'

table_string = ''

for server in serverlist:
    totalservers += 1

    # get our url
    serverurl = server.split(':')[0]

    # get our port and cast to an int because the a2s lib needs the port as an int
    serverport = int(server.split(':')[1])

    # recombine them into a proper tuple so that a2s recognizes it
    a2s_tuple = (serverurl, serverport)

    # these get overriden if we get a successful query, otherwise these display when an error occurs
    playercount = 0
    maxplayers  = 0
    hostname    = "Not set??? Report this to the site owner please"
    mapname     = "N/A"
    islocked    = False;
    threwerror  = True;

    # try querying 5 times with a 3s timeout for servers that may be map changing.
    # hostname is where we display our error msg if we get one.

    # "tHiS iSn'T pYtHoNiC" shut up
    for tries in range(10):
        try:
            query = a2s.info(a2s_tuple, timeout=1.0)
            playercount     = query.player_count
            maxplayers      = query.max_players
            hostname        = query.server_name
            mapname         = query.map_name
            islocked        = query.password_protected
            threwerror      = False;
            print('Got info for {}!'.format(str(server)))
            break
        except socket.timeout:
            print('Timeout for {}. Trying again... (try {})'.format(str(server), tries+1))
        # there's no reason to retry if we get any of these errors.
        except ConnectionRefusedError:
            hostname    = "Connection refused while querying."
            break
        except socket.gaierror:
            hostname    = "No server exists at this address."
            break
        except OSError:
            hostname    = "An OSError occurred."
            break
        except:
            hostname    = "An unknown error occurred!"
            break
    else:
        hostname        = "Query timeout."

    #print(hostname)

    # don't count or display locked servers
    if islocked:
        continue

    # count num of players on the whole network
    totalplayers    += playercount

    # PLAYER COUNT
    if threwerror:
        span_playerstype = error
    elif playercount >= maxplayers:
        span_playerstype = full
    elif playercount > 0:
        span_playerstype = notfull
    else:
        span_playerstype = empty

    playernum_column = '<td class="playernum"> <span class="{}">{}/{}</span> </td>'.format(span_playerstype, playercount, maxplayers)

    # STEAM CONNECT URL AND SERVER URL
    url_column = '<td class="link"> <a href="steam://connect/{}:{}">{}</a> </td>'.format(serverurl, serverport, server)

    # SERVER HOSTNAME (or error if one was thrown)
    hostname_column = '<td class="name">{}</td>'.format(hostname)

    # SERVER MAP
    map_column = '<td class="map">{}</td>'.format(mapname)

    # servers that err'd out should be less noticable on the server page
    # td_error sets their opacity to... i think its 50%?
    changeopacity = ''
    if threwerror:
        changeopacity = ' td_error'

    # add it to our string
    table_string += (
"""
            <tr class="server_tablerow{}">
                {}
                {}
                {}
                {}
            </tr>
""").format(changeopacity,
playernum_column,
url_column,
hostname_column,
map_column)

final_string = template_string.format(totalplayers, totalservers, table_string)

OUTPUT = '/var/www/sappho.io/rsrc/servertable.txt'

# this is so it gets flushed instantly because otherwise,
# you can have a race condition where
# script runs -> user connects to site before it's done -> they see a blank page
f = open(OUTPUT, "wb", 0)
# needs to be binary because... python? no clue
f.write(final_string.encode("utf-8"))
f.close()


#print(final_string)

sys.exit(0)

