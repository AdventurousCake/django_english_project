from django.db import IntegrityError
from django.shortcuts import render, redirect
from rest_framework import permissions
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from BOOKS.models import Book
from BOOKS.serializers import BookSerializer


# class UpdateLikeViewAPI(APIView):
#     permission_classes = (permissions.AllowAny,)
#
#     def post(self, request, pk):
#         msg = get_object_or_404(Message, id=pk)
#         try:
#             u = User.objects.get(pk=1)
#             like, is_created = Like.objects.get_or_create(user=u, message=msg)
#             # like, is_created = Like.objects.get_or_create(user=self.request.user, message=msg)
#
#             if not is_created:
#                 like.delete()
#
#             # return Response(status=status.HTTP_204_NO_CONTENT)
#             return redirect(to=reverse('form_msg:msg_list'))
#         except IntegrityError as e:
#             return Response({'error': f'Error updating like: {str(e)}'})

# mix
class CreateMix(CreateModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Book.objects.prefetch_related('author').all()  # явный prefetch

    permission_classes = (permissions.AllowAny,)
    serializer_class = BookSerializer

    # REWRITE
    # PUT, PATCH; createmix - post
    # def update(self, request, *args, **kwargs):
    #     msg = get_object_or_404(Book, id=kwargs['pk'])
    #     try:
    #         u = User.objects.get(pk=1)
    #         like, is_created = Like.objects.get_or_create(user=u, message=msg)
    #         # like, is_created = Like.objects.get_or_create(user=self.request.user, message=msg)
    #         if not is_created:
    #             like.delete()
    #         return Response(status=status.HTTP_204_NO_CONTENT)
    #     except IntegrityError as e:
    #         return Response({'error': f'Error updating like: {str(e)}'})
