def user_groups(request):
    return {
        'is_author': request.user.groups.filter(name='authors').exists() if request.user.is_authenticated else False
    }