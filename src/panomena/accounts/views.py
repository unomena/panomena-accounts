from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.views import logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from panomena.general.utils import class_from_string, json_redirect, \
    SettingsFetcher, is_ajax_request

from panomena.accounts.forms import AvatarForm, ForgotSMSForm
from panomena.accounts.utils import get_profile_model


settings = SettingsFetcher('accounts')


def register(request):
    """Registration view that takes it's form from the ACCOUNT_REGISTER_FORM
    setting and processes it.

    """
    register_form = settings.ACCOUNTS_REGISTER_FORM
    register_form = class_from_string(register_form)
    context = RequestContext(request)
    # handle the form
    if request.method == 'POST':
        form = register_form(request.POST)
        if form.is_valid():
            form.save()
            # authenticate and login user
            data = form.cleaned_data
            user = authenticate(
                username=data['username'],
                password=data['password']
            )
            auth_login(request, user)
            # redirect appropriately
            ajax = is_ajax_request(request)
            url = settings.LOGIN_REDIRECT_URL
            if ajax: return json_redirect(url)
            return redirect(url)
    else:
        form = register_form()
    context['form'] = form
    return render_to_response('accounts/register.html', context)


@login_required
def profile(request, id=None):
    """Account profile edit view for a current user profile."""
    # get the the requested profile if id specified
    profile_form = settings.ACCOUNTS_PROFILE_FORM
    profile_form = class_from_string(profile_form)
    user = request.user
    context = RequestContext(request)
    if request.method == 'POST':
        form = profile_form(request.POST, user=user)
        if form.is_valid():
            form.save()
    else:
        form = profile_form(user=user)
    context['form'] = form
    return render_to_response('accounts/profile.html', context)


def profile_display(request, pk):
    """Account profile display for user accounts."""
    context = RequestContext(request)
    context['user'] = get_object_or_404(User, pk=pk)
    return render_to_response('accounts/profile_display.html', context)


def login(request, template):
    """Login view for users."""
    login_form = settings.ACCOUNTS_LOGIN_FORM
    login_form = class_from_string(login_form)
    context = RequestContext(request)
    if request.method == 'POST':
        form = login_form(request, request.POST)
        if form.is_valid():
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
            ajax = is_ajax_request(request)
            if ajax: return json_redirect(url)
            else: return redirect(url)
    else:
        form = login_form(request)
        # todo: check for session middleware
        request.session.set_test_cookie()
    context['form'] = form
    context['next'] = request.GET.get('next', None)
    return render_to_response(template, context)


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
    context = RequestContext(request, {'form': form})
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
