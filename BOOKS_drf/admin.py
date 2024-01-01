from django.contrib import admin

# Register your models here.
from BOOKS_drf.models import Book, Author

admin.site.register(Book)
admin.site.register(Author)
