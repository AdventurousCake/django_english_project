from django.db import models


class CreatedUpdated(models.Model):
    created_date = models.DateTimeField(null=False, auto_now_add=True)
    updated_date = models.DateTimeField(null=False, auto_now=True)

    class Meta:
        abstract = True


class Author(CreatedUpdated):
    id = models.BigAutoField(null=False, unique=True, primary_key=True,
                             auto_created=True)
    name = models.CharField(null=False, max_length=256)
    b_date = models.DateTimeField(null=False)

    def __str__(self):
        return f"{self.id} {self.name}"


class Book(CreatedUpdated):
    id = models.BigAutoField(null=False, unique=True, primary_key=True,
                             auto_created=True)
    name = models.CharField(null=False, max_length=256)
    author = models.ManyToManyField(to=Author, related_name='books',) #on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.id} {self.name} {self.author}"


#  Model BOOKS.AuthorBook can't have more than one auto-generated field.
# class AuthorBook(models.Model):
#     author_id = models.BigAutoField(null=False, unique=True, primary_key=True)
#     book_id = models.BigAutoField(null=False, unique=True, primary_key=True)
