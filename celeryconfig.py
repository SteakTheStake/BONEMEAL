## Broker settings.
CELERY_BROKER_URL = 'redis://bonemeal.summitmc.xyz:6379/1'

# List of modules to import when the Celery worker starts.
imports = ('app.py',)

## Using the database to store task state and results.
result_backend = 'redis://bonemeal.summitmc.xyz:6379/1'

task_annotations = {'tasks.add': {'rate_limit': '10/s'}}
