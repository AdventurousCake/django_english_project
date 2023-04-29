from rest_framework import serializers

from BOOKS.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name', 'author', 'created_date', 'updated_date')
        model = Book
