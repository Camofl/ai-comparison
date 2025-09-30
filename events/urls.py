from django.urls import path

from . import views
from .views import PostListView, PostUpdateView

app_name = "events"
urlpatterns = [
    path("", views.index, name="index"),
    path("new", views.event_new, name="event_new"),
    path("details/<int:event_id>/", views.event_detail, name="event_detail"),
    path("edit/<int:event_id>/", views.event_edit, name="event_edit"),
    path("export_csv/<int:event_id>/", views.export_event_csv, name="export_event_csv"),
    path("posts/", PostListView.as_view(), name="post_list"),
    path("posts/edit/<int:pk>/", PostUpdateView.as_view(), name="post_edit"),
    path('users/', views.user_list, name='user_list'),
]
