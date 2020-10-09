from w.serializers import serializer


class UserSerializer(serializer.SerpySerializer):
    id = serializer.IntField()
    username = serializer.Field()
    first_name = serializer.Field()
    last_name = serializer.Field()
    email = serializer.Field()
    is_active = serializer.BoolField()


class UserWithDateSerializer(UserSerializer):
    date_joined = serializer.DateField()


class RequestResponseSerializer(serializer.SerpySerializer):
    content = serializer.Field()
    success = serializer.Field()
    status_code = serializer.Field()
    redirect_location = serializer.Field()


class MailOutboxSerializer(serializer.SerpySerializer):
    to = serializer.Field()
    bcc = serializer.Field()
    cc = serializer.Field()
    from_email = serializer.Field()
    reply_to = serializer.Field()
    subject = serializer.Field()
    body = serializer.Field()
    content_subtype = serializer.Field()
