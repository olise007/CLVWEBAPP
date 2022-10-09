#!/bin/bash
source /home/explore-student/anaconda3/etc/profile.d/conda.sh
conda activate clvwebapp
sudo s3fs intern-t20-2201-customer-lifetime-value -o use_cache=/tmp -o allow_other -o uid=$UID -o mp_umask=002 -o multireq_max=5 -o umask=0007 -o nonempty /home/explore-student/s3-drive
cd /home/explore-student/s3-drive/clvwebapp
streamlit run Home.py