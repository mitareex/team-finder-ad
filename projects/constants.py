PROJECTS_PER_PAGE = 12

NAME_MAX_LENGTH = 200
STATUS_MAX_LENGTH = 6

OPEN_STATUS = 'open'
CLOSED_STATUS = 'closed'

STATUS_CHOICES = [
    (OPEN_STATUS, 'Открыт'),
    (CLOSED_STATUS, 'Закрыт'),
]

API_STATUS_OK = 'ok'
API_STATUS_ERROR = 'error'
ACCESS_DENIED_MSG = 'Доступ запрещен'
AUTHOR_LEAVE_DENIED_MSG = 'Автор не может покинуть свой проект'

HTTP_BAD_REQUEST = 400
HTTP_FORBIDDEN = 403

NAME_LABEL = 'Название'
DESCRIPTION_LABEL = 'Описание'
STATUS_LABEL = 'Статус'
GITHUB_LABEL = 'Ссылка на Github'
