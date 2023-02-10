import json

from django.db.models import Q, F, Func
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, filters
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.core import serializers
from django.forms.models import model_to_dict

from service.models import PhotoItem
from service.serializers import PhotoItemSerializer, QueryCustomSerializerRAWQ, QueryCustomSerializerFORSEARCH


class ThrottleMix:
    # throttle_classes = [UserRateThrottle]
    throttle_scope = 'low_request'


class PhotoItemViewSet(ModelViewSet):
    http_method_names = ('get', 'post', 'put', 'patch', 'head', 'delete')  # option
    # pk_url_kwarg = 'id'

    # in url http://127.0.0.1:8000/photos/?search=exa
    # http://127.0.0.1:8000/photos/?lat=12.23000&long=12.12000000&author=3&is_public=1

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['author', 'description', 'lat', 'long', 'created_date', 'is_public']  # 'names' - err

    # filter_backends = [filters.SearchFilter] # DW bc nested items
    # search_fields = ['=names']
    # # search_fields = ['author', 'description', '=names']

    queryset = PhotoItem.objects.all()

    serializer_class = PhotoItemSerializer

    # PERFORM CREATE находится внутри create, после валидации(is_valid)! check overrides
    # TODO
    def perform_create(self, serializer):
        if self.request.user:
            serializer.save(author='default')
            # serializer.save(author=self.request.user)
        else:
            # 401 unauthorized
            return Response(status=status.HTTP_401_UNAUTHORIZED)


class GetOnlyNames(APIView):
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
            result_dict_list = [{'id': item.id, "x": item.x} for item in query]
            print(result_dict_list)

            data_to_serializer = result_dict_list
            res = QueryCustomSerializerRAWQ(data=data_to_serializer, many=True)
            is_v = res.is_valid()
            if not is_v:
                print(res.errors)
            return Response(data=res.validated_data)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class GetFilteredByName(APIView):
    def get(self, request, **kwargs):
        q = self.kwargs.get('query')

        if q:
            q_raw = q
            q = q + '%'  # process like
            result_dict_list = []

            # id,author,names
            # data = PhotoItem.objects.raw("SELECT * FROM service_photoitem, UNNEST(names) as name WHERE name LIKE %s;",
            #                              # "SELECT id,author,description,names,created_date,lat,long,image FROM service_photoitem, UNNEST(names) as name WHERE name LIKE %s;",
            #                              params=(q,))

            # data = PhotoItem.objects.filter(names__contains=[q_raw])  # ALT (!!! [])
            data = PhotoItem.objects.filter(names__icontains=q_raw)  # ALT

            # data = PhotoItem.objects.filter(names__contains=[q_raw]).values('names')  # ALT 2
            # data = PhotoItem.objects.filter(names__contains=q_raw).values('names')# dw
            # data = PhotoItem.objects.annotate(arr_els=Func(F('names'), function='unnest')).values_list('arr_els', flat=True)

            # 1
            # for item in data:
            #     print(item)
            #     result_dict_list.append({'id': item.id, "author": item.author, "names": item.names})
            #
            # res = QueryCustomSerializerFORSEARCH(data=result_dict_list, many=True)
            # is_v = res.is_valid()
            # if not is_v:
            #     print(res.errors)
            # return Response(data=res.validated_data)

            # 2
            # res = QueryCustomSerializerFORSEARCH(data=data, many=True)
            # is_v = res.is_valid()
            # if not is_v:
            #     print(res.errors)
            # # just data
            # return Response(res.data)

            # 3
            res = QueryCustomSerializerFORSEARCH(data=data, many=True)
            is_v = res.is_valid()
            if not is_v:
                print(res.errors)
            return Response(res.data)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# use APIView
class GetNamesSIMPLE(RetrieveAPIView):
    def get_queryset(self):
        q = self.kwargs.get('query')

        if q:
            q = q + '%'  # process like
            # or use %% for escape % in sql
            # SELECT array_agg(x) from service_photoitem, UNNEST(names) x where x like 'a%';
            return PhotoItem.objects.raw("SELECT array_agg(x) from service_photoitem, UNNEST(names) x where x like %s",
                                         params=(q,))
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    # def retrieve(self, request, *args, **kwargs):
    #     pass
