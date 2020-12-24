import numpy as np
import matplotlib.pyplot as plt
from utils import (rgb2ycbcr, ycbcr2rgb, CHROMINANCE, LUMINANCE, downsample, 
                    block_slice, dct2d, quantize, EOB, ZRL,
                    HUFFMAN_CATEGORIES, HUFFMAN_CATEGORY_CODEWORD, ZIGZAG_ORDER
                    )
#方便寫程式用
Y,Cb,Cr = 'Y','Cb','Cr'
DC,AC='DC','AC'

def read_img(img_path, size, is_rgb):
    '''
        對應圖片的色階來讀取影像
    '''
    return np.fromfile(img_path, dtype=np.uint8).reshape(size if not is_rgb else (*size, 3))

def show_img(img):
    '''
        顯示影像
    '''
    plt.imshow(img)
    plt.show()

def dc_encoding(blocks, channel_type):
    '''
        對dc部分編碼
    '''

    def index_2d(table, target):
        '''
            查表 取idx回傳
        '''
        for i, row in enumerate(table):
            for j, element in enumerate(row):
                if target == element:
                    return (i, j)
        raise ValueError('Cannot find the target value in the table.')
    
    dc_diff_list = [] #用來儲存所有的差值
    blocks = blocks.reshape(-1,8*8) #為了方便先reshape
    for idx, block in enumerate(blocks):
        '''
            第一個值直接塞進去，之後就計算和前面一個位置的數值的差值
        '''
        if idx == 0:
            dc_diff_list.append(block[0])
        else:
            #now = now - previous
            dc_diff_list.append(block[0] - blocks[idx-1][0])
    
    dc_result = '' #紀錄已經被編碼的部分

    '''
        遍歷所有差值，查表寫入dc_result
    '''
    for diff_value in dc_diff_list:
        
        if diff_value >= 2048 or diff_value <= -2048: #不能超過範圍
            raise ValueError('diff value should be within [-2047, 2047]')
        size, fixed_code_idx = index_2d(HUFFMAN_CATEGORIES, diff_value)

        if size == 0:
            dc_result += HUFFMAN_CATEGORY_CODEWORD[DC][channel_type][size]
        else:
            dc_result += (HUFFMAN_CATEGORY_CODEWORD[DC][channel_type][size]
                + '{:0{padding}b}'.format(fixed_code_idx, padding=size))
    return dc_result

def ac_encoding(blocks, channel_type):
    def pair2code(pair):
        '''
            用run和nonzero查表然後寫入編碼
        '''
        def index_2d(table, target):
            '''
                用nonzero查表
            '''
            for i, row in enumerate(table):
                for j, element in enumerate(row):
                    if target == element:
                        return (i, j)
            raise ValueError('Cannot find the target value in the table.')

        value = tuple(pair)
        if value in (EOB, ZRL):
            return HUFFMAN_CATEGORY_CODEWORD[AC][channel_type][value]

        run, nonzero = value
        if nonzero == 0 or nonzero <= -1024 or nonzero >= 1024:
            raise ValueError(
                f'AC coefficient nonzero {value} should be within [-1023, 0) '
                'or (0, 1023].'
            )

        size, fixed_code_idx = index_2d(HUFFMAN_CATEGORIES, nonzero)
        return (HUFFMAN_CATEGORY_CODEWORD[AC][channel_type][(run, size)]
                + '{:0{padding}b}'.format(fixed_code_idx, padding=size))
    ac_result = '' #紀錄結果
    for block_idx, block in enumerate(blocks):
        #runlenght encoding

        flatten_block = block.reshape(8*8) #為了方便先Reshape
        zero_count = 0 #紀錄已經經過了幾個0
        for zig_idx in ZIGZAG_ORDER: #查表進行zigzag的遍歷
            if zig_idx == 0: #如果是第一個(dc)就跳過
                continue
            if flatten_block[zig_idx] == 0:
                zero_count = zero_count + 1 #遇到0就增加counter
                if zero_count > 15: #超過15個0就是zrl
                    ac_result += pair2code(ZRL)    
                    #同時重製counter
                    zero_count = 0
            else:
                #查表填入編碼然後重製counter
                ac_result += pair2code((zero_count, flatten_block[zig_idx]))
                zero_count = 0
        #最後加入eob
        ac_result += pair2code(EOB)
    return ac_result

