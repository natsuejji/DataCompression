import huffman
import dpcm
import numpy as np
import matplotlib.pyplot as plt
import qm
import glob
import bit_plane
import argparse

def rundpcm(raws):
    print("開始執行dpcm")
    raws[:] = [x for x in raws if 'dpcm' not in x]
    for i in raws:
        if '_b' in i or '_halftone' in i:
            upbound, lowbound = 1, -1
            levels = 2
        else:
            upbound, lowbound = 255, -255
            levels = 8
        t = dpcm.DPCM(i,levels,upbound,lowbound)
        t.encode()
        t.decode()
        t.save()

def runhuffman(raws):
    print("開始執行霍夫曼壓縮")
    for i in raws:
        if 'reconstruct' in i :
            continue
        
        t = huffman.huffmanEncoder(i)
        t.encode()
    #壓縮後
    mumis = glob.glob(basepath + '\\Data\\result\\*.mumi')
    for i in mumis:
        decoder = huffman.huffmanDecoder(i)
        newf = decoder.saveAs()

def runqmencoder(raws):
    print("開始執行qmencoder")
    q = qm.QM_Coder()
    for i in raws:
        if 'dpcm' in i or '_compressed' in i:
            continue
        isGray = False if '_b' in i or '_halftone' in i else True
        
        #如果是灰階圖就弄成位元平面
        if isGray:
            img = bit_plane.Util.gray2Nbitplane(i,(256,256))
            count = 0
            for j in img:
                count +=1
                j = np.reshape(j,256*256)
                q.encode(j,i,count)    
            img = bit_plane.Util.gray28Cbitplane(i,(256,256))
            img = np.reshape(img,256*256*8)
            q.encode(img,i,0)
        #如果本來就是二值影像就直接讀取
        else:
            img = np.fromfile(i,dtype=np.uint8)
            img = np.reshape(img,256*256)
            q.encode(img,i,1)
def arg():
    '''
        設定argument parser
        rootpath是整個專案的根目錄，要用來存取圖片用的
    '''
    parser = argparse.ArgumentParser(description='ncu data compression hw1')
    parser.add_argument("--rootpath", help="project root directory",required=True)
    return parser

if __name__ == "__main__":
    parser = arg()
    args = parser.parse_args()

    basepath = args.rootpath
    #data
    raws = glob.glob(basepath + '\\Data\\RAW\\*.raw')
    #使用dpcm
    rundpcm(raws)
    #使用霍夫曼壓縮
    raws = glob.glob(basepath + '\\Data\\RAW\\*.raw')
    runhuffman(raws)
    runqmencoder(raws)