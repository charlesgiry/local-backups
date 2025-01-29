from datetime import datetime
from hashlib import sha1 as sha1_
from logging import getLogger, StreamHandler, Formatter
from os import listdir, rename, mkdir
from pathlib import Path
from shutil import copy


def sha1(file_path: Path | str) -> str:
	"""
	returns a sha1 hash of a file
	:param file_path:
	:return: str: the hash in string format
	"""
	hash = sha1_()
	with open(file_path, 'rb') as file:
		for chunk in iter(lambda: file.read(4096), b''):
			hash.update(chunk)
	return hash.hexdigest()

# Setup script
target_path = Path(r'Path/to/folder/to/monitor')	# folder to monitor
current_path = Path(r'Path/to/backup/folder')		# folder to copy files into
backup_path = current_path / 'backups'				# folder to keep older versions of files
latest_path = current_path / 'latest'				# folder to keep the latest version of files
extensions = ['txt', 'pdf']							# extensions of files to monitor
now = datetime.now()

# Setup logger
logger = getLogger('local-backups')
formatter = Formatter('%(asctime)s | %(message)s')
stream_handler = StreamHandler()
stream_handler.setFormatter(formatter)
logger.handlers.clear()
logger.filters.clear()
logger.addHandler(stream_handler)
logger.setLevel('INFO')
logger.propagate = False

# Creating folder if doesn't exist
if not backup_path.exists():
	logger.info(f'Creating folder {backup_path}')
	mkdir(backup_path)

if not latest_path.exists():
	logger.info(f'Creating folder {latest_path}')
	mkdir(latest_path)

# calculating hashes
target_sha1 = {}
current_sha1 = {}
# target hashes
for file in listdir(target_path):
	if file.split('.')[-1] in extensions:
		fp = target_path / file
		logger.info(f'Calculating hash for {fp}')
		hashed_file = sha1(fp)
		target_sha1[file] = hashed_file

# backup hashes
for file in target_sha1:
	fp = latest_path / file
	if Path.is_file(latest_path / file):
		logger.info(f'Calculating hash for {fp}')
		hashed_file = sha1(fp)
		current_sha1[file] = hashed_file

# comparing hashes
for file in target_sha1:
	backup_file = False
	# if file wasn't in latest_folder, copy it
	if file not in current_sha1:
		logger.info(f'New file to backup: {file}')
		backup_file = True

	# else, check both hashes to see if they're the same
	else:
		# If they're different, keep old file as "{hash}_{date}.{extension}"
		if target_sha1[file] != current_sha1[file]:
			backup_file = True
			logger.info(f'Change detected in {file}')
			old_filepath = latest_path / file
			filename_no_ext = '.'.join(file.split('.')[:-1])
			new_filename = f'{filename_no_ext}_{now.strftime("%Y-%m-%d")}_{int(now.timestamp())}.{file.split(".")[-1]}'
			new_filepath = backup_path / new_filename
			logger.info(f'Backup of old version as {new_filepath}')
			rename(old_filepath, new_filepath)

	# If file requires back-up, copy it in the new folder
	if backup_file:
		fp = target_path / file
		logger.info(f'Backup of file {fp}')
		copy(fp, latest_path)

# input("Press enter to exit...")