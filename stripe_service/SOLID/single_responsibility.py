"""В этом примере у нас есть три класса: «Заказ», «Клиент» и «Товар». У класса Order есть только одна обязанность:
управлять заказами. Он имеет методы для получения общей стоимости заказа и печати заказа. У класса `Customer` есть
только одна обязанность: управлять клиентами. Он имеет свойства для имени и электронной почты клиента. У класса
`Item` есть только одна обязанность: управлять предметами. Он имеет свойства для имени, цены и количества товара.

Разделяя обязанности этих классов, мы делаем код более модульным и простым в обслуживании. Если нам нужно что-то
изменить в заказах, нам нужно только изменить класс Order. Если нам нужно что-то изменить в отношении клиентов,
нам нужно изменить только класс «Клиент». И если нам нужно что-то изменить в элементах, нам нужно только изменить
класс `Item`. """


class Order:
    def __init__(self, customer, items):
        self.customer = customer
        self.items = items

    def get_total(self):
        total = 0
        for item in self.items:
            total += item.price * item.quantity
        return total

    def print_order(self):
        print("Order for:", self.customer.name)
        for item in self.items:
            print("- {} x {} = ${}".format(item.name, item.quantity, item.price * item.quantity))
        print("Total: ${}".format(self.get_total()))


class Customer:
    def __init__(self, name, email):
        self.name = name
        self.email = email


class Item:
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
