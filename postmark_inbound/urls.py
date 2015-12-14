from django.conf.urls import url

from .views import InboundMailWebhook


urlpatterns = [
    url(r'^inbound', InboundMailWebhook.as_view())
]
