// Базовые JavaScript функции для News Portal

document.addEventListener('DOMContentLoaded', function() {
    // Автоматическое скрытие сообщений через 5 секунд
    const messages = document.querySelectorAll('.messages div');
    messages.forEach(function(message) {
        setTimeout(function() {
            message.style.transition = 'opacity 0.5s ease';
            message.style.opacity = '0';
            setTimeout(function() {
                message.remove();
            }, 500);
        }, 5000);
    });

    // Подтверждение удаления
    const deleteButtons = document.querySelectorAll('form[method="post"] button[type="submit"]');
    deleteButtons.forEach(function(button) {
        if (button.textContent.toLowerCase().includes('удалить') ||
            button.textContent.toLowerCase().includes('delete')) {
            button.addEventListener('click', function(e) {
                if (!confirm('Вы уверены, что хотите удалить эту запись?')) {
                    e.preventDefault();
                }
            });
        }
    });

    // Плавная прокрутка для якорей
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
});

// Функция для динамической загрузки контента
function loadContent(url, containerId) {
    fetch(url)
        .then(response => response.text())
        .then(data => {
            document.getElementById(containerId).innerHTML = data;
        })
        .catch(error => console.error('Error loading content:', error));
}