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

"""
TO DO:

- Make bot say something when alone
. Someone enters
. By himself
- meet
- man
- facts
- randomize bash
- meow
- roof (dog)
- Remove self logging
"""

# twisted imports
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

# system imports
import time, sys, re

# For URL Grabbing
import urllib
import urllib2
from BeautifulSoup import BeautifulSoup
from re import findall

# for fortune
import subprocess
import os

argchannel = sys.argv[1]

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

        # Check to see if they're sending me a private message
        if channel == self.nickname:
            #msg = "Why don't you get a room with someone else. I don't do privates."
            msg = "Sorry, I don't support private messages."
            self.msg(user, msg)
            return

        """ Handles if a message directed at me """
        # Displays quick help options
        if re.search(r'%s[:,] (help|ping)$' % self.nickname, msg):
            msg = "Commands start with '!'\nAvailable options: help (full help), about, motd, history (chat history), mhistory (history of mlug), meet, wiki, man. \nFun options: bash, whoareyou, make me a sandwich, moo, fortune, facts"
            self.msg(channel, msg)

        # Full help options
        if msg == "!help":
            h=open("lib/help")
            hlp = h.read()
            for line in hlp.split(os.linesep):
                msg = ("%s" % line)
                self.msg(channel, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                #time.sleep(.2)
            h.close()

        # Fun commands
        if msg == "!fun":
            f=open("lib/fun")
            fun = f.read()
            for line in fun.split(os.linesep):
                msg = ("%s" % line)
                self.msg(channel, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                #time.sleep(.8)
            f.close()

        # Meet
        if msg == "!meet":
            msg = "I'm not programmed with this option yet"
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
#            f=open("lib/fun")
#            fun = f.read()
#            for line in fun.split(os.linesep):
#                msg = ("%s" % line)
#                self.msg(channel, msg)
#                self.logger.log("<%s> %s" % (self.nickname, msg))
#                #time.sleep(.8)
#            f.close()

        # man
        if msg == "!man":
            msg = "I'm not programmed with this option yet"
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
#            f=open("lib/fun")
#            fun = f.read()
#            for line in fun.split(os.linesep):
#                msg = ("%s" % line)
#                self.msg(channel, msg)
#                self.logger.log("<%s> %s" % (self.nickname, msg))
#                #time.sleep(.8)
#            f.close()

        # About
        if msg == "!about":
            f=open("lib/about")
            about = f.read()
            for line in about.split(os.linesep):
                msg = ("%s" % line)
                self.msg(channel, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                #time.sleep(.8)
            f.close()

        # Displays history in a private window
        #elif re.search(r'%s[:,] history$' % self.nickname, msg):
        elif msg == "!history":
            if channel == '#mlug-priv':
                self.msg(channel, "%s: I'm sorry but we don't log messages here" % user)
                return
            elif channel != '#mlug-ca':
                self.msg(channel, "%s: I don't think I should be here. This channel is not registered on my database" % user)
                return
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

        # Displays mlug history
        elif msg == "!mhistory":
            f=open("lib/history")
            history = f.read()
            for line in history.split(os.linesep):
                msg = ("%s" % line)
                self.msg(user, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                #time.sleep(.8)
            f.close()


        # Hello
        elif re.search(r"%s[:,] hello" % self.nickname, msg):
            msg = "Hello %s, I'm the MLUG channel bot. Type '!help' to view how I can help you." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # Displays motd
        #elif re.search(r'%s[:,] motd$' % self.nickname, msg):
        elif msg == "!motd":
            f=open("lib/motd")
            motd = f.read()
            for line in motd.split(os.linesep):
                msg = ("%s" % line)
                self.msg(channel, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))
                #time.sleep(.8)
            f.close()

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


            ''' ### Fun Options ###'''


        # Bash tip
        elif msg == "!bash":
            bashtp=open("/tmp/bashcookbook")
            msg = bashtp.read()
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            bashtp.close()

        # Who are you
        #elif re.search(r'%s[:,] who ?are ?you?' % self.nickname, msg):
        elif msg == "!whoareyou":
            msg = "%s: Who Are You is the eighth studio album by English rock band The Who, released through Polydor Records in the United Kingdom and MCA Records in the United States. It peaked at number 2 on the US charts and number 6 on the UK charts. It is The Who's last album with Keith Moon as the drummer; Moon died twenty days after the release of this album." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
            time.sleep(2)
            msg = "%s: Being serious now, I can't tell you who I am. But I'll give you a hint... \"I've got no strings on me\"" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # make me a sandwich
        elif re.search(r'!make me a sandwich', msg):
            msg = "%s: what? make it yourself!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # sudo make me a sandwich
        elif re.search(r'!sudo make me a sandwich', msg):
            msg = "%s: okay." % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # moo
        #elif re.search(r'%s[:,] moo$' % self.nickname, msg):
        elif msg == "!moo":
            self.msg(channel, '                 (__)')
            self.msg(channel, '                 (oo)')
            time.sleep(.5)
            self.msg(channel, '           /------\/ ')
            self.msg(channel, '          / |    ||  ')
            time.sleep(.5)
            self.msg(channel, '         *  /\---/\  ')
            self.msg(channel, '            ~~   ~~  ')
            self.msg(channel, '...\"Have you mooed today?\"...\n')

        # Fortune
        elif msg == '!fortune':
            f = subprocess.Popen('./lib/cowsay.sh', stdout=subprocess.PIPE)
            fortune = f.communicate()[0]
            for line in fortune.split(os.linesep):
                #msg = line.strip()
                msg = ("%s" % line)
                self.msg(channel, msg)
                self.logger.log("<%s> %s" % (self.nickname, msg))

        # Facts - who created me, swear count (need logger)
        if msg == "!facts":
            msg = "I'm not programmed with this option yet"
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))
#            f=open("lib/fun")
#            fun = f.read()
#            for line in fun.split(os.linesep):
#                msg = ("%s" % line)
#                self.msg(channel, msg)
#                self.logger.log("<%s> %s" % (self.nickname, msg))
#                #time.sleep(.8)
#            f.close()


            """ Message not directed to me """

        # Swearing
        elif re.search(r'(fuck|cunt|pussy|cock|asshole|shit|fag|slut|bitch)', msg):
            msg = "%s: No swearing!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # yelling
        elif re.search(r'^([^a-z]+[\s|\W][A-Z])', msg):
            msg = "%s: Please, NO YELLING IN THE CHAT!" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

        # Wikipedia
        elif re.search(r"!wiki .*", msg):
            searchstring = msg.split(' ', 1)[1]
            article = searchstring
            article = urllib.quote(article)

            opener = urllib2.build_opener()
            opener.addheaders = [('User-agent', 'Mozilla/5.0')] #wikipedia needs this

            resource = opener.open("http://en.wikipedia.org/wiki/" + article)
            data = resource.read()
            resource.close()
            soup = BeautifulSoup(data)
            soup = soup.find('div',id="bodyContent").p
            summary = soup.getText()
            utfsoup = summary.encode('utf-8')
            if re.search(r'refer to', utfsoup):
                msg = "^ Too many options on wikipedia"
            else:
                msg = "^ %s" % utfsoup
            self.msg(channel, msg)

        # Grabs URL
        elif re.search(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg):
            urls = findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", msg)
            if urls:
                #print urls
                url = urls[0]
                #print url
                soup = BeautifulSoup(urllib2.urlopen("%s" % url))
                finalsoup = soup.title.string
                utfsoup = finalsoup.encode('utf-8')
                msg = "^ %s" % utfsoup
                self.msg(channel, msg)

        # Heard my name
        elif re.search(r'%s' % self.nickname, msg):
            msg = "%s: I heard you saying my name. Do you need help? Type \"%s: help\" or \"!help\" if you do." % (user, self.nickname)
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))


    """ irc callbacks """

    def userRenamed(self, oldname, newname):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))
        #thischannel = "#vic-test"argchannel
#        print argchannel
#        pchannel = "#%s" % argchannel
#        self.logger.log("%s is now known as %s" % (oldname, newname))
        #msg = "%s is now known as %s" % (old_nick, new_nick)
#        msg = "%s morphed to %s" % (oldname, newname)
#        self.msg(pchannel, msg)


    def irc_JOIN(self, prefix, params):
        """ Welcomes user """
        nick = prefix.split('!', 1)[0]
        if nick != self.nickname:
            channel = params[-1]
            msg = "%s: welcome to mlug" % (nick)
            self.msg(channel, msg)
        elif nick == self.nickname:
            channel = params[-1]
            msg = "Yo yo... mlugbot is in the hood bitches!"
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
