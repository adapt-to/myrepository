#-*- coding:utf-8 -*-
'''
32位 python2.7.15(诱骗态可自定义)
'''
#import qrng_you_xin
import random_qrng # 伪随机测试
import time
import zmq
import logging
import os
import sys
import thread #多线程
MY_SOCKET_TIMEOUT = 1000

class Protocol(object):
    """实现bb84协议和cow协议的控制"""
    def __init__(self, region):   # region表示诱骗态占比
        self.region = region
        #self.list_1 = qrng_you_xin.receive_number(1) # 获取量子真随机数
        self.list_1 = random_qrng.random_qrng()  # 伪随机测试
        time.sleep(1)
        print 'input qrng successed'
    def jiesou_qrng(self):
        # self.list_1 = qrng_you_xin.receive_number(1)
        self.list_1 = random_qrng.random_qrng()
        time.sleep(3)
        print "qrng again = \n",self.list_1

    def panduan_qrng(self,l):
        if len(l) < 16:
            return 1
        else:
            return 0
    def trans(self,number):
        dic = {'0':'0000','1':'0001','2':'0010','3':'0011','4':'0100','5':'0101','6':'0110','7':'0111','8':'1000','9':'1001'}
        su = ''
        for i in number:
            su += dic[i]
        return su[::-1] # fpga倒序接收，所以这里倒序return

    # 将bb84_fpga列表中 每16个01代码 转换为 十六进制的字符型 并返回
    def bbb(self,list_2):
        self.list_2 = list_2
        j = 4
        bbbb=''
        while j:
            list_example = self.list_2[4*j-4:4*j]
            #for i in range(0,3):
            sum = list_example[0]*8+list_example[1]*4+list_example[2]*2+list_example[3]
            if sum < 10:
                bbbb += str(sum)
            else :
                switcher={10:'10',11:'11',12:'12',13:'13',14:'14',15:'15',}
                bbbb += switcher[sum]
            j -= 1
        #print "bbbb reverse = ",bbbb[::-1]
        return bbbb[::-1]     #  返回bbbb的反转字符串，因为上面的j是倒序给的

    # 将cow_fpga列表中 每16个01代码 转换为 十六进制的字符型 并返回
    def ccc(self,list_3):
        self.list_3 = list_3
        j = 4
        cccc=''
        while j:
            list_example = self.list_3[4*j-4:4*j]
            sum = list_example[0]*8+list_example[1]*4+list_example[2]*2+list_example[3]
            if sum < 10:
                cccc += str(sum)
            else :
                switcher={10:'0',11:'1',12:'2',13:'3',14:'4',15:'5',}
                cccc += switcher[sum]
            j -= 1
        #print "cccc reverse = ",cccc[::-1]
        return cccc[::-1] # 同bbbb

    def cow_number(self):
        cow_fpga = [x for x in range(1024)]
        j = 0
        for i in self.list_1:
            if i <= 127:
                cow_fpga[j] = 1
            else:
                cow_fpga[j] = 0
            j += 1
        #print "cow协议的随机的01代码为\n",cow_fpga
        return cow_fpga

    def bb84_number(self):
        bb84_fpga = [x for x in range(1024)]
        j = 0
        for i in self.list_1:
            if i <= 256 * self.region * 0.01:
                bb84_fpga[j] = 1  # 1表示触发诱骗态路的激光器发光
            elif i <= 255:
                bb84_fpga[j] = 0  # 0表示触发诱骗态路的激光器发光
            j += 1
        #print "bb84协议的随机的01代码为\n",bb84_fpga
        return bb84_fpga

# 与Easy-Phy建立连接        
class Slot_serial(object):
    def __init__(self, address, port):
        self.port = port
        self.address = address
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.REQ)
        self.socket.connect("tcp://%s:%s" % (self.address, self.port))
        self.poller = zmq.Poller()
        self.poller.register(self.socket, zmq.POLLIN)
    def __del__(self):
        pass
    def request_serial(self, message):
        try:
            self.socket.send(message)
        except zmq.ZMQError, s:
            self.socket.connect("tcp://%s:%s" % (self.address, self.port))
            print s
        '''
        timeout参数指定等待的毫秒数，无论I/O是否准备好，poll都会返回。
        timeout指定为负数值表示无限超时；
        timeout为0指示poll调用立即返回并列出准备好I/O的文件描述符，但并不等待其它的事件。
        这种情况下，poll()就像它的名字那样，一旦选举出来，立即返回。
        '''
        if self.poller.poll(MY_SOCKET_TIMEOUT):  # timeout in milliseconds
            text = self.socket.recv()
        else:
            text = ""
        return text

