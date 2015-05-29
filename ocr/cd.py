#coding:utf-8  
import sys,os,io
from StringIO import StringIO
import Image,ImageDraw,ImageChops
import urllib,urllib2,cookielib,urlparse
import re
import math
import urlparse
#from django.core.cache import cache

#转为黑白两色
def convBW(image):
    draw = ImageDraw.Draw(image)
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            c=image.getpixel((x,y))
            if c!=255 and c!=0:
                if c>230:
                    draw.point((x,y),255)
                else:
                    draw.point((x,y),0)

#降噪  
def clearNoise(image):
    draw = ImageDraw.Draw(image)
    #切边
    for x in range(0,image.size[0]):
        for y in range(0,image.size[1]):
            if  x==0 or y==0 or x == image.size[0]-1 or y == image.size[1]-1:
                draw.point((x,y),255)
    
    for x in range(0,image.size[0]):
        for y in range(0,image.size[1]):
            c=image.getpixel((x,y))
            c1 = 255 if x==0 else image.getpixel((x-1,y))
            c2 = 255 if x==image.size[0]-1 else image.getpixel((x+1,y))
            c3 = 255 if y==0 else image.getpixel((x,y-1))
            c4 = 255 if y==image.size[1]-1 else image.getpixel((x,y+1))

            c5 = 255 if x==0 or y==0  else image.getpixel((x-1,y-1))
            c6 = 255 if x==image.size[0]-1 or y==0 else image.getpixel((x+1,y-1))
            c7 = 255 if x==0 or y==image.size[1]-1 else image.getpixel((x-1,y+1))
            c8 = 255 if x==image.size[0]-1 or y==image.size[1]-1 else image.getpixel((x+1,y+1))
            
            if (c1 == c2 == c3 == c4 == c5 == c6 == c7 == c8):
                draw.point((x,y),255)


#装载对比图片
def loadFonts():
#    fontMods = cache.get('fontMods')
    fontMods=None
    if fontMods==None:
        fontMods = {}
        for flist in os.listdir('./fonts'):
            f="./fonts/%s" % flist
            if not f.endswith('bmp'): continue
            img = Image.open(open(f))
            p=[]
            for x in range(img.size[0]):
                t=[]
                for y in range(img.size[1]):
                    t.append(0 if img.getpixel((x,y))==255 else 1)
                p.append(t)
            fontMods[flist]=p   
#                fontMods.append([str(flist), StringIO(open(f).read())])
#        cache.set('fontMods',fontMods,3600)
#    for mods in fontMods:
#        mods[1]=Image.open(mods[1])
    return fontMods

#像素对比
def getResult(fontMods,img):
    p = []
    h=img.size[1]
    w=img.size[0]
    minpoint={"diff":10000,"name":""}
    
    for x in range(w):
        t=[]
        for y in range(h):
            t.append(0 if img.getpixel((x,y))==255 else 1)
        p.append(t)
    
    #计算四个边的有效像素，如果有效像素超过2，认为对比时，不可以忽略
    rx=[0]
    ry=[0]
    if sum(p[0])<3: rx.append(1)
#    if (1 in rx) and sum(p[1])<3: rx.append(2)
    if sum(p[-1])<3: rx.append(-1)
#    if (-1 in rx) and sum(p[-2])<3: rx.append(-2)
    if sum([p[i][0] for i in range(w)])<3: ry.append(1)
#    if (1 in ry) and sum([p[i][1] for i in range(w)])<3: ry.append(2)
    if sum([p[i][-1] for i in range(w)])<3: ry.append(-1)
#    if (-1 in ry) and sum([p[i][-2] for i in range(w)])<3: ry.append(-2)

    #图像移位对比
    for x in rx:
        for y in ry:
            for font in fontMods:
                diff = 0
                mh=len(fontMods[font][0])
                mw=len(fontMods[font])
                f_ps=sum([sum(fontMods[font][j]) for j in range(mw)])
                i_ps=sum([sum(p[j]) for j in range(w)])
                #有效像素相差30则放弃
                if abs(f_ps-i_ps)>30: continue
                #图片宽度相差5则放弃
                if abs(h+y-mh)>5 or abs(w+x-mw)>5: continue
                for yi in range(min(h+y,mh)):
                    for xi in range(min(w+x,mw)):
                        tx=xi+x
                        ty=yi+y
                        if tx<0 or ty<0 or tx>=w or ty>=h: continue
                        if fontMods[font][xi][yi] != p[tx][ty]:
                            diff += 1
                if diff<minpoint['diff']:
                    minpoint['diff']=diff
                    minpoint['name']=font  
                    minpoint['x']=x
                    minpoint['y']=y
                    minpoint['h']=min(h+y,mh)
                    minpoint['w']=min(w+x,mw)
#    print minpoint 
    return minpoint

