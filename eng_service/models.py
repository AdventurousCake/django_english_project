import re

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models

from eng_service.models_core import User
from eng_service.service_eng import EngFixParser


def validate_text_string(value):
    pattern = r"""^[a-zA-Z0-9\s\\.,\\?!’'"\-_]+$"""  # ’
    if not re.match(pattern, value):
        raise ValidationError("Only text are allowed")

#m2m; неявное созд доп таблицы
class Tag(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    name = models.CharField(null=False, max_length=256, unique=True)
    str_name = models.CharField(null=True, max_length=256)

    class Meta:
        indexes = [
            models.Index(fields=['name'], name='tagname_idx'),]

    def __repr__(self):
        return self.name

# o2m
class Request(models.Model):
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)  # db_index=True

    user_profile = models.ForeignKey(to='UserProfile', on_delete=models.CASCADE, null=True)  # or anonymous user
    fix = models.ForeignKey(to='EngFixer', on_delete=models.CASCADE, null=False)
    created_date = models.DateTimeField(null=False, auto_now_add=True)



class EngFixer(models.Model):
    # uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)

    input_sentence = models.CharField(null=False, max_length=256, unique=True, validators=[validate_text_string])
    # translated_RU = models.CharField(null=True, max_length=256)
    fixed_result_JSON = models.JSONField(null=True)
    fixed_sentence = models.CharField(null=False, blank=True, max_length=256)
    rephrases_list = ArrayField(models.CharField(max_length=150, blank=True), null=True)  # size=8,)
    its_correct = models.BooleanField(null=True, default=None)

    mistakes_most_TMP = models.CharField(null=True, max_length=256)
    mistakes_list_TMP = ArrayField(models.CharField(max_length=150, blank=True), null=True)

    # using eng_service_engfixer_tags
    tags = models.ManyToManyField(to='Tag') #through: related_name='fix', on_delete=models.SET_NULL)

    translated_input = models.CharField(null=True, max_length=256)
    translated_fixed = models.CharField(null=True, max_length=256)

    is_public = models.BooleanField(null=False, default=True)
    # created_by = models.ForeignKey(to='User', on_delete=models.CASCADE, null=False)
    created_date = models.DateTimeField(null=False, auto_now_add=True)

    def get_mistakes(self):
        return EngFixParser().parse_item_mistakes_V1(item=self.fixed_result_JSON)

    # model-level validation; validators - field level (by full_clean)
    def clean(self):
        if len(self.input_sentence) <= 3:
            raise ValidationError({"input_sentence": 'Input sentence is too short'})

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("eng_service:eng_get", kwargs={"pk": self.pk})
        # return reverse("eng_service:eng_get", kwargs={"pk": self.id})

    def __repr__(self):
        return f"(id:{self.id}, input:{self.input_sentence}, fixed:{self.fixed_sentence})"

    # def full_clean(self, exclude=None, validate_unique=True, validate_constraints=True):
    #     pass

    class Meta:
        # INDEX INPUT UNIQUE
        constraints = [
            models.UniqueConstraint(fields=['id', 'input_sentence'], name='unique_id_input_sentence'),
        ]
        indexes = [
            models.Index(fields=['its_correct'], name='its_correct_idx'), ]


class UserProfile(models.Model):
    """
    A OneToOneField is essentially the same as a ForeignKey, with the exception
    that it always carries a "unique" constraint with it and the reverse
    relation always returns the object pointed to (since there will only ever
    be one), rather than returning a list.
    """

    id = models.BigAutoField(primary_key=True, auto_created=True, null=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=False)