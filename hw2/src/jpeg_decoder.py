import numpy as np
import matplotlib.pyplot as plt
import jpeg_encoder
from utils import (rgb2ycbcr, ycbcr2rgb, CHROMINANCE, LUMINANCE, upsample, 
                    block_combine, idct2d, quantize, EOB, ZRL,
                    HUFFMAN_CATEGORIES, HUFFMAN_CATEGORY_CODEWORD, ZIGZAG_ORDER
                    )
Y,Cb,Cr = 'Y','Cb','Cr'
DC,AC='DC','AC'
def dc_decoding(dc_code, channel_type, max_len):
    dc_diff_data = [] #記錄所有差值
    target_table = HUFFMAN_CATEGORY_CODEWORD['DC'][channel_type].inv #反向查表
    '''
        利用一個暫存器紀錄每個bit之後，查表有查到就加入dc差值的集合。
    '''
    buffer = '' 
    idx = 0 
    while True:
        if idx >= max_len: #不能超過整串字元的大小
            break
        #將當下的字元加入buffer
        buffer+= dc_code[idx]

        if buffer in target_table:
            size = target_table[buffer]
            if size != 0: #size不為0 插入集合
                diff = int(dc_code[idx+1: idx+size+1], 2)
                dc_diff_data.append(HUFFMAN_CATEGORIES[size][diff])
                idx = idx + size 
            else:
                # 發現是0 插入0
                dc_diff_data.append(0)            
            #只要有差入數值就清空buffer
            buffer = ''
        #每次走一步
        idx = idx + 1
    #將差值還原為dc
    dc_data = []
    for idx, d in enumerate(dc_diff_data):
        if idx == 0: #第一個原封不動
            dc_data.append(d)
        else: #其他加回來
            dc_data.append(dc_diff_data[idx]+ dc_data[idx-1])
    return dc_data

def ac_decoding(ac_code, channel_type, max_len):
    #解碼ac_code
    temp = [] #暫存當下解出來的rle pair
    rle_list = [] #存放所有的rle
    target_table = HUFFMAN_CATEGORY_CODEWORD[AC][channel_type].inv #反向查表
    '''
        利用一個暫存器每次存進一個bit，然後拿去查表，有就插入數值
    '''
    buffer = '' 
    idx = 0
    while True:

        if idx >= max_len : #不能超過字串大小
            break
        buffer+= ac_code[idx] #把bit加入buffer
        
        '''
            查到字元的情況下如果是eob或zrl的話idx不用移動，是eob就換下一個rle，
            其餘狀況移動idx取得ac code然後都解出來
        '''
        if buffer in target_table: 
            run, size = target_table[buffer]
            if (run,size) == (0,0):
                rle_list.append(temp)
                temp = []
            elif (run, size) == (15,0):
                temp.append(ZRL)
            else:
                diff_code = int(ac_code[idx +1: idx+ size +1],2)
                nonzero = HUFFMAN_CATEGORIES[size][diff_code]
                temp.append((run, nonzero))
                idx += size
            buffer = ''

        idx += 1
    #利用runlength code重建block
    blocks = np.zeros((len(rle_list),64))
    for rle_idx, rle in enumerate(rle_list):
        idx = 1
        for pair in rle:
            #開始解rle
            run, nonzero = pair
            if run == 0:
                zigzag_idx = ZIGZAG_ORDER[idx]
                blocks[rle_idx][zigzag_idx] = nonzero
            else:
                idx = idx + run
                zigzag_idx = ZIGZAG_ORDER[idx]
                blocks[rle_idx][zigzag_idx] = nonzero
            idx = idx + 1
    return blocks

def read_data(img_path):
    image_h = 0
    image_w = 0

    ac_code = {}
    dc_code = {}

    with open(img_path,'rb') as input_f:

        quality = int.from_bytes(input_f.read(4),byteorder='big')

        image_h = int.from_bytes(input_f.read(4),byteorder='big')
        image_w = int.from_bytes(input_f.read(4),byteorder='big')
        img_size = (image_h, image_w)

        y_block_count = int.from_bytes(input_f.read(4),byteorder='big')
        cb_block_count = int.from_bytes(input_f.read(4),byteorder='big')
        cr_block_count = int.from_bytes(input_f.read(4),byteorder='big')
        block_num = {}
        block_num[Y] = y_block_count
        block_num[Cb] = cb_block_count
        block_num[Cr] = cr_block_count

        y_dc_len = int.from_bytes(input_f.read(4),byteorder='big')
        y_ac_len = int.from_bytes(input_f.read(4),byteorder='big')
        cb_dc_len = int.from_bytes(input_f.read(4),byteorder='big')
        cb_ac_len = int.from_bytes(input_f.read(4),byteorder='big')
        cr_dc_len = int.from_bytes(input_f.read(4),byteorder='big')
        cr_ac_len = int.from_bytes(input_f.read(4),byteorder='big')
        # code len set
        dc_code_len = {}
        dc_code_len[Y] = y_dc_len
        dc_code_len[Cb] = cb_dc_len
        dc_code_len[Cr] = cr_dc_len
        ac_code_len = {}
        ac_code_len[Y] = y_ac_len
        ac_code_len[Cb] = cb_ac_len
        ac_code_len[Cr] = cr_ac_len
        code_len = [dc_code_len, ac_code_len]
        mode = int.from_bytes(input_f.read(4), byteorder='big')
        if mode in [5,6]:
            is_rgb = False
        else:
            is_rgb = True

        '''
            order 
                y dc
                y ac
                cb dc
                cb ac
                cr dc
                cr ac
        '''
        buffer = ''
        curLen = 0
        while True :
            curbyte = input_f.read(1)
            if curbyte == b'':
                break
            buffer += format(int(curbyte.hex(),16), '08b')
        #將各個部份的位元字串分開來
        len_accum = 0
        if is_rgb:
            ch_set = ['Y', 'Cb', 'Cr']
        else:
            ch_set = ['Y']
        for ch in ch_set:
            padding_len = dc_code_len[ch] + (8-dc_code_len[ch]%8)
            dc_code[ch] = buffer[len_accum:padding_len+len_accum]
            len_accum += padding_len
            
            padding_len = ac_code_len[ch] + (8-ac_code_len[ch]%8)
            ac_code[ch] = buffer[len_accum:padding_len+len_accum]
            len_accum += padding_len

    return img_size, quality, mode, is_rgb, dc_code, ac_code, block_num, code_len, img_path

