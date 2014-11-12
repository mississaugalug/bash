################################################################################
################################################################################
# Name:          mlugBot.py
# Usage:
# Description:
# Created:       2014-11-09
# Last Modified:
# Modified by Victor Mendonca - http://mississaugalug.ca
# License: Released under the terms of the GNU GPL license
################################################################################
################################################################################

"""
## Based on Twisted Matrix Laboratories Framework ##

=> API Doc
http://twistedmatrix.com/documents/current/api/twisted.words.protocols.irc.IRCClient.html

=> How to Clients
http://twistedmatrix.com/documents/10.1.0/core/howto/clients.html
"""

"""
A modified IRC log bot that also logs channel's events to a file.

Run this script with two arguments, the channel name the bot should
connect to, and file to log to, e.g.:

    $ python ircLogBot.py test test.log

will log channel #test to the file 'test.log'.

To run the script:

    $ python ircLogBot.py <channel> <file>
"""


# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys


class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""

    nickname = "mlugbot"

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at %s]" %
                        time.asctime(time.localtime(time.time())))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at %s]" %
                        time.asctime(time.localtime(time.time())))
        self.logger.close()


    # callbacks for events

    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)
        msg = "Hello, I'm the MLUG channel bot. Type 'help' to view how I can help you."
        self.msg(channel, msg)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))

        prompt = ("%s" % self.nickname)
        prompt1 = ("%s:" % self.nickname)
        prompt2 = ("%s," % self.nickname)

        if msg == (prompt1) or msg == (prompt2):
            # someone is talking to me, lets respond:
            msg = "%s: sup? Say \"help\" for a list of commands" % user
            self.say(channel, msg)

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "Why don't you get a room with someone else. I don't do privates."
            self.msg(user, msg)
            return

        """ Handles if a message directed at me """
        # Displays help options
        #import re
        #if msg.match("%s: help" % self.nickname, msg):
        if msg == (prompt1 + " help") or msg == (prompt2 + " help"):
            self.msg(channel, "%s: Here's what you can ask me:" % user)
            import time
            self.msg(channel, "1- history\t\tPrints 25 lines of history in a new line")
            time.sleep(.8)
            self.msg(channel, "2- mlug\t\t\tPrints out the history of mlug \n3- who are you\t\tTells you who I really am")
            time.sleep(.8)
            self.msg(channel, "4- make me a sandwich\t?")

        # Displays history in a private window
        elif msg == (prompt1 + " history") or msg == (prompt2 + " history"):
        #elif msg.startswith(self.nickname + ": history"):
            self.msg(channel, "%s: Give me a sec. I'll open 25 lines of history for mlug's channel in a private window." % user)
            count = 25
            logfile=open("var/log/irc/current.log")
            for i in range(count):
                 import time
                 line=logfile.next().strip()
                 msg = (line)
                 self.msg(user, msg)
                 time.sleep(.8)
            logfile.close()

        # Displays mlug history
        elif msg == (prompt1 + " mlug") or msg == (prompt2 + " mlug"):
            self.msg(channel, "%s: Give me a sec. I'll show you mlug's history in a private window." % user)
            import time
            self.msg(user, "Mississauga LUG, originally known as MUMU (Mississauga Ubuntu MeetUp), started in September 2008 with a group of Ubuntu users that were looking to meet in the Mississauga area. The group wanted a laid back type of meeting, without an agenda, where users could come and talk about anything and everything and not just Linux (hence why a meet up, and not an official LUG).")
            time.sleep(2)
            self.msg(user, "For the first two years the meetings were held at Mulligan's Pub and Grill at Dundas and Erin Mills area. And around January 2011 the meetings moved to Shoeless Joe's at Meadowvale Town Center as most of the members lived in that area.")
            time.sleep(2)
            self.msg(user, "During the initial phase we advertised the meetings via Ubuntu's Wiki, Forum and the CA mailing list. The Wiki has been kept the same since August 2009, with exception of the name, so you can check it to see some of the notes from them. At some point after the first few meetings a Yahoo groups page was also created, which allowed users to register and ask questions, as well access to a mailing list.")
            time.sleep(2)
            self.msg(user, "Around August 2010, and after much talk between the members, Michael registered the group as an official LUG. A domain name was voted via a poll between the members and a template layout picked during one of our meetings. And only a couple of years later, (Halloween 2012 to be more exact), the site was finally created.")

        # make me a sandwich
        elif msg == (prompt1 + " who are you?") or msg == (prompt2 + " who are you?") or msg == (prompt1 + " who are you") or msg == (prompt2 + " Who are you?"):
            msg = "%s: Who Are You is the eighth studio album by English rock band The Who, released through Polydor Records in the United Kingdom and MCA Records in the United States. It peaked at number 2 on the US charts and number 6 on the UK charts. It is The Who's last album with Keith Moon as the drummer; Moon died twenty days after the release of this album." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # make me a sandwich
        elif msg == (prompt1 + " make me a sandwich") or msg == (prompt2 + " make me a sandwich"):
            msg = "%s: what? make it yourself!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # sudo make me a sandwich
        elif msg == (prompt1 + " sudo make me a sandwich") or msg == (prompt2 + " sudo make me a sandwich"):
            msg = "%s: okay." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        elif msg == (prompt1 + " hello") or msg == (prompt2 + " hello"):
            msg = "%s: Hello, I'm the MLUG channel bot. Type 'help' to view how I can help you." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        elif msg.startswith(prompt1) or msg.startswith(prompt2):
            msg = "I don't understand that command"
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))


    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks

    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))
        msg = "%s is now known as %s" % (old_nick, new_nick)
        self.msg(channel, msg)

    def irc_JOIN(self, prefix, params):
        nick = prefix.split('!', 1)[0]
        if nick != self.nickname:
            channel = params[-1]
            msg = "%s: welcome to mlug" % (nick)
            self.msg(channel, msg)


    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'



class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, channel, filename):
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()


if __name__ == '__main__':
    # initialize logging
    log.startLogging(sys.stdout)

    # create factory protocol and application
    f = LogBotFactory(sys.argv[1], sys.argv[2])

    # connect factory to this host and port
    reactor.connectTCP("irc.freenode.net", 6667, f)

    # run bot
    reactor.run()
