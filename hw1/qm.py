import numpy as np
import matplotlib.pyplot as plt
import bit_plane
import os
import glob

class QM_Coder:

    class qmstatus:
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
    
    def __readQMTable(self):
        qf = 'D:\\Programming\\DataCompression\\hw1\\qmstatus'
        #找不到table就報錯
        if not os.path.exists(qf):
            raise IOError('{:s} does not exist.'.format(qf))

        with open(qf,'r') as f:
            for l in f.readlines():                
                curr = ''.join(l.rsplit('\n')).split(' ')
                temp = self.qmstatus(curr)
                self.qmtable.append(temp)
    def __findState(self, Qc, isInc) -> qmstatus:
        n = 0
        state = 0
        for i in self.qmtable:
            if i.qcHex == Qc:
                n = i.In if isInc else i.De
                if n == 'S':
                    return None
                n = -1*int(n) if not isInc else int(n)

                state = i.state +n
                return self.qmtable[state]
        raise 'not find next status'
    def encode(self,image,isGray):
        
        #如果是灰階圖就弄成位元平面
        if isGray:
            img = bit_plane.Util.gray2bitplane(image,(256,256))
            img = np.reshape(img,256*256*8)
        #如果本來就是二值影像就直接讀取
        else:
            img = np.fromfile(image,dtype=np.uint8)
            img = np.reshape(img,256*256)

        LPS,MPS = '0','1'
        State =0
        Qc=0x59EB #LMS prob
        A=0x10000
        C=0x0000
        CT=11 #C&A left shift count
        SC=0 #STACK COUNT
        BP=0
        result = ''
        
        for i in img:
            currInputBit = str(int(i))
            if currInputBit == MPS:
                A = A-Qc
                if A<0x8000:
                    if A<Qc:
                        C+=A
                        A=Qc
                    #change Qn state
                    newSatate = self.__findState(Qc, True)
                    if newSatate == None:
                        LPS,MPS=MPS,LPS
                    else:
                        State = newSatate.state                        
                        Qc = newSatate.qcHex
                    #renormalize
                    while A < 0x8000:
                        A<<=1
                        C<<=1
                        CT -=1
                        
                        if CT == 0:
                            #byte_out
                            t = C>>19
                            if t > 0xff:
                                BP+=1
                                #stuff 0
                                if BP == 0xff:
                                    result += '{0:b}'.format(BP)
                                    BP=0
                                
                                #output stacked zeros
                                while SC>0:
                                    result += '{0:b}'.format(BP)
                                    BP = 0
                                    SC-=1
                                result += '{0:b}'.format(BP)
                                BP = t
                            else:
                                if t == 0xff:
                                    SC+=1
                                else:
                                    #Output_stacked_0xffs
                                    while SC>0:
                                        result += '{0:b}'.format(BP)
                                        BP = 0xff
                                        result += '{0:b}'.format(BP)
                                        BP = 0
                                        SC-=1
                                    result += '{0:b}'.format(BP)
                                BP = t
                            C = C & 0x7ffff
                            CT = 8
                            
            if currInputBit == LPS:
                A = A-Qc
                if A>=Qc:
                    C+=A
                    A=Qc
                #change Qn state
                newSatate = self.__findState(Qc, False)

                if newSatate == None:
                    LPS,MPS=MPS,LPS
                else:
                    State = newSatate.state
                    Qc = newSatate.qcHex
                #renormalize
                while A < 0x8000:
                    A<<=1
                    C<<=1
                    CT -=1
                        
                    if CT == 0:
                        #byte_out
                        t = C>>19
                        if t > 0xff:
                            BP+=1
                            #stuff 0
                            if BP == 0xff:
                                result += '{0:b}'.format(BP)
                                BP=0
                                
                            #output stacked zeros
                            while SC>0:
                                result += '{0:b}'.format(BP)
                                BP = 0
                                SC-=1
                            result += '{0:b}'.format(BP)
                            BP = t
                        else:
                            if t == 0xff:
                                SC+=1
                            else:
                                #Output_stacked_0xffs
                                while SC>0:
                                    result += '{0:b}'.format(BP)
                                    BP = 0xff
                                    result += '{0:b}'.format(BP)
                                    BP = 0
                                    SC-=1
                                result += '{0:b}'.format(BP)
                            BP = t
                        C = C & 0x7ffff
                        CT = 8


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
        newf = '\\'.join(image.split('\\')[:-2]) + '\\result\\qm_compressed_' + image.split('\\')[-1].split('.')[0] + '.mumi'
        with open(newf, 'wb') as f:
            f.write(bytecode)

    def decode(self):
        pass
    
    
if __name__ == "__main__":
    basepath ='D:\\Programming\\DataCompression\\hw1'
    test_imgpath = glob.glob(basepath + '\\Data\\RAW\\*.raw')
    q = QM_Coder()
    for i in test_imgpath:
        isGray = False if '_b' in i or '_halftone' in i else True
        q.encode(i,isGray)
        
    
    
'''
    
    #壓縮前
        
    #壓縮後
    test_muimipath = glob.glob(basepath + '\\Data\\*.mumi')
    for i in test_muimipath:
        
    
''' 




