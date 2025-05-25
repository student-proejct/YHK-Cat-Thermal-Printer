import sys
import os

if(os.path.exists(path := 'config.json')):
    with open(path, encoding='UTF-8') as f:
        data = f.read()
        print(data)
    
