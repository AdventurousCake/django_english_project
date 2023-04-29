# Определяем генератор
def my_generator():
    yield 1
    yield 2
    yield 3
    yield 4
    yield 5

# Получаем итератор из генератора
my_iterator = my_generator()

# Выводим элементы итератора
print(next(my_iterator))   # выведет 1
print(next(my_iterator))   # выведет 2
print(next(my_iterator))   # выведет 3
print(next(my_iterator))   # выведет 4
print(next(my_iterator))   # выведет 5
print(next(my_iterator))   # выведет StopIteration exception