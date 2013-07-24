import django.db.models as m
from django.contrib.contenttypes.models import ContentType

import refs
import credits

from utils.contexts import NestingTransaction
from utils.decorators import created_receiver
from utils.functions import getattr_recursive
from utils.fields import TimestampField
from utils.models import QuerySetModel, RequestQuerySet, QuerySetManager

from . import signals


class Rule(QuerySetModel):
    """
    A rule is a template for a hook. The template specifies a currency, a value
    and a receiving end. The rule can then be 'instantiated' into hooks.
    """
    NONE, SOURCE, SELF, HOOK = range(4)
    RECEIVERS = (
        (NONE, 'none'),  # Nobody gets anything
        (SOURCE, 'src'), # The user gets it all
        (HOOK, 'hook'),  # The targeted hook gets it
    )
    name = m.TextField()

    ruler = refs.RefField('rules')
    content_type = m.ForeignKey(ContentType)
    rerule = m.ForeignKey('self', related_name='rerulers', null=True)
    receiver = m.IntegerField(choices=RECEIVERS, default=NONE)

    currency = m.TextField()
    value = m.PositiveIntegerField(default=0)

    class Meta:
        unique_together = [('ruler', 'name')]

    class QuerySet(RequestQuerySet):
        def populate(self, model, ruler, name, **kwargs):
            """
            Creates or changes a given rule.
            """
            content_type = ContentType.objects.get_for_model(model)
            rule, created = self.model.objects.get_or_create(
                    content_type=content_type,
                    ruler=ruler,
                    name=name)
            if kwargs:
                for key, val in kwargs.items():
                    setattr(rule, key, val)
                rule.save()
            return rule


    def __str__(self):
        return '{} by {}'.format(self.name, self.ruler)


class BoostableManager(QuerySetManager):
    def get_query_set(self):
        return super(BoostableManager,
                self).get_query_set().filter(rule__rerule__isnull=True)


class ReruleManager(QuerySetManager):
    def get_query_set(self):
        return super(ReruleManager,
                self).get_query_set().filter(rule__rerule__isnull=False)


class Hook(m.Model):
    """
    A hook is an instance of a Rule.
    """
    rule = m.ForeignKey(Rule, related_name='hooks')
    owner = refs.RefField('hooks_owned')
    obj = refs.RefField('hooks')
    is_active = m.BooleanField(default=True)
    timestamp = TimestampField()

    objects = QuerySetManager()
    boostables = BoostableManager()
    rerulers = ReruleManager()

    class Meta:
        unique_together = [('rule', 'obj')]
        ordering = ['-timestamp']

    def __str__(self):
        return '{} for {} of {}' % (self.rule, self.obj, self.user)

    class QuerySet(RequestQuerySet):
        def targeting(self, model):
            """Return all hooks with given model as obj"""
            content_type = ContentType.objects.get_for_model(model)
            return self.filter(obj__namespace=content_type.app_label,
                    obj__model=content_type.model)

        def accepting(self, model):
            """Return all hooks with given model as content_type"""
            content_type = ContentType.objects.get_for_model(model)
            return self.filter(rule__content_type=content_type)

        def applicables(self, sender, obj):
            """Return all hooks that respond to given object"""
            # A hook's object is never its user
            return self.accepting(sender).filter(obj=obj).exclude(user=obj)

        def listen(self, sender, binder, target_attr, user_attr, obj_attr=None):
            #XXX This is a fairly narrow construct.
            # sender - model class that will trigger this check
            # binder - model class that hooks are bound to
            # target_attr - instance attribute that represents the target
            # user_attr - instance attribute that represents the user
            # obj_attr - instance attribute that represents the hook trigger
            dispatch_uid = '.'.join((sender.__name__, binder.__name__))
            @created_receiver(sender, dispatch_uid=dispatch_uid)
            def listener(instance, **kwargs):
                target = getattr_recursive(instance, target_attr)
                for h in self.applicables(binder, target):
                    user = getattr_recursive(instance, user_attr)
                    if obj_attr:
                        obj = getattr_recursive(instance, obj_attr)
                    else:
                        obj = instance
                    self.fire(user, obj)


    def resolve(self, src, obj):
        rule = self.rule

        # Create a hook when appropriate and give it the starting funds
        hook = None
        if rule.rerule:
            hook = rule.rerule.hooks.create(src=src, obj=obj)

        if not rule.value or rule.receiver == Rule.NONE:
            return

        # Create the hooks value by the app
        credits.move(rule.ruler, obj, rule.value, rule.currency)

        # Transfer the value to the user
        credits.move(obj, user, rule.value, rule.currency)

        if rule.receiver == Rule.SOURCE:
            # Notify any listeners that the user has received a fee
            signals.fee_signal.send(sender=hook, src=src, amount=rule.value,
                    currency=rule.currency)
        elif rule.receiver == Rule.HOOK:
            if hook:
                credits.move(src, hook, rule.value, rule.currency)
                signals.hook_signal.send(sender=hook, src=src, obj=obj)
            else:
                credits.move(src, self, rule.value, rule.currency)
                signals.hook_signal.send(sender=self, src=src, obj=obj)


    def boost(self, src, amount):
        return credits.move(src, self, amount, self.rule.currency)

    def fire(self, src, obj):
        return self.triggers.create(obj=obj, src=src)


class Trigger(QuerySetModel):
    PENDING, RESOLVING, ACCEPTED, REJECTED, REVERTED = range(5)
    STATES = (
        (PENDING, 'Pending'),
        (RESOLVING, 'Resolving'),  # Should not appear in db
        (ACCEPTED, 'Accepted'),
        (REJECTED, 'Rejected'),
        (REVERTED, 'Reverted'),
    )

    hook = m.ForeignKey(Hook, related_name='triggers')

    obj = refs.RefField('as_trigger')
    src = refs.RefField('triggers')

    timestamp = TimestampField()
    state = m.PositiveIntegerField(choices=STATES, default=PENDING)

    class Meta:
        #unique_together = [('hook', 'obj')]
        ordering = ['-timestamp']

    def __str__(self):
        return '{} with {} by {}'.format(self.hook, self.obj, self.src)

    class Rejection(Exception):
        """Alerts a trigger that should not be regarded"""
        #XXX: Could hold a message to add to the 'note' (or 'error') field
        pass

    def resolve(self):
        """Resolve a trigger if it is pending."""
        if self.state != Trigger.PENDING:
            return

        self.state = Trigger.RESOLVING
        with NestingTransaction() as t:
            try:
                self.hook.resolve(user=self.src, obj=self.obj)
            except Trigger.Rejection:
                t.rollback()
                self.state = Trigger.REJECTED
            else:
                self.state = Trigger.ACCEPTED
        self.save()
        return

    class QuerySet(RequestQuerySet):
        def resolve(self, limit=1):
            triggers = self.filter(state=Trigger.PENDING)[limit]
            return [t.resolve() for t in triggers]


@created_receiver(Trigger)
def trigger_handler(instance, **kwargs):
    #XXX This is for now as this should be a subtask, but we don't know
    # for sure if we're subtasking or not
    return instance.resolve()

