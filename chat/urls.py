from django.urls import path
from chat import views as chat_views

urlpatterns = [
    path('', chat_views.home, name='home1'),
    path('home/', chat_views.chat_view, name='home'),
    path('chat/<username>', chat_views.get_or_create_chatroom, name='start-chat'),
    path('chat/room/<chatroom_name>', chat_views.chat_view, name='chatroom'),
    path('chat/new_groupchat/', chat_views.create_groupchat, name="new-groupchat"),
    path('chat/edit/<chatroom_name>', chat_views.chatroom_edit_view, name="edit-chatroom"),
    path('chat/delete/<chatroom_name>', chat_views.chatroom_delete_view, name="chatroom-delete"),
    path('chat/leave/<chatroom_name>', chat_views.chatroom_leave_view, name="chatroom-leave"),
    path('chat/fileupload/<chatroom_name>', chat_views.chat_file_upload, name="chat-file-upload"),
]