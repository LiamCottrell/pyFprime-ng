"""main Absorb routines
   Copyright: 2009, Robert B. Von Dreele (Argonne National Laboratory)
"""
import os
import math
import wx
import Element
import numpy as np
import matplotlib as mpl

try:
    import wxmpl
except:
    # use a copy provided here, select the newer wxmpl when needed
    (main,sub) = mpl.__version__.split('.')[0:2]
    if int(main) > 0 or int(sub) > 91: 
        print "Loading Absorb distributed wxmpl v1.3.1"
        import wxmpl131 as wxmpl
    else:
        print "Loading Absorb distributed wxmpl v1.2.9a"
        import wxmpl129a as wxmpl
import pylab
import sys

__version__ = '0.1.0'
# print versions
print "Installed python module versions in use in Absorb v.",__version__,":"
print "python:     ",sys.version[:5]
print "wxpython:   ",wx.__version__
print "matplotlib: ",mpl.__version__
print "numpy:      ",np.__version__
print "wxmpl:      ",wxmpl.__version__

def create(parent):
    return Fprime(parent)
    
[wxID_CHOICE1, wxID_SPINTEXT1, wxID_SPINTEXT2, wxID_SPINTEXT3, wxID_SPINTEXT4,
 wxID_RESULTS,wxID_SLIDER1, wxID_SPINBUTTON, wxID_NUMELEM, wxID_SPINTEXT5,wxID_SPINTEXT6,
] = [wx.NewId() for _init_ctrls in range(11)]

[wxID_EXIT, wxID_DELETE, wxID_NEW, 
] = [wx.NewId() for _init_coll_ABSORB_Items in range(3)]
    
[wxID_KALPHAAGKA, wxID_KALPHACOKA, wxID_KALPHACRKA, 
 wxID_KALPHACUKA, wxID_KALPHAFEKA, wxID_KALPHAMNKA, 
 wxID_KALPHAMOKA, wxID_KALPHANIKA, wxID_KALPHAZNKA, 
] = [wx.NewId() for _init_coll_KALPHA_Items in range(9)]

[wxID_ABSORBABOUT] = [wx.NewId() for _init_coll_ABOUT_Items in range(1)]

