from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from service.models import PhotoItem
from service.serializers import PhotoItemSerializer


class PhotoItemViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'patch', 'head', 'delete')  # option
    # pk_url_kwarg = 'id'

    # in url http://127.0.0.1:8000/photos/?search=exa
    # filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'description']

    filter_backends = [filters.SearchFilter]
    search_fields = ['author', 'description']

    # permission_classes = (IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)  # (permissions.AllowAny,)
    # throttle_classes = [UserRateThrottle]
    # throttle_scope = 'low_request'

    # queryset = Message.objects.all() # not optimal for author field
    # queryset = Message.objects.all().select_related("author").prefetch_related("groups", "user_permissions") # invalid parameters in prefetch
    # queryset = Message.objects.all().select_related("author").prefetch_related("author.groups", "author.user_permissions") # invalid parameters in prefetch

    # queryset = Message.objects.all().select_related("author")  # not optimal for author fields fk
    queryset = PhotoItem.objects.all()

    # FOR ALL USER DATA; UNDERSCORE in fields
    # queryset = Message.objects.all().select_related("author").prefetch_related("author__groups", "author__user_permissions")

    serializer_class = PhotoItemSerializer

    # PERFORM CREATE находится внутри create, после валидации(is_valid)! check overrides
    def perform_create(self, serializer):
        if self.request.user:
            serializer.save(author='default')
            # serializer.save(author=self.request.user)
        else:
            # 401 unauthorized
            return Response(status=status.HTTP_401_UNAUTHORIZED)
