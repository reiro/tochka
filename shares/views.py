import json
import pdb
from .models import Share, TradeEvent, Insider, InsiderTradeEvent
from django.http import HttpResponse, HttpResponseNotFound, JsonResponse
from django.shortcuts import get_object_or_404, render
from datetime import date, datetime
from django.core.serializers.json import DjangoJSONEncoder
from psycopg2 import sql

def index(request):
    shares = Share.objects.order_by('-name')
    if request.path.startswith('/api'):
        serialized = json.dumps(list(shares.values()), cls=DjangoJSONEncoder)
        return JsonResponse({'shares': serialized})
    else:
        return render(request, 'shares/index.html', {'shares': shares})

def ticker(request, ticker):
    share = get_object_or_404(Share, name=ticker)
    three_moth_ago = date(2018, 1, 1)
    trade_events = share.tradeevent_set.filter(date__gte=three_moth_ago)
    context = {'share': share, 'trade_events': trade_events}
    
    if request.path.startswith('/api'):
        serialized = json.dumps(list(trade_events.values()), cls=DjangoJSONEncoder)
        return JsonResponse({'trade_events': serialized})
    else:
        return render(request, 'shares/share.html', context)

def insider(request, ticker):
    share = get_object_or_404(Share, name=ticker)
    insider_events = share.insidertradeevent_set.all()
    context = {'share': share, 'insider_events': insider_events}
    
    if request.path.startswith('/api'):
        serialized = json.dumps(list(insider_events.values()), cls=DjangoJSONEncoder)
        return JsonResponse({'insider_events': serialized})
    else:
        return render(request, 'shares/insider.html', context)

def insider_trades(request, ticker, insider_name):
    share = get_object_or_404(Share, name=ticker)
    insider = get_object_or_404(Insider, name=insider_name)
    insider_events = insider.insidertradeevent_set.all()
    context = {'share': share, 'insider': insider, 'insider_events': insider_events}
    
    
    if request.path.startswith('/api'):
        serialized = json.dumps(list(insider_events.values()), cls=DjangoJSONEncoder)
        return JsonResponse({'insider_events': serialized})
    else:
        return render(request, 'shares/insider_trades.html', context)

def analytics(request, ticker):
    share = get_object_or_404(Share, name=ticker)

    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    if date_from is '' or date_to is '':
        return HttpResponseNotFound('<h1>Wrong parameters</h1>')

    date_from = datetime.strptime(date_from, '%m-%d-%Y').strftime('%Y-%m-%d')
    date_to = datetime.strptime(date_to, '%m-%d-%Y').strftime('%Y-%m-%d')

    from_event = share.tradeevent_set.filter(date__lte=date_from)[:1][0]
    to_event = share.tradeevent_set.filter(date__lte=date_to)[:1][0]

    diff = {
        'open': to_event.open - from_event.open,
        'high': to_event.high - from_event.high,
        'low': to_event.low - from_event.low,
        'close': to_event.close - from_event.close,
        'volume': to_event.volume - from_event.volume
    }

    context = {'share': share, 'diff': diff, 'date_from': date_from, 'date_to': date_to}

    #http://localhost:8000/AAPL/analytics/?date_from=01-10-2018&date_to=03-17-2018
    
    if request.path.startswith('/api'):
        return JsonResponse({'shares': diff})
    else:
        return render(request, 'shares/analytics.html', context)

def delta(request, ticker):
    accepted_types = ['open', 'close', 'high', 'low']
    value = request.GET.get("value", '')
    type = request.GET.get("type", '')

    if type not in accepted_types or value is '':
        return HttpResponseNotFound('<h1>Wrong parameters</h1>')

    share = get_object_or_404(Share, name=ticker)

    query = sql.SQL('''
    select * from (
        select
            t1.id,
            t1.date,
            t1.{0} as value,
            (SELECT t2.{0} FROM shares_tradeevent t2 
            WHERE 
            abs("t2".{0} - "t1".{0}) > %(value)s 
            AND t2.share_id = %(share_id)s
            AND t2.date > t1.date
            ORDER BY t2.date LIMIT 1) as previous_value,
            
            (SELECT t2.date FROM shares_tradeevent t2 
            WHERE 
            abs("t2".{0} - "t1".{0}) > %(value)s
            AND t2.share_id = %(share_id)s
            AND t2.date > t1.date
            ORDER BY t2.date LIMIT 1) as previous_date
        FROM 
            shares_tradeevent t1
        where t1.share_id = %(share_id)s) 
    a where previous_value is not null and date < previous_date;
    ''').format(sql.Identifier(type))

    periods = TradeEvent.objects.raw(query, {'type': type, 'value': value, 'share_id': share.id}) #[type, type, type, type, value, share.id, type, type, value, share.id, share.id])
    context = {'share': share, 'periods': periods, 'value': value, 'type': type}
    #http://localhost:8000/CVX/delta/?value=10&type=open
    
    if request.path.startswith('/api'):
        json_res = []
        for p in periods:
            json_obj = [p.id, p.date.isoformat(), p.previous_date.isoformat()]
            json_res.append(json_obj)
        serialized = json.dumps(json.dumps(json_res), cls=DjangoJSONEncoder)
        return JsonResponse({'periods': serialized})
    else:
        return render(request, 'shares/delta.html', context)
