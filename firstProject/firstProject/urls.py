

from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
   # path('index.html', views.home, name='home'),
    path('about.html/', views.about, name='about'),
    path('Project.html/', views.Project, name='project'),
    path('project.html/', views.feedback, name='feedback'),
    path('load',views.load,name='load'),
]

