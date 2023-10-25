from django.shortcuts import render

import os

# Create your views here.
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.shortcuts import render

from django.http import JsonResponse
from .models import FormData, UploadedFile

from django.http import JsonResponse
from nb_proj.settings import MEDIA_ROOT

from django.conf import settings

from django.conf import settings
import os

from django.conf import settings
import os
import shutil
import subprocess
from subprocess import CalledProcessError, run
from .models import DockingProgress

@api_view(['POST'])
def submit_form(request):

    print('in submit form')

    def compute_center_and_size(range_str):
        """Helper function to compute center (mean) and size (difference) from a range string."""
        start, end = map(float, range_str.replace('[','').replace(']','').split(','))
        center = (start + end) / 2
        size = end - start
        return center, size

    # Process the form data here
    x_range = request.POST.get('x_range')
    y_range = request.POST.get('y_range')
    z_range = request.POST.get('z_range')
    pdb_file = request.FILES.get('file')

    center_x, size_x = compute_center_and_size(x_range)
    center_y, size_y = compute_center_and_size(y_range)
    center_z, size_z = compute_center_and_size(z_range)

    # Generate the config content
    config_content = f"""
    protein = {settings.BASE_DIR}\\docking\\receptors\\3lw0_cleaned.pdbqt
    ligand = {pdb_file.name if pdb_file else "$ligand"}

    center_x = {center_x}
    center_y = {center_y}
    center_z = {center_z}

    size_x = {size_x}
    size_y = {size_y}
    size_z = {size_z}

    energy_range = 4
    exhaustiveness = 8
    num_modes = 10
        """

    form_data = FormData(
        x_range = x_range,
        y_range = y_range,
        z_range = z_range,
        pdb_file = pdb_file
    )

    form_data.save()

    # Writing the config content to a file
    file_name = "config.txt"
    with open(os.path.join(settings.MEDIA_ROOT, file_name), 'w') as f:
        f.write(config_content.strip())

    pdb_file = form_data.pdb_file

    if pdb_file:
        source_path = os.path.join(settings.MEDIA_ROOT, pdb_file.name )
        pdbFileName = pdb_file.name.replace('uploads/','')
        destination_path = os.path.join(settings.BE_BASE_DIR, 'utilities', 'docking', 'receptors', pdbFileName)
        destination_path = os.path.normpath(destination_path)
        print('stop here')
        shutil.move(source_path, destination_path)


    cmd = ['python',f'{settings.BE_BASE_DIR}//utilities//docking//prep_receptor.py', '--basePath', f'{settings.BE_BASE_DIR}', '--filePath', f'{destination_path}'] # clean the .pdb file

    try:
        result = run(cmd, check=True) 

        # moving the .pdbqt file
        pdbqt_filename = os.path.splitext(pdbFileName)[0] + ".pdbqt"
        pdbqt_source_path = os.path.join(settings.BASE_DIR, pdbqt_filename)
        pdbqt_destination_path = os.path.join(os.path.dirname(destination_path), '..//cleaned_receptors', pdbqt_filename)
        shutil.move(pdbqt_source_path, pdbqt_destination_path)

        return JsonResponse({'message': 'File cleaned successfully', 'success': True})
    
    except CalledProcessError:
        return JsonResponse({'message': 'There was an error cleaning the file'})
    



@api_view(['GET'])
def get_form_data(request):
    # Retrieve the form data from the database
    form_data = FormData.objects.all()

    # Convert form data to a list of dictionaries
    serialized_data = [
        {
            'x_range': item.x_range,
            'y_range': item.y_range,
            'z_range ': item.z_range,
            'pdb_file': item.pdb_file.url if item.pdb_file else ''
        }
        for item in form_data
    ]

    return JsonResponse(serialized_data, safe=False)



def save_file(request):
    if request.method == 'POST':
        data = request.POST['data']
        file_name = 'testVinaConfig.txt'


        with open(os.path.join(MEDIA_ROOT, file_name), 'w') as f:
            f.write(data)


        uploaded_file = UploadedFile(name=file_name)
        uploaded_file.file.name = file_name
        uploaded_file.save()


        return JsonResponse({'message': 'File saved successfully!'})
    return JsonResponse({'message': 'Invalid request'}, status=400)




@api_view(['POST'])
def run_docking(request):

    total_ligands_count = 123  # Replace this with actual code that determines the count
    progress = DockingProgress.objects.create(total_ligands=total_ligands_count)
  # You'd need to set the total ligands here

    cmd = [
        'python', f'{settings.BE_BASE_DIR}/utilities/docking/dock_ligands.py',
        '--base_directory', f'{settings.BE_BASE_DIR}',
        '--task_id', str(progress.task_id)
    ]
    try:
        result = run(cmd, check=True) 
        return JsonResponse({'message': 'Docking study completed successfully', 'success': True})
    
    except CalledProcessError:
        return JsonResponse({'message': 'Docking study failed'})
    


def get_docking_progress(request):
    task_id = "task_001"
    progress = DockingProgress.objects.get(task_id=task_id)
    percentage = (progress.ligands_docked / progress.total_ligands) * 100
    return JsonResponse({'progress': percentage})
