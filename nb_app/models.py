
from django.db import models
import uuid

class FormData(models.Model):
    x_range = models.CharField(max_length=50)
    y_range = models.CharField(max_length=50)
    z_range = models.CharField(max_length=50)
    pdb_file = models.FileField(upload_to='uploads/')
    created_at = models.DateTimeField(auto_now_add=True)



class UploadedFile(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploaded_files/')




class DockingProgress(models.Model):
    task_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    total_ligands = models.IntegerField()
    ligands_docked = models.IntegerField(default=0)
