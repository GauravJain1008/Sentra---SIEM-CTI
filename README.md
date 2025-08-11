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

> Project Structure

SIEM/

 ├── agent/               
 ├── dashboard/           
 ├── siem/               
 ├── requirements.txt    
 ├── manage.py
 └── README.md
 
> Installation
1. Clone the repository
git clone https://github.com/GauravJain1008/Sentra---SIEM-CTI.git
cd Sentra---SIEM-CTI

2. Install dependencies

pip install -r requirements.txt

3. Run Django server

python manage.py runserver

4. Run the log agent (in another terminal)

python agent/log_agent_multi.py

5. Access Dashboard

    http://127.0.0.1:8000/

> Configuration

    > Update agent/log_agent_multi.py with your desired log file paths.

    > To run continuously in background, configure it as a systemd service.

_*Note: This repo is actively updated while the project is in development — expect frequent changes, experiments, and feature additions.*_

> Credits

Developed & maintained by Gaurav Jain <br>
Sentra - Custom Django-based SIEM for learning, experimentation, and real-time log monitoring.
















