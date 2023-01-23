from rest_framework import serializers

from service.models import PhotoItem


class PhotoItemSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    # author = UserSerializer(read_only=True)  # not many! v1
    # author = UserSerializer(read_only=True)  # not many! v2
    # author = serializers.StringRelatedField(source='message.author')  # v3 dw
    # owner = serializers.ReadOnlyField(source='owner.username')

    # or save in perform create

    class Meta:
        fields = ('id', 'author', 'description', 'names', 'created_date', 'lat', 'long', 'image', 'is_public')

        # сериализатор не ждёт в теле POST-запроса поле owner (а если оно придёт, то будет проигнорировано).
        read_only_fields = ('author',)  # ('post', 'created', 'OWNER')
        model = PhotoItem

    def validate_text(self, value):
        if value == 'not valid':
            raise serializers.ValidationError('Проверьте text (validate_text validator)')
        return value


class QueryCustomSerializerFORSEARCH(serializers.Serializer):
    id = serializers.IntegerField()
    author = serializers.CharField()
    names = serializers.ListField(child=serializers.CharField(), max_length=150)

class QueryCustomSerializer(serializers.Serializer):
    names = serializers.ListField(child=serializers.CharField(), max_length=150)


class QueryCustomSerializerRAWQ(serializers.Serializer):
    id = serializers.IntegerField()
    # name_list = serializers.ListField(child=serializers.CharField(), max_length=150)
    x = serializers.CharField()
