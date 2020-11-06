import huffman
import dpcm
import numpy as np
import matplotlib.pyplot as plt
import qm
import glob
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
        if 'dpcm' in i :
            continue
        isGray = False if '_b' in i or '_halftone' in i else True
        q.encode(i,isGray)

def arg():
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