def save_result(data):
    img_path, img_size, quality, mode, is_rgb, dc_data, ac_data, block_num  = data.values()

    '''
        8bit quality
        8bit image hegiht, 
        8bit image width, 
        8bit y block count, 
        8bit cb block count, 
        8bit cr block count, 
        8bit samplemode 1: 22 2: 21 3: 12 4: 11
        y dc, 
        y ac, 
        cb dc, 
        cb ac, 
        cr dc, 
        cr ac
    '''
    outputf = 'E:\\programming\\DataCompression\\hw2\\result\\' + img_path.split('\\')[-1].split('.')[0] + f'_{quality}_' + '.mumijpg'
    with open(outputf, 'wb') as output:
        output.write((quality).to_bytes(4,byteorder='big')) #七個位元組

        output.write(img_size[0].to_bytes(4,byteorder='big')) #影像的height
        output.write(img_size[1].to_bytes(4,byteorder='big')) #影像的width

        output.write(block_num[Y].to_bytes(4,byteorder='big')) #y的block數
        if is_rgb:
            output.write(block_num[Cb].to_bytes(4,byteorder='big')) #cb的block數
            output.write(block_num[Cr].to_bytes(4,byteorder='big')) #cr的block數

        output.write(len(dc_data[Y]).to_bytes(4,byteorder='big')) #y dc code長度
        output.write(len(ac_data[Y]).to_bytes(4,byteorder='big')) #y ac code長度

        if is_rgb:
            output.write(len(dc_data[Cb]).to_bytes(4,byteorder='big')) #cb dc code長度
            output.write(len(ac_data[Cb]).to_bytes(4,byteorder='big')) #cb ac code長度

            output.write(len(dc_data[Cr]).to_bytes(4,byteorder='big')) #cr dc code長度
            output.write(len(ac_data[Cr]).to_bytes(4,byteorder='big')) #cr ac code長度
        else:
            output.write((0).to_bytes(4,byteorder='big')) 
            output.write((0).to_bytes(4,byteorder='big')) 
            output.write((0).to_bytes(4,byteorder='big')) 
            output.write((0).to_bytes(4,byteorder='big'))

        #samplemode
        
        if mode == [2,2]:
            output.write((1).to_bytes(4,byteorder='big')) 
        elif mode == [2,1]:
            output.write((2).to_bytes(4,byteorder='big')) 
        elif mode == [1,2]:
            output.write((3).to_bytes(4,byteorder='big')) 
        elif mode == [1,1]:
            output.write((4).to_bytes(4,byteorder='big')) 
        elif mode == [1]:
            output.write((5).to_bytes(4,byteorder='big')) 
        elif mode == [2]:
            output.write((6).to_bytes(4,byteorder='big'))
        
        if is_rgb:
            ch_set = ['Y', 'Cb', 'Cr']
        else:
            ch_set = ['Y']
        for ch in ch_set:
            
            for i in range(8 - len(dc_data[ch]) % 8):
                dc_data[ch] += '0'
            for i in range(8 - len(ac_data[ch]) % 8):
                ac_data[ch] += '0'

            dccode = bytearray()
            for i in range(0, len(dc_data[ch]), 8):
                byte = dc_data[ch][i:i+8]
                dccode.append(int(byte,2))
            output.write(dccode)

            accode = bytearray()
            for i in range(0, len(ac_data[ch]), 8):
                byte = ac_data[ch][i:i+8]
                accode.append(int(byte,2))
            output.write(accode)
    return outputf
    
def encoding(img_path, img_size, is_rgb, mode, quality):
    '''
        return          'img_path' : img_path,
                        'img_size' : img_size,
                        'quality' : quality,
                        'mode' : mode,
                        'is_rgb' : is_rgb,
                        'dc_data' :dc_data,
                        'ac_data' :ac_data,
                        'block_num' : block_num

    '''
    #檢查 quality
    if quality <= 0 or quality > 95:
        raise ValueError('Quality should within (0, 95].')

    #讀取檔案
    raw_data = read_img(img_path, img_size, is_rgb)
    if is_rgb:
        #轉換成 y, cb, cr
        data = rgb2ycbcr(raw_data[:,:,0],raw_data[:,:,1],raw_data[:,:,2])

        # Subsampling
        data[Cb] = downsample(data[Cb], mode[0])
        data[Cr] = downsample(data[Cr], mode[1])

    else:  # gray scale
        data = {Y: raw_data.astype(float)}
    # Level Offset
    data[Y] = data[Y] - 128
    block_num = {}
    #分割成 8*8
    for key, channel in data.items():
        nrows, ncols = channel.shape

        # Pad Layers to 8N * 8N
        data[key] = np.pad(
            channel,
            (
                (0, (nrows // 8 + 1) * 8 - nrows if nrows % 8 else 0),
                (0, (ncols // 8 + 1) * 8 - ncols if ncols % 8 else 0)
            ),
            mode='constant'
        )

        # Block Slicing
        data[key] = block_slice(data[key], 8, 8)
        block_num[key] = len(data[key])
        for idx, block in enumerate(data[key]):
            # 2D DCT
            data[key][idx] = dct2d(block)

            # Quantization
            data[key][idx] = quantize(data[key][idx], key, quality=quality, inverse=False)
        # Rounding
        data[key] = np.rint(data[key]).astype(int)

    #Entropy coding
    dc_data = {}
    ac_data = {}
    for key, channel_blocks in data.items():
        #dc encoding
        dc_data[key] = dc_encoding(channel_blocks, key if key == LUMINANCE else CHROMINANCE)
        #ac encoding
        ac_data[key] = ac_encoding(channel_blocks, key if key == LUMINANCE else CHROMINANCE)

    return {
        'img_path' : img_path,
        'img_size' : img_size,
        'quality' : quality,
        'mode' : mode,
        'is_rgb' : is_rgb,
        'dc_data' :dc_data,
        'ac_data' :ac_data,
        'block_num' : block_num
    }