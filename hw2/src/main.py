import jpeg_encoder, jpeg_decoder
from utils import psnr
if __name__ == "__main__":
    specs =[
        {
        'img_path' : 'E:\programming\hw2\TestImages\ColorImages\BaboonRGB.raw',
        'img_size' : (512,512),
        'is_rgb' : True,
        'mode' : [2,2]
        },
        {
        'img_path' : 'E:\programming\hw2\TestImages\ColorImages\LenaRGB.raw',
        'img_size' : (512,512),
        'is_rgb' : True,
        'mode' : [2,2]
        },{
        'img_path' : 'E:\programming\hw2\TestImages\GrayImages\Baboon.raw',
        'img_size' : (512,512),
        'is_rgb' : False,
        'mode' : [2,2]
        },{
        'img_path' : 'E:\programming\hw2\TestImages\GrayImages\Lena.raw',
        'img_size' : (512,512),
        'is_rgb' : False,
        'mode' : [2,2]
        }
    ] 
    quality = [90,80,50,20,10,5]
    for spec in specs:
        for q in quality:
            img_name = spec['img_path'].split('\\')[-1].split('.')[0]
            image = jpeg_encoder.read_img(spec['img_path'],spec['img_size'],spec['is_rgb'])
            encoded_data = jpeg_encoder.encoding(**spec, quality=q)

            #save & read
            jpeg_fname = jpeg_encoder.save_result(encoded_data)
            data = jpeg_decoder.read_data(jpeg_fname)
            
            #解壓縮
            recovered_image = jpeg_decoder.extract(data, read_mode=1)
            #計算psnr
            cur_psnr = psnr(image, recovered_image)
            print('img_name: {}, quality : {}, psnr : {}'.format(img_name, q, cur_psnr))