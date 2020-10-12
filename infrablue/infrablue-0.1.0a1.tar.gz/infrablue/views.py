from typing import Optional

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import PermissionRequiredMixin as GlobalPermissionRequiredMixin
from django.contrib.auth.models import Group, AnonymousUser
from django.contrib.auth.views import PasswordChangeView
from django.core.exceptions import PermissionDenied
from django.http import HttpRequest, HttpResponse, HttpResponseNotFound, HttpResponseForbidden, HttpResponseRedirect
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _

from django.views.generic.edit import CreateView, DeleteView, FormView, UpdateView
from django.views.generic import DetailView, ListView
from django.contrib.auth.forms import SetPasswordForm, PasswordChangeForm

from bigbluebutton.django.models import BigBlueButton, BigBlueButtonGroup, Meeting
from dynamic_preferences.forms import preference_form_builder
from dynamic_preferences.users.forms import UserPreferenceForm
from dynamic_preferences.users.registries import user_preferences_registry
from guardian.shortcuts import assign_perm, get_objects_for_user, get_users_with_perms
from guardian.mixins import LoginRequiredMixin, PermissionRequiredMixin
from datetime import datetime
from uuid import uuid4

from .forms import (
    SitePreferenceForm,
    ServerFormset,
    UserChangeForm,
    UserChangeFormAdmin,
    UserChangeFormStaff,
    MeetingFormset,
    MeetingForm,
    MeetingFormsetNew,
    UsernameForm,
    AttendeePwForm,
    ModeratorPwForm,
)

from .bigbluebutton import MEETING_METADATA
from .registries import site_preferences_registry
from .models import MeetingURL
from .mixins import StaffRequiredMixin

User = get_user_model()


def index(request: HttpRequest) -> HttpResponse:
    return render(request, "infrablue/index.html")


def preferences(
        request: HttpRequest,
        registry_name: str = "person",
        pk: Optional[int] = None,
        section: Optional[str] = None,
) -> HttpResponse:
    """View for changing preferences."""
    context = {}

    # Decide which registry to use and check preferences
    if registry_name == "site":
        registry = site_preferences_registry
        instance = request.site
        form_class = SitePreferenceForm

        if not request.user.is_staff:
            raise PermissionDenied()
    elif registry_name == "user":
        registry = user_preferences_registry
        instance = request.user
        form_class = UserPreferenceForm

    else:
        # Invalid registry name passed from URL
        return HttpResponseNotFound()

    # Build final form from dynamic-preferences
    form_class = preference_form_builder(form_class, instance=instance, section=section)

    if request.method == "POST":
        form = form_class(request.POST, request.FILES or None)
        if form.is_valid():
            form.update_preferences()
            messages.success(request, _("The preferences have been saved successfully."))
    else:
        form = form_class()

    context["registry"] = registry
    context["registry_name"] = registry_name
    context["section"] = section
    context["registry_url"] = "preferences_" + registry_name
    context["form"] = form
    context["instance"] = instance

    return render(request, "dynamic_preferences/form.html", context)


class GroupList(LoginRequiredMixin, GlobalPermissionRequiredMixin, ListView):
    model = Group
    paginate_by = 100
    template_name = 'infrablue/group_list.html'
    fields = ['name']
    permission_required = "auth.view_group"


class GroupUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Group
    paginate_by = 100
    template_name = 'infrablue/group_update.html'
    fields = ['name']
    permission_required = "auth.change_group"

    def get_success_url(self):
        return reverse_lazy("group_detail", kwargs={"pk": self.object.id})


class GroupCreate(LoginRequiredMixin, GlobalPermissionRequiredMixin, CreateView):
    model = Group
    template_name = 'infrablue/group_update.html'
    fields = ['name']
    permission_required = "auth.add_group"

    def get_success_url(self):
        return reverse_lazy("group_detail", kwargs={"pk": self.object.id})


class GroupDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Group
    template_name = 'infrablue/group_delete.html'
    success_url = reverse_lazy("group_list")
    permission_required = "auth.delete_group"


class GroupDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Group
    template_name = "infrablue/group_detail.html"
    permission_required = "auth.view_group"


