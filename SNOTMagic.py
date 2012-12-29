# Library that monitors the SNOT logs and takes action when certain actions
# happen.
# For example, you can have certain people or channels be notified whenever a
# ticket is flagged as UNIX. Or make have it alert people when a VIP0 ticket
# arrives. Or have it tell people when somebody assigned a ticket to them. The
# possibilities are endless

import CommandMonitoring as cm
import yaml, re
import snotparser.snotparser as sp
from twisted.internet import reactor

# Import YAML configuration. This should really be consolidated into one
# dictionary that can be accessed from multiple places. 
CONFIG_FILE = "config.yaml"
config = None
with open(CONFIG_FILE) as cfgFile:
    config = yaml.load(cfgFile)

# Function that creates another function that is called with the contents of
# each line of the snot log.
def makeSNOTLogHandler(client):
    def handleSNOTLogLine(line):
        print line,
        regex = r"^(?P<date>.+?) CMD: (?P<cmd>\w+?) TKT: (?P<tkt>\d+?) BY: (?P<by>.+?)($| TO: (?P<to>.+))?$"
        match = re.match(regex, line)
        if match:
            mdict = match.groupdict()
            message = str(mdict)
            formattedTicket = sp.formatTicket(int(mdict["tkt"]), "$from_line | $assigned_to | $subject | $flags")
            # "Case" statement for various ticket commands
            cmd = mdict["cmd"].lower()
            if cmd == "flags":
                message = "#{tkt} flagged as {to} by {by}".format(**mdict)
                if mdict['to'] in config['snot']['alerts']['flag']:
                    for target in config['snot']['alerts']['flag'][mdict['to']]:
                        client.msg(target, formattedTicket)
                return
            elif cmd == "recv":
                message = "Received ticket #{tkt} from {by}".format(**mdict)
            elif cmd == "resp":
                message = "{by} assigned #{tkt} to {to}".format(**mdict)
            elif cmd == "complete":
                message = "#{tkt} completed by {by}".format(**mdict)
            elif cmd == "update":
                message = "#{tkt} updated by {by}".format(**mdict)
            elif cmd == "append":
                message = "#{tkt} appended to #{to} by {by}".format(**mdict)
            else:
                message = line
            client.msg(config['snot']['snot_channel'], message)
        else:
            client.msg("#snot", "Could not match '%s'" % line)
        reactor.wakeUp()

    return handleSNOTLogLine

# Main function to be called in a subthread by the main program
def monitorLogs(client):
   cm.monitorFile(config['snot']['basedir'] + "logs/log",
                    makeSNOTLogHandler(client))
