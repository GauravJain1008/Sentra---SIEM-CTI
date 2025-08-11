import re
import json
from django.utils.dateparse import parse_datetime
from django.db.models import Q
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import render
from django.utils import timezone
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Count
from django.db.models.functions import TruncMinute
from .serializers import LogEventSerializer
from .models import LogEvent, IoC, Alert
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def dashboard(request):
    return render(request, "core/dashboard.html")


def live_logs(request):
    return render(request, "core/live_logs.html")

from django.utils.dateparse import parse_datetime
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

@api_view(["GET"])
@permission_classes([AllowAny])
def fetch_logs(request):
    """
    Query params:
      - minutes (int)  (default 10)   # ignored if start/end provided
      - start, end (ISO8601)
      - level, host, source, q (icontains)
      - limit (default 1000, max 5000)
    """
    qs = LogEvent.objects.all().order_by("-ts")

    start = request.GET.get("start")
    end = request.GET.get("end")
    minutes = int(request.GET.get("minutes", 10))
    level = request.GET.get("level")
    host = request.GET.get("host")
    source = request.GET.get("source")
    q = request.GET.get("q")
    limit = min(int(request.GET.get("limit", 1000)), 5000)

    if start or end:
        if start:
            qs = qs.filter(ts__gte=parse_datetime(start))
        if end:
            qs = qs.filter(ts__lte=parse_datetime(end))
    else:
        since = timezone.now() - timedelta(minutes=minutes)
        qs = qs.filter(ts__gte=since)

    if level:
        qs = qs.filter(level__iexact=level)
    if host:
        qs = qs.filter(host__icontains=host)
    if source:
        qs = qs.filter(source__icontains=source)
    if q:
        qs = qs.filter(
            Q(message__icontains=q) |
            Q(host__icontains=q) |
            Q(source__icontains=q)
        )

    qs = qs[:limit]

    data = [
        {
            "ts": obj.ts.isoformat(),
            "host": obj.host,
            "source": obj.source,
            "level": obj.level,
            "message": obj.message,
        }
        for obj in qs
    ]
    return Response({"results": list(reversed(data))})  # oldest first for rendering


@csrf_exempt
@api_view(["POST"])
@permission_classes([AllowAny])
def ingest(request):
    ser = LogEventSerializer(data=request.data, many=isinstance(request.data, list))
    ser.is_valid(raise_exception=True)
    events = ser.save()

    iocs = list(IoC.objects.values_list("value", flat=True))
    if not isinstance(events, list):
        events = [events]

    channel_layer = get_channel_layer()

    for ev in events:
        if any(ioc in ev.message for ioc in iocs):
            ev.matched_ioc = True
            ev.save(update_fields=["matched_ioc"])

        async_to_sync(channel_layer.group_send)(
            "logs",
            {
                "type": "log.message",
                "event": {
                    "ts": ev.ts.isoformat(),
                    "host": ev.host,
                    "source": ev.source,
                    "level": ev.level,
                    "message": ev.message,
                },
            },
        )
    return Response({"status": "ok"}, status=status.HTTP_202_ACCEPTED)


@csrf_exempt
@api_view(["GET"])
@permission_classes([AllowAny])
def search_logs(request):
    q = request.GET.get("q", "")
    start = request.GET.get("start")
    end = request.GET.get("end")
    qs = LogEvent.objects.all().order_by("-ts")

    if q:
        qs = qs.filter(
            Q(message__icontains=q) |
            Q(host__icontains=q) |
            Q(source__icontains=q)
        )
    if start:
        qs = qs.filter(ts__gte=start)
    if end:
        qs = qs.filter(ts__lte=end)

    data = [
        {
            "ts": obj.ts.isoformat(),
            "host": obj.host,
            "source": obj.source,
            "level": obj.level,
            "message": obj.message[:500],
            "matched_ioc": obj.matched_ioc,
        }
        for obj in qs[:1000]
    ]
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def stats_api(request):
    now = timezone.now()
    since = now - timedelta(minutes=60)

    per_min = (
        LogEvent.objects.filter(ts__gte=since)
        .annotate(m=TruncMinute("ts"))
        .values("m")
        .annotate(count=Count("id"))
        .order_by("m")
    )
    logs_per_min = {
        "labels": [x["m"].strftime("%H:%M") for x in per_min],
        "data": [x["count"] for x in per_min],
    }

    level_counts_qs = (
        LogEvent.objects.values("level")
        .annotate(count=Count("id"))
        .order_by("-count")
    )
    level_counts = {
        "labels": [x["level"] or "UNKNOWN" for x in level_counts_qs],
        "data": [x["count"] for x in level_counts_qs],
    }

    since_day = now - timedelta(days=1)
    top_sources_qs = (
        LogEvent.objects.filter(ts__gte=since_day)
        .values("source")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    top_sources = {
        "labels": [x["source"] or "unknown" for x in top_sources_qs],
        "data": [x["count"] for x in top_sources_qs],
    }

    top_hosts_qs = (
        LogEvent.objects.filter(ts__gte=since_day)
        .values("host")
        .annotate(count=Count("id"))
        .order_by("-count")[:10]
    )
    top_hosts = {
        "labels": [x["host"] or "unknown" for x in top_hosts_qs],
        "data": [x["count"] for x in top_hosts_qs],
    }

    kpi_last_hour = LogEvent.objects.filter(ts__gte=since).count()
    kpi_total_alerts = Alert.objects.count()
    kpi_ioc_hits = LogEvent.objects.filter(matched_ioc=True).count()

    return JsonResponse({
        "kpis": {
            "logs_last_hour": kpi_last_hour,
            "total_alerts": kpi_total_alerts,
            "ioc_hits": kpi_ioc_hits,
        },
        "logs_per_min": logs_per_min,
        "level_counts": level_counts,
        "top_sources": top_sources,
        "top_hosts": top_hosts,
    })
