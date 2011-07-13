from django.utils.translation import ugettext_lazy as _


class PasswordResetFieldException(Exception):
    """Raised if the profile model has no 'password_reset' field."""

    def __init__(self):
        super(PasswordResetFieldException, self).__init__(_(
           "The 'password_reset' field is required " \
           "on the user profile model."
        ))