#获得一个连续的图像
count = 0
def getfont(image,x,y,draw,outdraw):
    c=image.getpixel((x,y))
    if c==255 : return 
    c1 = 255 if x==0 else image.getpixel((x-1,y))
    c2 = 255 if x==image.size[0]-1 else image.getpixel((x+1,y))
    c3 = 255 if y==0 else image.getpixel((x,y-1))
    c4 = 255 if y==image.size[1]-1 else image.getpixel((x,y+1))
    c5 = 255 if x==0 or y==0  else image.getpixel((x-1,y-1))
    c6 = 255 if x==image.size[0]-1 or y==0 else image.getpixel((x+1,y-1))
    c7 = 255 if x==0 or y==image.size[1]-1 else image.getpixel((x-1,y+1))
    c8 = 255 if x==image.size[0]-1 or y==image.size[1]-1 else image.getpixel((x+1,y+1))
    outdraw.point((x,y),c)
    draw.point((x,y),255)
    global count
    count = count+1
    if c1!=255: getfont(image,x-1,y,draw,outdraw)
    if c2!=255: getfont(image,x+1,y,draw,outdraw)
    if c3!=255: getfont(image,x,y-1,draw,outdraw)
    if c4!=255: getfont(image,x,y+1,draw,outdraw)
    if c5!=255: getfont(image,x-1,y-1,draw,outdraw)
    if c6!=255: getfont(image,x+1,y-1,draw,outdraw)
    if c7!=255: getfont(image,x-1,y+1,draw,outdraw) 
    if c8!=255: getfont(image,x+1,y+1,draw,outdraw)

#获得第一个非空白的像素点坐标
def getfirstPoint(image):
    for x in range(0,image.size[0]):
        for y in range(0,image.size[1]):
            c=image.getpixel((x,y))
            if c!=255 : return x,y
    return -1,-1

#自动裁边
def autoCrop(image):
    bg = Image.new("L", image.size, 255)
    diff = ImageChops.difference(image, bg)
    bbox = diff.getbbox()
    if bbox:
        return image.crop(bbox)
    return image


#分割图片到单个字符
def splitImage(image):
    draw = ImageDraw.Draw(image)
    i=1;
    images=[]
    while True: 
        im = Image.new("L", image.size, "white")
        outdraw = ImageDraw.Draw(im)
        x,y = getfirstPoint(image)
        if x==-1 or y == -1: break
#        print 'first point:',x,y
        global count
        count = 0 
        getfont(image,x,y,draw,outdraw)
#        print "count:",count
        if count>10:
            im=autoCrop(im) 
            images.append(im)
#            im.save("o_%s.bmp"%i)
#            print "save %s"%i
            i=i+1
  
    while len(images)<4:
#        print u"分割的图片数为 %s，继续分割"%len(images)
        l=[]        
        for im in images:
            l.append(im.size[0])
        w=max(l) #宽度
        i=l.index(w) 
        im=images[i] #图片
        h=im.size[1] #高度
#        print u"找到最长的图片为 %s 宽度为 %s 高度为 %s"%(i,w,h)

        #取4个角的有效像素对比
        v=[0,0]
        for x in range(w):
            for y in range(h):
                p=(w/2.0-x)*h/w 
                if x<(w/2.0) and (y>p and y<(h-p)): continue
                p=int((x-w/2.0)*h/w) 
                if x>(w/2.0) and (y>p and y<(h-p)): continue
                c=im.getpixel((x,y))
                if (x<w/2.0 and y<h/2.0) or (x>w/2.0 and y>h/2.0):
                    if c!=255: v[0]=v[0]+1     
                else:     
                    if c!=255: v[1]=v[1]+1
       
#        print u"对角的有效像素为：",v
        if (v[1]-v[0]<5) or v[0]>10:
#            print u"对角的像素差为 %s ,斜角像素为 %s，使用垂直分割"%(v[1]-v[0],v[0])
            p=[]
            s,e=int(w*0.25),int(w-w*0.25)+1
            for x in range(s,e):
                t=0
                for y in range(h):
                    pix=im.getpixel((x,y))
                    if pix!=255: t=t+1
                p.append(t)     
            e=p.index(min(p))+s+1 
#            print u"找到像素最少的分割线为 %s ，位于 %s"%(min(p),e)
            bbox=(0,0,e,h)
            im1=autoCrop(im.crop(bbox))
            bbox=(e,0,w,h)
            im2=autoCrop(im.crop(bbox))
        else:
#            print u"对角的像素差为 %s ,斜角像素为 %s，使用斜线分割"%(v[1]-v[0],v[0])
            du=75 #斜角度
            p=[]
            s,e=2,w-2
            for x in range(s,e):
                t={}
                f=True
                for y in range(h):
                   # x1=cot(du)*(h-y)+x
                    x1 = int((h-y)/math.tan(math.radians(du)))+x
                    if x1>=w or y>=h:
                        f=False
                        break 
                    pix=im.getpixel((x1,y))
                    key='%s,%s'%(x1,y)
                    if pix!=255: t[key]=1
                if not f: break
                p.append(sum(t.values()))
            e=p.index(min(p))+s+1
