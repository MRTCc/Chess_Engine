import sys
import threading
import queue
import time
import gametreesearching as gm

legalucicommands = ("uci", "isready", "setoption", "ucinewgame", "position", "go", "stop", "quit", "showstate",
                    "showboard")
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
        stdprinter("Insert command: \n")  # solo per debug
        msg = input()
        commandintokens = msg.split()
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
        self.daemon = True
        self.isrequestactive = False
        self.bestmove = None

    def getbestmove(self):
        pass

    def run(self):
        # stdprinter("Thread finito!!!")
        pass


class UciManager:
    def __init__(self):
        self.isconnectionstate = True
        self.isinitnewgamestate = False
        self.ispositionstate = False
        self.isgostate = False
        self.streaminthread = threading.Thread(target=stream_in_manager, args=())
        self.searchthread = SearchThread()
        self.stdprinter = StdPrinter()

    def _setoption(self, parameter, value):
        try:
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
                if value == 'minmax' or value == 'alphabeta':
                    gm.algorithm = value
                else:
                    raise ValueError("UciManager --> _setoption : invalid value ", value, "for parameter ", parameter)
            elif parameter == 'maxply':
                try:
                    ply = int(value)
                    gm.maxply = ply
                except ValueError:
                    raise ValueError("UciManager --> _setoption : invalid value ", value, "for parameter ", parameter)
            else:
                raise ValueError("UciManager --> _setoption : invalid parameter ", parameter)
        except ValueError as e:
            self.stdprinter(str(e.args))

    @staticmethod
    def _setnewgame():
        gm.initnewgame()

    def _searchfinished(self):
        # TODO da implementare come si deve
        pass

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
            if self.searchthread.is_alive():
                self._searchfinished()
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
                    self.searchthread = SearchThread()
                elif keyword == 'setoption':
                    if self.ispositionstate or self.isgostate:
                        continue
                    if tokens[1] != 'name' or len(tokens) != 4:
                        raise ValueError("UciManager --> setoption invalid syntax!!!")
                    self._setoption(tokens[2], tokens[3])
                elif keyword == 'ucinewgame':
                    if self.isconnectionstate:
                        self.stdprinter("UciManager --> not ready to start game!")
                        continue
                    elif self.ispositionstate:
                        self._setnewgame()
                    elif self.isgostate and not self.searchthread.is_alive():
                        # TODO vedere bene searchthread.is_alive a searchthread.isrequestactive
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
                    self.isconnectionstate = False
                    self.isinitnewgamestate = True
                elif keyword == 'quit':
                    # bisogna aggiungere roba
                    break
                elif keyword == 'showstate':
                    self._showstate()
                elif keyword == 'showboard':
                    self.stdprinter(str(gm.rootposition))
                else:
                    # gestire eventuali cose andate storte
                    pass
            except Exception as e:
                # TODO da sistemare la lista dei tipi di eccezioni da intercettare
                self.stdprinter(str(e.args))
                raise e


def protocol_launcher():
    stdprinter = StdPrinter()
    protocol = input("Insert protocol:")   # per debug ok, ma alla fine non ci dovrà essere nessun msg in out
    if protocol == 'uci':
        stdprinter("id name MRTuCc\nid author MRTuCc\noption isactivetraspositiontable type check default true\n"
                   "option hashingmethod type string default zobrist\n"
                   "option algorithm type string default minmax\n"
                   "option maxply type spin min 1 max 20 default 5\nuciok\n")
        return UciManager()
    else:
        # altri eventuali protocolli
        raise Exception("protocol_launcher --> Not yet implemented!!!")


if __name__ == '__main__':
    protocolmanager = protocol_launcher()
    protocolmanager()
