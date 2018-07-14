#-*- coding:utf-8 -*-
'''
注意事项：32位python才能调用32位的dll
32位python3.6.4测试成功

'''
from ctypes import *
'''
class QRNG_context(Structure):
    pass
'''
def receive_number(b):
    print("starting...")
    lib = CDLL('QRNG.dll')      
    #context = QRNG_context()
    context = lib.QRNG_init()
    a = lib.QRNG_set_data_address(context, 'ttyusb', None, 0xFFFF)
    if a != 0 :
        print("\nUSB open failed!\n")
    if context == None:
        print('-1')
    while 1:
        print('\nplease select item test:\n')
        print("1:read qrng data continu  0:exit\n")
        if b == 0:
            break
        elif b == 1:
            class POINT(Structure):
                _fields_ =[("x",c_char)]
            tmpBuf = POINT * 1024  # 通过修改数组的长度来指定输出的长度
            arr = tmpBuf()
            list_1 = [jj for jj in range(1024)]
            i=0
            if a == 0:
                for pt in arr:
                    rlen = lib.QRNG_data_receive(context,pt.x,1024,1024)
                    aaa=ord(pt.x) # 转为十进制 0~255
                    list_1[i]=aaa
                    i=i+1
                print(list_1)  # 打印随机数
                print('\nsuccessed,ret:%d\n' %rlen)
            elif a != 0:
                for pt in arr:
                    rlen = lib.QRNG_data_receive(context,pt.x,1024,1024)
                print('get data fail,ret:%d\n' %rlen)
            else:
                pass
            break
    if context != None:
        lib.QRNG_release(context)
        print('released QRNG_context!')
    return list_1


if __name__=="__main__":
    receive_number(1)
 
