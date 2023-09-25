from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Sum
from django.utils.text import gettext_lazy as _


# TODO
class EngFixer(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    input_sentence = models.CharField(null=False, max_length=256, unique=True)
    translatedRU = models.CharField(null=True, max_length=256)

    CORRECT_RESPONSE = models.JSONField(null=True)
    fixed_result = models.CharField(null=False, blank=True, max_length=256)
    # rephrases_list
    rephrases = ArrayField(models.CharField(max_length=150, blank=True), null=True)
    # size=8,)
    mistakes = models.CharField(null=True, max_length=256)

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['id', 'input_sentence'], name='unique_id_input_sentence'),
    #     ]



