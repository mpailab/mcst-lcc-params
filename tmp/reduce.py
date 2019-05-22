import sys
import os
import re
import shutil

source_path = sys.argv[1]
dist_path = sys.argv[2]

if os.path.exists(dist_path):
    shutil.rmtree(dist_path)
os.makedirs(dist_path)

for spec in os.listdir(source_path):
    os.makedirs(dist_path + '/' + spec)
    for proc in os.listdir(source_path + '/' + spec):
        source = open(source_path + '/' + spec + '/' + proc + '/regions.txt')
        dist = open(dist_path + '/' + spec + '/' + proc + '.txt', 'w')
        for str in source:
            if str.startswith('N:') or str.startswith('dom_') or str.startswith('pdom_'):
                if not re.match('^N:[0-9]* uniq', str):
                    dist.write(str)
        dist.close()
        source.close()
