from django import template
import re
from django.utils.html import strip_tags
from html import unescape

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

# Список запрещенных слов для нового фильтра
FORBIDDEN_WORDS = [
    'редиска',
    'плохой',
    'нежелательный',
    'запрещенный',
    'секрет',
    'конфиденциально',
    # добавьте другие слова по необходимости
]


def censor_word(word):
    """Цензурирует одно слово"""
    original_word = word

    # Проверяем по списку запрещенных слов
    clean_word = word.strip('.,!?;:"()[]').lower()
    if clean_word in [fw.lower() for fw in FORBIDDEN_WORDS]:
        if len(word) <= 2:
            return '*' * len(word)
        else:
            return word[0] + '*' * (len(word) - 2) + word[-1]

    # Проверяем по корням матных слов
    for root_pattern in CENSOR_ROOTS:
        pattern = r'\w*' + root_pattern + r'\w*'
        if re.search(pattern, word, re.IGNORECASE):
            if len(word) > 1:
                return word[0] + '*' * (len(word) - 1)

    return word


@register.filter
def censor(value):
    """Простая цензура только для текста (без HTML)"""
    if not isinstance(value, str):
        return value

    # Сначала убираем HTML теги, потом декодируем HTML-сущности
    text = strip_tags(value)
    text = unescape(text)  # Преобразует &quot; в ", &amp; в & и т.д.

    words = text.split()
    result = []

    for word in words:
        clean_word = word.strip('.,!?;:"()[]').lower()

        # Проверяем запрещенные слова
        if clean_word in [fw.lower() for fw in FORBIDDEN_WORDS]:
            if len(word) <= 2:
                result.append('*' * len(word))
            else:
                result.append(word[0] + '*' * (len(word) - 2) + word[-1])
        else:
            # Проверяем матные корни
            censored = False
            for root_pattern in CENSOR_ROOTS:
                if re.search(root_pattern, word, re.IGNORECASE):
                    if len(word) > 1:
                        result.append(word[0] + '*' * (len(word) - 1))
                        censored = True
                        break
            if not censored:
                result.append(word)

    return ' '.join(result)


@register.filter
def censor_text(value):
    """Цензура для HTML-текста (сохраняет разметку)"""
    if not isinstance(value, str):
        return value

    # Декодируем HTML-сущности перед обработкой
    value = unescape(value)

    # Если текст содержит HTML-теги, обрабатываем только текстовые узлы
    if '<' in value and '>' in value:
        # Простая обработка HTML - разбиваем на теги и текст
        parts = re.split(r'(<[^>]+>)', value)
        result = []

        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                # Это HTML-тег, оставляем как есть
                result.append(part)
            else:
                # Это текст, применяем цензуру
                result.append(censor(part))

        return ''.join(result)
    else:
        # Простой текст без HTML
        return censor(value)


@register.filter
def hide_forbidden(value):
    """Фильтр только для списка запрещенных слов"""
    if not isinstance(value, str):
        return value

    # Декодируем HTML-сущности
    value = unescape(value)

    # Обрабатываем HTML аналогично censor_text
    if '<' in value and '>' in value:
        parts = re.split(r'(<[^>]+>)', value)
        result = []

        for part in parts:
            if part.startswith('<') and part.endswith('>'):
                result.append(part)
            else:
                # Обрабатываем только запрещенные слова
                words = re.split(r'(\W+)', part)
                processed_words = []

                for word in words:
                    if word.strip():
                        clean_word = word.strip('.,!?;:"()[]')
                        if clean_word.lower() in [fw.lower() for fw in FORBIDDEN_WORDS]:
                            if len(word) <= 2:
                                processed_words.append('*' * len(word))
                            else:
                                processed_words.append(word[0] + '*' * (len(word) - 2) + word[-1])
                        else:
                            processed_words.append(word)
                    else:
                        processed_words.append(word)

                result.append(''.join(processed_words))

        return ''.join(result)
    else:
        # Простой текст
        words = re.split(r'(\W+)', value)
        result = []

        for word in words:
            if word.strip():
                clean_word = word.strip('.,!?;:"()[]')
                if clean_word.lower() in [fw.lower() for fw in FORBIDDEN_WORDS]:
                    if len(word) <= 2:
                        result.append('*' * len(word))
                    else:
                        result.append(word[0] + '*' * (len(word) - 2) + word[-1])
                else:
                    result.append(word)
            else:
                result.append(word)

        return ''.join(result)