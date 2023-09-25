"""Функции, которые используют базовый тип, должны иметь возможность использовать подтипы базового типа не зная об
этом». См. также контрактное программирование. """


class Shape:
    def area(self):
        pass


class Rectangle(Shape):
    def __init__(self, width, height):
        self.width = width
        self.height = height

    def area(self):
        return self.width * self.height


class Square(Shape):
    def __init__(self, side):
        self.side = side

    def area(self):
        return self.side ** 2
