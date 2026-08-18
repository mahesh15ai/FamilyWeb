from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.db.models import Q
from django.apps import apps
from django.contrib.auth import get_user_model

User = get_user_model()


class GlobalSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get("q", "").strip()
        if not query or len(query) < 2:
            return Response(
                {
                    "query": query,
                    "members": [],
                    "posts": [],
                    "albums": [],
                    "events": [],
                    "total_results": 0,
                },
                status=status.HTTP_200_OK,
            )

        user = request.user

        # Dynamically resolve models
        Family = apps.get_model("families", "Family")
        Post = apps.get_model("posts", "Post")
        Album = apps.get_model("albums", "Album")
        Event = apps.get_model("events", "Event")

        # Resolve Membership model (checks 'membership', 'families', or 'accounts')
        MembershipModel = None
        for app_label in ["membership", "families", "accounts"]:
            for model_name in ["FamilyMembership", "Membership", "Member"]:
                try:
                    MembershipModel = apps.get_model(app_label, model_name)
                    break
                except LookupError:
                    continue
            if MembershipModel:
                break

        # 1. Resolve User's Current Family
        family = None
        if MembershipModel:
            mem = MembershipModel.objects.filter(user=user).select_related("family").first()
            if mem:
                family = mem.family

        if not family:
            family = Family.objects.filter(Q(created_by=user) | Q(owner=user) if hasattr(Family, 'owner') else Q(created_by=user)).first()

        if not family:
            return Response({"error": "No active family found."}, status=status.HTTP_404_NOT_FOUND)

        # 2. Search Family Members
        members_data = []
        if MembershipModel:
            member_matches = MembershipModel.objects.filter(
                family=family
            ).filter(
                Q(user__first_name__icontains=query)
                | Q(user__last_name__icontains=query)
                | Q(user__email__icontains=query)
            ).select_related("user")[:8]

            for m in member_matches:
                u = m.user
                name = f"{u.first_name} {u.last_name}".strip() or u.email.split("@")[0]
                avatar_url = None
                if hasattr(u, "avatar") and u.avatar:
                    avatar_url = request.build_absolute_uri(u.avatar.url)
                members_data.append({
                    "id": u.id,
                    "name": name,
                    "email": u.email,
                    "role": getattr(m, "role", "MEMBER"),
                    "avatar": avatar_url,
                    "target_url": "/families/members",
                })

        # 3. Search Posts
        post_matches = Post.objects.filter(
            family=family
        ).filter(
            Q(content__icontains=query)
        )[:8]

        posts_data = []
        for p in post_matches:
            author = getattr(p, "author", None) or getattr(p, "user", None)
            author_name = (
                f"{author.first_name} {author.last_name}".strip() if author else "Family Member"
            )
            content_text = getattr(p, "content", "") or ""
            preview = (content_text[:80] + "...") if len(content_text) > 80 else content_text
            posts_data.append({
                "id": p.id,
                "title": f"Post by {author_name}",
                "content": preview,
                "created_at": getattr(p, "created_at", None),
                "target_url": "/posts",
            })

        # 4. Search Albums
        album_matches = Album.objects.filter(
            family=family
        ).filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )[:8]

        albums_data = [
            {
                "id": a.id,
                "title": a.title,
                "description": (a.description[:60] + "...") if getattr(a, "description", None) and len(a.description) > 60 else (getattr(a, "description", "") or ""),
                "target_url": f"/albums/{a.id}",
            }
            for a in album_matches
        ]

        # 5. Search Events
        event_matches = Event.objects.filter(
            family=family
        ).filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(location__icontains=query)
        )[:8]

        events_data = [
            {
                "id": e.id,
                "title": e.title,
                "date": str(getattr(e, "start_date", "")),
                "location": getattr(e, "location", "") or "",
                "target_url": "/events",
            }
            for e in event_matches
        ]

        total = len(members_data) + len(posts_data) + len(albums_data) + len(events_data)

        return Response(
            {
                "query": query,
                "members": members_data,
                "posts": posts_data,
                "albums": albums_data,
                "events": events_data,
                "total_results": total,
            },
            status=status.HTTP_200_OK,
        )