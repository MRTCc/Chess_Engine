import sys
import threading
import queue
import time
import gametreesearching as gm

legalucicommands = ("uci", "isready", "setoption", "ucinewgame", "position", "go", "stop", "quit", "showstate",
                    "showboard", "showstats")
streaminqueue = queue.Queue()
sleeptime = 0.3
outputfilemutex = threading.Lock()


class StdPrinter:
    def __init__(self):
        self.outputfile = sys.stdout
        self.outputfilemutex = outputfilemutex

    def __call__(self, msg):
        with self.outputfilemutex:
            self.outputfile.write(msg + '\n')


def stream_in_manager():
    stdprinter = StdPrinter()
    again = True
    while again:
        # stdprinter("Insert command:")
        msg = input()
        commandintokens = msg.split()
        if len(commandintokens) < 1:
            continue
        command = commandintokens[0]
        if command not in legalucicommands:
            stdprinter("stream_in_manager --> Not a legal uci commands!!!")
            continue
        streaminqueue.put(commandintokens)
        if msg == 'quit':
            again = False


class SearchThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.strbestmove = None
        self.isrequestactive = False
        self.iscorrectlycompleted = False
        self.daemon = True

    def getstrbestmove(self):
        gm.isrunning = False
        if self.isrequestactive and self.iscorrectlycompleted:
            return self.strbestmove
        else:
            self.strbestmove = gm.rootposition.getrandomoutmove()
            return self.strbestmove

    def run(self):
        self.isrequestactive = True
        bestmove = gm.rootposition.calcbestmove(gm.maxply)
        self.strbestmove = bestmove.short__str__()
        self.iscorrectlycompleted = True


