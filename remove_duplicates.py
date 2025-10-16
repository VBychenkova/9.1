import os
import re


def remove_duplicates_from_po(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Разделяем на сообщения
    messages = content.split('\n\n')

    seen_messages = {}
    unique_messages = []

    for message in messages:
        # Ищем msgid
        msgid_match = re.search(r'msgid "(.*?)"', message, re.DOTALL)
        if msgid_match:
            msgid = msgid_match.group(1)

            # Если это новый msgid, добавляем
            if msgid not in seen_messages:
                seen_messages[msgid] = message
                unique_messages.append(message)
            else:
                # Если дубликат, объединяем источники
                existing_message = seen_messages[msgid]
                # Добавляем новый источник к существующему сообщению
                source_match = re.search(r'#: (.*?)\n', message)
                if source_match:
                    new_source = source_match.group(1)
                    # Добавляем источник к существующему сообщению
                    seen_messages[msgid] = seen_messages[msgid].replace(
                        '#: ', f'#: {new_source} '
                    )

    # Записываем обратно
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write('\n\n'.join(unique_messages))

    print(f"Удалено дубликатов: {len(messages) - len(unique_messages)}")


# Запускаем для русского языка
remove_duplicates_from_po('locale/ru/LC_MESSAGES/django.po')