class Absorb(wx.Frame):
    Elems = []
    Wave = 1.5405      #CuKa default
    Kev = 12.397639    #keV for 1A x-rays
    for arg in sys.argv:
        if '-w' in arg:
            Wave = float(arg.split('-w')[1])
        elif '-e' in arg:
            E = float(arg.split('-e')[1])
            Wave = Kev/E
        elif '-h' in arg:
            print '''
Absorb.py can take the following arguments:
-h   -  this help listing
-wv  -  set default wavelength to v, e.g. -w1.54 sets wavelength to 1.54A
-ev  -  set default energy to v, e.g. -e27 sets energy to 27keV
without arguments Absorb uses CuKa as default (Wave=1.54052A, E=8.0478keV)
'''
            sys.exit()
    Wmin = 0.05        #wavelength range
    Wmax = 3.0
    Wres = 0.004094    #plot resolution step size as const delta-lam/lam - gives 1000 steps for Wmin to Wmax
    Eres = 1.5e-4      #typical energy resolution for synchrotron x-ray sources
    Energy = Kev/Wave
    ifWave = True
    Volume = 0
    ifVol = False
    Zcell = 1
    Pack = 0.50
    Radius = 0.4
    def _init_coll_ABOUT_Items(self, parent):

        parent.Append(help='', id=wxID_ABSORBABOUT, kind=wx.ITEM_NORMAL,
              text='About')
        self.Bind(wx.EVT_MENU, self.OnABOUTItems0Menu, id=wxID_ABSORBABOUT)

    def _init_coll_menuBar1_Menus(self, parent):

        parent.Append(menu=self.ABSORB, title='Absorb')
        parent.Append(menu=self.KALPHA, title='Kalpha')
        parent.Append(menu=self.ABOUT, title='About')

    def _init_coll_KALPHA_Items(self, parent):
        "Set of characteristic radiation from sealed tube sources"

        parent.Append(help='', id=wxID_KALPHACRKA, kind=wx.ITEM_NORMAL,
              text='CrKa')
        parent.Append(help='', id=wxID_KALPHAMNKA, kind=wx.ITEM_NORMAL,
              text='MnKa')
        parent.Append(help='', id=wxID_KALPHAFEKA, kind=wx.ITEM_NORMAL,
              text='FeKa')
        parent.Append(help='', id=wxID_KALPHACOKA, kind=wx.ITEM_NORMAL,
              text='CoKa')
        parent.Append(help='', id=wxID_KALPHANIKA, kind=wx.ITEM_NORMAL,
              text='NiKa')
        parent.Append(help='', id=wxID_KALPHACUKA, kind=wx.ITEM_NORMAL,
              text='CuKa')
        parent.Append(help='', id=wxID_KALPHAZNKA, kind=wx.ITEM_NORMAL,
              text='ZnKa')
        parent.Append(help='', id=wxID_KALPHAMOKA, kind=wx.ITEM_NORMAL,
              text='MoKa')
        parent.Append(help='', id=wxID_KALPHAAGKA, kind=wx.ITEM_NORMAL,
              text='AgKa')
        self.Bind(wx.EVT_MENU, self.OnCrkaMenu, id=wxID_KALPHACRKA)
        self.Bind(wx.EVT_MENU, self.OnMnkaMenu, id=wxID_KALPHAMNKA)
        self.Bind(wx.EVT_MENU, self.OnFekaMenu, id=wxID_KALPHAFEKA)
        self.Bind(wx.EVT_MENU, self.OnCokaMenu, id=wxID_KALPHACOKA)
        self.Bind(wx.EVT_MENU, self.OnNikaMenu, id=wxID_KALPHANIKA)
        self.Bind(wx.EVT_MENU, self.OnCukaMenu, id=wxID_KALPHACUKA)
        self.Bind(wx.EVT_MENU, self.OnZnkaMenu, id=wxID_KALPHAZNKA)
        self.Bind(wx.EVT_MENU, self.OnMokaMenu, id=wxID_KALPHAMOKA)
        self.Bind(wx.EVT_MENU, self.OnAgkaMenu, id=wxID_KALPHAAGKA)

    def _init_coll_ABSORB_Items(self, parent):
        parent.Append(help='Add new element', id=wxID_NEW, kind=wx.ITEM_NORMAL,
              text='&New Element')
        self.Delete = parent.Append(help='Delete an element', id=wxID_DELETE, kind=wx.ITEM_NORMAL,
              text='&Delete Element')
        self.Delete.Enable(False)
        parent.Append(help='Exit Fprime', id=wxID_EXIT, kind=wx.ITEM_NORMAL,
              text='&Exit')
        self.Bind(wx.EVT_MENU, self.OnExitMenu, id=wxID_EXIT)
        self.Bind(wx.EVT_MENU, self.OnNewMenu, id=wxID_NEW)
        self.Bind(wx.EVT_MENU, self.OnDeleteMenu, id=wxID_DELETE)
        
    def _init_utils(self):
        self.ABSORB = wx.Menu(title='')

        self.KALPHA = wx.Menu(title='')
        self.KALPHA.SetEvtHandlerEnabled(True)

        self.ABOUT = wx.Menu(title='')

        self.menuBar1 = wx.MenuBar()

        self._init_coll_ABSORB_Items(self.ABSORB)
        self._init_coll_KALPHA_Items(self.KALPHA)
        self._init_coll_ABOUT_Items(self.ABOUT)
        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, parent):
        wx.Frame.__init__(self, parent=parent,
              size=wx.Size(500, 300),style=wx.DEFAULT_FRAME_STYLE, title='Absorb')              
        self._init_utils()
        self.SetMenuBar(self.menuBar1)
        self.DrawPanel()
        
    def SetSize(self):
        w,h = self.GetClientSizeTuple()
        self.panel.SetSize(wx.Size(w,h))

    def DrawPanel(self):
        self.panel = wx.Panel(self)

        mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.Results = wx.TextCtrl( parent=self.panel,
            style=wx.TE_MULTILINE|wx.TE_DONTWRAP )
        self.Results.SetEditable(False)
        mainSizer.Add(self.Results,1,wx.ALIGN_CENTER_HORIZONTAL|wx.EXPAND)
        mainSizer.Add((10,15),0)
        
        if self.Elems:
            lablSizer = wx.BoxSizer(wx.HORIZONTAL)
            lablSizer.Add((5,10),0)
            lablSizer.Add(wx.StaticText(parent=self.panel,label='Chemical Formula:'),0,
                wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT)
            mainSizer.Add(lablSizer,0)
            mainSizer.Add((5,5),0)
            nRow = len(self.Elems)/5
            compSizer = wx.FlexGridSizer(nRow+1,10,0,0)
            for Elem in self.Elems:
                compSizer.Add(wx.StaticText(parent=self.panel,label="  "+Elem[0].capitalize(),
                    size=wx.Size(30,20)),0,wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT)
                numElem = wx.TextCtrl(id=wxID_NUMELEM,parent=self.panel,name=Elem[0],
                    size=wx.Size(70,20),value="%8.2f" % (Elem[2]),style=wx.TE_PROCESS_ENTER)
                compSizer.Add(numElem,0)
                numElem.SetToolTipString('Enter number of atoms in formula')
                numElem.Bind(wx.EVT_TEXT_ENTER, self.OnNumElem, id=wxID_NUMELEM)
            mainSizer.Add(compSizer,0)
            mainSizer.Add((10,15),0)           

        selSizer = wx.BoxSizer(wx.HORIZONTAL)
        selSizer.Add((5,10),0)
        selSizer.Add(wx.StaticText(parent=self.panel, label='Wavelength:'),0,
            wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        selSizer.Add((5,10),0)
        self.SpinText1 = wx.TextCtrl(id=wxID_SPINTEXT1, parent=self.panel, 
            size=wx.Size(100,20), value = "%6.4f" % (self.Wave),style=wx.TE_PROCESS_ENTER )
        selSizer.Add(self.SpinText1,0)
        selSizer.Add((5,10),0)
        self.SpinText1.SetToolTipString('Enter desired wavelength')
        self.SpinText1.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText1, id=wxID_SPINTEXT1)
        
        selSizer.Add(wx.StaticText(parent=self.panel, label='Energy:'),0,
            wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        selSizer.Add((5,10),0)
        self.SpinText2 = wx.TextCtrl(id=wxID_SPINTEXT2, parent=self.panel, 
            size=wx.Size(100,20), value = "%7.4f" % (self.Energy),style=wx.TE_PROCESS_ENTER) 
        selSizer.Add(self.SpinText2,0)
        selSizer.Add((5,10),0)
        self.SpinText2.SetToolTipString('Enter desired energy')
        self.SpinText2.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText2, id=wxID_SPINTEXT2)
        
        selSizer.Add(wx.StaticText(parent=self.panel, label='Plot scale:'),
            0,wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        selSizer.Add((5,10),0)
        self.choice1 = wx.ComboBox(id=wxID_CHOICE1, parent=self.panel, value='Wavelength',
             choices=['Wavelength','Energy'],style=wx.CB_READONLY|wx.CB_DROPDOWN)
        selSizer.Add(self.choice1,0)
        selSizer.Add((10,10),0)
        self.choice1.SetToolTipString('Switch between wavelength and energy scale')
        self.choice1.Bind(wx.EVT_COMBOBOX, self.OnChoice1, id=wxID_CHOICE1)
        mainSizer.Add(selSizer,0)
        mainSizer.Add((10,10),0)
        
        slideSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SpinButton = wx.SpinButton(id=wxID_SPINBUTTON, parent=self.panel, 
              size=wx.Size(25,24), style=wx.SP_VERTICAL | wx.SP_ARROW_KEYS)
        slideSizer.Add(self.SpinButton,0,wx.ALIGN_RIGHT)
        self.SpinButton.SetToolTipString('Fine control of wavelength')
        self.SpinButton.SetRange(int(10000.*self.Wmin),int(10000.*self.Wmax))
        self.SpinButton.SetValue(int(10000.*self.Wave))
        self.SpinButton.Bind(wx.EVT_SPIN, self.OnSpinButton, id=wxID_SPINBUTTON)

        self.slider1 = wx.Slider(id=wxID_SLIDER1, maxValue=int(1000.*self.Wmax),
            minValue=int(1000.*self.Wmin), parent=self.panel,style=wx.SL_HORIZONTAL,
            value=int(self.Wave*1000.), )
        slideSizer.Add(self.slider1,1,wx.EXPAND|wx.ALIGN_RIGHT)
        self.slider1.SetToolTipString('Coarse control of wavelength')
        self.slider1.Bind(wx.EVT_SLIDER, self.OnSlider1, id=wxID_SLIDER1)
        mainSizer.Add(slideSizer,0,wx.EXPAND)
        mainSizer.Add((10,10),0)
        
        cellSizer = wx.BoxSizer(wx.HORIZONTAL)
        cellSizer.Add((5,10),0)
        cellSizer.Add(wx.StaticText(parent=self.panel, label='Volume:'),0,
            wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        cellSizer.Add((5,10),0)
        self.SpinText3 = wx.TextCtrl(id=wxID_SPINTEXT3, parent=self.panel, 
              size=wx.Size(100,20), value = "%6.4f" % (self.Volume),style=wx.TE_PROCESS_ENTER )
        cellSizer.Add(self.SpinText3,0)
        cellSizer.Add((5,10),0)
        self.SpinText3.SetToolTipString('Enter unit cell volume in A^3')
        self.SpinText3.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText3, id=wxID_SPINTEXT3)
        
        cellSizer.Add((5,10),0)
        cellSizer.Add(wx.StaticText(parent=self.panel, label='Z vol:'),0,
            wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        cellSizer.Add((5,10),0)
        self.SpinText4 = wx.TextCtrl(id=wxID_SPINTEXT4, parent=self.panel, 
              size=wx.Size(50,20), value = "%d" % (self.Zcell),style=wx.TE_PROCESS_ENTER )
        cellSizer.Add(self.SpinText4,0)
        cellSizer.Add((5,10),0)
        self.SpinText4.SetToolTipString('Enter no. formula units per volume')
        self.SpinText4.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText4, id=wxID_SPINTEXT4)
        
        cellSizer.Add((5,10),0)
        cellSizer.Add(wx.StaticText(parent=self.panel, label='Sample R:'),0,
            wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        cellSizer.Add((5,10),0)
        self.SpinText5 = wx.TextCtrl(id=wxID_SPINTEXT5, parent=self.panel, 
              size=wx.Size(50,20), value = "%6.2f" % (self.Radius),style=wx.TE_PROCESS_ENTER )
        cellSizer.Add(self.SpinText5,0)
        cellSizer.Add((5,10),0)
        self.SpinText5.SetToolTipString('Enter sample radius in mm')
        self.SpinText5.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText5, id=wxID_SPINTEXT5)

        cellSizer.Add((5,10),0)
        cellSizer.Add(wx.StaticText(parent=self.panel, label='packing:'),0,
            wx.ALIGN_CENTER_VERTICAL|wx.EXPAND)
        cellSizer.Add((5,10),0)
        self.SpinText6 = wx.TextCtrl(id=wxID_SPINTEXT6, parent=self.panel, 
              size=wx.Size(50,20), value = "%6.2f" % (self.Pack),style=wx.TE_PROCESS_ENTER )
        cellSizer.Add(self.SpinText6,0)
        cellSizer.Add((5,10),0)
        self.SpinText6.SetToolTipString('Enter packing fraction')
        self.SpinText6.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText6, id=wxID_SPINTEXT5)

        mainSizer.Add(cellSizer,0)
        mainSizer.Add((10,10),0)
        self.panel.SetSizer(mainSizer)
        self.panel.Fit()
        self.panel.GetParent().SetSize()

    def __init__(self, parent):
        self._init_ctrls(parent)
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['legend.fontsize'] = 10
        self.Bind(wx.EVT_CLOSE, self.ExitMain)
        self.Lines = []
        self.linePicked = None

    def ExitMain(self, event):
        sys.exit()
        
    def OnExitMenu(self, event):
        pylab.close('all')
        self.Close()

    def OnNewMenu(self, event):
        ElList = []
        for Elem in self.Elems: ElList.append(Elem[0])
        PE = Element.PickElement(self,ElList)
        if PE.ShowModal() == wx.ID_OK:
            for El in PE.Elem:
                ElemSym = El.strip().upper()
                if ElemSym not in ElList:
                    atomData = Element.GetAtomInfo(ElemSym)
                    FormFactors = Element.GetFormFactorCoeff(ElemSym)
                    for FormFac in FormFactors:
                        FormSym = FormFac['Symbol'].strip()
                        if FormSym == ElemSym:
                            Z = FormFac['Z']                #At. No.
                            N = 1.                          #no atoms / formula unit
                            Orbs = Element.GetXsectionCoeff(ElemSym)
                            Elem = [ElemSym,Z,N,FormFac,Orbs,atomData]
                    self.Elems.append(Elem)
            self.Delete.Enable(True)
            self.panel.Destroy()
            self.DrawPanel()
            self.SetWaveEnergy(Absorb.Wave)
        PE.Destroy()
            
    def OnDeleteMenu(self, event):
        if len(self.Elems):
            ElList = []
            for Elem in self.Elems: ElList.append(Elem[0])
            S = []
            DE = Element.DeleteElement(self)
            if DE.ShowModal() == wx.ID_OK:
                El = DE.GetDeleteElement().strip().upper()
                for Elem in self.Elems:
                    if Elem[0] != El:
                        S.append(Elem)
                self.Elems = S
                self.CalcFPPS()
                if not self.Elems:
                    self.Delete.Enable(False)
                self.panel.Destroy()
                self.DrawPanel()
                self.SetWaveEnergy(self.Wave)
        
    def OnCrkaMenu(self, event):
        self.SetWaveEnergy(2.28962)

    def OnMnkaMenu(self, event):
        self.SetWaveEnergy(2.10174)

    def OnFekaMenu(self, event):
        self.SetWaveEnergy(1.93597)

    def OnCokaMenu(self, event):
        self.SetWaveEnergy(1.78896)

    def OnNikaMenu(self, event):
        self.SetWaveEnergy(1.65784)

    def OnCukaMenu(self, event):
        self.SetWaveEnergy(1.54052)

    def OnZnkaMenu(self, event):
        self.SetWaveEnergy(1.43510)

    def OnMokaMenu(self, event):
        self.SetWaveEnergy(0.70926)

    def OnAgkaMenu(self, event):
        self.SetWaveEnergy(0.55936)
        
    def OnNumElem(self, event):
        for Elem in self.Elems:
            if event.GetEventObject().GetName() == Elem[0]:
                Elem[2] = float(event.GetEventObject().GetValue())
                event.GetEventObject().SetValue("%8.2f" % (Elem[2]))
                self.SetWaveEnergy(Absorb.Wave)                
        
    def OnSpinText1(self, event):
        self.SetWaveEnergy(float(self.SpinText1.GetValue()))
        
    def OnSpinText2(self, event):
        self.SetWaveEnergy(self.Kev/(float(self.SpinText2.GetValue())))
        
    def OnSpinText3(self,event):
        self.Volume = max(10.,float(self.SpinText3.GetValue()))
        self.ifVol = True
        self.SetWaveEnergy(self.Wave)
        
    def OnSpinText4(self,event):
        self.Zcell = max(1,float(self.SpinText4.GetValue()))
        self.SetWaveEnergy(self.Wave)
        
    def OnSpinText5(self, event):
        self.Radius = max(0.01,float(self.SpinText5.GetValue()))
        self.SetWaveEnergy(self.Wave)
       
    def OnSpinText6(self, event):
        self.Pack = min(1.0,max(0.01,float(self.SpinText6.GetValue())))
        self.SetWaveEnergy(self.Wave)
       
    def OnSpinButton(self, event):
        if self.ifWave:
            Wave = float(self.SpinButton.GetValue())/10000.
        else:
            Wave = self.Kev/(float(self.SpinButton.GetValue())/10000.)
        self.SetWaveEnergy(Wave)

    def OnSlider1(self, event):
        if self.ifWave:
            Wave = float(self.slider1.GetValue())/1000.
        else:
            Wave = self.Kev/(float(self.slider1.GetValue())/1000.)
        self.SetWaveEnergy(Wave)
        
    def SetWaveEnergy(self,Wave):
        self.Wave = Wave
        self.Energy = self.Kev/self.Wave
        self.Energy = round(self.Energy,4)
        E = self.Energy
        DE = E*self.Eres                         #smear by defined source resolution
        self.SpinText1.SetValue("%6.4f" % (self.Wave))
        self.SpinText2.SetValue("%7.4f" % (self.Energy))
        self.SpinText1.Update()
        self.SpinText2.Update()
        if self.ifWave:
            self.slider1.SetValue(int(1000.*self.Wave))
            self.SpinButton.SetValue(int(10000.*self.Wave))
        else:
            self.slider1.SetValue(int(1000.*self.Energy))
            self.SpinButton.SetValue(int(10000.*self.Energy))
        Text = ''
        if not self.ifVol:
            self.Volume = 0
            for Elem in self.Elems:
                self.Volume += 10.*Elem[2]
        muT = 0
        Mass = 0
        for Elem in self.Elems:
            Mass += self.Zcell*Elem[2]*Elem[5]['Mass']
            r1 = Element.FPcalc(Elem[4],E+DE)
            r2 = Element.FPcalc(Elem[4],E-DE)
            Els = Elem[0]
            Els = Els.ljust(2).lower().capitalize()
            mu = 0
            if Elem[1] > 78 and self.Energy+DE > self.Kev/0.16:
                mu = self.Zcell*Elem[2]*(r1[2]+r2[2])/2.0
                Text += "%s\t%s%8.2f  %s%6s  %s%6.3f  %s%10.2f %s\n" %    (
                    'Element= '+str(Els),"N = ",Elem[2]," f'=",'not valid',
                    ' f"=',(r1[1]+r2[1])/2.0,' mu=',mu,'barns')
            elif Elem[1] > 94 and self.Energy-DE < self.Kev/2.67:
                mu = 0
                Text += "%s\t%s%8.2f  %s%6s  %s%6s  %s%10s%s\n" %    (
                    'Element= '+str(Els),"N = ",Elem[2]," f'=",'not valid',
                    ' f"=','not valid',' mu=','not valid')
            else:
                mu = self.Zcell*Elem[2]*(r1[2]+r2[2])/2.0
                Text += "%s\t%s%8.2f  %s%6.3f  %s%6.3f  %s%10.2f %s\n" %    (
                    'Element= '+str(Els),"N = ",Elem[2]," f'=",(r1[0]+r2[0])/2.0,
                    ' f"=',(r1[1]+r2[1])/2.0,' mu=',mu,'barns')
            muT += mu
        
        if self.Volume:
            Text += "%s %s%10.2f %s\n" % ("Total",' mu=',self.Pack*muT/self.Volume,'cm-1')
            self.Results.SetValue(Text)
            Text += "%s%10.2f" % ('Total muR=',self.Radius*self.Pack*muT/(10.0*self.Volume))                
            if self.ifVol:
                Text += '%s%6.3f %s\n' % (', Theor. density=',Mass/(0.602*self.Volume),'g/cm^3')
            else:  
                Text += '%s%6.3f %s\n' % (', Est. density=',Mass/(0.602*self.Volume),'g/cm^3')
            self.Results.SetValue(Text)
        self.Results.Update()
        self.SpinText3.SetValue(str(self.Volume))
        self.SpinText3.Update()
        self.CalcFPPS()
        self.UpDateAbsPlot(Wave)

    def CalcFPPS(self):
        """generate f" curves for selected elements
           does constant delta-lambda/lambda steps over defined range
        """
        FPPS = []
        if self.Elems:
            wx.BeginBusyCursor()
            Corr = self.Zcell*self.Radius*self.Pack/(10.0*self.Volume)
            try:
                muT = []
                for iE,Elem in enumerate(self.Elems):
                    Els = Elem[0]
                    Els = Els = Els.ljust(2).lower().capitalize()
                    Wmin = self.Wmin
                    Wmax = self.Wmax
                    Z = Elem[1]
                    lWmin = math.log(Wmin)
                    N = int(round(math.log(Wmax/Wmin)/self.Wres))    #number of constant delta-lam/lam steps
                    I = range(N+1)
                    Ws = []
                    for i in I: Ws.append(math.exp(i*self.Wres+lWmin))
                    mus = []
                    Es = []
                    for j,W in enumerate(Ws):
                        E = self.Kev/W
                        DE = E*self.Eres                         #smear by defined source resolution
                        res1 = Element.FPcalc(Elem[4],E+DE)
                        res2 = Element.FPcalc(Elem[4],E-DE)
                        muR = Corr*Elem[2]*(res1[2]+res2[2])/2.0
                        mus.append(muR)
                        if iE:
                            muT[j] += muR
                        else:
                            muT.append(muR)
                        Es.append(E)
                    if self.ifWave:
                        Fpps = (Els,Ws,mus)
                    else:
                        Fpps = (Els,Es,mus)
                    FPPS.append(Fpps)
                Fpps = ('Total',Ws,muT)
                FPPS.append(Fpps)
            finally:
                wx.EndBusyCursor()
        self.FPPS = FPPS

    def OnChoice1(self, event):
        if event.GetString() == "Wavelength":
            self.ifWave = True
            self.NewFPPlot = True
            self.Wave = round(self.Wave,4)
            self.slider1.SetRange(int(1000.*self.Wmin),int(1000.*self.Wmax))
            self.slider1.SetValue(int(1000.*self.Wave))
            self.SpinButton.SetRange(int(10000.*self.Wmin),int(10000.*self.Wmax))
            self.SpinButton.SetValue(int(10000.*self.Wave))
            self.SpinText1.SetValue("%6.4f" % (self.Wave))
            self.SpinText2.SetValue("%7.4f" % (self.Energy))
            self.SpinButton.SetToolTipString('Fine control of wavelength')
            self.slider1.SetToolTipString('Coarse control of wavelength')
        else:
            self.ifWave = False
            self.NewFPPlot = True
            Emin = self.Kev/self.Wmax
            Emax = self.Kev/self.Wmin
            self.Energy = round(self.Energy,4)
            self.slider1.SetRange(int(1000.*Emin),int(1000.*Emax))
            self.slider1.SetValue(int(1000.*self.Energy))
            self.SpinButton.SetRange(int(10000.*Emin),int(10000.*Emax))
            self.SpinButton.SetValue(int(10000.*self.Energy))
            self.SpinText1.SetValue("%6.4f" % (self.Wave))
            self.SpinText2.SetValue("%7.4f" % (self.Energy))
            self.SpinButton.SetToolTipString('Fine control of energy')
            self.slider1.SetToolTipString('Coarse control of energy')
        self.CalcFPPS()
        self.UpDateAbsPlot(self.Wave)
        
    def UpDateAbsPlot(self,Wave):
        """Plot mu vs wavelength 0.05-3.0A"""
        try:
            self.fplot.canvas.set_window_title('X-Ray Absorption')
            newPlot = False
        except:
            self.fplot = pylab.figure(facecolor='white',figsize=(8,6))  #BTW: default figsize is (8,6)
            self.fplot.canvas.set_window_title('X-Ray Absorption')
            self.fplot.canvas.mpl_connect('pick_event', self.OnPick)
            self.fplot.canvas.mpl_connect('button_release_event', self.OnRelease)
            self.fplot.canvas.mpl_connect('motion_notify_event', self.OnMotion)
            newPlot = True
        ax = self.fplot.add_subplot(111)
        ax.clear()
        ax.set_title('X-Ray Absorption',x=0,ha='left')
        ax.set_ylabel(r"$\mu R$",fontsize=14)
        Ymin = 0.0
        Ymax = 0.0
        if self.FPPS: 
            for Fpps in self.FPPS:
                Ymin = min(Ymin,min(Fpps[2]))
                Ymax = max(Ymax,max(Fpps[2]))
                fppsP1 = np.array(Fpps[1])
                fppsP2 = np.array(Fpps[2])
                ax.plot(fppsP1,fppsP2,label=r'$\mu R$ '+Fpps[0])
        if self.ifWave: 
            ax.set_xlabel(r'$\mathsf{\lambda, \AA}$',fontsize=14)
            ax.axvline(x=Wave,picker=3,color='black')
        else:
            ax.set_xlabel(r'$\mathsf{E, keV}$',fontsize=14)
            ax.set_xscale('log')
            ax.axvline(x=self.Kev/Wave,picker=3,color='black')
        ax.axhline(y=1.0,color='b')
        ax.axhline(y=5.0,color='r')
        ax.set_ylim(Ymin,Ymax)
        if self.FPPS:
            legend = ax.legend(loc='best')
        
        if newPlot:
            newPlot = False
            pylab.show()
        else:
            pylab.draw()
        
    def OnPick(self, event):
        self.linePicked = event.artist
        
    def OnMotion(self,event):
        if self.linePicked:
            xpos = event.xdata
            if xpos and hasattr(self.fplot.canvas,'SetToolTipString'):
                self.fplot.canvas.SetToolTipString('%9.3f'%(xpos))
                
    def OnRelease(self, event):
        if self.linePicked is None: return
        self.linePicked = None
        xpos = event.xdata
        if xpos:
            if self.ifWave:
                Wave = xpos
            else:
                Wave = self.Kev/xpos               
            self.SetWaveEnergy(Wave)
            
    def OnABOUTItems0Menu(self, event):
        info = wx.AboutDialogInfo()
        info.Name = 'Absorb'
        info.Version = __version__
        info.Copyright = '''
Robert B. Von Dreele, 2009(C)
Argonne National Laboratory
This product includes software developed 
by the UChicago Argonne, LLC, as 
Operator of Argonne National Laboratory.        '''
        info.Description = '''
For calculating X-ray absorbtion factors to 250keV for cylindrical      
powder samples; based on Fortran program Fprime of Cromer & Liberman 
corrected for Kissel & Pratt energy term; Jensen term not included
        '''
        wx.AboutBox(info)

class AbsorbApp(wx.App):
    def OnInit(self):
        self.main = Absorb(None)
        self.main.Show()
        self.SetTopWindow(self.main)
        self.main.OnNewMenu(None)
        return True

def main():
    application = AbsorbApp(0)
    application.MainLoop()

if __name__ == '__main__':
    main()
