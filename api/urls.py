from django.conf.urls import include, url
import views

urlpatterns = [
    url(r'^template/add/$', views.add_template),
    url(r'^template/get_list/$', views.get_list),
    url(r'^case/add/$', views.add_case),
    url(r'^step/add/$', views.add_step),
    url(r'^task/add/$', views.add_task),
    url(r'^task/run/$', views.run_task),
]