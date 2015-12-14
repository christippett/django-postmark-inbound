import django.dispatch

inbound_mail_received = django.dispatch.Signal(providing_args=["mail_data",
                                                               "mail_object"])
