from .import views
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
     path("view_users/", views.view_users, name="view_users"),
      path('category/', views.category_page, name='category_page'),
    path('category/edit/<int:id>/', views.category_page, name='edit_category'),
    path('category/delete/<int:id>/', views.delete_category, name='delete_category'),

      path('properties/', views.admin_properties, name='admin_properties'),
    path('property/<int:property_id>/', views.admin_property_detail, name='admin_property_detail'),
   
    path('property/<int:property_id>/reject/', views.admin_reject_property, name='admin_reject_property'),

    path('admin_plots/', views.admin_plots, name='admin_plots'),
    path('admin_plot/<int:plot_id>/', views.admin_plot_detail, name='admin_plot_detail'),

    path('admin_plot/<int:plot_id>/reject/', views.admin_reject_plot, name='admin_reject_plot'),
    path('admin_analytics/', views.admin_analytics, name='admin_analytics'),
    path('property/<int:property_id>/restore/', views.admin_restore_property, name='admin_restore_property'),
     path('admin_plot/<int:plot_id>/restore/', views.admin_restore_plot, name='admin_restore_plot'),
      path('feedback/', views.admin_feedback_list, name='admin_feedback_list'),
    
]