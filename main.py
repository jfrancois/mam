import wx
import os
import static
import threading
import inspect
import image_viewer
from optparse import OptionParser
import sys

try: 
    from maggregator.src.multiAggregator import main_aggregator
    import features
    from features import *
except:
    sys.path.append(".")
    sys.path.append('./maggregator')
    import maggregator
    from maggregator.multiAggregator import main_aggregator
    import features
    from features import *
  
'''
app = wx.App(False)  # Create a new app, don't redirect stdout/stderr to a window.
frame = wx.Frame(None, wx.ID_ANY, "Hello World",size=(200,100)) # A Frame is a top-level window.
frame.control = wx.TextCtrl(frame, style=wx.TE_MULTILINE)
frame.Show(True)     # Show the frame.
app.MainLoop()
'''



class MainWindow(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(850,600))
        #0s elf.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.CreateStatusBar() # A Statusbar in the bottom of the window

        
        self.features = []
        for mod in inspect.getmembers(features,inspect.ismodule):
            for cla in inspect.getmembers(mod[1],inspect.isclass):
                if issubclass(cla[1],features.feature.Feature):
                    self.features.append((cla[0],cla[1]))
       
        #self.features = inspect.getmembers(feature, inspect.isclass)
        # Setting up the menu.
        filemenu= wx.Menu()
        helpmenu= wx.Menu()
        # wx.ID_ABOUT and wx.ID_EXIT are standard ids provided by wxWidgets.
        
        
        menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
        menuAbout = helpmenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
        menuConfigLoad = filemenu.Append(wx.ID_ANY,"&Load Configuration File", "Load a configuration file for prefined values")
        menuConfigSave = filemenu.Append(wx.ID_ANY,"&Save Configuration File", "Save the configuration to a file")
        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        menuBar.Append(helpmenu,"&Help") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

        

        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        
        self.Bind(wx.EVT_MENU, self.onLoadConfig,menuConfigLoad)
        self.Bind(wx.EVT_MENU, self.onSaveConfig,menuConfigSave)
        
        self.Bind(wx.EVT_BUTTON, self.OnBrowse, id=10)
        
        self.Bind(wx.EVT_BUTTON, self.OnRun, id=11)
        self.Bind(wx.EVT_CHAR, self.onKeyDown)
        sizer = wx.GridBagSizer(12, 4)
        #Setting up the panels.
        
        #Input
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Input', (20,20)),(0,0))
        self.input_file = wx.TextCtrl(self,size=(400,25))
        sizer.Add(self.input_file,(0,1))
        sizer.Add(wx.Button(self, 10, 'Browse', (80, 220)),(0,2))
        
        #Alpha
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Aggregation %', (20,20)),(1,0))
        #self.alpha = wx.SpinCtrl(self, -1, '2',  (150, 75), (60, -1))
        self.alpha = wx.TextCtrl(self,size=(100,25))
        sizer.Add(self.alpha,(1,1))
        
        #Window
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Window', (20,20)),(2,0))
        self.window = wx.TextCtrl(self,size=(400,25))
        sizer.Add(self.window,(2,1))
        
        #RegExp
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'RegExp', (20,20)),(3,0))
        self.regexp = wx.TextCtrl(self,size=(400,25))
        sizer.Add(self.regexp,(3,1))
        
        #Fields
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Fields (prefix by \'d_\' to specify fields to use)', (20,20)),(4,0))
        self.fields =wx.TextCtrl(self,size=(400,25))
        sizer.Add(self.fields,(4,1))
        
        #Dimensions
        #sizer.Add(wx.StaticText(self,wx.ID_ANY,'Dimentions', (20,20)),(5,0))
        #self.dimensions = wx.TextCtrl(self,size=(400,25))
        #sizer.Add(self.dimensions,(5,1))
        
        #Types
        tsizer = wx.GridBagSizer(1, 3)
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Types', (20,20)),(5,0))
        self.types = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (170, 130),map(lambda x:x[0],self.features) , wx.LB_MULTIPLE)
        self.types.Bind(wx.EVT_LISTBOX, self.onSelectFeature)
        self.selected_types = wx.ListBox(self, wx.ID_ANY, wx.DefaultPosition, (170, 130), [] , wx.LB_MULTIPLE)
        self.selected_types.Bind(wx.EVT_LISTBOX, self.onDeselectFeature)
        tsizer.Add(self.types,(0,1))
        
        
        btsizer = wx.GridBagSizer(2, 1)
        addb = wx.Button(self, 1, '>', (50, 130))
        addb.Bind(wx.EVT_BUTTON,self.addSelected)
        btsizer.Add(addb, (0,0))
        
        remb=wx.Button(self, 1, '<', (50, 130))
        remb.Bind(wx.EVT_BUTTON,self.removeSelected)
        btsizer.Add(remb,(1,0))
        tsizer.Add(btsizer,(0,2))
        tsizer.Add(self.selected_types,(0,3))
        sizer.Add(tsizer,(5,1))
        
        #self.types =wx.TextCtrl(self,size=(400,25))
        #sizer.Add(self.types,(6,1))
        
        #Strategy
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Strategy', (20,20)),(6,0))
        self.strategy =wx.ComboBox(self, choices=['Root','LRU'], style=wx.CB_READONLY) 
        sizer.Add(self.strategy,(6,1))
        
        #Max Nodes
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Max Nodes', (20,20)),(7,0))
        self.nodes = wx.TextCtrl(self,size=(400,25)) 
        sizer.Add(self.nodes,(7,1))
        
        
        #Node Size highlighting
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Aggregation Highlighting', (20,20)),(8,0))
        self.ahighlight = wx.ComboBox(self, choices=['Accumulated','Node'], style=wx.CB_READONLY)
        sizer.Add(self.ahighlight,(8,1))
        
        #Stability threshold highlighting
        sizer.Add(wx.StaticText(self,wx.ID_ANY,'Stability', (20,20)),(9,0))
        self.shighlight = wx.ComboBox(self, choices=['Average','Min'], style=wx.CB_READONLY)
        sizer.Add(self.shighlight,(9,1))
        
        sizer.Add(wx.Button(self, 11, 'Run', (80, 220)),(10,1))
        self.SetSizer(sizer)
        self.Show(True)
        
    def removeSelected(self,event):
        for i in self.selected_types.GetSelections():
            self.selected_types.Delete(i)
    
    def addSelected(self,event):
        pos = 0
        for i in self.types.GetSelections():
            self.selected_types.Insert(self.features[i][0],pos)
            pos+=1
        
    def onDeselectFeature(self,event):
        ''        
    def onSelectFeature(self,event):
        #self.selected_types.Insert(self.features[event.GetSelection()][0],0)
        pass
        
    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, static.about, "About MaM", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.

    def OnExit(self,e):
        self.Close(True)  # Close the frame.
        
    def OnBrowse(self,e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
           self.filename = dlg.GetFilename()
           self.dirname = dlg.GetDirectory()
           self.input_file.SetValue("%s/%s"%(self.dirname,self.filename))
    
    def onLoadConfig(self,e):
        """ Open a file"""
        self.dirname = '.'
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
           self.filename = dlg.GetFilename()
           self.dirname = dlg.GetDirectory()
           f = open(os.path.join(self.dirname, self.filename), 'r')
           for line in (lines for lines in f):
               try:
                   if '=' in line:
                       field,value = line.split('=')[0].strip(),line.split('=')[1].strip()
                       if field == 'types':
                           features_indexes = map(lambda x: map(lambda x: x[0], self.features).index(x), value.split())
                           for fi in features_indexes:
                               self.types.SetSelection(fi)
                               self.selected_types.Insert(self.features[fi][0],len(self.selected_types.GetItems()))
                       else:
                           eval('''self.%s.SetValue("%s")'''%(field,value))
               except Exception, e:
                   print e
               
                   
           f.close()
           dlg.Destroy()
           
    def onSaveConfig(self,e):
        """ Save a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*", wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:

        
           f = open(dlg.GetPath(), 'w')
           
           for fie in ["input_file","alpha","window","regexp","fields","nodes","shighlight","ahighlight","strategy"]:
               f.write("%s = %s\n" % (fie,eval("str(self.%s.GetValue())" % fie))) 
               
                   
           f.close()
           dlg.Destroy()
           
    def onKeyDown(self,event):
        #print "keydown"
        pass
           
    def OnRun(self,e):
        # Set the panel
        types = " ".join(self.selected_types.GetItems())
        fields = self.fields.GetValue().split(" ")
        dimensions =filter(lambda x: "d_" in x,fields)
        strategy = "" if self.strategy.GetValue() != None else self.strategy.GetValue()
        
        for i in xrange(0,len(fields)):
            if fields[i][0:2] == 'd_':
                fields[i] = fields[i][2:]
                 
        for i in xrange(0,len(dimensions)):
            if dimensions[i][0:2] == 'd_':
                dimensions[i] = dimensions[i][2:]
        fields = " ".join(fields)
        dimensions = " ".join(dimensions)
        
     
        
        #types = " ".join(map(lambda x: x[0], map(lambda x: self.features[x],[i for i in self.types.GetSelections()])))
        #print ' '.join(map(lambda x: self.features[x],list(self.types.GetSelections())))
        lineparser = OptionParser("")
        
        
        lineparser.add_option('-i','--input', dest='input', default=self.input_file.GetValue().encode('utf8'),type='string',help="input file (txt flow file)", metavar="FILE")    
        lineparser.add_option('-w','--window-size', dest='window', default=int(self.window.GetValue()),type='int',help="window size in seconds")    
        lineparser.add_option('-r','--reg-exp', dest='reg_exp', default=self.regexp.GetValue(),type='string',help="regular expression to extract flow information")    
        lineparser.add_option('-f','--fields', dest='fields', default=fields,type='string',help="fields naming corresponding to the regular expression, have to be split by a space character and HAS TO INCLUDE value and timestamp")    
        lineparser.add_option('-d','--dimensions', dest='dim', default=dimensions,type='string',help="dimension to use for the radix tree, have to be split by a space character and correspond to the field naming")    
        lineparser.add_option('-t','--type-dimension', dest='types', default=types,type='string',help="types of dimension")    
        lineparser.add_option('-c','--cut', dest='cut', default=0.02,type='float',help="threshold (%) under which removing a node is not allowed during the construction(it's include the parents values)")    
        lineparser.add_option('-a','--aggregate', dest='aggregate', default=float(self.alpha.GetValue()),type='float',help="threshold (%) for the aggregation")    
        lineparser.add_option('-l','--log-file', dest='log',default="log.att",type='string',help="log file containing the attacks", metavar="FILE")    
        lineparser.add_option('-s','--split', dest='split', default=20,type='float',help="percentage of data used for training")
        lineparser.add_option('-g','--type-aggregation', dest='type_aggr', default="NumericalValueNode",type='string',help="type of the aggregation for nodes")   
        
        lineparser.add_option('-n','--name', dest='namefile', default="bytes",type='string',help="suffix for name of file results")    
        lineparser.add_option('-S','--strategy', dest='strategy', default='',type='string',help="stratrgy for selecting nodes to aggregate")
        lineparser.add_option('-m','--max-nodes', dest='max_nodes', default=int(self.nodes.GetValue()),type='int',help="max size of tree")
        lineparser.add_option('-A','--aggregation-highlight', dest='ahighlight', default=self.ahighlight.GetValue(),type='string',help="Highligh nodes on behalf aggregation")
        lineparser.add_option('-T','--stability-highlight', dest='shighlight', default=self.ahighlight.GetValue(),type='string',help="Highligh nodes on behalf node stability")
        
        #main_aggregator(lineparser)

        
        class FuncThread(threading.Thread):
            def __init__(self, target, *args):
                self._target = target
                self._args = args
                threading.Thread.__init__(self)
                
            def run(self):
                return self._target(*self._args)
        
        
        
        t1 = FuncThread(main_aggregator, lineparser)
        
        list_res = t1.run()
        print list_res
        files =  list_res[1]
        
        frame = image_viewer.ImgViewer(None, -1, 'Tree',files)
 
        frame.Show(True)
        
                
class MyFrame(wx.Frame):
    def __init__(self, parent, id, title,bitmapfile):
        wx.Frame.__init__(self, parent, id, title, size = (1024, 800))
        self.panel = wx.Panel(self, -1)
        self.panel.SetScrollbar(wx.VERTICAL, 0, 6, 50);
        self.panel.SetScrollbar(wx.HORIZONTAL, 0, 6, 50);
        
        
        bitmap = wx.Bitmap(bitmapfile)
        self.bitmap = self.scale_bitmap(bitmap, 600,800)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         self.bitmap)
        self.panel.Refresh() 
        #wx.EVT_PAINT(self, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.Centre()
        
    def OnSize(self, event):
        event.GetSize()[0], event.GetSize()[1]
        
    def scale_bitmap(self,bitmap, w,h):
            image = wx.ImageFromBitmap(bitmap)
            '''if image.GetWidth() > image.GetHeight():
                neww = w
                newh = h * h / float(w)
            else:
                newh = h
                neww = w * w / float(h)
                 
            image = image.Scale(neww, newh, wx.IMAGE_QUALITY_HIGH)'''
            result = wx.BitmapFromImage(image)
            return result
        
    def OnPaint(self, event):
        self.imageCtrl.SetBitmap(self.bitmap)
        self.panel.Refresh()



        
app = wx.App(False)
frame = MainWindow(None, "MaM")
app.MainLoop()