class UciManager:
    def __init__(self):
        self.defaultinitmsg = ("id name MRTuCc\nid author MRTuCc\noption isactivetraspositiontable type check default "
                               "true\n"
                               "option hashingmethod type string default zobrist\n"
                               "option algorithm type string default alphabeta\n"
                               "option maxply type spin min 1 max 20 default 5\n"
                               "option evalfunctype type spin min 0 max 1 default 0\n"
                               "uciok\n")
        self.isconnectionstate = True
        self.isinitnewgamestate = False
        self.ispositionstate = False
        self.isgostate = False
        self.streaminthread = threading.Thread(target=stream_in_manager, args=())
        self.searchthread = SearchThread()
        self.stdprinter = StdPrinter()
        self.stdprinter(self.defaultinitmsg)

    @staticmethod
    def _setoption(parameter, value):
        if parameter == 'isactivetranspositiontable':
            if value == 'true' or value == 'True':
                gm.isactivetraspositiontable = True
            elif value == 'false' or value == 'False':
                gm.isactivetraspositiontable = False
            else:
                raise ValueError("UciManager --> _setoption : invalid value ", value, "for parameter ", parameter)
        elif parameter == 'hashingmethod':
            if value == 'zobrist':
                gm.hashingmethod = value
            else:
                raise ValueError("UciManager --> _setoption : invalid value ", value, "for parameter ", parameter)
        elif parameter == 'algorithm':
            if value in ('minmax', 'alphabeta', 'iterdeep'):
                gm.algorithm = value
            else:
                raise ValueError("UciManager --> _setoption : invalid value ", value, "for parameter ", parameter)
        elif parameter == 'maxply':
            try:
                ply = int(value)
                gm.maxply = ply
            except ValueError:
                raise ValueError("UciManager --> _setoption : invalid value ", value, "for parameter ", parameter)
        elif parameter == 'evalfunctype':
            gm.evalfunctype = int(value)
        else:
            raise ValueError("UciManager --> _setoption : invalid parameter ", parameter)

    @staticmethod
    def _setnewgame():
        gm.initnewgame()

    def _searchfinished(self):
        bestmove = self.searchthread.getstrbestmove()
        self.stdprinter('bestmove ' + bestmove)
        if gm.isrunning is True:
            raise Exception("IMPOSSIBLE!!!!!!!")
        self.searchthread = SearchThread()

    def _showstate(self):
        msg = ""
        if self.isconnectionstate:
            msg += 'connection state'
        if self.isinitnewgamestate:
            msg += 'init new game state'
        if self.ispositionstate:
            msg += 'position state'
        if self.isgostate:
            msg += 'go state'
        self.stdprinter(msg)

    def __call__(self):
        self.streaminthread.start()
        again = True
        while again:
            time.sleep(sleeptime)
            if self.searchthread.isrequestactive and self.searchthread.iscorrectlycompleted:
                self._searchfinished()
                self.ispositionstate = True
                self.isgostate = False
            try:
                tokens = streaminqueue.get(block=False)
            except queue.Empty:
                # outputfile.write("Time to sleep\n")
                continue
            keyword = tokens[0]
            try:
                if keyword == 'position':
                    if not self.ispositionstate:
                        continue
                    if 'moves' not in tokens or len(tokens) < 3:
                        raise ValueError("UciManager --> invalid position command syntax!!!")
                    gm.initgameposition(tokens[1:])
                    self.ispositionstate = False
                    self.isgostate = True
                elif keyword == 'go':
                    if not self.isgostate:
                        continue
                    self.searchthread.start()
                elif keyword == 'stop':
                    if not self.isgostate:
                        continue
                    self._searchfinished()
                    self.isgostate = False
                    self.ispositionstate = True
                elif keyword == 'setoption':
                    if self.ispositionstate or self.isgostate:
                        continue
                    if len(tokens) < 5 or tokens[1] != 'name' or tokens[3] != 'value':
                        raise ValueError("UciManager --> setoption invalid syntax!!!")
                    self._setoption(tokens[2], tokens[4])
                elif keyword == 'ucinewgame':
                    if self.isconnectionstate:
                        self.stdprinter("UciManager --> not ready to start game!")
                        continue
                    elif self.ispositionstate:
                        self._setnewgame()
                    elif self.isgostate and not self.searchthread.is_alive():
                        self._setnewgame()
                        self.isgostate = False
                    elif self.isinitnewgamestate:
                        self._setnewgame()
                        self.isinitnewgamestate = False
                    self.ispositionstate = True
                    self.stdprinter("UciManager --> new game initialized")
                elif keyword == 'isready':
                    if not self.isconnectionstate:
                        continue
                    self.stdprinter("readyok")
                    self.isconnectionstate = False
                    self.isinitnewgamestate = True
                elif keyword == 'quit':
                    break
                elif keyword == 'showstate':
                    self._showstate()
                elif keyword == 'showboard':
                    self.stdprinter(str(gm.rootposition))
                elif keyword == 'showstats':
                    self.stdprinter("Last complete search data:\n\tNumber of visited positions: " + str(gm.nposition) +
                                    "\n\tNumber of alpha cuts: " + str(gm.nalphacut) +
                                    "\n\tNumber of beta cuts: " + str(gm.nbetacut) +
                                    "\n\tNumber of matches with t.t.: " + str(gm.nmatch) +
                                    "\n\tTotal search time: " + str(gm.totaltime) +
                                    "\n\tGeneration time: " + str(gm.generationtime) +
                                    "\n\tEvaluation time: " + str(gm.evaluationtime))
                else:
                    # gestire eventuali cose andate storte
                    pass
            except Exception as e:
                self.stdprinter(str(e.args))
                if self.isconnectionstate:
                    continue
                elif self.isinitnewgamestate:
                    self.stdprinter(self.defaultinitmsg)
                    self.isinitnewgamestate = False
                    self.isconnectionstate = True
                elif self.ispositionstate:
                    self.stdprinter("Something goes wrong! Please, insert again the position!\n\n")
                elif self.isgostate:
                    self.stdprinter("Something goes wrong! Search not correctly finished...\n\n")
                    self.ispositionstate = True
                    self.isgostate = False


def protocol_launcher():
    stdprinter = StdPrinter()
    while True:
        try:
            protocol = input("Insert protocol:")   # per debug ok, ma alla fine non ci dovrà essere nessun msg in out
            if protocol == 'uci':
                return UciManager()
            else:
                # altri eventuali protocolli
                raise ValueError("protocol_launcher --> protocol " + protocol + " not supported!!!")
        except ValueError as e:
            stdprinter(str(e))
            continue


if __name__ == '__main__':
    protocolmanager = protocol_launcher()
    protocolmanager()
