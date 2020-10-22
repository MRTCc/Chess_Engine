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
        super().__init__(printer, logger, command)

    def parse(self, msg):
        self.tokens = msg.split()
        if len(self.tokens) < 1:
            self._log(command=msg, response="No command")
            return None
        command = self.tokens[0]
        resultstate = None
        if "go" == command:
            resultstate = GoState(self.printer, self.logger, msg, self.boardposition, self.engine_color)
        elif "stop" == command:
            # operazione di stop
            resultstate = self
        elif "quit" == command:
            self._log(command=msg, response="I\'m quitting")
            resultstate = QuitState(self.printer, self.logger, msg)
        else:
            self._log(command=msg, response="Not a valid command! Commands accepted: go, stop, quit")
            resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)

        return resultstate

    def execute(self):
        # aggiornamento della posizione e di tutte le strutture dati coinvolte
        tokens = self.command.split()
        keyword = tokens[1]
        index = tokens.index('moves')
        try:
            if keyword == 'startpos':
                # startpos
                listpiece = gm.startpos_factory()
                self.boardposition = gm.WhiteGamePosition(listpiece)
            else:
                # fenstring
                fenparser = gm.FenStrParser()
                self.boardposition = fenparser(tokens[1:index])
                pass
            movesetter = gm.UciMoveSetter(self.boardposition, tokens[index + 1:])
            movesetter()
            # debug
            self.printer.send("Position set\nreadyok\n" + str(self.boardposition) + '\n')
        except Exception as e:
            raise e


class GoState(State):
    def __init__(self, printer, logger, command, boardposition, engine_color):
        self.threading = False
        self.boardposition = boardposition
        self.engine_color = engine_color
        super().__init__(printer, logger, command)

    def parse(self, msg):
        self.tokens = msg.split()
        command = self.tokens[0]
        resultstate = None
        # ho un dubbio... non è che qui si rischia di saltare alla prossima mossa prima che l'engine abbia finito?
        if "position" == command and self.threading == True:
            self._log(command=msg, response="Not possible: current evaluation not finished!")
        elif "position" == command and self.threading == False:
            resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)
        elif "stop" == command:
            # qui bisogna stoppare il thread di calcolo della mossa
            self._log(command=self.command, response="I'm stopping")
            resultstate = PositionState(self.printer, self.logger, msg, self.engine_color)
        elif "quit" == command:
            self._log(command=msg, response="I\'m quitting")
            resultstate = QuitState(self.printer, self.logger, msg)
        else:
            self._log(command=msg, response="Not a valid command! Commands accepted: position, stop, quit")
            resultstate = self

        return resultstate

    def execute(self):
        if self.threading:
            return None

        # questo è il nucleo dell'engine... qui parte  il thread per il calcolo della mossa

        self.printer.send("bestmove a7a6\n")
        self._log(command=self.command, response="Evaluation going on!")


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
            if not command.run:
                isrunning = False
    except Exception as e:
        raise e
    finally:
        ucilogfile.close()
