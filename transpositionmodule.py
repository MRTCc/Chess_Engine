def transpositiontablefactory(algorithm):
    if algorithm == 'minmax':
        transpositiontable = TranspositionTable(MinMaxRecord)
    elif algorithm == 'alphabeta':
        transpositiontable = TranspositionTable(AlphaBetaRecord)
    else:
        raise ValueError("Transpositiontablefactory --> algorithm not valid!!!")
    return transpositiontable


class TranspositionTable:
    def __init__(self, record_class):
        self.records = {}
        self.record_class = record_class

    def lookup(self, key):
        return self.records[key]

    def getrecordfromkey(self, key):
        record = self.records[key]
        if record:
            return record.getrecorddata()
        else:
            return None

    def insertnewrecord(self, key, *args):
        pass

    def _collisionmanagement(self):
        pass


class Record:
    def __init__(self, key, score, searchdepth):
        self.key = key
        self.score = score
        self.searchdepth = searchdepth

    def getrecorddata(self):
        pass


class MinMaxRecord(Record):
    def __init__(self, key, score, searchdepth):
        super().__init__(key, score, searchdepth)

    def getrecorddata(self):
        return self.score


class AlphaBetaRecord(Record):
    def __init__(self, key, score, alpha, beta, searchdepth):
        super().__init__(key, score, searchdepth)
        self.alpha = alpha
        self.beta = beta

    def getrecorddata(self):
        return self.score, self.alpha, self.beta


if __name__ == '__main__':
    pass
