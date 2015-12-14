from django.conf import settings


DEFAULTS = {
    'ATTACHMENT_UPLOAD_TO': 'attachments',  # /media/attachments
    'SAVE_MAIL_TO_DB': True,
    'IP_WHITE_LIST': [
        '50.31.156.104',
        '50.31.156.105',
        '50.31.156.106',
        '50.31.156.107',
        '50.31.156.108',
        '50.31.156.6',
        '127.0.0.1']
}


class PostmarkInboundMailOptions(object):
    """
    A settings object, that allows settings to be accessed as properties.
    For example:
        from django_postmark_inbound.settings import inbound_mail_options
        print(inbound_mail_options.ATTACHMENT_UPLOAD_TO)
    """
    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'POSTMARK_INBOUND_MAIL',
                                          {})
        return self._user_settings

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid option: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Cache the result
        setattr(self, attr, val)
        return val

inbound_mail_options = PostmarkInboundMailOptions(None, DEFAULTS)
