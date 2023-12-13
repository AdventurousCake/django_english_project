from rest_framework import serializers
from rest_framework.viewsets import ModelViewSet

from eng_service.models import EngFixer, Tag, User, UserProfile, Request


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class EngSerializer(serializers.ModelSerializer):
    class Meta:
        model = EngFixer
        fields = '__all__'
        # exclude = ['tags']

    tags = TagSerializer(many=True, read_only=True)

    # tags2 = TagSerializer(
    #     source='tags',
    #     many=True, read_only=True)


class EngViewSet(ModelViewSet):
    """_vset/ get by id"""
    queryset = EngFixer.objects.prefetch_related('tags').all()
    serializer_class = EngSerializer

# TODO =========================
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Request
        fields = '__all__'

    fix = EngSerializer()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

    # user = UserSerializer()
    req1 = RequestSerializer(source='request_set', many=True)
    req = serializers.CharField(source='request_set')
    # fixes = serializers.CharField(source='request_set__fix__fixed_sentence')


class UserViewSet(ModelViewSet):
    queryset = UserProfile.objects.select_related('user').prefetch_related('request_set__fix__tags').all()
    serializer_class = UserProfileSerializer


if __name__ == '__main__':
    from eng_service.models import EngFixer, Tag, User, UserProfile
    print(dir(UserProfile))
