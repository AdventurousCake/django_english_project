from rest_framework import serializers


class MsgSerializer(serializers.ModelSerializer):
    # author = serializers.StringRelatedField(read_only=True)
    # author = UserSerializer(read_only=True)  # not many! v1
    author = UserSerializer(read_only=True)  # not many! v2

    # author = serializers.StringRelatedField(source='message.author')  # v3 dw
    # owner = serializers.ReadOnlyField(source='owner.username')

    # or save in perform create

    class Meta:
        fields = ('id', 'name', 'text', 'created_date', 'author', 'msg_length')  # 'author'

        # сериализатор не ждёт в теле POST-запроса поле owner (а если оно придёт, то будет проигнорировано).
        read_only_fields = ('author',)  #('post', 'created', 'OWNER')

        model = Message

    def validate_text(self, value):
        if value == 'not valid':
            raise serializers.ValidationError('Проверьте text (validate_text validator)')
        return value