#            print u"找到像素最少的分割线为 %s ，位于 %s"%(min(p),e)
            im1=Image.new("L", im.size , 255)
            outdraw = ImageDraw.Draw(im1)
            for y in range(h):
                x1=e+int((h-y)/math.tan(math.radians(du)))
                for x in range(x1):
                    c=im.getpixel((x,y))
                    outdraw.point((x,y),c)
            im1=autoCrop(im1)   
            im2=Image.new("L", im.size , 255)
            outdraw = ImageDraw.Draw(im2)
            for y in range(h):
                x1=e+int((h-y)/math.tan(math.radians(du)))
                for x in range(x1,w):
                    c=im.getpixel((x,y))
                    outdraw.point((x,y),c)
            im2=autoCrop(im2)       
        images[i]=im1
        images.insert(i+1,im2)  
    return images

#获得图片校验码  
def getVerifyNumber(imageFileName):
    #打开图片      
    image = Image.open(imageFileName)
    image.save("x_1.bmp")
    #将图片转换成灰度图片  
    image = image.convert("L")
    image.save("x_2.bmp")
    clearNoise(image)
    image.save("x_3.bmp")
    #将图片转为黑白两色    
    convBW(image)
    image.save("x_4.bmp")
    #加载对比字形库
    fontMods=loadFonts()
    #分割验证码
    ims = splitImage(image)
    
    if len(ims)!=4:
#        print u"分离验证码失败"
        return ""

    result=''  
    for im in ims:
        im.save('im%s.bmp'%ims.index(im)) 
        r = getResult(fontMods,im)
        if r['diff']>10:
#            print u"差异过大，需要加入字体库"
#            im.save("./fonts/z_%s.bmp"%ims.index(im))
            return ""
        result += r['name'][0]

    return result

def openurl(opener,url):
    request = urllib2.Request(url)
    request.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.27 Safari/537.36')
    request.add_header('Referer','http://www.haiguan.info/onlinesearch/gateway/Gatewaystate.aspx')
    return opener.open(request,timeout=120).read()

def posturl(opener,url,data):
    request = urllib2.Request(url)
    request.add_header('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.27 Safari/537.36')
    request.add_header('Referer','http://www.haiguan.info/onlinesearch/gateway/Gatewaystate.aspx')
    postData = urllib.urlencode(data)
    return opener.open(request,postData,timeout=120).read()

def test():
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    imgurl = "http://query.customs.gov.cn/MNFTQ/Image.aspx"
    imagefile = io.BytesIO(openurl(opener,imgurl))
    code=getVerifyNumber(imagefile)
    print code

def test2():
    imagefile = open("x_1.bmp")
    code=getVerifyNumber(imagefile)
    print code


def cdquery(queryType,p1,p2):
    if queryType=='1':
        url="http://query.customs.gov.cn/MNFTQ/MRoadQuery.aspx"
    else:
        url="http://query.customs.gov.cn/MNFTQ/MRoadTransportQuery.aspx"    
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    html = openurl(opener,url)
    if queryType=='1':
        match = re.search(r'<img id="MRoadQueryCtrl1_imgCode" src="(.*?)"',html,re.DOTALL)
    else:
        match = re.search(r'<img id="MRoadTransportQueryCtrl1_Image1" src="(.*?)"',html,re.DOTALL)    
    if not match:
        return ""
    imgurl = urlparse.urljoin(url, match.group(1)) 
    code=""
    while True:
        imagefile = io.BytesIO(openurl(opener,imgurl))
        code=getVerifyNumber(imagefile)
        if code=="":
             pass
        else:
            break
    match = re.findall(r'<input type="hidden" name=".*?/>',html)
    data={}
    for inputmatch in match:
        m = re.search(r'id="(.*?)".{1,5}value="(.*?)"',inputmatch)
        data[m.group(1)]=m.group(2)
    if queryType=='1':        
        data['MRoadQueryCtrl1$txtManifestID']=p1
        data['MRoadQueryCtrl1$txtBillNo']=p2
        data['MRoadQueryCtrl1$btQuery']='查询'
        data['MRoadQueryCtrl1$txtCode']=code
    else:
        data['MRoadTransportQueryCtrl1$txtManifestID']=p1
        data['MRoadTransportQueryCtrl1$txtTransportID']=p2
        data['MRoadTransportQueryCtrl1$txtCode']=code
        data['MRoadTransportQueryCtrl1$btQuery']='查询'    
    rHtml=posturl(opener,url,data)
#    print rHtml
    if queryType=='1':            
        match = re.search(r'<td id="MRoadQueryCtrl1_tdMessage".*?>(.*?)<',rHtml,re.DOTALL)
    else:    
        match = re.search(r'<td id="MRoadTransportQueryCtrl1_tdMessage".*?>(.*?)<',rHtml,re.DOTALL)
    
    if match:
#        print match.group(1)
        return unicode(match.group(1),'GBK')
#        print match.group(1)
    else:
        return "" 
#        print u"查询失败"   

if __name__ == '__main__':
    print cdquery('2','222222','333333')
