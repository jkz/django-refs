import django.db.models as m

import refs

class Privacy(m.Model):
    PUBLIC, PRIVATE = range(3)
    LEVELS = (
        (PUBLIC, 'Public'),
        (PRIVATE, 'Private'),
    )
    owner = refs.OneToOneField('privacy', primary_key=True)
    level = m.IntegerField(choices=LEVELS, default='Private')

class Permission(m.Model):
    UNDEFINED, PENDING, DENIED, GRANTED = range(4)
    LEVELS = (
        (UNDEFINED, 'Undefined'),
        (PENDING, 'Granted'),
        (DENIED, 'Denied'),
        (GRANTED, 'Granted'),
    )

    granter = refs.ManyToOneField('permissionings')
    grantee = refs.ManyToOneField('permissions')
    level = m.IntegerField(choices=LEVELS)

    class Meta:
        unique_together = [('granter', 'grantee')]

def has_permission(user, owner):
    priv = owner.privacy.level
    try:
        perm = Permission.objects.get(grantee=user, granter=owner).level
    except Permission.DoesNotExist:
        perm = Permission.LEVELS.UNDEFINED
    return perm == Permission.LEVELS.GRANTED or \
            (priv == Privacy.LEVELS.PUBLIC and perm != Permission.LEVELS.DENIED)
