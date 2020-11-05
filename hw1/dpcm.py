import numpy as np
import glob
import matplotlib.pyplot as plt
import cv2
class DPCM:
    def __init__(self, filename, levels,upbound,lowbound):
        self.filename = filename
        self.ori = None
        self.result = None
        self.levels= levels
        self.reconstruct = None
        self.alpha = 0.97
        self.beta = 0.97
        self.upbound = upbound
        self.lowbound = lowbound
        #print(self.filename)
    def encode(self):
        self.ori = np.fromfile(self.filename,dtype=np.uint8,count= 256*256)
        self.ori = np.reshape(self.ori, (256,256))

        newimg = np.zeros((256,256),dtype=np.uint8)
        predictor = np.zeros((256,256),dtype=np.uint8)
        for i in range(np.shape(self.ori)[0]):
            for j in range(np.shape(self.ori)[1]):
                if i == 0:
                    if j == 0:
                        yp =0
                    else:
                        yp =self.alpha*predictor[i][j-1]
                else:
                    yp =self.beta*predictor[i-1][j] + self.alpha*predictor[i][j-1] 

                error = self.ori[i][j] -yp
                #newimg[i][j] = np.uint8(error)
                newimg[i][j] = self.quantization_error(error,self.levels)
                predictor[i][j] = yp + newimg[i][j]
            
            for j in range(i+1,np.shape(self.ori)[1]):
                if i == 0:
                    yp =self.alpha*predictor[j-1][i]
                else:
                    yp =self.beta*predictor[j-1][i] + self.alpha*predictor[j][i-1] 

                error = self.ori[i][j] -yp
                newimg[j][i] = self.quantization_error(error,self.levels)
                predictor[j][i] = yp + newimg[j][i]
            
        self.result = newimg

    def decode(self):
        self.reconstruct = np.zeros((256,256), dtype=np.uint8)
        predictor = np.zeros((256,256),dtype=np.uint8)

        for i in range(np.shape(self.result)[0]):
            for j in range(np.shape(self.result)[1]):
                if i == 0:
                    if j == 0:
                        yp =0
                    else:
                        yp =self.alpha*predictor[i][j-1]
                else:
                    yp =self.beta*predictor[i-1][j] + self.alpha*predictor[i][j-1] 
                self.reconstruct[i][j] = self.result[i][j] + yp
                predictor[i][j] = self.reconstruct[i][j]
            
            for j in range(i+1,np.shape(self.result)[1]):
                if i == 0:
                    yp =self.alpha*predictor[j-1][i]
                else:
                    yp =self.beta*predictor[j-1][i] + self.alpha*predictor[j][i-1] 
                self.reconstruct[j][i] = self.result[j][i] + yp
                predictor[j][i] = self.reconstruct[j][i]
            
    def quantization_error(self,error,levels):
        '''
        均勻量化
        '''
        _max = self.upbound
        _min = self.lowbound
        q = (_max-_min)/levels
        i=1
        while error>= (_min+q*i):
            i+=1
        return _min+q*(i-1)+q/2

    def show(self):
        plt.figure(num=self.filename.split('\\')[-1],figsize=(8, 6))
        plt.subplot(131)
        plt.title('dpcm')
        plt.imshow(self.result,cmap='gray')
        plt.subplot(132)
        plt.title('reconstruct')
        plt.imshow(self.reconstruct,cmap='gray')
        plt.subplot(133)
        plt.title('original')
        plt.imshow(self.ori,cmap='gray')
        plt.show()

    def save(self):
        if self.result is not None:
            qfname = '\\'.join(self.filename.split('\\')[:-2]) + '\\raw\\dpcm_qerr_' + self.filename.split('\\')[-1].split('.')[0] + '.raw'
            qf = np.reshape(self.result,(256*256)) 
            with open(qfname,'wb') as f:
                for i in qf:
                    f.write(int(i).to_bytes(1, byteorder='big'))

        if self.reconstruct is not None:
            rfname = '\\'.join(self.filename.split('\\')[:-2]) + '\\raw\\dpcm_recostruct_' + self.filename.split('\\')[-1].split('.')[0] + '.raw'
            rf = np.reshape(self.reconstruct,(256*256)) 
            with open(rfname,'wb') as f:
                for i in rf:
                    f.write(int(i).to_bytes(1, byteorder='big'))
        
        
if __name__ == "__main__":
    basepath ='E:\\programming\\DataCompression'
    #data
    raws = glob.glob(basepath + '\\Data\\RAW\\*.raw')
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