# log
class Slot_log():
    def __init__(self, file_name=None):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # create a file handler
        self.filename = os.path.splitext(os.path.basename(file_name))[0]
        self.filename = self.filename + '_' + \
                        time.strftime("%Y-%m-%d", time.localtime(time.time())) + '.log'
        self.handler = logging.FileHandler(self.filename, mode="w")
        self.handler.setLevel(logging.INFO)

        # create a logging format
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.handler.setFormatter(self.formatter)

        # add the handlers to the logger
        self.logger.addHandler(self.handler)



# UI 基于pyqt4（2.7.15  win32位）
from realize import *

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)


## con    
class Slot_con(QtGui.QWidget, Ui_Form):
    def __init__(self, address=None, port=None, parent=None):
        QtGui.QWidget.__init__(self, parent)
        self.setupUi(self)  # Ui_Form.setupUi
        self.logger = Slot_log(__file__)  # logging
        self.serialer = Slot_serial(address, port)
        self.calibration_status = False
        self.parameter_status = False
        #print "Slot_con init"

    def con_serial(self, message):
        a = self.tabWidget.currentIndex()

        starttime = time.strftime("%H:%M:%S - ", time.localtime(time.time()))
        # log window
        if a == 0:
            self.textBrowser_BB84_show.append(starttime + message)
            textcursor = QtGui.QTextCursor(self.textBrowser_BB84_show.textCursor())
            self.textBrowser_BB84_show.moveCursor(textcursor.atStart())
        elif a == 1:
            self.textBrowser_COW_show.append(starttime + message)
            textcursor = QtGui.QTextCursor(self.textBrowser_COW_show.textCursor())
            self.textBrowser_COW_show.moveCursor(textcursor.atStart())
        else:
            self.textBrowser_other_show.append(_translate("From", starttime + message, None))
            textcursor = QtGui.QTextCursor(self.textBrowser_other_show.textCursor())
            self.textBrowser_other_show.moveCursor(textcursor.atStart())
        # log file
        self.logger.logger.info(message)
        #text = ""
        text = self.serialer.request_serial(message)      

        try:
            text = unicode(text,'gb2312')
            text = text.encode('utf8')
        except:
            pass

        endtime = time.strftime("%H:%M:%S - ", time.localtime(time.time()))
        # log window
        if a == 0:
            self.textBrowser_BB84_show.append(endtime + text)
            textcursor = QtGui.QTextCursor(self.textBrowser_BB84_show.textCursor())
            self.textBrowser_BB84_show.moveCursor(textcursor.atStart())
        elif a == 1:
            self.textBrowser_COW_show.append(endtime + text)
            textcursor = QtGui.QTextCursor(self.textBrowser_COW_show.textCursor())
            self.textBrowser_COW_show.moveCursor(textcursor.atStart())
        else:
            self.textBrowser_other_show.append(_translate("From", endtime + text, None))
            textcursor = QtGui.QTextCursor(self.textBrowser_other_show.textCursor())
            self.textBrowser_other_show.moveCursor(textcursor.atStart())
        # log file
        self.logger.logger.info(text)
        return text

    #voa温度显示
    @QtCore.pyqtSignature("")
    def on_pushButton_att_t_clicked(self):
        answer = self.con_serial("MEASure:TEMPerature?")
        if answer != "":
            self.lineEdit_att_t.setText(_translate("From", answer, None))
      


    #设置voa衰减值
    # voa通道1 衰减设置 单通道范围为0-40dB
    @QtCore.pyqtSignature("")
    def on_pushButton_att_set_1_clicked(self):
        voa_1 = unicode(self.lineEdit_att_set_1.text(), 'utf8', 'ignore').encode('gb2312')
        answer = self.con_serial("CONFigure:VOA:CHannel" + " " + voa_1 + ",1")
    
    # voa通道2 衰减设置 单通道范围为0-40dB
    @QtCore.pyqtSignature("")
    def on_pushButton_att_set_2_clicked(self):
        voa_2 = unicode(self.lineEdit_att_set_2.text(), 'utf8', 'ignore').encode('gb2312')
        answer = self.con_serial("CONFigure:VOA:CHannel" + " " + voa_2 + ",2")

    """        
    # voa通道1 插损设置 0-5dB
    @QtCore.pyqtSignature("")
    def on_pushButton_insertloss_set_1_clicked(self):
        insert_1 = str(self.lineEdit_att_insertloss_1_show.text())
        answer_str_insert_1 = "CONFigure:INSErtloss:CHANnel" + " " + insert_1 + ",1"
        answer_insert_1 = answer_str_insert_1.encode('utf-8')
        answer = self.con_serial(answer_insert_1)

    # voa通道2 插损设置 0-5dB
    @QtCore.pyqtSignature("")
    def on_pushButton_insertloss_set_2_clicked(self):
        insert_2 = str(self.lineEdit_att_insertloss_2_show.text())
        answer_str_insert_2 = "CONFigure:INSErtloss:CHANnel" + " " + insert_2 + ",2"  #CHANnel
        answer_insert_2 = answer_str_insert_2.encode('utf-8')
        answer = self.con_serial(answer_insert_2)
    """        
    def COW_clicked(self):
        cow_sendfpga = bb84.cow_number()
        #print  "cow_sendfpga  = ：\n",cow_sendfpga
        while 1 :
            ii = bb84.panduan_qrng(cow_sendfpga)
            print 'in this time ,len = ：',len(cow_sendfpga)
            if ii == 1: # 数据小于16个
                print "\nlen < 16,receive qrng again\n"
                bb84.jiesou_qrng()
                cow_sendfpga = bb84.cow_number()
            elif ii == 0: # 数据大于16个
                print '\nlen > 16 ,pass\n'
                pass

            while 1:
                cow_data = bb84.ccc(cow_sendfpga[0:16])
                print 'cow_data =',cow_data
                fpga_cowwanbi = self.con_serial("CONFigure:RAND" + " " + cow_data + ",0")  # 接收FPGA发送的数据传输完毕的标志位 OK表示传输完毕 please wite 100ms表示还未完毕
                print '\nfpga_cowwanbi=',fpga_cowwanbi
                if fpga_cowwanbi == 'invalid value' or fpga_cowwanbi == ' ':
                    print "waiting 100ms"
                    time.sleep(0.1)
                    continue
                else :
                    time.sleep(0.9)
                    print '\nwrite in FPGA success,\nput the 0/1 write in .txt\n'
                    #list_cow = cow_sendfpga[0:16]
                    with open('D:/cow.txt', 'a') as f:
                        starttime_cow = time.strftime("%H:%M:%S - ", time.localtime(time.time()))
                        f.write(starttime_cow + bb84.trans(cow_data) + '\t')
                    print 'writer successed\n'
                    for aaa in range(16):
                        cow_sendfpga.pop(0)  # 删除已传入fpga的16个数
                    break  # 跳出内循环

    
    def BB84_clicked(self):
        bb84_sendfpga = bb84.bb84_number()
        #print "bb84_sendfpga = ：\n",bb84_sendfpga
        while 1:
            ii = bb84.panduan_qrng(bb84_sendfpga)
            print '\nin this time ,len = ：',len(bb84_sendfpga)
            if ii == 1:
                print "\nlen < 16,receive qrng again\n"
                bb84.jiesou_qrng()
                bb84_sendfpga = bb84.bb84_number()
            elif ii == 0:
                print '\nlen > 16 ,pass\n'
                pass

            while 1:
                bb84_data = bb84.bbb(bb84_sendfpga[0:16])
                print 'bb84_data = ',bb84_data
                fpga_bb84wanbi = self.con_serial("CONFigure:RAND" + " " + bb84_data + ",1")
                print '\nfpga_bb84wanbi = ',fpga_bb84wanbi
                #fpga_bb84wanbi='OK'
                if fpga_bb84wanbi == 'invalid value' or fpga_bb84wanbi == ' ':
                    print "please waiting 100ms"
                    time.sleep(0.2)
                    continue

                else :
                    #time.sleep(0.5)
                    print '\nwrite in FPGA success\nput the 0/1 write in .txt'
                    list_bb84 = bb84_sendfpga[0:16]
                    with open('D:/bb84.txt', 'a') as f:
                        starttime_bb84 = time.strftime("%H:%M:%S - ", time.localtime(time.time()))
                        f.write(starttime_bb84 + str(list_bb84[::-1]) + '\t')
                        print '\nwriter successed\n'
                    for aaa in range(16):
                        bb84_sendfpga.pop(0)  # 删除已传入fpga的16个数
                    break  # 跳出内循环


    
    #多线程处理bb84和cow
    @QtCore.pyqtSignature("")
    def on_pushButton_BB84_clicked(self):
        thread.start_new_thread (self.BB84_clicked,())

    @QtCore.pyqtSignature("")
    def on_pushButton_COW_clicked(self):
        thread.start_new_thread (self.COW_clicked,())           

    #laser通道口频率显示         
    @QtCore.pyqtSignature("")
    def on_pushButton_BB84_fre_clicked(self):  # 一个按钮只能对应一个槽
        ch1 = self.con_serial("CONFigure:TFReq? 1")# 查询通道1的频率
        ch2 = self.con_serial("CONFigure:TFReq? 2")# 查询通道2的频率
        if ch1 != "":
            self.lineEdit_BB84_ch1_fre.setText(_translate("Form", ch1, None))
        if ch2 != "":
            self.lineEdit_BB84_ch2_fre.setText(_translate("Form", ch2, None))
        
    #显示激光通道口温度
    # BB84下的查询
    @QtCore.pyqtSignature("")
    def on_pushButton_BB84_t_clicked(self):
        ch1 = self.con_serial("MEASure:LTEMperature? 1")  # 查询通道1的温度
        ch2 = self.con_serial("MEASure:LTEMperature? 2") # 查询通道2的温度
        if ch1 != "":
            self.lineEdit_BB84_ch1_t.setText(_translate("Form", ch1, None))
        if ch2 != "":
            self.lineEdit_BB84_ch2_t.setText(_translate("Form", ch2, None))

    # COW下的查询（仅查询通道1）
    @QtCore.pyqtSignature("")
    def on_pushButton_COW_t_clicked(self):
        ch1 = self.con_serial("MEASure:LTEMperature? 1")
        if ch1 != "":
            self.lineEdit_COW_ch1_t.setText(_translate("Form", ch1, None))

    @QtCore.pyqtSignature("")
    def on_pushButton_COW_fre_clicked(self):
        ch1 = self.con_serial("CONFigure:TFReq? 1")  # 查询通道1的频率
        if ch1 != "":
            self.lineEdit_COW_ch1_fre.setText(_translate("Form", ch1, None))
    #信号板无频率测量函数


   #信号板温度测量
    @QtCore.pyqtSignature("")
    def on_pushButton_sig_t_clicked(self):
        answer = self.con_serial("MEASure:TEMPerature?")
        if answer != "":
            self.lineEdit_sig_t.setText(_translate("From", answer, None))
