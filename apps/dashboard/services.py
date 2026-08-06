from datetime import timedelta
from django.utils import timezone
from apps.membership import services as membership_services

try:
    from apps.posts.models import Post
except ImportError:
    Post = None

try:
    from apps.events.models import Event
except ImportError:
    Event = None

try:
    from apps.photos.models import Photo
except ImportError:
    Photo = None


def get_user_family(user):
    membership = membership_services.get_membership_for_user(user=user)
    return membership.family if membership else None


def _display_name(user):
    """
    Safe display name for any user — never calls get_full_name(), which
    doesn't exist on our custom User model (it extends AbstractBaseUser,
    not AbstractUser). Falls back to the email's local part.
    """
    full_name = getattr(user, "full_name", "") or ""
    return full_name.strip() or user.email.split("@")[0]


def get_overview_data(family):
    if not family:
        return {
            "family": "No Family Workspace",
            "member_count": 0,
            "recent_posts": 0,
            "upcoming_events": 0,
        }

    now = timezone.now()
    member_count = membership_services.list_family_members(family=family).count()
    recent_posts = Post.objects.filter(family=family).count() if Post else 0
    upcoming_events = Event.objects.filter(family=family, date__gte=now.date()).count() if Event else 0

    return {
        "family": family.name,
        "member_count": member_count,
        "recent_posts": recent_posts,
        "upcoming_events": upcoming_events,
    }


def get_statistics_data(family):
    if not family:
        return {"posts": 0, "photos": 0, "events": 0, "members": 0}

    posts_count = Post.objects.filter(family=family).count() if Post else 0
    photos_count = Photo.objects.filter(family=family).count() if Photo else 0
    events_count = Event.objects.filter(family=family).count() if Event else 0
    members_count = membership_services.list_family_members(family=family).count()

    return {
        "posts": posts_count,
        "photos": photos_count,
        "events": events_count,
        "members": members_count,
    }


def get_recent_activities_data(family):
    if not family:
        return {"count": 0, "results": []}

    activities = []

    if Post:
        posts = Post.objects.filter(family=family).select_related("author").order_by("-created_at")[:10]
        for p in posts:
            activities.append({
                "actor": _display_name(p.author),
                "action": f'posted "{p.content[:25]}..."' if getattr(p, 'content', None) else "created a post",
                "timestamp": getattr(p, 'created_at', timezone.now()),
            })

    if not activities:
        memberships = membership_services.list_family_members(family=family).order_by("-joined_at")[:5]
        for m in memberships:
            activities.append({
                "actor": _display_name(m.user),
                "action": "joined the family workspace",
                "timestamp": getattr(m, 'joined_at', timezone.now()),
            })

    return {"count": len(activities), "results": activities}


def get_upcoming_events_data(family):
    if not family or not Event:
        return {"count": 0, "results": []}

    today = timezone.now().date()
    upcoming = Event.objects.filter(family=family, date__gte=today).order_by("date")[:5]
    results = [{"id": e.id, "title": e.title, "date": e.date} for e in upcoming]
    return {"count": len(results), "results": results}


def get_upcoming_birthdays_data(family):
    """Categorizes member birthdays into TODAY vs UPCOMING within 30 days."""
    if not family:
        return {"count": 0, "results": [], "today": []}

    today = timezone.now().date()
    thirty_days_later = today + timedelta(days=30)
    memberships = membership_services.list_family_members(family=family)

    upcoming_birthdays = []
    today_birthdays = []

    for m in memberships:
        dob = getattr(m.user, "date_of_birth", None)
        user_name = _display_name(m.user)

        if dob:
            try:
                this_year_bday = dob.replace(year=today.year)
            except ValueError:
                this_year_bday = dob.replace(year=today.year, month=3, day=1)

            if this_year_bday == today:
                today_birthdays.append({
                    "member": user_name,
                    "birthday": this_year_bday.strftime("%B %d"),
                })
            elif today < this_year_bday <= thirty_days_later:
                upcoming_birthdays.append({
                    "member": user_name,
                    "birthday": this_year_bday.strftime("%B %d"),
                })

    upcoming_birthdays.sort(key=lambda x: x["birthday"])

    return {
        "count": len(upcoming_birthdays) + len(today_birthdays),
        "today": today_birthdays,
        "results": upcoming_birthdays,
    }