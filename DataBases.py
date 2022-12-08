import inspect, sys
from tinydb import TinyDB, Query


def Classes():

    return inspect.getmembers(sys.modules[__name__], inspect.isclass)


class DatabaseTinyDB:

    def __init__(self):
        self.db = TinyDB('testdb.json')
        self.q = Query()

    def add(self, x):
        '''

        :param x:
        :return:
        '''
        self.db.insert(x)

    def readAll(self):
        '''

        :return:
        '''
        return self.db.all()

    def columnsDistinct(self, x):
        '''
        Must be changed, as db gets bigger this will slow down like hell. does not take nested lists into account!!
        Used to get all valid items within a datacolumn
        Example usage: columnsDistinct('type')
        :param x: (str) 'column' to search for distinct items
        :return: list[]
        '''
        values = []
        for i in self.db.search(self.q[x].exists()):
            if i.get(x) not in values:
                values.append(i.get(x))
        return values

    def find(self, field, x):
        '''
        Example usage: print(db.find(['type'], ['apple']))
        :param field: (str) database 'column' to be searched for
        :param x: (str) value looked for
        :return: list[dic{}]
        '''
        # return self.db.search(self.q[tuple(field)].one_of(x))
        print(self.db.search(self.q[tuple(field)].one_of(field)))
        return []  # self.db.search(self.db.table('_default').all())

    def columnNames(self):
        values = []
        for i in self.db.table('_default').all()[0]:
            if i not in values:
                values.append(i)
        return values


