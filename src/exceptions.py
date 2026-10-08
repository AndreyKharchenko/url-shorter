# Кастомные ошибки
# Создаем базовый класс ошибки для приложения ShortenerBaseError

class ShortenerBaseError(Exception):
    pass

class NoLongUrlFoundError(ShortenerBaseError):
    pass

class SlugAlreadyExistsError(ShortenerBaseError):
    pass