#_*_ coding:utf-8 _*_

import random

def random_qrng():
    list_1 = [x for x in range(1024)]
    for i in range(1024):
        list_1[i] = random.randint(0,255)
    return list_1
if __name__ == "__main__":
    random_qrng()
