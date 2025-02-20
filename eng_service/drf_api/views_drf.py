from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.drf_api.serializers import InputSerializer, RespSerializer, EngSerializerVSETsimple
from eng_service.models import EngFixer
from eng_service.utils_ import FixerResultProcessor


class EngFixApiPOST(APIView):

    @swagger_auto_schema(request_body=InputSerializer)
    def post(self, request):
        """data passed in post data"""
        serializer = InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_sentence = serializer.validated_data.get('input_sentence')
        data = FixerResultProcessor.process_data(input_sentence)

        r = RespSerializer(data=data)
        if r.is_valid():
            return Response(r.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(r.errors, status=status.HTTP_400_BAD_REQUEST)

class FixViewSetRO(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly,]
    # http_method_names = ['get']

    queryset = EngFixer.objects.prefetch_related('tags').all()
    serializer_class = EngSerializerVSETsimple


class EngFixApiFILTER(APIView):
    """filter http://127.0.0.1:8000/api1/test/?filter=grammar
    """
    def get(self, request):
        params=request.GET.get('filter')
        queryset = EngFixer.objects.prefetch_related('tags').filter(tags__name__iexact=params).all()

        serializer = EngSerializerVSETsimple(queryset, many=True)
        return Response(serializer.data)
