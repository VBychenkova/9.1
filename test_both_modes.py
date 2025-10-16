import os
import django
import logging


def test_logging():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'newsportal.settings')
    django.setup()

    from django.conf import settings
    print(f"=== Текущий режим: DEBUG = {settings.DEBUG} ===")

    # Получаем логгеры
    django_logger = logging.getLogger('django')
    request_logger = logging.getLogger('django.request')
    security_logger = logging.getLogger('django.security')

    # Тестовые сообщения
    django_logger.debug("DEBUG сообщение")
    django_logger.info("INFO сообщение")
    django_logger.warning("WARNING сообщение")

    try:
        raise ValueError("Тестовая ошибка")
    except Exception:
        django_logger.error("ERROR сообщение с исключением", exc_info=True)

    django_logger.critical("CRITICAL сообщение")
    request_logger.error("Ошибка запроса")
    security_logger.warning("Предупреждение безопасности")

    print("=== Тест завершен ===")
    print("Проверьте файлы логов")


if __name__ == "__main__":
    test_logging()