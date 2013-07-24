from django.core.validators import MinValueValidator
import django.db.models as m

import refs

from utils.contexts import NestingTransaction
from utils.models import QuerySetModel, TimestampMixin, PaginatorMixin
from utils.fields import TimestampField

class Move(QuerySetModel):
    """A Move represents a transaction of an amount of currency from one
    object to another.
    """

    giver = refs.RefField('gives')
    taker = refs.RefField('takes')
    reason = refs.RefField('moves', null=True)
    amount = m.PositiveIntegerField(validators=[MinValueValidator(1)])
    currency = m.TextField()
    timestamp = TimestampField()

    def __str__(self):
        return 'Move: {} {} from {} to {}'.format(self.amount, self.currency,
                self.giver, self.taker)

    class Error(Exception): pass
    class Nop(Error): pass
    class NeedMore(Error): pass
    class Self(Nop): pass
    class Zero(Nop, ValueError): pass
    class Negative(Nop, ValueError): pass

    class QuerySet(m.query.QuerySet, TimestampMixin, PaginatorMixin):
        @property
        def total(self):
            return self.aggregate(m.Sum('amount'))['amount__sum'] or 0


class Maker(m.Model):
    """Makers are the currency pool of the system. They make credits out of
    nothing. (Or more accurately, serve as anti-credit)"""
    owner = refs.OneToOneRef(primary_key=True, related_name='_maker')

    # Makes maxint by default
    def make(self, currency, amount=None):
        if not amount:
            amount = 2 ** 31 - 1
        return Move.objects.create(giver=self, taker=self.owner,
                amount=amount, currency=currency)


class Stash(m.Model):
    owner = refs.RefField('stashes')
    name = m.TextField()

    class Meta:
        unique_together = [('owner', 'name')]


class Have(object):
    """A Have represents the balance of an object for given currency."""
    def __init__(self, obj, currency):
        self.obj = obj
        self.currency = currency

    @property
    def moves(self):
        return Move.objects.filter(m.Q(giver=self.obj) | m.Q(taker=self.obj))

    def __getattr__(self, attr):
        return getattr(self.moves, attr)

    def create(self, **kwargs):
        return self.moves.create(giver=self.obj, currency=self.currency, **kwargs)

    @property
    def takes(self):
        return self.moves.filter(taker=self.obj)

    @property
    def gives(self):
        return self.moves.filter(giver=self.obj)

    @property
    def have(self):
        return self.takes.total - self.gives.total

    @property
    def moved(self):
        return self.takes.total + self.gives.total

    def give(self, amount, taker, **kwargs):
        amount = int(amount)
        if not amount:
            raise Move.Zero("Can't give 0")
        elif amount < 0:
            raise Move.Negative("Can't give negative")

        with NestingTransaction():
            if refs.equals(taker, self.obj):
                raise Move.Self("Can't give to self")
            have = self.have
            if have < amount:
                raise Move.NeedMore("{} is not enough to give {}".format(have, amount))
            return self.create(taker=taker, amount=amount, **kwargs)

