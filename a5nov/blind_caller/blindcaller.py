# Author : isaac
# Email  : mkalafsaz@gmail.com
# Time   : Wed 26 Nov 2025 | 23:32:09

import os
import subprocess


def main():
    for i in range(0, 1000000):
        subprocess.run(['termux-telephony-call', f'*1*{i}#'])


#    for i in range (0,1000000):
#       subprocess.run(["termux-telephony-call",f"*10*{i}#"])
#  for i in range (0,1000000):
#     subprocess.run(["termux-telephony-call",f"*100*{i}#"])
# for i in range (0,1000000):
#     subprocess.run(["termux-telephony-call",f"*1000*{i}#"])

#    for i in range (0,1000000):
#       subprocess.run(["termux-telephony-call",f"*100*3*{i}#"])

if __name__ == '__main__':
    main()
