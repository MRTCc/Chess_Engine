"""
Created on Fri Sep 25 12:11:28 2020

@author: martu
"""


class Printer:
    """
    Sends every comunication of the engine on the file 'outfile'
    """

    def __init__(self, outfile):
        self.outfile = outfile

    def send(self, msg):
        self.outfile.write(msg)


class Logger:
    """
    Logs every messagge the engine passes to it 'msg' on the 'logfile'
    The log format is:
        1. date and time
        2. class that wants to log
        3. message (a string)
    """

    def __init__(self, logfile):
        self.logfile = logfile
        from datetime import datetime
        self.datetime = datetime
        self.initcurlogsession()

    def getstrcurdatetime(self):
        now = self.datetime.now()
        return now.strftime("%d/%m/%Y %H:%M:%S")

    def initcurlogsession(self):
        # example --------------------started at: 25/09/2020 15:53:44--------------------
        resline = ("-" * 20 + "started at: " + self.getstrcurdatetime() +
                   "-" * 20 + '\n')
        self.logfile.write(resline)

    def log(self, clientname, msg):
        line = self.getstrcurdatetime() + " --> " + clientname + ":   " + msg + "\n"
        self.logfile.write(line)


# debug
if __name__ == '__main__':
    import sys

    try:
        ucilogfile = open("ucilog.txt", "a")
        logger = Logger(ucilogfile)
        logger.initcurlogsession()
        logger.log("IL GRANDE GATSBY", "messaggio del grande gatsby")
        logger.log("homer", "nooooo")
    except Exception as e:
        print(e)

    """
    try:
       outfile = sys.stdout
       printer = Printer(outfile)
       printer.send("vedioamo se funziona")
    except Exception as e:
        print(e)
        """
