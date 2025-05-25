import sys
import os
import json

def getBlutoothMac():
    if (os.path.exists(path := 'config.json')):
        with open(path, encoding='UTF-8') as f:
            data = f.read()
            try:
                m = json.loads(data)
                return m.get('BTMAC')
            except:
                return None;
    else:
        print('Config file not found')

