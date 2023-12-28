from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import TodoListCreateView, TodoDetailView

urlpatterns = [
    # path('', views.calendar, name='calendar'),
    path('api/login/', views.login_api, name='login_api'),
    path('api/signup/', views.signup_api, name='signup_api'),
    path('api/get-csrf-token/', views.get_csrf_token, name='get_csrf_token'),
    path('todos/', TodoListCreateView.as_view(), name='todo-list'),
    path('todos/<int:pk>/', TodoDetailView.as_view(), name='todo-detail'),
]