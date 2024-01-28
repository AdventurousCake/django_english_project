from django.contrib.postgres.aggregates import ArrayAgg
from django.contrib.postgres.fields.array import ArrayContains
from django.db.models import Q, CharField
from django.db.models.functions import Cast
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
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

    # todo
    tags2 = serializers.CharField(source='tags')
    tag_names_list = serializers.ListField()

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


class SearchFix(APIView):
    def get(self, request):
        selected_tag = request.GET.get("tag")
        # request.query_params.get("tag", "Punctuation")
        if not selected_tag:
            selected_tag = 'Punctuation'

        eng = (
            EngFixer.objects
            .prefetch_related('tags')
            # .filter(tags__name__contains=selected_tag) # INCORR

            .filter(id__in=EngFixer.objects.filter(tags__name='Grammar')
                    .values_list('id', flat=True))

            .annotate(tag_names_list=ArrayAgg('tags__name')) #,distinct=True))
            # .annotate(has_grammar=Cast(ArrayContains('tags', 'Grammar'), CharField()))
            # .filter(has_grammar=True)

            # .filter(tags__name=selected_tag)

            # .filter(Q(tags__name=selected_tag))
            .order_by('-created_date')
            [:15])

        serializer = EngSerializer(eng, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class SearchStrFix(APIView):
    def get(self, request):
        q = request.GET.get("q").lower()
        # request.query_params.get("tag", "Punctuation")
        if not q:
            pass

        eng = (
            EngFixer.objects
            .prefetch_related('tags')
            .filter(input_sentence__icontains=q)
            .order_by('-created_date')
            [:15])

        serializer = EngSerializer(eng, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


if __name__ == '__main__':
    from eng_service.models import EngFixer, Tag, User, UserProfile

    print(dir(UserProfile))
