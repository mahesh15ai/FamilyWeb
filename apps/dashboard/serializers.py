from rest_framework import serializers


class DashboardOverviewSerializer(serializers.Serializer):
    family = serializers.CharField()
    member_count = serializers.IntegerField()
    recent_posts = serializers.IntegerField()
    upcoming_events = serializers.IntegerField()


class DashboardStatisticsSerializer(serializers.Serializer):
    posts = serializers.IntegerField()
    photos = serializers.IntegerField()
    events = serializers.IntegerField()
    members = serializers.IntegerField()


class RecentActivityItemSerializer(serializers.Serializer):
    actor = serializers.CharField()
    action = serializers.CharField()
    timestamp = serializers.DateTimeField()


class RecentActivitySerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = RecentActivityItemSerializer(many=True)


class UpcomingEventItemSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField()
    # Map start_date from dictionary/model to 'date' with fallback
    date = serializers.DateField(source="start_date", required=False)
    start_date = serializers.DateField(required=False)
    start_time = serializers.TimeField(required=False, allow_null=True)
    location = serializers.CharField(required=False, allow_null=True)


class UpcomingEventsSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    results = UpcomingEventItemSerializer(many=True)


class BirthdayItemSerializer(serializers.Serializer):
    member = serializers.CharField()
    birthday = serializers.CharField()


class BirthdaysSerializer(serializers.Serializer):
    count = serializers.IntegerField()
    today = BirthdayItemSerializer(many=True)
    results = BirthdayItemSerializer(many=True)