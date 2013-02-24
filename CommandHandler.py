import re
import urllib2
import snotparser.snotparser as sp
import SNOTMagic
import Help
from twisted.internet import reactor
from string import Template
from datetime import datetime
#import UnderscoreBot

def parseCommand(prefix, msg):
    command = re.match("^" + prefix + ":?\s*(?P<command>\S*)\s*(?P<args>.*)", msg)
    if command:
        return command.groupdict()
    else:
        return None

def handleCommand(client, user, channel, msg): 
    command = parseCommand(client.nickname, msg)
     
    if command:
        client.logger.write("Command in %s from %s: %s: '%s'" % (channel, user, command["command"], command["args"]))
        if command["command"] == "help":
            client.msg(channel, Help.getHelp(command["args"].strip()))

#            client.msg(channel,
#"""Type `snot <ticketNumber>` to get the contents of a ticket.
#snot <ticketNumber> <formatString> to customize the output.
#Example: $number | $summary_email | $assigned_to | $subject | $flags""")

        elif command["command"] == "snot":
            snotCommand = re.match("\s*#?(?P<ticketNumber>\d+)\s*(?P<fString>.*)", command["args"])
            
            number = snotCommand.group("ticketNumber")
            #fString = snotCommand.group("fString")
            fString = None
            if fString:
                formattedString = sp.formatTicket(int(number), fString) 
            else:
                formattedString = sp.formatTicket(int(number), "$number | $from_line | $assigned_to | $subject | $flags")
            #client.msg(channel,"SNOT COMMAND TIME: %s" % snotCommand.groups("ticketNumber"))
            client.msg(channel, formattedString)

        elif command["command"] == "join":
            channeljoin = re.match("(#?\S*)\s*(.*)", command["args"])       
            # client.msg(channel, str(channeljoin.groups()))
            # for item in channeljoin.groups():
            #     client.msg(channel, item)
            chan = channeljoin.group(1)
            key  = channeljoin.group(2)
            if (key):
                client.msg(channel, "Joining %s with key \"%s\"" % (chan, key)) 
                client.join(chan, key)
            else:
                client.msg(channel, "Joining %s (no key)" % (chan,))
                client.join(chan)

        elif command["command"] in ("part", "leave"):
            channelPart = re.match("(#?\S*)\s*", command["args"])       
            client.leave(channelPart.group(1), "Parting is such sweet sorrow")
        
        elif command["command"] in ("listHandlers", "lh"):
            client.msg(channel, "Current handlers:")
            for handler in client.handlers:
                client.msg(channel, handler)

        elif command["command"] in ("reload", "rel"):
            client.msg(channel, client.reloadModule(command["args"].strip()))
        
        elif command["command"] in ("reloadHandler", "rh"):
            client.msg(channel, client.reloadHandler(command["args"].strip()))

#        elif command["command"] in ("reloadConfig", "rc"):
#            CONFIG_FILE = "config.yaml"
#            with open(CONFIG_FILE) as cfgFile:
#                UnderscoreBot.config = yaml.load(cfgFile)

        elif command["command"] in ("startSNOTMonitoring", "ssm"):
            client.logger.write("Calling snot monitoring in subthread")
            client.msg(channel, "Restarting snot monitoring")
            reactor.callInThread(SNOTMagic.monitorLogs, client)

        elif command["command"] in ("ticketHistory", "th"):
            lines = sp.getTicketHistory(command["args"])
            for line in lines:
                client.msg(channel, line.strip())

        elif command["command"] in ("chronicle", "chron"):
            ticketCommand = re.match("\s*#?(?P<ticketNumber>\d+)\s*(?P<fString>.*)", command["args"])
            number = int(ticketCommand.group("ticketNumber"))
            try:
                d = client.redmine_instance.getTicket(number)
                client.msg(channel, str(Template("#$id ($project) | $author | $assigned_to | $subject | $tracker").safe_substitute(d)))
            except urllib2.HTTPError as e:
                client.logger.write(str(type(e)))
                client.msg(channel, str(e))
        else:
            print "Unrecognized command" 
