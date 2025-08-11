# Sentra - SIEM+CTI
Sentra - From "Sentinel" (watchguard) + "Central" (hub for logs)

A lightweight, real-time Security Information & Event Management system built entirely in Python + Django.
Designed for continuous development and live log monitoring from multiple sources — similar in spirit to big siem type tools, but Sentra is fully custom-built.

> Features

    Multi-source log ingestion — system logs, app logs, and custom sources

    Real-time dashboard — auto-updates every second via /api/stats/

    Severity parsing — INFO / WARNING / ERROR / CRITICAL

    Persistent log agent — can run in background (systemd-ready)

    Django backend — clean API endpoints for stats & logs

