import os
import subprocess

for folder in [f.path for f in os.scandir('.') if f.is_dir()]:
    folder = folder[2:]
    history = True
    with open(f"git_history_output_{folder}.txt", "w+", buffering=1) as file:
        file.write(f'Checking {folder}...')
        success = True
        while success:
            os.chdir(folder)
            git = subprocess.call(
                ['git', 'checkout', 'HEAD^'], stdout=file)
            hash = subprocess.call(
                ['git', 'rev-parse', 'HEAD'], stdout=file, stderr=file)
            success = git == 0
            os.chdir('..')
            check = subprocess.call(['./checker.sh', folder], stdout=file)
