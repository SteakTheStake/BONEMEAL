## Broker settings.
CELERY_BROKER_URL = 'redis://162.33.23.205:6379/1'

# List of modules to import when the Celery worker starts.
imports = ('app.tasks',)

## Using the database to store task state and results.
result_backend = 'redis://162.33.23.205:6379/1'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
