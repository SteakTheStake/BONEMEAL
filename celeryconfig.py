## Broker settings.
CELERY_BROKER_URL = 'redis://localhost:6379/1'

# List of modules to import when the Celery worker starts.
imports = ('app.py',)

## Using the database to store task state and results.
result_backend = 'redis://localhost:6379/1'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
