from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.families.models import Family
from apps.membership.models import FamilyMembership
from .models import ChatRoom, Message
from .serializers import ChatRoomSerializer, MessageSerializer

User = get_user_model()


def get_user_family(user):
    membership = FamilyMembership.objects.filter(user=user).select_related("family").first()
    return membership.family if membership else None


class ChatRoomListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response({"error": "No family workspace found."}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the Family General Group Room exists
        ChatRoom.objects.get_or_create(
            family=family,
            room_type="group",
            defaults={"name": f"{family.name} Lounge"}
        )

        rooms = ChatRoom.objects.filter(
            Q(family=family, room_type="group") |
            Q(family=family, room_type="direct", participants=request.user)
        ).distinct().order_by("-updated_at")

        serializer = ChatRoomSerializer(rooms, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Create or fetch a 1-on-1 direct message room."""
        family = get_user_family(request.user)
        if not family:
            return Response({"error": "No family workspace found."}, status=status.HTTP_404_NOT_FOUND)

        target_user_id = request.data.get("recipient_id")
        if not target_user_id:
            return Response({"error": "recipient_id is required."}, status=status.HTTP_400_BAD_REQUEST)

        target_user = get_object_or_404(User, id=target_user_id)

        if target_user.id == request.user.id:
            return Response({"error": "You cannot start a direct chat with yourself."}, status=status.HTTP_400_BAD_REQUEST)

        existing_room = (
            ChatRoom.objects.filter(family=family, room_type="direct")
            .filter(participants=request.user)
            .filter(participants=target_user)
            .first()
        )

        if existing_room:
            serializer = ChatRoomSerializer(existing_room, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)

        room = ChatRoom.objects.create(family=family, room_type="direct")
        room.participants.add(request.user, target_user)

        serializer = ChatRoomSerializer(room, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ChatMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)
        
        family = get_user_family(request.user)
        if room.family != family:
            return Response({"error": "Unauthorized access to this chat room."}, status=status.HTTP_403_FORBIDDEN)

        if room.room_type == "direct" and not room.participants.filter(id=request.user.id).exists():
            return Response({"error": "You are not a participant in this conversation."}, status=status.HTTP_403_FORBIDDEN)

        messages = room.messages.select_related("sender").order_by("created_at")[:100]
        serializer = MessageSerializer(messages, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, room_id):
        room = get_object_or_404(ChatRoom, id=room_id)

        family = get_user_family(request.user)
        if room.family != family:
            return Response({"error": "Unauthorized access to this chat room."}, status=status.HTTP_403_FORBIDDEN)

        if room.room_type == "direct" and not room.participants.filter(id=request.user.id).exists():
            return Response({"error": "You are not a participant in this conversation."}, status=status.HTTP_403_FORBIDDEN)

        content = request.data.get("content", "").strip()
        image = request.FILES.get("image")

        if not content and not image:
            return Response({"error": "Message cannot be empty."}, status=status.HTTP_400_BAD_REQUEST)

        msg = Message.objects.create(
            room=room,
            sender=request.user,
            content=content,
            image=image
        )
        room.save()

        serializer = MessageSerializer(msg, context={"request": request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class FamilyChatMembersView(APIView):
    """Returns a list of all family members in the workspace except the requesting user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        family = get_user_family(request.user)
        if not family:
            return Response([], status=status.HTTP_200_OK)

        memberships = (
            FamilyMembership.objects.filter(family=family)
            .exclude(user=request.user)
            .select_related("user")
        )

        data = []
        for m in memberships:
            u = m.user
            name = f"{u.first_name} {u.last_name}".strip() or u.email.split("@")[0]
            avatar_url = None
            if hasattr(u, "avatar") and u.avatar:
                avatar_url = request.build_absolute_uri(u.avatar.url)

            data.append({
                "id": u.id,
                "name": name,
                "email": u.email,
                "avatar": avatar_url,
                "role": m.role,
            })

        return Response(data, status=status.HTTP_200_OK)