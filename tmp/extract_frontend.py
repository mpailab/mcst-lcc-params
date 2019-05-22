import sys
import os
import re
import shutil

source_path = sys.argv[1]
dist_path = sys.argv[2]

if not os.path.exists(dist_path):
    os.makedirs(dist_path)

for dir in os.listdir(source_path):
    data = dir.split('_')[1]
    for file in os.listdir(source_path + '/' + dir):
        if int(data) < 20181221:
            spec = '.'.join(file.split('.')[1:3])
            p = file.split('.')[0]

        elif file[0].isdigit():
            spec = '.'.join(file.split('.')[0:2])
            p = file.split('.')[2]

        elif file.split('.')[0] == 'all_tasks':
            spec = 'all_tasks'
            p = file.split('.')[1]

        else:
            spec = 'all_tasks'
            p = file.split('all_tasks')[0]

        if not os.path.exists(dist_path + '/' + spec + '/' + data):
            os.makedirs(dist_path + '/' + spec + '/' + data)
        shutil.copyfile(source_path + '/' + dir + '/' + file, dist_path + '/' + spec + '/' + data + '/' + p + '.txt')