class MeetingList(LoginRequiredMixin, ListView):
    model = Meeting
    template_name = "infrablue/meeting_list.html"
    paginate_by = 50
    ordering = ["name"]

    def get_queryset(self):
        return get_objects_for_user(self.request.user, 'bigbluebutton.view_meeting')


class MeetingUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Meeting
    permission_required = "bigbluebutton.change_meeting"
    template_name = "infrablue/meeting_update.html"
    object = None

    def get_form_class(self):
        form_class = MeetingForm

        if not self.request.user.has_perm("bigbluebutton.enforce_conference_pin"):
            form_class.layout = form_class.layout_without_pin

        return form_class

    def get_success_url(self):
        return reverse_lazy("meeting_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["urls"] = MeetingFormset(self.request.POST or None, instance=self.object)
        else:
            context["urls"] = MeetingFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        urls = context["urls"]
        form.save()
        if urls.is_valid():
            urls.instance = self.object
            urls.save()
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                "instance": self.get_object()
            })

        return kwargs

    def post(self, request, *args, **kwargs):
        form_meeting = self.get_form()
        form_urls = MeetingFormset(data=request.POST, instance=self.get_object())
        if form_meeting.is_valid() and form_urls.is_valid():
            print("VALID")
            return self.form_valid(form_meeting)
        else:
            print("INVALID")
            print(form_meeting.errors, form_urls.errors)
            return self.form_invalid(form_meeting)


