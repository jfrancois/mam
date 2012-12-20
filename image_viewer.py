import wx
from copy import deepcopy
import math
class ImgViewer(wx.Frame):

    def fit_window(self):
        p = 1
        
        if self.bitmap.GetHeight() >= self.bitmap.GetWidth() and self.bitmap.GetHeight() > self.window_h:
            p = (self.window_h - self.bitmap.GetHeight()) / self.bitmap.GetHeight()
            
            
        if self.bitmap.GetHeight() < self.bitmap.GetWidth() and self.bitmap.GetWidth() > self.window_w:
            p = (self.window_w - self.bitmap.GetWidth()) / self.bitmap.GetWidth()
            #print p
        if p != 1:
            
            self.scale_per(p)

    def __init__(self, parent, id, title,blist):
        self.window_w = 1280.0
        self.window_h = 960.0
        self.zoom_unit = 0.1
        self.current_zoom = None
        self.blist = blist
        self.bitmap = wx.Bitmap(blist[0])
        wx.Frame.__init__(self, parent, id, title, size = (self.window_w, self.window_h))
        #self.Maximize()
        self.sw = wx.ScrolledWindow(self)
        self.sw.SetScrollbars(1, 1, 1, 1)
        n = wx.Button(self.sw, label="Display next")
        p = wx.Button(self.sw, label="Display previous")
        zi = wx.Button(self.sw, label="Zoom In")
        zo = wx.Button(self.sw, label="Zoom Out")
        self.kz = wx.CheckBox(self.sw, label="Keep Zoom")
        
        n.Bind(wx.EVT_BUTTON, self.nextImage)
        p.Bind(wx.EVT_BUTTON, self.previousImage)
        zo.Bind(wx.EVT_BUTTON, self.reduceImage)
        zi.Bind(wx.EVT_BUTTON, self.enlargeImage)
        
        self.current = 0
        box = wx.BoxSizer(wx.VERTICAL)
        butbox = wx.BoxSizer(wx.HORIZONTAL)
        butbox.Add(n, 0, wx.LEFT|wx.ALL, 10)
        butbox.Add(p, 0, wx.LEFT|wx.ALL, 10)
        butbox.Add(zi,0, wx.LEFT|wx.ALL, 10)
        butbox.Add(zo,0, wx.LEFT|wx.ALL, 10)
        butbox.Add(self.kz,0, wx.LEFT|wx.ALL, 10)
        box.Add(butbox,0)
        box.Add((1,1),1)
        
        self.imageCtrl = wx.StaticBitmap(self.sw, wx.ID_ANY, 
                                        self.bitmap)
        #self.panel.Refresh()
        #self.imageCtrl.Bind(wx.EVT_LEFT_DCLICK, self.enlargeImage, self.panel.imageCtrl)
        
        #self.imageCtrl.Bind(wx.EVT_RIGHT_DCLICK, self.reduceImage, self.panel.imageCtrl)
        
        #self.imageCtrl.Bind(wx.EVT_MIDDLE_UP, self.changeImage)
        box.Add(self.imageCtrl, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL|wx.ADJUST_MINSIZE, 10)
        
        box.Add((1,1),1)
        
        self.sw.SetSizer(box)
        self.image = self.bitmap.ConvertToImage()
        self.setScrolls()
        #self.panel = wx.Panel(self.sw, -1,style=wx.SUNKEN_BORDER)
        
        
        
        
        #h = 1 * bitmap.GetHeight()
        #w = 1 * bitmap.GetWidth()
        #self.bitmap = self.scale_bitmap(bitmap,w,h)
        
        
        
        #self.fit_window()
        
        #self.panel.imageCtrl.Bind(wx.EVT_MIDDL)
         
        #self.sw.Bind(wx.EVT_SIZE, self.OnSize)
        self.w,self.h= self.bitmap.GetWidth(),self.bitmap.GetHeight()
        #print self.w,self.h
        self.SetTitle("Tree %s/%s" % (str(self.current),str(len(self.blist))))
        #self.panel.SetFocus()
        
        
        #self.toolbar = wx.ToolBar(self, -1, style=wx.TB_HORIZONTAL | wx.NO_BORDER)
        #self.toolbar.AddLabelTool(wx.ID_ANY, '', wx.ArtProvider.GetBitmap(wx.ART_FIND))
        #self.toolbar.Realize()
        # Add Choice box, its parent is the toolbar, with default position and size
  

        self.Show(True)
        self.fit_window()
        #self.Centre()
        
    def setScrolls(self):
        wstep = 55
        hstep = 40
        wsize = self.bitmap.GetWidth() / wstep
        hsize = self.bitmap.GetHeight() / hstep
        self.sw.SetScrollbars(wsize,hsize,wstep,hstep)

    def scale_per(self,p=1):
        image = self.image
        wval = math.floor(p * self.image.ConvertToBitmap().GetWidth()) 
        hval = math.floor(p * self.image.ConvertToBitmap().GetHeight())
        w = self.bitmap.GetWidth() + wval 
        h = self.bitmap.GetHeight() + hval  
        
        self.bitmap = image.Scale(w,h).ConvertToBitmap()
        self.imageCtrl.SetBitmap(self.bitmap)
        self.Refresh()
        self.setScrolls()
        #self.panel.SetFocus()
        #print w,h
                   
    def reduceImage(self, event):
        if self.current_zoom :
            self.current_zoom = self.current_zoom - self.zoom_unit
        else: 
            self.current_zoom = -1 * self.zoom_unit
        return self.scale_per(-1 * self.zoom_unit)
        
        
        
    def enlargeImage(self, event):
        if self.current_zoom :
            self.current_zoom = self.current_zoom + self.zoom_unit
        else: 
            self.current_zoom = self.zoom_unit
        return self.scale_per(self.zoom_unit)
    
    def nextImage(self,event):
        self.changeImage(1)
        if self.kz.GetValue():
            return self.scale_per(self.current_zoom)
        else:
            self.current_zoom = None
    
    def previousImage(self,event):
        self.changeImage(-1)
        if self.kz.GetValue():
            return self.scale_per(self.current_zoom)
        else:
            self.current_zoom = None
        
    def changeImage(self,step=1):
       # print "keydown"
        self.current= self.current + step if self.current < len(self.blist) - 1 else 0
        self.bitmap = wx.Bitmap(self.blist[self.current])
        self.image = self.bitmap.ConvertToImage()
        self.imageCtrl.SetBitmap(self.bitmap)
        self.Refresh()
        self.setScrolls()
        self.SetTitle("Tree %s/%s" % (str(self.current),str(len(self.blist))))
        self.fit_window()
                        
    def OnSize(self, event):
        w , h =event.GetSize()[0], event.GetSize()[1]
        if w != self.w and h!= self.h:
            #print "<"
            image = self.image
            self.bitmap = image.Scale(w,h).ConvertToBitmap()
            self.imageCtrl.SetBitmap(self.bitmap)
            #self.panel.Refresh()
            self.w = w
            self.h = h
            #print ">"
            
            #self.panel.Refresh()
        #self.bitmap=self.scale_bitmap(self.bitmap, w,h)
        #self.imageCtrl.SetBitmap(self.bitmap)
        
        #
        
    def scale_bitmap(self,bitmap, w,h):
            image = wx.ImageFromBitmap(bitmap)
            if image.GetWidth() > image.GetHeight():
                neww = w
                newh = h * h / float(w)
            else:
                newh = h
                neww = w * w / float(h)
                 
            image = image.Scale(neww, newh, wx.IMAGE_QUALITY_HIGH)
            result = wx.BitmapFromImage(image)
            return result
        
    '''def OnPaint(self, event):
        self.imageCtrl.SetBitmap(self.bitmap)'''
        
 
if __name__ == '__main__':
    app = wx.App(False)
    frame = ImgViewer(None, -1, 'Tree',["/home/lautaro/workspace/maggregator/test/app_ipv4/appxipv4_0_2.0.png","/home/lautaro/workspace/maggregator/test/app_ipv4/appxipv4_1_2.0.png"])
    #frame = MyFrame(None, -1, 'Tree',"test.png")
    frame.Show(True)
    app.MainLoop()