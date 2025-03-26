import math


class Paginator:
    def __init__(self, array: list | tuple, page: int=1, per_page: int=1):
        self.array = array
        self.page = page
        self.per_page = per_page
        self.len = len(self.array)
        # math.ceil - округление в большую сторону до целого числа
        self.pages = math.ceil(self.len / self.per_page)

    def __get_slice(self):
        start = (self.page - 1) * self.per_page
        stop = start + self.per_page
        return self.array[start:stop]

    # функция, забирающая срез из списка array
    def get_page(self):
        page_items = self.__get_slice()
        return page_items

    # функция для определения есть ли следующая страница, для того чтобы корректно отображать эти кнопки
    def has_next(self):
        if self.page < self.pages:
            return self.page + 1
        return False

    # функция для определения есть ли предыдущая страница, для того чтобы корректно отображать эти кнопки
    def has_previous(self):
        if self.page > 1:
            return self.page - 1
        return False
