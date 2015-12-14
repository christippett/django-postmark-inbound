# -*- coding: utf-8 -*-
import json
import re

from django.conf import settings

from rest_framework.parsers import JSONParser, ParseError, six


# Parser logic taken from vbabiy's djangorestframework-camel-case project
# https://github.com/vbabiy/djangorestframework-camel-case

first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_underscore(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


def underscoreize(data):
    if isinstance(data, dict):
        new_dict = {}
        for key, value in data.items():
            if key in ['From', 'To', 'Cc', 'Bcc']:
                key = key + 'Email'
            new_key = camel_to_underscore(key)
            new_dict[new_key] = underscoreize(value)
        return new_dict
    if isinstance(data, (list, tuple)):
        for i in range(len(data)):
            data[i] = underscoreize(data[i])
        return data
    return data


class PostmarkJSONParser(JSONParser):
    """
    Append "Email" to the from/to/cc/bcc keys in Postmark's JSON request. We do this because Postmark's "From" key conflicts with the Python keyword of the same name and therefore we cannot use it as a model/serializer field. By using fields named from_email, to_email, etc we can match to the renamed keys from Postmark's JSON (FromEmail, ToEmail, etc)
    """
    def parse(self, stream, media_type=None, parser_context=None):
        parser_context = parser_context or {}
        encoding = parser_context.get('encoding', settings.DEFAULT_CHARSET)

        try:
            data = stream.read().decode(encoding)
            return underscoreize(json.loads(data))
        except ValueError as exc:
            raise ParseError('JSON parse error - %s' % six.text_type(exc))
