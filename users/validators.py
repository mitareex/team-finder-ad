from django.core.exceptions import ValidationError


GITHUB_URL_ERROR_MESSAGE = 'Введите корректную ссылку на GitHub.'


def check_github_domain(value):
    '''Validates the provided URL'''
    if "github.com" not in value.lower():
        raise ValidationError(GITHUB_URL_ERROR_MESSAGE)
    return value
