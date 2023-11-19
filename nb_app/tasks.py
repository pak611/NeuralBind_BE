# tasks.py
from celery import shared_task
from subprocess import run, CalledProcessError
from django.conf import settings
from nb_app.models import DockingProgress
from celery.utils.log import get_task_logger

# Initialize the logger
logger = get_task_logger(__name__)

@shared_task(bind=True)
def run_docking_task(self, total_ligands_count, task_id):
    logger.info('Patrick: Running docking task')
    cmd = [
        'python', f'{settings.BE_BASE_DIR}/entry_dock.py',
        '--base_directory', f'{settings.BE_BASE_DIR}',
        '--task_id', str(task_id)
    ]

    try:
        result = run(cmd, check=True)
        return {'message': 'Docking study completed successfully', 'success': True}
    except CalledProcessError as e:
        # Log the error with more details
        logger.error(f'Docking study failed: {e}')
        return {'message': 'Docking study failed'}
    except Exception as e:
        # Catch any other exceptions and log
        logger.error(f'Unexpected error in docking task: {e}')
        raise  # Re-raise the exception if you want the task to be marked as failed
    finally:
        try:
            progress = DockingProgress.objects.get(task_id=task_id)
            progress.delete()
        except DockingProgress.DoesNotExist:
            logger.error(f'DockingProgress record not found for task_id: {task_id}')
