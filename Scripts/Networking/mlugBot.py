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
import time, sys, re


class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

#    def log(self, message, channel, msg):
    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()
#        if re.search(r"mlugbot", message):
#            msg = "Don't yell"
#            self.msg(channel, msg)

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

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "Why don't you get a room with someone else. I don't do privates."
            self.msg(user, msg)
            return

        """ Handles if a message directed at me """
        # Displays help options
        if re.search(r'%s[:,] (help|ping)$' % self.nickname, msg):
            msg = "Available options: motd, history (chat history), mlug_history. \nFun options: bash_tip (tip of the day), whoareyou, make me a sandwich, moo"
            self.msg(channel, msg)

        # Displays history in a private window
        elif re.search(r'%s[:,] history$' % self.nickname, msg):
            self.msg(channel, "%s: Give me a sec. I'll open 25 lines of history for mlug's channel in a private window." % user)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            count = 25
            logfile=open("var/log/irc/current.log")
            for i in range(count):
                 #import time
                 line=logfile.next().strip()
                 msg = (line)
                 self.msg(user, msg)
                 time.sleep(.8)
            logfile.close()

        # Bash tip
        elif re.search(r'%s[:,] bash_tip' % self.nickname, msg):
            bashtp=open("/tmp/bashcookbook")
            msg = bashtp.read()
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            bashtp.close()

        # Displays mlug history
        elif re.search(r'%s[:,] mlug_history$' % self.nickname, msg):
            self.msg(channel, "%s: Give me a sec. I'll show you mlug's history in a private window." % user)
            #import time
            self.msg(user, "Mississauga LUG, originally known as MUMU (Mississauga Ubuntu MeetUp), started in September 2008 with a group of Ubuntu users that were looking to meet in the Mississauga area. The group wanted a laid back type of meeting, without an agenda, where users could come and talk about anything and everything and not just Linux (hence why a meet up, and not an official LUG).")
            time.sleep(2)
            self.msg(user, "For the first two years the meetings were held at Mulligan's Pub and Grill at Dundas and Erin Mills area. And around January 2011 the meetings moved to Shoeless Joe's at Meadowvale Town Center as most of the members lived in that area.")
            time.sleep(2)
            self.msg(user, "During the initial phase we advertised the meetings via Ubuntu's Wiki, Forum and the CA mailing list. The Wiki has been kept the same since August 2009, with exception of the name, so you can check it to see some of the notes from them. At some point after the first few meetings a Yahoo groups page was also created, which allowed users to register and ask questions, as well access to a mailing list.")
            time.sleep(2)
            self.msg(user, "Around August 2010, and after much talk between the members, Michael registered the group as an official LUG. A domain name was voted via a poll between the members and a template layout picked during one of our meetings. And only a couple of years later, (Halloween 2012 to be more exact), the site was finally created.")

        # Who are you
        elif re.search(r'%s[:,] who ?are ?you?' % self.nickname, msg):
            msg = "%s: Who Are You is the eighth studio album by English rock band The Who, released through Polydor Records in the United Kingdom and MCA Records in the United States. It peaked at number 2 on the US charts and number 6 on the UK charts. It is The Who's last album with Keith Moon as the drummer; Moon died twenty days after the release of this album." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            time.sleep(2)
            msg = "%s: Being serious now, I can't tell you who I am. But I'll give you a hint... \"I've got no strings on me\"" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # make me a sandwich
        elif re.search(r'%s[:,] make me a sandwich' % self.nickname, msg):
            msg = "%s: what? make it yourself!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # sudo make me a sandwich
        elif re.search(r'%s[:,] sudo make me a sandwich' % self.nickname, msg):
            msg = "%s: okay." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
        
        # Hello
        elif re.search(r"%s[:,] hello" % self.nickname, msg):
            msg = "Hello %s, I'm the MLUG channel bot. Type 'help' to view how I can help you." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            
        # Displays motd
        elif re.search(r'%s[:,] motd$' % self.nickname, msg):
            self.msg(channel, "         ##############################################")
            self.msg(channel, "  -o)    ##       Welcome to MLUG's IRC Channel      ##")
            time.sleep(.5)
            self.msg(channel,  '  /\\\    ##############################################')
            self.msg(channel,  ' _\_V')
            time.sleep(.5)
            self.msg(channel,  "         Official site: http://mississaugalug.ca/")
            self.msg(channel,  "         Blog: http://goo.gl/nyfNNk")
            time.sleep(.5)
            self.msg(channel,  "         Meetings: Every 3rd Tuesday of the month")
            self.msg(channel,  "         	  Calendar - http://goo.gl/mzrcd0")
            time.sleep(.5)
            self.msg(channel,  "         Mailing list: http://goo.gl/bt2ujZ")
            self.msg(channel,  "         ")
            self.msg(channel,  "         IRC logs: https://botbot.me/freenode/mlug-ca/\n")

        # moo
        elif re.search(r'%s[:,] moo$' % self.nickname, msg):
            self.msg(channel, '                 (__)')
            self.msg(channel, '                 (oo)')
            time.sleep(.5)
            self.msg(channel, '           /------\/ ')
            self.msg(channel, '          / |    ||  ')
            time.sleep(.5)
            self.msg(channel, '         *  /\---/\  ')
            self.msg(channel, '            ~~   ~~  ')
            self.msg(channel, '...\"Have you mooed today?\"...\n')
            
        # swearing at me
        elif re.search(r'%s[:,] .*(fuck|cunt|pussy|cock|asshole|shit|fag|slut|bitch)' % self.nickname, msg):
            swear = re.search(r'(fuck|cunt|pussy|cock|asshole|shit|fag|slut|bitch)', msg)
            msg = "%s: No you are the %s!" % (user, swear.group())
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            msg = "%s: Now stop swearing!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            
        # Unknown option
        elif re.search(r'%s[:,] .+' % self.nickname, msg):
            msg = "I don't understand that command"
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # Talking to me
        elif re.search(r'%s[:,] ?$' % self.nickname, msg):
            # someone is talking to me, lets respond:
            msg = "%s: sup? Say \"%s: help\" for a list of commands" % (user, self.nickname)
            self.say(channel, msg)
            

            """ Message not directed to me """
            
        # Swearing
        elif re.search(r'(fuck|cunt|pussy|cock|asshole|shit|fag|slut|bitch)', msg):
            msg = "%s: No swearing!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
        
        # yelling
        elif re.search(r'^([A-Z]{2,} ?.?)+$', msg):
            msg = "%s: Please, NO YELLING IN THE CHAT!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            
        # Heard my name
        elif re.search(r'%s' % self.nickname, msg):
            msg = "%s: I heard you saying my name. Do you need help? Type \"%s: help\" if you do." % (user, self.nickname)
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

        
    """ irc callbacks """

    def userRenamed(self, oldname, newname):
        """Called when an IRC user changes their nickname."""
        #old_nick = prefix.split('!')[0]
        #new_nick = params[0]
        #self.logger.log("%s is now known as %s" % (old_nick, new_nick))
        thischannel = "#vic-test"
        self.logger.log("%s is now known as %s" % (oldname, newname))
        #msg = "%s is now known as %s" % (old_nick, new_nick)
        msg = "%s morphed to %s" % (oldname, newname)
        self.msg(thischannel, msg)

        
    def irc_JOIN(self, prefix, params):
        """ Welcomes user """
        nick = prefix.split('!', 1)[0]
        if nick != self.nickname:
            channel = params[-1]
            msg = "%s: welcome to mlug" % (nick)
            self.msg(channel, msg)


    def userKicked(self, kickee, channel, kicker, message):
        """ Called when a user is kicked from the channel """
        msg = "Haha!! %s just got kicked from the channel" % (kickee)
        self.msg(channel, msg)

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '1'



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
