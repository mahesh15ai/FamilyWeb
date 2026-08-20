from django.urls import path
from .views import ChatRoomListView, ChatMessagesView, FamilyChatMembersView

app_name = "chat"

urlpatterns = [
    path("rooms/", ChatRoomListView.as_view(), name="chat-rooms"),
    path("rooms/<int:room_id>/messages/", ChatMessagesView.as_view(), name="chat-messages"),
    path("family-members/", FamilyChatMembersView.as_view(), name="chat-family-members"),
]