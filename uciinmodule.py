"""
Created on Fri Sep 25 11:51:59 2020

@author: martu
"""
import ucioutmodule
import gametreesearching as gm

uciincommands = ["uci", "isready", "setoption", "ucinewgame",
                 "position", "go", "stop", "quit"]


class State:
    def __init__(self, printer, logger, command=""):
        """
        Parameters
        ----------
        printer : Printer
            object that manages the sys.stdout.
        logger : Logger
            object that manages the log file ucilog.txt .
        command : string, optional
            UCI command from client. The default is "".
        run : boolean
            run == False means the engine has stopped all its activities
        """
        self.printer = printer
        self.logger = logger
        self.command = command
        self.run = True

    def parse(self, msg):
        return self

    def execute(self):
        self.printer.send("Not implemented execution of the current command!")

    def _log(self, **kwargs):
        msg = ""
        for key, value in kwargs.items():
            tmp = str(key) + " = " + str(value)
            msg += tmp
            msg += " ; "
        self.logger.log(str(self.__class__), msg)

    # per ora metodo inutilizzato, ma lo lascio, non si sa mai ...
    def _commandprintandlog(self, **kwargs):
        msg = ""
        for key, value in kwargs.items():
            tmp = str(value)
            msg += tmp
        msg += '\n'
        self.printer.send(msg)
        self._log(**kwargs)


class StartState(State):
    def parse(self, msg):
        resultstate = None
        if "uci" != msg:
            self._log(command=msg,
                      response="Not a valid command! First, establish used protocol")
            resultstate = self
        else:
            self._log(command=msg, response="UCI protocl established")
            resultstate = ConnectionState(self.printer, self.logger, msg)

        return resultstate


class ConnectionState(State):
    def parse(self, msg):
        resultstate = None
        if "ucinewgame" == msg:
            resultstate = NewGameInitState(self.printer, self.logger, msg)
        elif "quit" == msg:
            self._log(command=msg, response="I\'m quitting")
            resultstate = QuitState(self.printer, self.logger, msg)
        else:
            self._log(command=msg, response="Not a valid command! First, establish a new game!")
            resultstate = self

        return resultstate

    def execute(self):
        self.printer.send("id MRTuCcEngine\n")
        self.printer.send("id martuc\n")

        # qui si da eventualmente il comando option
        self.printer.send("option engine_color\n")

        self.printer.send("uciok\n")

        self._log(command="uci", response="connection established")
        # eventuali log per il comando option


class NewGameInitState(State):
    def __init__(self, printer, logger, command):
        self.engine_color = None
        super().__init__(printer, logger, command)

    def parse(self, msg):
        tokens = msg.split()
        command = tokens[0]
        if "position" == command:
            keyword = tokens[1]
            if 'moves' not in tokens:
                self._log(command=self.command, response="Invalid Position command syntax")
                resultstate = self
            elif keyword == 'startpos':
                resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)
            elif len(tokens[1:tokens.index('moves')]) != 6:
                self._log(command=self.command, response="Invalid Position command syntax")
                resultstate = self
            else:
                resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)
        elif "isready" == command:
            resultstate = self
        elif "quit" == command:
            self._log(command=msg, response="I\'m quitting")
            resultstate = QuitState(self.printer, self.logger, msg)
        elif "setoption" == command and len(tokens) == 3:
            # eventuali setoption
            if "engine_color" == tokens[1]:
                if tokens[2] in ("white", "black"):
                    self.engine_color = tokens[2]
                    self._log(command=self.command, response="setoption command executed")
                else:
                    self._log(command=msg, response="Not a valid setoption syntax!")
            resultstate = self
        else:
            self._log(command=msg, response="Not a valid command! Commands accepted: position, quit")
            resultstate = self

        return resultstate

    def execute(self):
        # inizializzazione delle strutture dati necessarie
        self.printer.send("readyok\n")

        self._log(command="ucinewgame", response="New game initialization")


