from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_form, name='submit_form'),
    path('get_form/', views.get_form_data, name='get_form_data'),
    path('run_docking/', views.run_docking, name='run_docking' ),
    path('get_docking_progress/<uuid:task_id>/', views.get_docking_progress, name='get_docking_progress')


]
