from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView

from eng_service.utils_ import ResultProcessor


class InputSerializer(serializers.Serializer):
    input_sentence = serializers.RegexField(max_length=100, min_length=3, regex=r"""^[a-zA-Z0-9\s\\.,\\?!’'"\-_]+$""",
                                            required=True)


class RespSerializer(serializers.Serializer):
    # input_str = serializers.CharField()
    input_str = serializers.CharField(source='input_sentence')
    fixed_sentence = serializers.CharField()
    rephrases_list = serializers.ListField(child=serializers.CharField())
    its_correct = serializers.BooleanField()


class EngFixAPI(APIView):
    def post(self, request):
        serializer = InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        input_sentence = serializer.validated_data.get('input_sentence')
        data = ResultProcessor.process_data(input_sentence)

        r = RespSerializer(data=data)
        if r.is_valid():
            return Response(r.validated_data, status=status.HTTP_200_OK)
        else:
            return Response(r.errors, status=status.HTTP_400_BAD_REQUEST)