class MeetingCreate(LoginRequiredMixin, CreateView):
    model = Meeting
    template_name = "infrablue/meeting_update.html"
    object = None

    def get_form_class(self):
        form_class = MeetingForm

        if not self.request.user.has_perm("bigbluebutton.enforce_conference_pin"):
            form_class.layout = form_class.layout_without_pin

        return form_class

    def get_success_url(self):
        return reverse_lazy("meeting_detail", kwargs={"pk": self.object.id})

    def get_context_data(self, **kwargs):
        initial = {
            "urls-TOTAL_FORMS": 1,
            "urls-INITIAL_FORMS": 0,
            "urls-MIN_NUM_FORMS": 1,
            "'urls-MAX_NUM_FORMS": 3,
            "urls-0-slug": uuid4(),
            "urls-0-default_role": "VIEWER",
        }
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["urls"] = MeetingFormset(self.request.POST or None, instance=self.object)
        else:
            context["urls"] = MeetingFormset(initial, instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        urls = context["urls"]
        self.object = form.save()
        # User is owner of this meeting
        assign_perm("bigbluebutton.change_meeting", user_or_group=self.request.user, obj=self.object)
        assign_perm("bigbluebutton.delete_meeting", user_or_group=self.request.user, obj=self.object)
        assign_perm("bigbluebutton.view_meeting", user_or_group=self.request.user, obj=self.object)
        assign_perm("bigbluebutton.add_urls", user_or_group=self.request.user, obj=self.object)
        assign_perm("bigbluebutton.grant_attendee", user_or_group=self.request.user, obj=self.object)
        assign_perm("bigbluebutton.grant_moderator", user_or_group=self.request.user, obj=self.object)
        assign_perm("bigbluebutton.join_as_moderator", user_or_group=self.request.user, obj=self.object)
        if urls.is_valid():
            urls.instance = self.object
            urls.save()
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        form_meeting = self.get_form()
        form_urls = MeetingFormset(data=request.POST, instance=self.object)
        if form_meeting.is_valid() and form_urls.is_valid():
            print("VALID")
            return self.form_valid(form_meeting)
        else:
            print("INVALID")
            print(form_meeting.errors, form_urls.errors)
            return self.form_invalid(form_meeting)


class MeetingDetail(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Meeting
    permission_required = ("bigbluebutton.view_meeting", "bigbluebutton.add_urls")
    template_name = "infrablue/meeting_detail.html"
    form_class = MeetingFormsetNew

    def get_success_url(self):
        return reverse_lazy("meeting_detail", kwargs={"pk": self.get_object().id})

    def post(self, request, *args, **kwargs):
        request.POST = request.POST.copy()
        request.POST["meeting"] = self.get_object().pk
        return super(MeetingDetail, self).post(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(MeetingDetail, self).get_context_data(**kwargs)
        obj = self.get_object()

        context["meeting_metadata"] = MEETING_METADATA
        context["meeting_info"] = obj.meeting.get_meeting_info()

        meeting_owners = get_users_with_perms(obj, only_with_perms_in=["change_meeting"])
        if meeting_owners:  # Administrators can't be shown
            context["meeting_owners"] = meeting_owners

        return context


class MeetingDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Meeting
    permission_required = "bigbluebutton.delete_meeting"
    template_name = "infrablue/meeting_delete.html"
    success_url = reverse_lazy("meeting_list")


class MeetingURLDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    permission_required = ("bigbluebutton.change_meeting", "bigbluebutton.add_urls")
    model = MeetingURL
    template_name = "infrablue/meeting_url_delete.html"

    def get_permission_object(self):
        return self.get_object().meeting

    def get(self, request, *args, **kwargs):
        meeting = self.get_object().meeting
        success_url = reverse_lazy("meeting_detail", kwargs={"pk": meeting.pk})
        if len(meeting.urls.all()) > 1:
            return super(MeetingURLDelete, self).get(request, *args, **kwargs)

        else:
            messages.error(request, _("This meeting must have at least one URL."))
            return HttpResponseRedirect(success_url)

    def get_success_url(self):
        return reverse_lazy("meeting_detail", kwargs={"pk": self.object.meeting.pk})


class MeetingJoinID(LoginRequiredMixin, DetailView):
    model = Meeting

    def get(self, request, *args, **kwargs):
        meeting_bbb = self.get_object()
        return HttpResponseRedirect(meeting_bbb.join(self.request.user))


class MeetingJoin(DetailView):
    model = MeetingURL
    meeting_bbb = None

    def get_object(self, queryset=None):
        object_ = super().get_object(queryset)
        self.object = object_
        self.meeting_bbb = object_.meeting

        return object_

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["card_properties"] = context["card_properties"] = MEETING_METADATA.values()

        context["meeting_info"] = meeting_info = self.meeting_bbb.meeting.get_meeting_info()

        if self.request.user.has_perm("bigbluebutton.join_as_attendee",
                                      self.meeting_bbb) or not self.object.attendee_pw:
            context["show_attendees"] = True
        else:
            context["show_attendees"] = False

        meeting_owners = get_users_with_perms(self.meeting_bbb, only_with_perms_in=["change_meeting"])
        if meeting_owners:  # Administrators can't be shown
            context["meeting_owners"] = meeting_owners
        print(meeting_owners)

        if meeting_info.start_time >= 0:
            start_time_str = str(meeting_info.start_time)
            start_time = float(f"{start_time_str[:-3]}.{start_time_str[-3:]}")
            start_time = datetime.fromtimestamp(start_time)
        else:
            start_time = 0

        context["start_time"] = start_time

        return context

    def get(self, *args, **kwargs):
        meeting_url = self.get_object()
        attendee_pw = meeting_url.attendee_pw
        moderator_pw = meeting_url.moderator_pw

        context = self.get_context_data()
        if attendee_pw and not self.request.user.has_perm("bigbluebutton.join_as_attendee", self.meeting_bbb):
            context["attendee_pw_form"] = AttendeePwForm()
        if moderator_pw and not self.request.user.has_perm("bigbluebutton.join_as_moderator", self.meeting_bbb):
            context["moderator_pw_form"] = ModeratorPwForm()
        if not self.request.user.is_authenticated:
            context["user_form"] = UsernameForm()

        context["meeting"] = self.meeting_bbb
        return render(request=self.request, template_name="infrablue/meeting_join.html", context=context)

    def post(self, *args, **kwargs):
        meeting_url = self.get_object()
        default_role = meeting_url.default_role
        attendee_pw = meeting_url.attendee_pw
        moderator_pw = meeting_url.moderator_pw

        user = self.request.user
        POST = self.request.POST  # noqa

        context = self.get_context_data()
        attendee_valid = False
        moderator_valid = False
        name_valid = False

        # Check if the user is authenticated, show form if not
        if "full_name" in POST.keys() or not user.is_authenticated:
            form = UsernameForm(POST)

            if POST.get("full_name", "").strip():
                full_name = POST["full_name"].strip()
                user = AnonymousUser()
                user.username = full_name or _("Anonymous User")
                name_valid = True

            else:
                name_valid = False
                form.add_error("full_name", _("Please fill in this field!"))
            context["user_form"] = form

        else:
            user = self.request.user
            name_valid = True

        """
        This method determins the role based on this table:
        | Attende Password | Moderator Password | DEFAULT VALUE | JOINS AS ATTENDEE        | JOINS AS MODERATOR       |
        |------------------|--------------------|---------------|--------------------------|--------------------------|
        | YES              | YES                | ATT           | possibly (with password) | possibly (with password) |
        | YES              | YES                | MOD           | possibly (with password) | possibly (with password) |
        | YES              | NO                 | ATT           | possibly (with password) | never                    |
        | YES              | NO                 | MOD           | possibly (with password) | never                    |
        | NO               | YES                | ATT           | anytime                  | possibly (with password) |
        | NO               | YES                | MOD           | never                    | possibly (with password) |
        | NO               | NO                 | ATT           | anytime                  | never                    |
        | NO               | NO                 | MOD           | never                    | anytime                  |
        """

        if not attendee_pw or user.has_perm("bigbluebutton.join_as_attendee", self.meeting_bbb) or user.has_perm(
                "bigbluebutton.join_as_moderator", self.meeting_bbb):
            """
            It is allowed to join the meeting, without an attendee password → role is either attendee or maybe moderator
            """
            attendee_valid = True
            if (default_role == "MODERATOR" and not moderator_pw) or user.has_perm("bigbluebutton.join_as_moderator",
                                                                                   self.meeting_bbb):
                """The default is moderator and no moderator password is needed → you can't join as a viewer"""
                moderator_valid = True

            elif default_role == "MODERATOR" and moderator_pw:
                """You only can join as moderator, but you need a password"""
                attendee_valid = False

                form = ModeratorPwForm(POST)

                if POST.get("moderator_pw") == moderator_pw:
                    moderator_valid = True
                else:
                    moderator_valid = False
                    form.add_error("moderator_pw", _("The password is wrong. Please try again!"))
                context["moderator_pw_form"] = form

            elif default_role == "VIEWER" and moderator_pw:
                """
                The default is viewer but there is a moderator password → you can be moderator if you know the password
                """
                form = ModeratorPwForm(POST)

                if POST.get("moderator_pw") == moderator_pw:
                    moderator_valid = True
                else:
                    moderator_valid = False
                    form.add_error("moderator_pw", _("The password is wrong. Please try again!"))
                context["moderator_pw_form"] = form

        elif attendee_pw:
            """
            Attende password is needed, ignore default value
            """
            form = AttendeePwForm(POST)

            if POST.get("attendee_pw") == attendee_pw:
                attendee_valid = True
            else:
                attendee_valid = False
                form.add_error("attendee_pw", _("The password is wrong. Please try again!"))
            context["attendee_pw_form"] = form

            if moderator_pw:
                """It is possible to be moderator, but only with a password"""
                form = ModeratorPwForm(POST)

                if POST.get("moderator_pw") == moderator_pw:
                    moderator_valid = True
                else:
                    moderator_valid = False
                    form.add_error("moderator_pw", _("The password is wrong. Please try again!"))
                context["moderator_pw_form"] = form

        if name_valid and any([attendee_valid, moderator_valid]):
            if attendee_valid:
                assign_perm("bigbluebutton.join_as_attendee", user, self.meeting_bbb)
            if moderator_valid:
                assign_perm("bigbluebutton.join_as_moderator", user, self.meeting_bbb)
            return self.join(user)

        else:
            context["meeting"] = self.meeting_bbb
            return render(request=self.request, template_name="infrablue/meeting_join.html", context=context)

    def join(self, user):
        return HttpResponseRedirect(self.meeting_bbb.join(user))


class UserList(LoginRequiredMixin, GlobalPermissionRequiredMixin, ListView):
    model = User
    paginate_by = 100
    template_name = 'infrablue/user_list.html'
    fields = ['username']
    permission_required = "auth.view_user"


class UserUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = User
    paginate_by = 100
    template_name = 'infrablue/user_update.html'
    permission_required = "auth.change_user"

    def has_permission(self):
        perms = self.get_permission_required()
        return self.request.user.has_perms(perms, self.get_object())

    def get_form_class(self):
        if self.request.user.is_superuser:
            return UserChangeFormAdmin
        elif self.request.user.is_staff:
            return UserChangeFormStaff
        else:
            return UserChangeForm

    def get_success_url(self):
        return reverse_lazy("user_detail", kwargs={"pk": self.object.id})


class UserCreate(LoginRequiredMixin, GlobalPermissionRequiredMixin, CreateView):
    model = User
    template_name = 'infrablue/user_update.html'
    permission_required = "auth.create_user"

    def get_form_class(self):
        if self.request.user.is_superuser:
            return UserChangeFormAdmin
        elif self.request.user.is_staff:
            return UserChangeFormStaff
        else:
            return UserChangeForm

    def get_success_url(self):
        return reverse_lazy("user_detail", kwargs={"pk": self.object.id})


class UserDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = User
    template_name = 'infrablue/user_delete.html'
    success_url = reverse_lazy("user_list")
    permission_required = "auth.delete_user"


class UserChangePassword(PasswordChangeView):
    template_name = 'infrablue/user_change_password.html'

    def get_form_class(self):
        if "pk" in self.kwargs.keys() and self.request.user.is_superuser and int(
                self.kwargs["pk"]) != self.request.user.pk:
            form_class = SetPasswordForm
        else:
            form_class = PasswordChangeForm
        return form_class

    def get_success_url(self):
        user = self.get_form_kwargs()["user"]
        if user != self.request.user:
            succes_url = reverse_lazy("user_detail", kwargs={"pk": user.id})
        else:
            succes_url = reverse_lazy("self_detail")
        return succes_url

    def get_form_kwargs(self):
        form_kwargs = super(UserChangePassword, self).get_form_kwargs()
        if "pk" in self.kwargs.keys() and self.request.user.is_superuser and int(
                self.kwargs["pk"]) != self.request.user.pk:
            form_kwargs['user'] = User.objects.get(pk=int(self.kwargs['pk']))
        else:
            form_kwargs['user'] = self.request.user
        print(form_kwargs)
        return form_kwargs


class UserDetail(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = User
    template_name = "infrablue/user_detail.html"
    permission_required = "auth.view_user"


class SelfDetailView(LoginRequiredMixin, DetailView):
    model = User
    template_name = "infrablue/user_detail.html"

    def get_object(self, queryset=None):
        return self.request.user


class ServerGroupList(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = BigBlueButtonGroup
    paginate_by = 100
    template_name = "infrablue/server_group_list.html"
    fields = ["name", "apis.name"]


class ServerGroupUpdate(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = BigBlueButtonGroup
    paginate_by = 100
    template_name = "infrablue/server_group_update.html"
    success_url = reverse_lazy("server_group_list")
    fields = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["servers"] = ServerFormset(self.request.POST or None, instance=self.object)
        else:
            context["servers"] = ServerFormset(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        servers = context["servers"]
        self.object = form.save()
        if servers.is_valid():
            servers.instance = self.object
            servers.save()
        return super().form_valid(form)


class ServerGroupCreate(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = BigBlueButtonGroup
    template_name = "infrablue/server_group_update.html"
    success_url = reverse_lazy("server_group_list")
    fields = ["name"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["servers"] = ServerFormset(self.request.POST or None)
        else:
            context["servers"] = ServerFormset()
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        servers = context["servers"]
        self.object = form.save()
        if servers.is_valid():
            servers.instance = self.object
            servers.save()
        return super().form_valid(form)


class ServerGroupDelete(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = BigBlueButtonGroup
    template_name = "infrablue/server_group_delete.html"
    success_url = reverse_lazy("server_group_list")
