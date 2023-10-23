import re

import uuid
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils.text import gettext_lazy as _

from eng_service.models_core import User


def validate_text_string(value):
    # todo and nubmers?
    pattern = r'^[a-zA-Z\s\.,?!]+$'
    if not re.match(pattern, value):
        raise ValidationError("Only text are allowed")

#m2m; неявное созд доп таблицы
# class Tag(models.Model):
#     id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
#     name = models.CharField(null=False, max_length=256)

# o2m
class Request(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)  # db_index=True
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True)  # or anonymous user
    fix = models.ForeignKey(to='EngFixer', on_delete=models.CASCADE, null=False)
    created_date = models.DateTimeField(null=False, auto_now_add=True)


# INDEX INPUT UNIQUE
class EngFixer(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)

    input_sentence = models.CharField(null=False, max_length=256, unique=True, validators=[validate_text_string])
    # input_sentence = models.CharField(null=False, max_length=256)
    translated_RU = models.CharField(null=True, max_length=256)
    fixed_result_JSON = models.JSONField(null=True)
    fixed_sentence = models.CharField(null=False, blank=True, max_length=256)
    rephrases_list = ArrayField(models.CharField(max_length=150, blank=True), null=True)
    # size=8,)
    mistakes = models.CharField(null=True, max_length=256)

    created_date = models.DateTimeField(null=False, auto_now_add=True)

    # model-level validation; validators - field level (by full_clean)
    def clean(self):
        if len(self.input_sentence) <= 3:
            raise ValidationError({"input_sentence": 'Input sentence is too short'})
            # raise ValidationError('Input sentence is too short') # err

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("eng_service:eng_get", kwargs={"pk": self.pk})
        # return reverse("eng_service:eng_get", kwargs={"pk": self.id})

    # def __repr__(self):
    #     return self.input_sentence

    # form class clean
    # def clean(self):
    #     data = self.cleaned_data["input_sentence"]
    #
    #     if len(data) <= 3:
    #         raise ValidationError('Input sentence is too short')
    #     return data

    # def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
    #     pass

    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(fields=['id', 'input_sentence'], name='unique_id_input_sentence'),
    #     ]


# profile = UserProfile.objects.select_related('user').get(id=user_profile_id)
class UserProfile(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)