class PositionState(State):
    def __init__(self, printer, logger, command, engine_color):
        self.boardposition = None
        self.engine_color = engine_color
        self.tokens = None
        self.invalidcommand = False
        super().__init__(printer, logger, command)

    def parse(self, msg):
        resultstate = self
        self.tokens = msg.split()
        if len(self.tokens) < 1:
            self._log(command=msg, response="No command")
            return None
        command = self.tokens[0]
        if "go" == command:
            resultstate = GoState(self.printer, self.logger, msg, self.boardposition, self.engine_color)
        elif "stop" == command:
            # operazione di stop
            pass
        elif "quit" == command:
            self._log(command=msg, response="I\'m quitting")
            resultstate = QuitState(self.printer, self.logger, msg)
        else:
            self._log(command=msg, response="Not a valid command! Commands accepted: go, stop, quit")
            self.invalidcommand = True

        return resultstate

    def execute(self):
        if self.invalidcommand:
            return
        # aggiornamento della posizione e di tutte le strutture dati coinvolte
        tokens = self.command.split()
        keyword = tokens[1]
        index = tokens.index('moves')
        try:
            if keyword == 'startpos':
                # startpos
                self.boardposition = gm.startpos_factory(self.engine_color)
                iswhiteactivecolor = True
            else:
                # fenstring
                fenparser = gm.FenStrParser(self.engine_color)
                self.boardposition = fenparser(tokens[1:index])
                iswhiteactivecolor = fenparser.activecolor
            movesetter = gm.UciMoveSetter(self.boardposition, tokens[index + 1:])
            movesetter(iswhiteactivecolor)
            # debug
            self.printer.send("Position set\nEngine color: " + self.engine_color + '\n' + str(self.boardposition) + 'readyok\n')
        except Exception as e:
            raise e


class GoState(State):
    def __init__(self, printer, logger, command, boardposition, engine_color):
        self.threading = False
        self.boardposition = boardposition
        self.engine_color = engine_color
        self.gamethread = None
        self.bestmove = None
        self.command = None
        super().__init__(printer, logger, command)

    def parse(self, msg):
        resultstate = self
        tokens = msg.split()
        if len(tokens) < 1:
            return PassState(self)
        command = tokens[0]
        # ho un dubbio... non è che qui si rischia di saltare alla prossima mossa prima che l'engine abbia finito?
        if "position" == command and self.gamethread.is_alive():
            self._log(command=msg, response="Not possible: current evaluation not finished!")
        elif "position" == command and not self.gamethread.is_alive():
            keyword = tokens[1]
            if 'moves' not in tokens:
                self._log(command=self.command, response="Invalid Position command syntax")
            elif keyword == 'startpos':
                resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)
            elif len(tokens[1:tokens.index('moves')]) != 6:
                self._log(command=self.command, response="Invalid Position command syntax")
            else:
                resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)
        elif "stop" == command:
            # TODO al momento implemento STOP in maniera semplificata, poi metterò a posto
            self._log(command=self.command, response="I'm stopping")
            resultstate = PassState(self)
            self.gamethread.killthread()
            self.gamethread.randommove()
        elif "quit" == command:
            self._log(command=msg, response="I\'m quitting")
            resultstate = QuitState(self.printer, self.logger, msg)
            self.run = False
            self.gamethread.killthread()
        else:
            self._log(command=msg, response="Not a valid command! Commands accepted: position, stop, quit")
            resultstate = PassState(self)

        return resultstate

    def execute(self):
        if self.threading:
            return None
        # TODO setoption per poter settare la ply
        self.gamethread = gm.GameThread(self.boardposition, 4)
        isrunning = self.gamethread.is_alive()
        self.command = self
        while isrunning:
            if not self.gamethread.is_alive():
                break
            msg = input()
            self.command = self.command.parse(msg)
            self.command.execute()
            if isinstance(self.command, PassState):
                self.command = self.command.client
            if not command.run:
                isrunning = False
            if not self.gamethread.is_alive():
                break
        self.gamethread.join()
        self.bestmove = self.gamethread.getstrbestmove()
        self.printer.send(str(self.bestmove) + '\n')
        self._log(command=self.command, response="Evaluation going on!")


class PassState:
    def __init__(self, client):
        self.client = client

    def execute(self):
        pass


class QuitState(State):
    def execute(self):
        self.run = False
        self._log(command=self.command)


# debug
if __name__ == '__main__':
    import sys

    try:
        isrunning = True
        ucilogfile = open("ucilog.txt", "a")
        logger = ucioutmodule.Logger(ucilogfile)
        logger.initcurlogsession()
        printer = ucioutmodule.Printer(sys.stdout)
        command = StartState(printer, logger)
        while isrunning:
            msg = input()
            command = command.parse(msg)
            command.execute()
            if isinstance(command, PassState):
                command = command.client
            if not command.run:
                isrunning = False
    except Exception as e:
        raise e
    finally:
        ucilogfile.close()
