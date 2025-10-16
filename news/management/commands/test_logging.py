from django.core.management.base import BaseCommand
import logging


class Command(BaseCommand):
    help = 'Test the logging system'

    def handle(self, *args, **options):
        self.stdout.write("=== Тестирование системы логирования ===")

        # Получаем логгеры
        django_logger = logging.getLogger('django')
        request_logger = logging.getLogger('django.request')
        server_logger = logging.getLogger('django.server')
        template_logger = logging.getLogger('django.template')
        db_logger = logging.getLogger('django.db.backends')
        security_logger = logging.getLogger('django.security')

        self.stdout.write("\n1. Тест основного логгера (django):")
        django_logger.debug("DEBUG сообщение - должно быть только в консоли")
        django_logger.info("INFO сообщение - в консоль и general.log")
        django_logger.warning("WARNING сообщение - в консоль и general.log")

        try:
            raise ValueError("Тестовая ошибка для ERROR")
        except Exception as e:
            django_logger.error("ERROR сообщение с исключением", exc_info=True)

        django_logger.critical("CRITICAL сообщение")

        self.stdout.write("\n2. Тест логгеров для errors.log:")
        request_logger.error("Ошибка запроса - должно быть в errors.log, почте")
        server_logger.error("Ошибка сервера - должно быть в errors.log, почте")
        template_logger.error("Ошибка шаблона - должно быть в errors.log")
        db_logger.error("Ошибка БД - должно быть в errors.log")

        self.stdout.write("\n3. Тест логгера безопасности:")
        security_logger.warning("Подозрительная операция - должно быть в security.log")
        security_logger.error("Нарушение безопасности - должно быть в security.log")

        self.stdout.write("\n=== Тест завершен ===")
        self.stdout.write("Проверьте файлы: general.log, errors.log, security.log")
        self.stdout.write("Проверьте консоль на наличие сообщений")