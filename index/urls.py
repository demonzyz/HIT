from django.conf.urls import include, url
import views
urlpatterns = [
    url(r'home/', views.home),
    url(r'^task/$', views.task),
    # url(r'task/delete/', views.task_delete),


]