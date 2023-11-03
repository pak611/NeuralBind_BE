# tasks.py
from celery import shared_task
from subprocess import run, CalledProcessError
from django.conf import settings
from nb_app.models import DockingProgress

@shared_task(bind=True)
def run_docking_task(self, total_ligands_count, task_id):
    cmd = [
        'python', f'{settings.BE_BASE_DIR}/entry_dock.py',
        '--base_directory', f'{settings.BE_BASE_DIR}',
        '--task_id', str(task_id)
    ]

    try:
        result = run(cmd, check=True)
        return {'message': 'Docking study completed successfully', 'success': True}
    except CalledProcessError:
        return {'message': 'Docking study failed'}
    finally:
        progress = DockingProgress.objects.get(task_id=task_id)
        progress.delete()
