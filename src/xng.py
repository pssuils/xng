from PIL import Image
import cStringIO
import base64
from os import listdir
from os.path import join
from math import floor
from optparse import OptionParser

SVG = "<svg xmlns='http://www.w3.org/2000/svg' xmlns:A='http://www.w3.org/1999/xlink' width='640' height='360'>\n%s</svg>"
IMAGE_DATA = "<image id='%s'  height='100%%' A:href='data:image/png;base64,%s'/>\n"
IMAGE_SET_FIRST = "<set A:href='#%s' id='A%s' attributeName='width' to='100%%' dur='%sms' begin='A%s.end; 0s'/>\n"
IMAGE_SET = "<set A:href='#%s' id='A%s' attributeName='width' to='100%%' dur='%sms' begin='A%s.begin+%sms'/>\n"
IMAGE_SET_KEY = "<set A:href='#%s' id='A%s' attributeName='width' to='100%%' dur='%sms' begin='A%s.end'/>\n"
ZERO = (0,0,0,0)

class ImageData:
    """ Image plus some metadata """
    def __init__(self, path):
        self.data=Image.open(path)
        self.data.convert("RGBA")#make sure that we we have alpha channel
        self.data.putalpha(255)# and make it non transparent
        self.duration=0 # duration of the image
        self.begin=0 #when this image begins
        self.key=None #the key frame for this image


    def encode64(self):
        """ returns the images as a png enconded in base64 """
        buf=cStringIO.StringIO()
        self.data.save(buf,format="PNG",mode="RGBA")
        return base64.encodestring(buf.getvalue())

class Transform:
    """ 
        Transforms the list of images compressing the images based on the 
        key frame
    """ 

    def __init__(self, images,keyframe,duration,threshold):
        self.images=images #list of images
        self.keyframe=keyframe #keyframe ratio
        self.threshold=threshold #threshold (0-255) 
        self.duration=duration #duration of the images
    
    def transform(self):
        """ iterate throught the images seting to transparent those
            pixels whose difference with the key frame  is less 
            than the threshold
        """
        last_key=0 #last key 
        
        for i,img in enumerate(self.images):
            if i % self.keyframe == 0: #it's a key frame
                last_key=i #i'm a the key
                img.key=i-self.keyframe #but my key is the previous one
                local_duration=0#reset the previous duration
                img.begin=local_duration
                key = img.data.getdata()
                #The duration of the keyframe covers to the next keyframe
                img.duration=self.duration*self.keyframe
            else:
                #this is my key
                img.key=last_key
                local_duration+=self.duration
                #duration from my key
                img.begin=local_duration
                #duration
                img.duration = self.duration
                data=list(img.data.getdata())
                if len(data) != len(key):
                    raise RuntimeError("Images sizes don't fit!")

                #for each pixel compare with the key
                for j,ref_pixel in enumerate(key):
                    pixel=data[j]
                    diff=(ref_pixel[0]-pixel[0],ref_pixel[1]-pixel[1],ref_pixel[2]-pixel[2],ref_pixel[3]-pixel[3])
                    #make them zero and transparent if the difference of each colour channel is less than  the threshold
                    if abs(diff[0])< self.threshold  and abs(diff[1])<self.threshold  and abs(diff[2]) <self.threshold :
                        data[j]=ZERO
                
                #save the new data
                img.data.putdata(data)

class XngSerialiser:
    def __init__(self, images):
        """ Serialises a list of images into a svg file """
        self.images = images

    def xml(self):
        xml_data = ''
        xml_set = ''
        for id, image in enumerate(self.images):
            xml_data += IMAGE_DATA %(id, image.encode64())
            if id == 0:
                xml_set += IMAGE_SET_FIRST %(id, id, image.duration, len(self.images)-1)
            elif image.begin==0:#I'm a key
                xml_set += IMAGE_SET_KEY %(id, id, image.duration, image.key)
            else:
                xml_set += IMAGE_SET %(id, id, image.duration, image.key,image.begin)
                pass

        return SVG %(xml_data + xml_set) 


def load_folder(path):
    """ sorts the files by path name """
    files=sorted(listdir(path))
    images=[ImageData(join(path,f)) for f in files]
    return images


parser = OptionParser()
parser.add_option("-d", "--dir", dest="dir", help="path to the directory of the images, is mandatory")
parser.add_option("-f", "--frame", dest="frame", type=int, help="frame duration in milliseconds", default=20)
parser.add_option("-k", "--keyframe", dest="keyframe", type=int, help="rate for keyframe refreshing", default=2)
parser.add_option("-t", "--threshold", dest="threshold", type=float, help="similiraty to consider on the compression between 0 and 1", default=0.05)
parser.add_option("-o", "--out", dest="out", help="name of the file which will contain the result, is mandatory")


(options, args) = parser.parse_args()

if  options.dir == None or options.out == None:
    parser.print_help()
else:
    imgs=load_folder(options.dir)
    trans=Transform(imgs,options.keyframe,options.frame,options.threshold*255)
    trans.transform()
    serialiser = XngSerialiser(imgs)
    with open(options.out, 'w') as f:
        f.write(serialiser.xml())

