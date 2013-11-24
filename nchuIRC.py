import socket
import time
import os
import json

HOST = "irc.freenode.org"
PORT = 6667
CHANNEL = "#nchusg.it"
NICKNAME = "SG_Bot"
IDENTITY = "sg_bot"
REALNAME = "SG BOT"


def connect(HOST, PORT, CHANNEL, NICKNAME, IDENTITY, REALNAME):
    global connected
    while connected is False:
        try:
            irc.connect((HOST, PORT))
            irc.send("NICK {0}\r\n".format(NICKNAME).encode("utf-8"))
            irc.send("USER {0} {1} bla: {2}\r\n".format(IDENTITY, HOST, REALNAME).encode('utf-8'))
            irc.send("JOIN {0}\r\n".format(CHANNEL).encode("utf-8"))
            connected = True
        except socket.error:
            print("Retrying to connect...")
            time.sleep(3)
            continue


def logDown(msg):
    # Write to day-mon-year.log
    os.chdir(os.path.dirname(__file__))

    try:
        os.mkdir("{0}".format(CHANNEL[1:]))
        os.chdir("{0}".format(CHANNEL[1:]))
    except OSError:
        os.chdir("{0}".format(CHANNEL[1:]))

    global dateList
    logFile = open("{0}-{1}-{2}.log".format(dateList[1], dateList[2], dateList[4]), "a")
    logFile.write(msg)
    logFile.close()


def logToJson():
    global dateList
    filename = "{0}-{1}-{2}".format(dateList[1], dateList[2], dateList[4])

    logFile = open("{0}.log".format(filename), "r")
    jsonFile = open("{0}.json".format(filename), "a")

    ele = ['time', 'name', 'content']
    line = logFile.readlines()[-1].split(" ", 2)
    result = {ele[i]: line[i].strip() for i in range(3)}

    jsonData = json.dumps(result, indent=4, separators=(',', ':'), ensure_ascii=False)
    jsonFile.write("{0}, \n".format(jsonData))

    logFile.close()
    jsonFile.close()


# Login to the server
irc = socket.socket()
connected = False
connect(HOST, PORT, CHANNEL, NICKNAME, IDENTITY, REALNAME)

# Read from the channel
while connected:
    raw_msg = irc.recv(1024).decode("utf-8")
    if raw_msg[0:4] == "PING":
        # raw_msg looks like "PING :HELLO_WORLD"
        irc.send("PONG {0}\r\n".format(raw_msg.split()[1]))

    if len(raw_msg.split()) > 2 and raw_msg.split()[1] == "PRIVMSG":
        # raw_msg looks like "NICKNAME!~IDENTITY@HOST PRIVMSG #CHA.NNEL :CONTENTS"
        dateList = time.ctime().split()
        nickname = raw_msg.split("!")[0][1:]
        contents = raw_msg.split(" ", 3)[3][1:]

        msg = "{0} {1} {2}".format(dateList[3], nickname, contents)
        logDown(msg)
        logToJson()
        print(msg)

        time.sleep(0.01)
