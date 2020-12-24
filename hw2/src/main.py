import jpeg_encoder, jpeg_decoder
import matplotlib.pyplot as plt
from utils import psnr
def show_recover_img(recover, img, psnr, img_name, q, is_rgb):

    fig, axes = plt.subplots(1,2)
    if is_rgb:
        axes[0].imshow(recover)
    else:
        axes[0].imshow(recover, cmap='gray')
    axes[0].set_title('recovered')

    if is_rgb:
        axes[1].imshow(img)
    else:
        axes[1].imshow(img, cmap='gray')

    axes[1].set_title('target')

    plt.suptitle(f'{img_name} quality : {q} psnr: { str(round(psnr,3))}')
    plt.show()
    
if __name__ == "__main__":
    specs =[
        {
        'img_path' : 'E:\programming\DataCompression\hw2\TestImages\GrayImages\Baboon.raw',
        'img_size' : (512,512),
        'is_rgb' : False,
        'mode' : [2]
        },{
        'img_path' : 'E:\programming\DataCompression\hw2\TestImages\GrayImages\Lena.raw',
        'img_size' : (512,512),
        'is_rgb' : False,
        'mode' : [2]
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
            #畫面比對
            show_recover_img(recovered_image.astype(int), image, cur_psnr, img_name, q, data[3])

            
            print('img_name: {}, quality : {}, psnr : {}'.format(img_name, q, cur_psnr))