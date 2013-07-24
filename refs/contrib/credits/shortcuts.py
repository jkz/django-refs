import refs

from .models import Have, Maker, Stash

def maker(obj):
    """Get or create a credit source for given object"""
    return Maker.objects.get_or_create(owner=obj)[0]

def make(obj, currency, amount=None):
    """Create an amount of currency for given object"""
    maker(obj).make(currency, amount)

def move(giver, taker, amount, currency, **kwargs):
    """Transfer an amount of currency from giver to taker"""
    return Have(giver, currency).give(amount, taker, **kwargs)

def have(obj, currency):
    """Return the current balance of currency of given object"""
    return Have(obj, currency).have

def taken(obj, currency):
    """Return total of receivings of currency for given object"""
    return Have(obj, currency).takes.total

def given(obj, currency):
    """Return the total of spendings of currency for given object"""
    return Have(obj, currency).gives.total

def moved(obj, currency):
    """Return the total currency moved involving given object"""
    return taken(obj) + given(obj)

def stash(obj, name):
    return Stash.objects.get_or_create(name=name, owner=obj)[0]

refs.Ref.have = have
refs.Ref.taken = taken
refs.Ref.given = given
refs.Ref.gives = moved
refs.Ref.give = move

Stash.have = have
Stash.taken = taken
Stash.given = given
Stash.gives = moved
Stash.give = move

class Haves(object):
    """This class exists for convenient template access"""
    def __init__(self, obj):
        self.obj = obj

    def __getitem__(self, key):
        return Have(self.obj, key)

refs.Ref.haves = property(lambda self: Haves(self))
refs.Ref.maker = property(lambda self: Haves(self._maker))
