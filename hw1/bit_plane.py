import numpy as np
import matplotlib.pyplot as plt
class Util:
    @staticmethod
    def gray2bitplane(filename:str, shape:tuple):
        '''
            shape -> (x,y)
        '''
        
        result = np.zeros((shape[0],shape[1],8))
        img = np.fromfile(filename, dtype=np.uint8)
        img = np.reshape(img,(shape[0],shape[1]))

        bit = 1
        for i in range(8):
            
            temp = np.bitwise_and(img,bit)
            temp = np.divide(temp,bit)
            result[:,:,i] = temp
            bit <<= 1
        return result
if __name__ == "__main__":
    result = Util.gray2bitplane('C:\\Users\\leeyihan\\Desktop\\hw\\datacompresshw1\\Data\\RAW\\baboon.raw',(256,256))
    print(np.shape(result))