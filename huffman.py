import heapq
import numpy as np
import glob
import matplotlib.pyplot as plt
class t_node:
    def __init__(self, freq, symbol):
        self.freq = freq
        self.symbol = symbol
        self.leftnode = None
        self.rightnode = None
    def __gt__(self, other) -> bool:
        return self.freq > other.freq
    def __eq__(self, other) -> bool:
        return self.freq == other.freq
    def __lt__(self, other) -> bool:
        return self.freq < other.freq
    def __str__(self):
        return str(self.symbol)
    def __repr__(self):
        return str(self.symbol)
        
class huffmanEncoder:
    def __init__(self, filename):

        self.root = None
        self.data = []
        self.filename = filename
        self.table = {}

        self.__initTree()
        
    def __readRaw(self):
        image = np.fromfile(self.filename, dtype='uint8', count=256*256)
        return image
    
    def __initTree(self):
        img = self.__readRaw()
        data = {}
        #計算每個symbol的總數
        for i in img:
            if i in data:
                data[i] +=1
            else:
                data[i] = 1
        
        #轉換成node
        for idx,i in data.items():
            self.data.append(t_node(i,idx))
            self.table[idx] = ''
        #轉成heap方便排序
        heapq.heapify(self.data)
        while len(self.data)>1:
            #pop出最小的兩個然後組合再一起
            s1 = heapq.heappop(self.data)
            s2 = heapq.heappop(self.data)
            #internal node的symbol設定為-1
            newNode = t_node(s1.freq+s2.freq, -1)
            newNode.leftnode=s1
            newNode.rightnode=s2
            heapq.heappush(self.data,newNode)
        #最後剩下的是root
        self.root = self.data[0]
        #建立table
        self.setCodeTable(self.root,'')
        #去掉internal symbol
        del self.table[-1]

    def setCodeTable(self, node: t_node, code):
        #用遞迴的方法從root開始記錄每個symbol的Code
        if node.leftnode is not None:
            self.setCodeTable(node.leftnode,'0'+code)
        if node.rightnode is not None:
            self.setCodeTable(node.rightnode,'1'+code)
        #如果是葉子節點就將code寫入table
        self.table[node.symbol] = code
        return

    def encode(self):
        code = ''

        #開啟影像
        with open(self.filename, 'rb') as f:
            #每次讀取1KB後從Table找code再接成字串
            byte = f.read(1)
            while byte:
                code += self.table[int.from_bytes(byte, byteorder='big')]
                byte = f.read(1)
        #設定新擋名
        newf = '\\'.join(self.filename.split('\\')[:-2]) + '\\result\\' + self.filename.split('\\')[-1].split('.')[0] + '.mumi'

        #把少於8個bit的補完
        padbitnum = 8 - len(code) % 8
        padbit = ''
        for i in range(padbitnum):
            padbit+=''
        code = code + padbit

        #將code字串中的編碼用byte為單位加入bytearray後寫入檔案
        bytecode = bytearray()
        for i in range(0, len(code), 8):
            byte = code[i:i+8]
            bytecode.append(int(byte,2))
        with open(newf, 'wb') as f:
            f.write(bytecode)
        
        

        

if __name__ == "__main__":
    test_imgpath = glob.glob('C:\\Users\\leeyihan\\Desktop\\hw\\datacompresshw1\\Data\\RAW\\*.raw')
    t = huffmanEncoder(test_imgpath[2])
    t.encode()
    
    for i in test_imgpath:
        t = huffmanEncoder(i)
        t.encode()
    

    