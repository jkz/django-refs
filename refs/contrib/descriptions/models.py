import django.db.models as m

from django.conf.global_settings import LANGUAGES
from django.conf.settings import LANGUAGE_CODE

import refs

class Description(m.Model):
    obj = refs.RefField('descriptions')
    lang = m.CharField(max_length=7, choices=LANGUAGES,
            default=LANGUAGE_CODE)

    head = m.TextField()
    body = m.TextField()

    class Meta:
        unique_together = [('obj', 'lang')]

    def __str__(self):
        return '({}) {}'.format(self.lang, self.head or self.body[:20])

    def to_json(self):
        return {'obj': self.obj.pk,
                'lang': self.lang,
                'head': self.head,
                'body': self.body}
