from django.conf.urls.defaults import *


urlpatterns = patterns('panomena_accounts.views',
    url(r'^register/$', 'register', {}, 'accounts_register'),
    url(r'^profile/$', 'profile', {}, 'accounts_profile'),
    url(r'^profile/(?P<pk>\d+)/$', 'profile_display', {}, 'accounts_profile'),
    url(r'^login/$', 'login', {'template': 'accounts/login.html'},
        'accounts_login'),
    url(r'^login_form/$', 'login', {'template': 'accounts/login_form.html'},
        'accounts_login_form'),
    url(r'^logout/$', 'logout', {}, 'accounts_logout'),
    url(r'^forgot/sms/$', 'forgot_sms', {}, 'accounts_forgot_sms'),
    url(r'^avatar/$', 'avatar', {}, 'accounts_avatar'),
    url(r'^avatar/remove/$', 'avatar_clear', {}, 'accounts_avatar_clear'),
)
