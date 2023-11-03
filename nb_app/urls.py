from django.urls import path
from . import views

urlpatterns = [
    path('submit/', views.submit_form, name='submit_form'),
    path('get_form/', views.get_form_data, name='get_form_data'),
    path('run_docking/', views.run_docking, name='run_docking' ),
    path('check-docking-progress/<str:task_id>/', views.check_docking_progress),
    #path('get-docking-progress/', views.get_docking_progress), # Add


]
