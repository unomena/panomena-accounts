from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm

from panomena_mobile.fields import MsisdnField

from panomena_accounts.utils import get_profile_model


class LoginForm(AuthenticationForm):
    """Generic lgoin form base on django auth login form, but handles
    'next' parameter as a field.

    """

    next = forms.CharField(
        required=False,
        widget=forms.widgets.HiddenInput
    )

    def __init__(self, request, *args, **kwargs):
        # set the 'next' field if value found in request
        next = request.REQUEST.get('next', None)
        if next:
            initial = kwargs.get('initial', {})
            initial['next'] = next
            kwargs['initial'] = initial
        # run the super method
        super(LoginForm, self).__init__(request, *args, **kwargs)


class BaseProfileForm(forms.Form):
    """Generic form for saving and editing user profiles. It takes care of
    setting and saving both the user and it's attached profile object.

    """
    excluded_fields = (
        'password',
        'confirm_password',
    )

    def __init__(self, *args, **kwargs):
        self.user = user = kwargs.pop('user', None)
        super(BaseProfileForm, self).__init__(*args, **kwargs)
        # setup intial values from instances
        if user:
            # attempt to get the profile for the user
            profile_model = get_profile_model()
            try:
                profile = user.get_profile()
            except profile_model.DoesNotExist:
                profile = None
            # update the initial values
            self.initial.update(self.get_field_values(user))
            self.initial.update(self.get_field_values(profile))

    def get_field_values(self, obj):
        """Gathers field values from an object."""
        values = {}
        if issubclass(obj.__class__, dict):
            # extract values from dictionary
            for field in self.fields:
                if field in self.excluded_fields: continue
                if obj.has_key(field):
                    values[field] = obj[field]
        else:
            # extract values from an object
            for field in self.fields:
                if field in self.excluded_fields: continue
                if hasattr(obj, field):
                    values[field] = getattr(obj, field)
        # return the extracted values
        return values

    def clean_username(self):
        """Check for unique username and clean value."""
        username = self.cleaned_data.get('username', None)
        # check for user with same username
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return username
        # check for unchanged username
        if self.user is not None:
            if user.username == self.user.username:
                return username
        # raise validation error
        raise forms.ValidationError(_('Username already in use by another user.'))

    def clean(self):
        """Check for non field errors and clean data accordingly."""
        cleaned_data = self.cleaned_data
        password = cleaned_data.get('password', '')
        confirm_password = cleaned_data.get('confirm_password', '')
        if password != confirm_password:
            raise forms.ValidationError(_("Passwords don't match."))
        # return the cleaned data
        return cleaned_data

    def save(self):
        """Populates the user and profile objects with data from relevant 
        fields and saves them.
        
        """
        cleaned_data = self.cleaned_data
        profile_model = get_profile_model()
        user = self.user
        # construct the user if necessary
        if user is None: user = User()
        # get or construct the profile
        try:
            profile = user.get_profile()
        except profile_model.DoesNotExist:
            profile = profile_model()
        # set relative values on objects
        for key, value in cleaned_data.items():
            # skip excluded fields
            if key in self.excluded_fields: continue
            # set field values on user
            if hasattr(user, key):
                setattr(user, key, value)
            # set field values on profile
            if hasattr(profile, key):
                setattr(profile, key, value)
        # set the user password
        password = cleaned_data.get('password', '')
        if len(password) > 0:
            user.set_password(password)
        # save the user
        user.save()
        # save the profile
        if profile.id is None:
            profile.user = user
        profile.save()
        # return the user object
        return user


class AvatarForm(forms.Form):
    """Avatar updating form."""

    avatar = forms.FileField(
        label=_('Avatar')
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AvatarForm, self).__init__(*args, **kwargs)

    def save(self):
        """Saves the avatar for the indicated user."""
        profile_model = get_profile_model()
        user = self.user
        try:
            avatar = self.cleaned_data['avatar']
            profile = user.get_profile()
            profile.image.save(avatar.name, avatar)
        except profile_model.DoesNotExist:
            pass
        return user


class ForgotSMSForm(forms.Form):
    """SMS forgotten password form."""

    mobile_number = MsisdnField(
        label='Mobile Number',
    )

    def __init__(self, *args, **kwargs):
        self.user = None
        super(ForgotSMSForm, self).__init__(*args, **kwargs)

    def clean_mobile_number(self):
        """Checks if the mobile number exists and caches the user
        related to it.
        
        """
        mobile_number = self.cleaned_data.get('mobile_number', None)
        # check for user with given mobile number
        try:
            self.user = User.objects.get(mobile_number=mobile_number)
        except User.DoesNotExist:
            raise forms.ValidationError(_('No user registered with this mobile number.'))
        # return the mobile number
        return mobile_number

    def send(self):
        """Sends an SMS tot he user containing the forgotten password."""
        print self.cleaned_data

