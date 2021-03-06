import numpy as np
import matplotlib.pyplot as plt
import bit_plane
import os
import glob

class QM_Coder:
    '''
        目前只有做qm encoder
    '''
    class qmstatus:
        '''
        用來存qm表的資料結構
        '''
        def __init__(self, args:list):
            self.state = int(args[0])
            self.qcHex = int(args[1],16)
            self.qcDec = float(args[2])
            self.In = args[3]
            self.De = args[4]
        def __str__(self):
            return str(self.state)
        def __repr__(self):
            return self.__str__()

    def __init__(self):
        self.qmtable = []
        self.__readQMTable()
        self.State =0
        self.Qc=0x59EB #LMS prob
        self.A=0x10000
        self.C=0x0000
        self.CT=11 #C&A left shift count
        self.SC=0 #STACK COUNT
        self.BP=0
        self.MPS='1'
        self.LPS='0'
    
    def __readQMTable(self):
        '''
            讀取qmtable
        '''
        qf = 'E:\\programming\\DataCompression\\hw1\\qmstatus'
        #找不到table就報錯
        if not os.path.exists(qf):
            raise IOError('{:s} does not exist.'.format(qf))
        with open(qf,'r') as f:
            for l in f.readlines():                
                curr = ''.join(l.rsplit('\n')).split(' ')
                temp = self.qmstatus(curr)
                self.qmtable.append(temp)
    def __ChangeState(self, isInc) -> qmstatus:
        '''
            查表改變qm的數值
            遇到S就conditional exchange
        '''
        for i in self.qmtable:
            if i.qcHex == self.Qc:
                n = i.In if isInc else i.De
                if n == 'S':
                    self.LPS,self.MPS=self.MPS,self.LPS        
                else:
                    n = -1*int(n) if not isInc else int(n)
                    self.State = i.state + n
                    self.Qc = self.qmtable[self.State].qcHex
                return 
        raise 'not find next status'
    #依照老師的參考資料 'qmimplement.pdf' 寫的
    def __renormalize_E(self, result:str):
        while self.A < 0x8000:
            self.A<<=1
            self.C<<=1
            self.CT-=1
            
            if self.CT == 0:
                #byte_out
                t = self.C>>19
                
                if t > 0xff:
                    self.BP+=1
                    #stuff 0
                    if self.BP == 0xff:
                        result += '{0:b}'.format(self.BP)
                        self.BP = 0
                    #output stacked zeros
                    while self.SC >0:
                        result += '{0:b}'.format(self.BP)
                        self.BP = 0
                        self.SC -=1
                    result += '{0:b}'.format(self.BP)
                    self.BP = t
                else:
                    if t == 0xff:
                        self.SC +=1
                    else:
                        while self.SC >0:
                            result += '{0:b}'.format(self.BP)
                            self.BP = 0xff
                            result += '{0:b}'.format(self.BP)
                            self.BP = 0
                            self.SC -=1
                        result += '{0:b}'.format(self.BP)
                        self.BP = t
                self.C &= 0x7ffff
                self.CT = 8
        return result
    def __saveEncodedFile(self,fn,result):
        #把少於8個bit的補完
        padbitnum = 8 - len(result) % 8
        padbit = ''
        for i in range(padbitnum):
            padbit+=''
        result = result + padbit
        #將code字串中的編碼用byte為單位加入bytearray後寫入檔案
        bytecode = bytearray()
        for i in range(0, len(result), 8):
            byte = result[i:i+8]
            bytecode.append(int(byte,2))
        newf = '\\'.join(fn.split('\\')[:-2]) + '\\result\\qm_compressed_' + fn.split('\\')[-1].split('.')[0] + '.peko'
        nf = newf.split('\\')[-1]
        print('file : {} compressed bitstream len:{}'.format(nf,len(result)))

        with open(newf, 'wb') as f:
            f.write(bytecode)

    def encode(self,image,fn,count):
        result = ''
        for i in image:
            currInputBit = str(int(i))
            if currInputBit == self.MPS:
                self.A = self.A-self.Qc
                if self.A<0x8000:
                    if self.A<self.Qc:
                        self.C+=self.A
                        self.A=self.Qc
                    #change Qn state
                    self.__ChangeState(True)
                    #renormalize
                    result = self.__renormalize_E(result)
                            
            if currInputBit == self.LPS:
                self.A = self.A-self.Qc
                if self.A>=self.Qc:
                    self.C+=self.A
                    self.A=self.Qc
                #change Qn state
                self.__ChangeState(False)
                #renormalize
                result = self.__renormalize_E(result)
        #存檔
        fn = fn.split('.')[0] + '_' + str(count) + '.raw'
        self.__saveEncodedFile(fn,result)

    def decode(self):
        '''
            之後課餘時間再來做
        '''
        pass
    
if __name__ == "__main__":
    basepath ='E:\\programming\\DataCompression'
    test_imgpath = glob.glob(basepath + '\\Data\\RAW\\*.raw')
    q = QM_Coder()
    for i in test_imgpath:
        if 'dpcm' in i :
            continue
        isGray = False if '_b' in i else True
        
        #如果是灰階圖就弄成位元平面
        if isGray:
            #分成八個圖片來編碼
            img = bit_plane.Util.gray2Nbitplane(i,(256,256))
            count = 0
            for j in img:
                count +=1
                j = np.reshape(j,256*256)
                q.encode(j,i,count)    
            #弄成8個channel來編碼
            img = bit_plane.Util.gray28Cbitplane(i,(256,256))
            img = np.reshape(img,256*256*8)
            q.encode(img,i,0)
        #如果本來就是二值影像就直接做處理
        else:
            img = np.fromfile(i,dtype=np.uint8)
            img = np.reshape(img,256*256)
            q.encode(img,i,1)