from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('reporting', '0004_rename_taskhistory_completedtask_and_more')]
    operations = [
        migrations.AddField(model_name='completedtask', name='description', field=models.TextField(blank=True, default='')),
        migrations.AddField(model_name='completedtask', name='status', field=models.CharField(default='Completed', max_length=50)),
        migrations.AddField(model_name='completedtask', name='action', field=models.CharField(default='Task completed', max_length=100)),
    ]