def get_samplemode (mode):
    if mode == 5:
        return [1]
    elif mode == 6:
        return [2]
    elif mode == 1:
        return [2,2]
    elif mode == 2:
        return [2,1]
    elif mode == 3:
        return [1,2]
    elif mode == 4:
        return [1,1]
    else:
        return None


def extract(data, read_mode):
    def school_round(val):
        if float(val) % 1 >= 0.5:
            return math.ceil(val)
        return round(val)
    '''
        read_mode = 0 從ram直接讀
                  = 1 從檔案讀
    '''
    if read_mode == 0:
        img_size, quality, mode, is_rgb, dc_data, ac_data, block_num, img_path= (data).values()
        dc_code_len = {}
        ac_code_len = {}
        if is_rgb:
            
            dc_code_len[Y] = dc_data[Y]
            dc_code_len[Cb] = dc_data[Cb]
            dc_code_len[Cr] = dc_data[Cr]
            ac_code_len[Y] = ac_data[Y]
            ac_code_len[Cb] = ac_data[Cb]
            ac_code_len[Cr] = ac_data[Cr]
        else:
            dc_code_len[Y] = dc_data[Y]
            ac_code_len[Y] = ac_data[Y]
    elif read_mode == 1:
        img_size, quality, mode, is_rgb, dc_data, ac_data, block_num, code_len, img_path = data
        dc_code_len, ac_code_len = code_len
    else:
        raise ValueError('readmode should within [0,1]')

    mode = get_samplemode(mode)
    # Calculate the size after subsampling.
    subsampled_size = []
    for idx,m in enumerate(mode):
        subsampled_size.append((img_size[0] if mode[idx] == 2 else school_round(img_size[0] / 2),
                            school_round(img_size[1] / 2)))
            

    output_path = 'E:\\programming\\hw2\\result\\' + img_path.split('\\')[-1].split('.')[0] + 'mumijpg'
    dc_decoded_data = {}
    ac_decoded_data = {}
    decoded_data = {}

    #dc decoding
    for key, dc in dc_data.items():
        dc_decoded_data[key] = dc_decoding(dc, key if key == LUMINANCE else CHROMINANCE, dc_code_len[key])
    #ac decoding
    for key, ac in ac_data.items():
        ac_decoded_data[key] = ac_decoding(ac, key if key == LUMINANCE else CHROMINANCE, ac_code_len[key])
    
    #combine dc,ac
    for key, ac_decoded in ac_decoded_data.items():
        for idx, dc in enumerate(dc_decoded_data[key]):
            ac_decoded_data[key][idx][0] = dc
        decoded_data[key] = ac_decoded_data[key].reshape(-1,8,8)

    #inverse quantization and inverse dct
    for key, blocks in decoded_data.items():
        for idx, block in enumerate(blocks):
            #inverse quantization
            decoded_data[key][idx] = quantize(block, key, quality, True)
            #idct 2d
            decoded_data[key][idx] = idct2d(block)
        decoded_data[key] = np.rint(decoded_data[key]).astype(int)
        #combine sliced blocks

        # Calculate the size after subsampling and padding.

        if key == Y:
            padded_size = ((s // 8 + 1) * 8 if s % 8 else s for s in img_size)
        else:
            padded_size = ((s // 8 + 1) * 8 if s % 8 else s for s in subsampled_size[CHROMINANCE.index(key)])
        decoded_data[key] = block_combine(blocks, *padded_size)

    #inverse level offset
    decoded_data['Y'] = decoded_data['Y'] + 128
    #convert y cb cr space to r g b space
    # Clip Padded Image
    decoded_data[Y] = decoded_data[Y][:img_size[0], :img_size[1]]
    if is_rgb:
        decoded_data[Cb] = decoded_data[Cb][:subsampled_size[0][0], :subsampled_size[0][1]]
        decoded_data[Cr] = decoded_data[Cr][:subsampled_size[1][0], :subsampled_size[1][1]]

        # Upsampling and Clipping
        decoded_data[Cb] = upsample(decoded_data[Cb], mode[0])[:img_size[0], :img_size[1]]
        decoded_data[Cr] = upsample(decoded_data[Cr], mode[1])[:img_size[0], :img_size[1]]

        # Color Space Conversion
        decoded_data = ycbcr2rgb(decoded_data[Y],decoded_data[Cb],decoded_data[Cr])
    #show decompressed image
    img = np.zeros((*img_size, 3) if is_rgb else (img_size[0],img_size[1]))
    if is_rgb:
        img[:,:,0] = decoded_data['r']
        img[:,:,1] = decoded_data['g']
        img[:,:,2] = decoded_data['b']
    else:
        img = decoded_data[Y]
    return img