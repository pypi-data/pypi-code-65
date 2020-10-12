from django.forms import Form, ModelForm, ModelChoiceField, CharField
from django.contrib.auth.models import User, Group
from django.forms.models import inlineformset_factory
from django.utils.translation import gettext_lazy as _

from bigbluebutton.django.models import BigBlueButton, BigBlueButtonGroup, Meeting
from infrablue.models import MeetingURL
from dynamic_preferences.forms import PreferenceForm
from dynamic_preferences.users.forms import UserPreferenceForm
from material import Row, Layout, Fieldset

from .registries import group_preferences_registry, site_preferences_registry

ServerFormset = inlineformset_factory(
    BigBlueButtonGroup, BigBlueButton, fields=("name", "url", "salt")
)


class MeetingURLForm(ModelForm):
    class Meta:
        model = MeetingURL
        fields = "__all__"

    layout = Layout(
        Row("slug"),
        Row("default_role"),
        Row("attendee_pw"),
        Row("moderator_pw"),
        Row("DELETE"),
    )

    layout_minimal = Layout(
        Row("slug", "default_role"),
        Row("attendee_pw", "moderator_pw"),
    )


MeetingFormset = inlineformset_factory(
    Meeting, MeetingURL, form=MeetingURLForm, extra=0, min_num=1, max_num=3, validate_min=True, validate_max=True,
)

MeetingFormsetNew = inlineformset_factory(
    Meeting, MeetingURL, form=MeetingURLForm, extra=1, min_num=1, max_num=3, validate_min=True, validate_max=True,
)


class UsernameForm(Form):
    full_name = CharField(label=_("Display Name"), help_text=_("Name to join the meeting with"), required=True)
    layout = Layout(
        Fieldset(
            _("Display Name"), "full_name"
        )
    )


class AttendeePwForm(Form):
    attendee_pw = CharField(label=_("Attendee password"), required=True)
    layout = Layout(
        Fieldset(
            _("Attendee password"), "attendee_pw"
        )
    )


class ModeratorPwForm(Form):
    moderator_pw = CharField(label=_("Moderator password"), required=False)
    layout = Layout(
        Fieldset(
            _("Moderator password"), "moderator_pw"
        )
    )


class MeetingForm(ModelForm):
    class Meta:
        model = Meeting
        fields = "__all__"

    layout = Layout(
        Row("name", "api_group"),
        Row("welcome_message", "moderator_message"),
        Row("conference_pin"),
        Row("max_participants", "duration"),
        Row(
            Fieldset(
                _("Recording"),
                "record", "auto_start_recording", "allow_start_stop_recording"
            ),
            Fieldset(
                _("Webcam"),
                "enable_cam", "webcams_only_for_moderator"
            ),
            Fieldset(
                _("Microphone"),
                "enable_mic", "mute_on_start", "allow_mods_to_unmute_users"
            ),
            Fieldset(
                _("Additional Features"),
                "enable_private_chat", "enable_public_chat", "enable_note"
            ),
        ),
    )

    layout_without_pin = Layout(
        Row("name", "api_group"),
        Row("welcome_message", "moderator_message"),
        Row("max_participants", "duration"),
        Row(
            Fieldset(
                _("Recording"),
                "record", "auto_start_recording", "allow_start_stop_recording"
            ),
            Fieldset(
                _("Webcam"),
                "enable_cam", "webcams_only_for_moderator"
            ),
            Fieldset(
                _("Microphone"),
                "enable_mic", "mute_on_start", "allow_mods_to_unmute_users"
            ),
            Fieldset(
                _("Additional Features"),
                "enable_private_chat", "enable_public_chat", "enable_note"
            ),
        ),
    )


class SitePreferenceForm(PreferenceForm):
    """Form to edit site preferences."""

    registry = site_preferences_registry


class GroupPreferenceForm(PreferenceForm):
    """Form to edit site preferences."""

    registry = group_preferences_registry


class NamedModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.name


class UserChangeForm(ModelForm):
    layout = Layout(Row("first_name", "last_name"), Row("username", "email"), Row("groups"))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'groups']


class UserChangeFormStaff(ModelForm):
    layout = Layout(
        Row("first_name", "last_name"), Row("username", "email"), Row("groups"), Row("is_staff", "is_active")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'groups', 'is_staff', 'is_active']


class UserChangeFormAdmin(ModelForm):
    layout = Layout(
        Row("first_name", "last_name"),
        Row("username", "email"),
        Row("groups"),
        Row("is_staff", "is_active", "is_superuser")
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'groups', 'is_staff', 'is_superuser', 'is_active']

