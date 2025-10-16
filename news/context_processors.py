from django.utils import timezone
import pytz


def timezone_context(request):
    return {
        'current_time': timezone.now(),
        'timezones': pytz.common_timezones,
    }

def user_groups(request):
    return {
        'is_author': request.user.groups.filter(name='authors').exists() if request.user.is_authenticated else False
    }