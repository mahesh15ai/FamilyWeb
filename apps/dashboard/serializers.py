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
    date = serializers.DateField()


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