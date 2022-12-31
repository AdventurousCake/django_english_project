from rest_framework.viewsets import ModelViewSet


class MessagesViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'patch', 'head', 'delete')  # option
    # permission_classes = (IsOwnerOrReadOnly, permissions.IsAuthenticatedOrReadOnly)  # (permissions.AllowAny,)
    # throttle_classes = [UserRateThrottle]
    # throttle_scope = 'low_request'

    # queryset = Message.objects.all() # not optimal for author field
    # queryset = Message.objects.all().select_related("author").prefetch_related("groups", "user_permissions") # invalid parameters in prefetch
    # queryset = Message.objects.all().select_related("author").prefetch_related("author.groups", "author.user_permissions") # invalid parameters in prefetch

    # queryset = Message.objects.all().select_related("author")  # not optimal for author fields fk
    queryset = Message.objects.all().prefetch_related("author")

    # FOR ALL USER DATA; UNDERSCORE in fields
    # queryset = Message.objects.all().select_related("author").prefetch_related("author__groups", "author__user_permissions")

    serializer_class = MsgSerializer

    # PERFORM CREATE находится внутри create, после валидации(is_valid)! check overrides
    def perform_create(self, serializer):
        if self.request.user:
            serializer.save(author=self.request.user)
        else:
            # 401 unauthorized
            return Response(status=status.HTTP_401_UNAUTHORIZED)