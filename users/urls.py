from django.urls import path
from users import views as users_views

urlpatterns = [
    path('', users_views.profile_view, name="profile"),
    path('edit/', users_views.profile_edit_view, name="profile-edit"),
    path('onboarding/', users_views.profile_edit_view, name="profile-onboarding"),
    path('settings/', users_views.profile_settings_view, name="profile-settings"),
    path('emailchange/', users_views.profile_emailchange, name="profile-emailchange"),
    path('emailverify/', users_views.profile_emailverify, name="profile-emailverify"),
    path('delete/', users_views.profile_delete_view, name="profile-delete"),
    path('users_list/', users_views.users_list, name='users-list'),
]