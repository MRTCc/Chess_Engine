import threading
import queue
import time

legalucicommands = ("uci", "isready", "setoption", "ucinewgame", "position", "go", "stop", "quit")
streaminqueue = queue.Queue()
sleeptime = 0.3


def stream_in_manager():
    again = True
    while again:
        msg = input("Insert command\n")
        commandintokens = msg.split()
        command = commandintokens[0]
        if command not in legalucicommands:
            print("stream_in_manager --> Not a legal uci commands!!!")
            continue
        streaminqueue.put(commandintokens)
        if msg == 'quit':
            again = False


class SearchThread(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.isrequestactive = False

    def run(self):
        print("Thread finito!!!")


class UciManager:
    def __init__(self):
        self.isconnectionstate = True
        self.isinitnewgamestate = False
        self.ispositionstate = False
        self.isgostate = False
        self.streaminthread = threading.Thread(target=stream_in_manager, args=())
        self.searchthread = SearchThread()

    def __call__(self):
        self.streaminthread.start()
        again = True
        while again:
            try:
                tokens = streaminqueue.get(block=False)
            except queue.Empty:
                time.sleep(sleeptime)
                continue
            keyword = tokens[0]
            if keyword == 'position':
                if not self.ispositionstate:
                    continue
                # qua la robba
                pass
            elif keyword == 'go':
                if not self.isgostate:
                    continue
                # qua la robba
                pass
            elif keyword == 'stop':
                if not self.isgostate:
                    continue
                # qua la robba
                pass
            elif keyword == 'setoption':
                if self.ispositionstate or self.isgostate:
                    continue
                # qua la robba
                pass
            elif keyword == 'ucinewgame':
                pass
            elif keyword == 'isready':
                if not self.isinitnewgamestate:
                    continue
                # qua la roba
                pass
            elif keyword == 'quit':
                again = False
            else:
                # gestire eventuali cose andate storte
                pass
            if self.searchthread.isrequestactive and self.searchthread.is_alive():
                # inviare il risultato al client
                print("invio il risultato al client")
            time.sleep(sleeptime)


def protocol_launcher():
    protocol = input("Insert protocol:")   # per debug ok, ma alla fine non ci dovrà essere nessun msg in out
    if protocol == 'uci':
        # TODO bisogna stampare uciok, id ed eventuali options
        return UciManager()
    else:
        # altri eventuali protocolli
        raise Exception("protocol_launcher --> Not yet implemented!!!")


if __name__ == '__main__':
    protocolmanager = protocol_launcher()
    protocolmanager()