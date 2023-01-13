import json

from django.http import JsonResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.core import serializers
from django.forms.models import model_to_dict

from service.models import PhotoItem
from service.serializers import PhotoItemSerializer, QueryCustomSerializerRAWQ


class PhotoItemViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'patch', 'head', 'delete')  # option
    # pk_url_kwarg = 'id'

    # in url http://127.0.0.1:8000/photos/?search=exa
    # http://127.0.0.1:8000/photos/?lat=12.23000&long=12.12000000&author=3
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'description', 'lat', 'long', 'created_date']  # 'names' - err

    # filter_backends = [filters.SearchFilter]
    # search_fields = ['author', 'description', '=names']

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


class GetNames(APIView):
    def get(self, request, **kwargs):
        q = kwargs.get('query')

        if q:
            q = q + '%'  # process like
            # or use %% for escape % in sql; TUPLE IN PARAMS, dont use '' in query
            # SELECT array_agg(x) from service_photoitem, UNNEST(names) x where x like %s';
            query = PhotoItem.objects.raw("SELECT id, x from service_photoitem, UNNEST(names) x where x like %s",
                                         params=(q,))
            print(query.query)

            # serialize to list
            result = []
            result_dict_list = []
            for item in query:
                result.append(item.x)

                # result_dict_list.append(item.__dict__)
                result_dict_list.append({'id': item.id, "x": item.x})

                print(item.id, item.x)

                # print(item.__dict__)
                # print(model_to_dict(item))

            # data = serializers.serialize('json', query, safe=False)
            # return JsonResponse(data=query, safe=False)

            # return Response(data={'data': result})
            print(result_dict_list)

            data_to_serializer = result_dict_list
            res = QueryCustomSerializerRAWQ(data=data_to_serializer, many=True)
            is_v = res.is_valid()
            res = res.validated_data
            print('valid: ', is_v)
            return Response(data=res)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetNamesR(RetrieveAPIView):
    def get_queryset(self):
        q = self.kwargs.get('query')

        if q:
            q = q + '%'  # process like
            # or use %% for escape % in sql
            # SELECT array_agg(x) from service_photoitem, UNNEST(names) x where x like 'a%';
            return PhotoItem.objects.raw("SELECT array_agg(x) from service_photoitem, UNNEST(names) x where x like %s",
                                         params=(q))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # def retrieve(self, request, *args, **kwargs):
    #     pass
