from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.views import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from panomena_general.utils import class_from_string, SettingsFetcher, \
    ajax_redirect

from panomena_accounts.forms import AvatarForm, ForgotForm, ResetForm, \
    ForgotSMSForm
from panomena_accounts.utils import get_profile_model
from panomena_accounts.exceptions import PasswordResetFieldException


settings = SettingsFetcher('accounts')


class RegisterView(object):
    """Account registration view."""

    def authenticate(self, data):
        """Authenticate and return the user."""
        user = authenticate(
            username=data['username'],
            password=data['password']
        )
        return user

    def valid(self, request, form):
        """Process a valid form."""
        form.save()
        # authenticate and login user
        data = form.cleaned_data
        user = self.authenticate(data)
        auth_login(request, user)
        # redirect appropriately
        url = settings.LOGIN_REDIRECT_URL
        return ajax_redirect(request, url)

    def form(self):
        """Returns the form to be used."""
        return class_from_string(settings.ACCOUNTS_REGISTER_FORM)

    def __call__(self, request):
        """Basic form view mechanics."""
        register_form = self.form()
        context = RequestContext(request)
        # handle the form
        if request.method == 'POST':
            form = register_form(request, request.POST)
            if form.is_valid():
                return self.valid(request, form)
        else:
            form = register_form(request)
        context = RequestContext(request, {
            'title': 'Register',
            'form': form,
        })
        return render_to_response('accounts/register.html', context)

register = RegisterView()


@login_required
def profile(request, id=None):
    """Account profile edit view for a current user profile."""
    # get the the requested profile if id specified
    profile_form = settings.ACCOUNTS_PROFILE_FORM
    profile_form = class_from_string(profile_form)
    user = request.user
    context = RequestContext(request)
    if request.method == 'POST':
        form = profile_form(request, request.POST, user=user)
        if form.is_valid():
            form.save()
    else:
        form = profile_form(request, user=user)
    context = RequestContext(request, {
        'title': 'Profile',
        'form': form,
    })
    return render_to_response('accounts/profile.html', context)


def profile_display(request, pk):
    """Account profile display for user accounts."""
    context = RequestContext(request)
    context['user'] = get_object_or_404(User, pk=pk)
    return render_to_response('accounts/profile_display.html', context)


class LoginView(object):
    """Account login view."""

    def valid(self, request, form):
        """Process a valid form."""
        # authenticate and login user
        data = form.cleaned_data
        # todo: if form is based on django auth form then this step can be removed
        user = authenticate(
            username=data['username'],
            password=data['password'],
        )
        auth_login(request, user)
        # redirect to next url if available
        # todo: check that form is base on LoginForm
        next_url = data.get('next', '')
        if len(next_url) > 0:
            return redirect(next_url)
        # redirect to url indicated in settings
        url = settings.LOGIN_REDIRECT_URL
        return ajax_redirect(request, url)

    def __call__(self, request):
        login_form = settings.ACCOUNTS_LOGIN_FORM
        login_form = class_from_string(login_form)
        if request.method == 'POST':
            form = login_form(request, request.POST)
            if form.is_valid():
                return self.valid(request, form)
        else:
            form = login_form(request)
            # todo: check for session middleware
            request.session.set_test_cookie()
        # build context and render template
        context = RequestContext(request, {
            'title': 'Login',
            'form': form,
            'next': request.GET.get('next', None),
        })
        return render_to_response('accounts/login.html', context)

login = LoginView()


@login_required
def avatar(request):
    """Displays and updates the users avatar."""
    user = request.user
    if request.method == 'POST':
        form = AvatarForm(user, request.POST, request.FILES)
        if form.is_valid():
            form.save()
    else:
        form = AvatarForm(user)
    context = RequestContext(request, {
        'title': 'Avatar',
        'form': form,
    })
    return render_to_response('accounts/avatar.html', context)


@login_required
def avatar_clear(request):
    """Clears the avatar of a user."""
    profile_model = get_profile_model()
    try:
        profile = request.user.get_profile()
        profile.image.delete()
    except profile_model.DoesNotExist:
        pass
    return redirect('accounts_avatar')


def forgot(request, template):
    """View for retrieving a forgotten password."""
    form = ForgotForm(request)
    context = RequestContext(request, {'form': form})
    return render_to_response(template, context)


def reset(request, reset_uuid):
    """View for resetting a user password."""
    profile_model = get_profile_model()
    profile = None
    # validate the provided uuid
    try:
        profile = profile_model.objects.get(password_reset=reset_uuid)
        # check if the profile model has the password reset field
        if not hasattr(profile, 'password_reset'):
            raise PasswordResetFieldException()
        authenticated = True
    except profile_model.DoesNotExist:
        authenticated = False
    # handle the form
    if request.method == 'POST' and profile:
        form = ResetForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            # set the user's password
            profile.user.set_password(data['password'])
            profile.user.save()
            # nullify the reset identifier to disable the old link
            profile.password_reset = None
            profile.save()
    else:
        form = ResetForm()
    # build context and render
    context = RequestContext(request, {
        'form': form,
        'authenticated': authenticated,
    })
    return render_to_response('accounts/reset.html', context)


def logout(request):
    """Logout user and run extra requirements."""
    # django auth logout
    response = auth_logout(request)
    return response


def forgot_sms(request):
    """Allows the user to send forgotten password to registered
    mobile number.
    
    """
    if request.method == 'POST':
        form = ForgotSMSForm(request.POST)
        if form.is_valid():
            # send the sms to the user
            pass
    else:
        form = ForgotSMSForm()
    context = RequestContext(request, {'form': form})
    return render_to_response('accounts/forgot_sms.html', context)
