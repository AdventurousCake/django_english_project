from rest_framework import serializers

from BOOKS.models import Book, Author


class AuthorSerializerSIMPLE(serializers.ModelSerializer):
    class Meta:
        fields = ('id', 'name')
        model = Author


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializerSIMPLE(many=True)

    class Meta:
        fields = ('id', 'name', 'author', 'created_date', 'updated_date')
        model = Book
