from rest_framework import serializers

from eng_service.models import EngFixer, Tag


class InputSerializer(serializers.Serializer):
    input_sentence = serializers.RegexField(max_length=100, min_length=3, 
                                            regex=r"""^[a-zA-Z0-9\s\\.,\\?!’'"\-_]+$""",
                                            required=True)


class RespSerializer(serializers.Serializer):
    input_str = serializers.CharField(source='input_sentence')
    fixed_sentence = serializers.CharField()
    rephrases_list = serializers.ListField(child=serializers.CharField())
    its_correct = serializers.BooleanField()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class EngSerializerVSETsimple(serializers.ModelSerializer):
    class Meta:
        model = EngFixer
        fields = '__all__'

    tags = TagSerializer(many=True, read_only=True)
