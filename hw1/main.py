import huffman
import dpcm
import numpy as np
import matplotlib.pyplot as plt
import glob

def rundpcm(raws):
    raws[:] = [x for x in raws if 'dpcm' not in x]
    for i in raws:
        if '_b' in i or '_halftone' in i:
            upbound, lowbound = 1, -1
            levels = 2
        else:
            upbound, lowbound = 255, -255
            levels = 8
        t = DPCM(i,levels,upbound,lowbound)
        t.encode()
        t.decode()
        t.show()


def runhuffman(raws):

    for i in raws:
        t = huffman.huffmanEncoder(i)
        t.encode()
    #壓縮後
    mumis = glob.glob(basepath + '\\Data\\result\\*.mumi')
    for i in mumis:
        decoder = huffman.huffmanDecoder(i)
        newf = decoder.saveAs()

if __name__ == "__main__":

    basepath ='E:\\programming\\DataCompression'
    #data
    raws = glob.glob(basepath + '\\Data\\RAW\\*.raw')
    raws[:] = [x for x in raws if 'dpcm' not in x]
    #使用dpcm
    rundpcm(raws)
    #使用霍夫曼壓縮
    raws = glob.glob(basepath + '\\Data\\RAW\\*.raw')
    runhuffman(raws)