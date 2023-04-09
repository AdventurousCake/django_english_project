class Printable:
    def print(self):
        pass


class Displayable:
    def display(self):
        pass


class Document:
    def __init__(self, title, content):
        self.title = title
        self.content = content


class Book(Document, Printable, Displayable):
    def print(self):
        print("Printing book:", self.title)

    def display(self):
        print("Displaying book:", self.title)


class Magazine(Document, Printable):
    def print(self):
        print("Printing magazine:", self.title)


b = Book(title='title', content='content')