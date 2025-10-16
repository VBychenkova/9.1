import os
import django
import logging

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
django.setup()

# Получаем логгеры
django_logger = logging.getLogger('django')
request_logger = logging.getLogger('django.request')
server_logger = logging.getLogger('django.server')
template_logger = logging.getLogger('django.template')
db_logger = logging.getLogger('django.db.backends')
security_logger = logging.getLogger('django.security')

print("=== Тестирование системы логирования ===")

# Тест 1: Сообщения разных уровней в основной логгер
print("\n1. Тест основного логгера (django):")
django_logger.debug("DEBUG сообщение - должно быть только в консоли")
django_logger.info("INFO сообщение - в консоль и general.log")
django_logger.warning("WARNING сообщение - в консоль и general.log")
try:
    raise ValueError("Тестовая ошибка для ERROR")
except Exception as e:
    django_logger.error("ERROR сообщение с исключением", exc_info=True)
django_logger.critical("CRITICAL сообщение")

# Тест 2: Специфичные логгеры для errors.log
print("\n2. Тест логгеров для errors.log:")
request_logger.error("Ошибка запроса - должно быть в errors.log, почте")
server_logger.error("Ошибка сервера - должно быть в errors.log, почте")
template_logger.error("Ошибка шаблона - должно быть в errors.log")
db_logger.error("Ошибка БД - должно быть в errors.log")

# Тест 3: Логгер безопасности
print("\n3. Тест логгера безопасности:")
security_logger.warning("Подозрительная операция - должно быть в security.log")
security_logger.error("Нарушение безопасности - должно быть в security.log")

print("\n=== Тест завершен ===")
print("Проверьте файлы: general.log, errors.log, security.log")
print("Проверьте консоль на наличие сообщений")