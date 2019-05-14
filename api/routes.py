from api import views

routes = [
    ('POST', '/api/v1/users/registration/', views.registration),
    ('POST', '/api/v1/users/login/', views.login),
    ('GET', '/api/v1/jokes/', views.jokes_list),
    ('POST', '/api/v1/jokes/', views.joke_create),
    ('GET', r'/api/v1/jokes/{id:\d+}/', views.joke_detail),
    ('PATCH', r'/api/v1/jokes/{id:\d+}/', views.joke_update),
    ('DELETE', r'/api/v1/jokes/{id:\d+}/', views.joke_delete),
]
