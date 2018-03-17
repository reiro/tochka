from django.contrib import admin

from .models import Share, TradeEvent, Insider, InsiderTradeEvent

admin.site.register(Share)
admin.site.register(TradeEvent)
admin.site.register(Insider)
admin.site.register(InsiderTradeEvent)