#建立端口连接
class slot(QtGui.QMainWindow):
    def __init__(self, ui, address, port, tab):
        QtGui.QMainWindow.__init__(self)
        self.tab = tab
        self.tab_active = False
        self.empty = False

        self.logactive = 0
        self.resetactive = 0
        self.port = port
        self.address = address

    def initialize(self):
        return 1

    def on_timer(self): pass

    def graphical_intf(self):
        self.con = Slot_con(self.address, self.port, self.tab)
        self.con.setGeometry(QtCore.QRect(0, 0, 1355, 750))
        #self.con.show()

if __name__=="__main__":

    bb84 = Protocol(30) #诱骗态占比为30%，可自调
    app = QtGui.QApplication(sys.argv)

    widget = QtGui.QTabWidget()
    widget.resize(750, 500)
    
    widget_laser = QtGui.QTabWidget()
    widget_laser.setCurrentIndex(0)
    widget_laser.setCurrentIndex(1)
    #widget_laser

    widget_voa = QtGui.QTabWidget()
    widget_voa.setCurrentIndex(2)
    
    widget_voa.resize(750, 500)
    widget_laser.resize(750, 500)

    #wi = QtGui.QWidget()
    widget.addTab(widget_laser, "laser")
    widget.addTab(widget_voa, "voa")

    t_laser = QtGui.QFrame(widget_laser)
    t_laser.setGeometry(QtCore.QRect(0, 0, 1355, 750))


    t_voa = QtGui.QFrame(widget_voa)
    t_voa.setGeometry(QtCore.QRect(0, 0, 1355, 750))

    w_laser = slot(widget_laser, "192.168.2.200", "5569", t_laser) # 5559
    w_laser.graphical_intf()
    if w_laser.initialize():
        print "\nlaser open successed\n"
    else:
        pass

    w_voa = slot(widget_voa, "192.168.2.200", "5550", t_voa) # 填voa的端口
    w_voa.graphical_intf()
    if w_voa.initialize():
        print "voa open successed"
    else:
        pass

    widget.show()#显示窗口
    sys.exit(app.exec_())
