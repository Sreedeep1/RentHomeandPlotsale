from .import views
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('user_properties/', views.property_list, name='property_list'),
    path('property/add/', views.property_form, name='add_property'),
    path('property/edit/<int:id>/', views.property_form, name='edit_property'),
    path('property/delete/<int:id>/', views.delete_property, name='delete_property'),
    path('property/image/delete/<int:id>/', views.delete_property_image, name='delete_property_image'),    
    path('property/add-images/<int:property_id>/', views.add_images, name='add_images'),

    ###########plot management##########
     path('plots/manage/', views.plot_manage, name='plot_manage'),
    path('plots/manage/<int:plot_id>/', views.plot_manage, name='plot_edit'),
    path('plots/delete/<int:plot_id>/', views.plot_delete, name='plot_delete'),
    path('plots/add-images/', views.plot_add_images, name='plot_add_images'),
    path('plots/interest/respond/', views.plot_interest_respond, name='plot_interest_respond'),
    path('plot/<int:plot_id>/wishlist/toggle/', views.toggle_plot_wishlist, name='toggle_plot_wishlist'),
    path('send-message/user/', views.send_message_to_user, name='send_message_to_user'),
    path('my-plots/', views.my_plots, name='my_plots'),    


       path('browse-property/', views.browse_property, name='browse_property'),
       path('property/detail/<int:property_id>/', views.property_detail, name='property_detail'),
###########FRO PLOT

       path('plot/detail/<int:plot_id>/', views.plot_detail, name='plot_detail'),

       ################chat system#########
     path('chat/<int:property_id>/<int:user_id>/', views.chat_page, name='chat_page'),
    path('send_message/', views.send_message, name='send_message'),
    path('get_messages/<int:room_id>/', views.get_messages, name='get_messages'),


    ########owner chat
    #ALL CHAT for a property
    path('owner/property/<int:property_id>/chats/', views.property_chat_list, name='property_chat_list'),
    #owner open one chat
    path('owner/chat/<int:room_id>/', views.owner_chat_room, name='owner_chat_room'),

     path('interest-plot/<int:id>/', views.interest_request_plot, name='interest_request_plot'),
    path('wishlist-plot/<int:id>/', views.wishlist_plot, name='wishlist_plot'),
    ################33profile##################
    path('profile',views.profile_view,name="profile"),
       path('profile/update/', views.update_profile, name='update_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    path('profile/wishlist/', views.wishlist_view, name='wishlist'),
    path('profile/interested-plots/', views.interested_plots_view, name='interested_plots'),
     path('profile/interested-properties/', views.interested_rent_properties, name='interested_rent_properties'),
    path('profile/remove-wishlist/<int:plot_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('profile/remove-interest/<int:interest_id>/', views.remove_interest, name='remove_interest'),
     path('profile/remove-rental-interest/<int:property_id>/', views.remove_rental_interest, name='remove_rental_interest'),
        path('feedbackks/', views.feedback_list, name='feedback_list'),
    path('feedback/submit/', views.submit_feedback, name='submit_feedback'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)