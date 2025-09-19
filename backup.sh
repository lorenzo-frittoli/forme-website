python3 -c "from helpers import *; make_backup('timed')"
mkdir -p data_backup
cp data/* data_backup
cp templates/archive.html data_backup
cp archive.py data_backup
