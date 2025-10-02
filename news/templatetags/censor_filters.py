from django import template
import re

register = template.Library()

# Более полный список корней с разными вариантами
CENSOR_ROOTS = [
    'ху[йяюе]',  # хуй, хуя, хую, хуе
    'пизд',  # пизда, пиздец, распиздяй
    'еб[ауё]',  # ебать, ебун, ебёшь
    'бля[дт]',  # блядь, блять
    'гондон',  # гондон
    'мудак',  # мудак
    'су[кч]',  # сука, сучара
]


@register.filter
def censor(value):
    if not isinstance(value, str):
        return value

    result = value

    for root_pattern in CENSOR_ROOTS:
        # Ищем слова с запрещенными корнями
        pattern = r'\b\w*' + root_pattern + r'\w*\b'
        matches = re.finditer(pattern, result, re.IGNORECASE)

        for match in matches:
            original_word = match.group()
            # Цензурируем всё слово
            if len(original_word) > 1:
                censored_word = original_word[0] + '*' * (len(original_word) - 1)
                # Заменяем только полное совпадение
                result = re.sub(r'\b' + re.escape(original_word) + r'\b', censored_word, result)

    return result