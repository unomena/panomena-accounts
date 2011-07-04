from django.db import models
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.contrib.auth.models import SiteProfileNotAvailable


def get_profile_model():
    """Retrieves the profile model from AUTH_PROFILE_MODULE and raises the
    appropriate exceptions when something goes wrong.

    """
    # check if present
    if not getattr(settings, 'AUTH_PROFILE_MODULE', False):
        raise SiteProfileNotAvailable('You need to set AUTH_PROFILE_MODULE ' \
            'in your project settings')
    # check the format
    try:
        app_label, model_name = settings.AUTH_PROFILE_MODULE.split('.')
    except ValueError:
        raise SiteProfileNotAvailable('app_label and model_name should ' \
            'be separated by a dot in the AUTH_PROFILE_MODULE setting')
    # attempt to get the model
    try:
        model = models.get_model(app_label, model_name)
        if model is None:
            raise SiteProfileNotAvailable('Unable to load the profile '
                'model, check AUTH_PROFILE_MODULE in your project settings')
    except (ImportError, ImproperlyConfigured):
        raise SiteProfileNotAvailable
    return model
