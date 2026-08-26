from django.db import models
from django.contrib.auth.models import User
from dashboard.models import Category


class CompletedTask(models.Model):
    title = models.CharField(max_length=255, default="Task")
    description = models.TextField(blank=True, default="")
    status = models.CharField(max_length=50, default="Completed")
    action = models.CharField(max_length=100, default="Task completed")
    created_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    category = models.CharField(max_length=255, default="Others")
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Completed Task"
    
    
    

class TaskHistory(models.Model):
    task = models.ForeignKey('dashboard.Task', on_delete=models.CASCADE, related_name='history')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    action = models.CharField(max_length=100)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-changed_at']
