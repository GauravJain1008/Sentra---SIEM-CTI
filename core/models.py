from django.db import models
from django.utils import timezone

class LogEvent(models.Model):
    ts = models.DateTimeField(default=timezone.now, db_index=True)
    host = models.CharField(max_length=255, blank=True, null=True)
    source = models.CharField(max_length=255, blank=True, null=True)  # app/file name
    level = models.CharField(max_length=32, blank=True, null=True)    # INFO/WARN/ERROR
    message = models.TextField()
    extra = models.JSONField(default=dict, blank=True)
    matched_ioc = models.BooleanField(default=False)

    def __str__(self):
        return f"[{self.ts}] {self.level or ''} {self.message[:80]}"

class IoC(models.Model):
    IOC_TYPES = [("ip", "IP"), ("domain", "Domain"), ("hash", "Hash")]
    value = models.CharField(max_length=255, unique=True)
    ioc_type = models.CharField(max_length=16, choices=IOC_TYPES)
    source = models.CharField(max_length=255, blank=True, null=True)
    added_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.value

class Rule(models.Model):
    """
    Super-simple MVP rule:
    - pattern: substring or regex
    - threshold: N events
    - window_seconds: within time window
    """
    name = models.CharField(max_length=128, unique=True)
    pattern = models.CharField(max_length=512)
    use_regex = models.BooleanField(default=False)
    threshold = models.PositiveIntegerField(default=5)
    window_seconds = models.PositiveIntegerField(default=300)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Alert(models.Model):
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    hit_count = models.PositiveIntegerField(default=0)
    key = models.CharField(max_length=255, blank=True, null=True)  # e.g., src_ip/user
    sample_message = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"[{self.created_at}] Alert via {self.rule}"
