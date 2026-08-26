from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [('dashboard', '0005_remove_task_subtask_delete_subtask')]
    operations = [migrations.AddField(model_name='task', name='description', field=models.TextField(blank=True, default=''))]
