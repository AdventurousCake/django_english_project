from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.drf_api.serializers import InputSerializer, RespSerializer, EngSerializerVSETsimple
from eng_service.models import EngFixer
from eng_service.utils_ import FixerResultProcessor


class EngFixAPI(APIView):
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

class FixViewSet(viewsets.ReadOnlyModelViewSet):
    # http_method_names = ['get']

    queryset = EngFixer.objects.prefetch_related('tags').all()
    serializer_class = EngSerializerVSETsimple