"""main Fprime routines
   Copyright: 2008, Robert B. Von Dreele (Argonne National Laboratory)
"""
import os
import math
import wx
import Element
import matplotlib as mpl
import numpy
# use the newer wxmpl when needed
(main,sub) = mpl.__version__.split('.')[0:2]
if int(main) > 0 or int(sub) > 91: 
    import wxmpl131 as wxmpl
else:
    import wxmpl129a as wxmpl

import pylab
import sys

# print versions
print "Available python module versions for pyFprime:"
print "python:     ",sys.version[:5]
print "wxpython:   ",wx.__version__
print "matplotlib: ",mpl.__version__
print "numpy:      ",numpy.__version__
print "wxmpl:      ",wxmpl.__version__

__version__ = '0.1.2'

def create(parent):
    return Fprime(parent)

[wxID_FPRIME, wxID_FPRIMEBUTTON1, wxID_FPRIMEBUTTON2, wxID_SPINTEXT1, wxID_SPINTEXT2,
 wxID_FPRIMERESULTS,wxID_FPRIMESLIDER1, wxID_SPINBUTTON,
] = [wx.NewId() for _init_ctrls in range(8)]

[wxID_FPRIMEEXIT, wxID_FPRIMEDELETE, wxID_FPRIMENEW, 
] = [wx.NewId() for _init_coll_FPRIME_Items in range(3)]

[wxID_FPRIMEKALPHAAGKA, wxID_FPRIMEKALPHACOKA, wxID_FPRIMEKALPHACRKA, 
 wxID_FPRIMEKALPHACUKA, wxID_FPRIMEKALPHAFEKA, wxID_FPRIMEKALPHAMNKA, 
 wxID_FPRIMEKALPHAMOKA, wxID_FPRIMEKALPHANIKA, wxID_FPRIMEKALPHAZNKA, 
] = [wx.NewId() for _init_coll_KALPHA_Items in range(9)]

[wxID_FPRIMEABOUT] = [wx.NewId() for _init_coll_ABOUT_Items in range(1)]

class Fprime(wx.Frame):
    Elems = []
    Wave = 1.5405      #CuKa default
    Kev = 12.397639    #keV for 1A x-rays
    Wmin = 0.05        #wavelength range
    Wmax = 3.0
    Wres = 0.004094    #plot resolution step size as const delta-lam/lam - gives 1000 steps for Wmin to Wmax
    Eres = 1.5e-4      #typical energy resolution for synchrotron x-ray sources
    ffpfignum = 1
    fppfignum = 2
    Energy = Kev/Wave
    ifWave = True
    NewFPPlot = True
    FFxaxis = 'S'      #default form factor plot is vs sin(theta)/lambda
    def _init_coll_ABOUT_Items(self, parent):

        parent.Append(help='', id=wxID_FPRIMEABOUT, kind=wx.ITEM_NORMAL,
              text='About')
        self.Bind(wx.EVT_MENU, self.OnABOUTItems0Menu, id=wxID_FPRIMEABOUT)

    def _init_coll_menuBar1_Menus(self, parent):

        parent.Append(menu=self.FPRIME, title='Fprime')
        parent.Append(menu=self.KALPHA, title='Kalpha')
        parent.Append(menu=self.ABOUT, title='About')

    def _init_coll_KALPHA_Items(self, parent):
        "Set of characteristic radiation from sealed tube sources"

        parent.Append(help='', id=wxID_FPRIMEKALPHACRKA, kind=wx.ITEM_NORMAL,
              text='CrKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHAMNKA, kind=wx.ITEM_NORMAL,
              text='MnKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHAFEKA, kind=wx.ITEM_NORMAL,
              text='FeKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHACOKA, kind=wx.ITEM_NORMAL,
              text='CoKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHANIKA, kind=wx.ITEM_NORMAL,
              text='NiKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHACUKA, kind=wx.ITEM_NORMAL,
              text='CuKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHAZNKA, kind=wx.ITEM_NORMAL,
              text='ZnKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHAMOKA, kind=wx.ITEM_NORMAL,
              text='MoKa')
        parent.Append(help='', id=wxID_FPRIMEKALPHAAGKA, kind=wx.ITEM_NORMAL,
              text='AgKa')
        self.Bind(wx.EVT_MENU, self.OnKALPHACrkaMenu, id=wxID_FPRIMEKALPHACRKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHAMnkaMenu, id=wxID_FPRIMEKALPHAMNKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHAFekaMenu, id=wxID_FPRIMEKALPHAFEKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHACokaMenu, id=wxID_FPRIMEKALPHACOKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHANikaMenu, id=wxID_FPRIMEKALPHANIKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHACukaMenu, id=wxID_FPRIMEKALPHACUKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHAZnkaMenu, id=wxID_FPRIMEKALPHAZNKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHAMokaMenu, id=wxID_FPRIMEKALPHAMOKA)
        self.Bind(wx.EVT_MENU, self.OnKALPHAAgkaMenu, id=wxID_FPRIMEKALPHAAGKA)

    def _init_coll_FPRIME_Items(self, parent):
        # generated method, don't edit

        parent.Append(help='Add new element', id=wxID_FPRIMENEW, kind=wx.ITEM_NORMAL,
              text='&New Element')
        self.Delete = parent.Append(help='Delete an element', id=wxID_FPRIMEDELETE, kind=wx.ITEM_NORMAL,
              text='&Delete Element')
        self.Delete.Enable(False)
        parent.Append(help='Exit Fprime', id=wxID_FPRIMEEXIT, kind=wx.ITEM_NORMAL,
              text='&Exit')
        self.Bind(wx.EVT_MENU, self.OnFPRIMEExitMenu, id=wxID_FPRIMEEXIT)
        self.Bind(wx.EVT_MENU, self.OnFPRIMENewMenu, id=wxID_FPRIMENEW)
        self.Bind(wx.EVT_MENU, self.OnFPRIMEDeleteMenu, id=wxID_FPRIMEDELETE)

    def _init_utils(self):
        # generated method, don't edit
        self.FPRIME = wx.Menu(title='')

        self.KALPHA = wx.Menu(title='')
        self.KALPHA.SetEvtHandlerEnabled(True)

        self.ABOUT = wx.Menu(title='')

        self.menuBar1 = wx.MenuBar()

        self._init_coll_FPRIME_Items(self.FPRIME)
        self._init_coll_KALPHA_Items(self.KALPHA)
        self._init_coll_ABOUT_Items(self.ABOUT)
        self._init_coll_menuBar1_Menus(self.menuBar1)

    def _init_ctrls(self, parent):
        # generated method, don't edit
        wx.Frame.__init__(self, id=wxID_FPRIME, name='Fprime', parent=parent,
              size=wx.Size(650, 350),style=wx.DEFAULT_FRAME_STYLE, title='Fprime')              
        self._init_utils()
        self.SetMenuBar(self.menuBar1)

        self.Results = wx.TextCtrl(id=wxID_FPRIMERESULTS, name='Results',
              parent=self, pos=wx.Point(25,25), size=wx.Size(600, 150),
              style=wx.TE_MULTILINE, value='', )
        self.Results.SetEditable(False)

        self.SpinText1 = wx.TextCtrl(id=wxID_SPINTEXT1, parent=self, pos=wx.Point(25,200),
              size=wx.Size(100,20), value = "%6.4f" % (self.Wave),style=wx.TE_PROCESS_ENTER )
        self.SpinText1.SetToolTipString('Enter desired wavelength')
        self.SpinText1.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText1, id=wxID_SPINTEXT1)
                
        self.SpinText2 = wx.TextCtrl(id=wxID_SPINTEXT2, parent=self, pos=wx.Point(175,200),
              size=wx.Size(100,20), value = "%7.4f" % (self.Energy),style=wx.TE_PROCESS_ENTER )
        self.SpinText2.SetToolTipString('Enter desired energy')
        self.SpinText2.Bind(wx.EVT_TEXT_ENTER, self.OnSpinText2, id=wxID_SPINTEXT2)
        
        wx.StaticText(parent=self, pos=wx.Point(25,180),label=' Wavelength:',size=wx.Size(80,15)).SetBackgroundColour('White')
        wx.StaticText(parent=self, pos=wx.Point(175,180),label=' Energy:',size=wx.Size(75,15)).SetBackgroundColour('White')
        
        self.SpinButton = wx.SpinButton(id=wxID_SPINBUTTON, parent=self, pos=wx.Point(25,225),
              name='SpinButton',size=wx.Size(25,24), style=wx.SP_VERTICAL | wx.SP_ARROW_KEYS)
        self.SpinButton.SetToolTipString('Fine control of wavelength')
        self.SpinButton.SetRange(int(10000.*self.Wmin),int(10000.*self.Wmax))
        self.SpinButton.SetValue(int(10000.*self.Wave))
        self.SpinButton.Bind(wx.EVT_SPIN, self.OnSpinButton, id=wxID_SPINBUTTON)

        self.slider1 = wx.Slider(id=wxID_FPRIMESLIDER1, maxValue=int(1000.*self.Wmax),
              minValue=int(1000.*self.Wmin), name='slider1', parent=self, pos=wx.Point(50,
              225), size=wx.Size(550, 24), style=wx.SL_HORIZONTAL,
              value=int(self.Wave*1000.), )
        self.slider1.SetToolTipString('Coarse control of wavelength')
        self.slider1.Bind(wx.EVT_SLIDER, self.OnSlider1, id=wxID_FPRIMESLIDER1)
        
        wx.StaticText(parent=self, pos=wx.Point(50,257),label=' Plot scales:',size=wx.Size(75,15)).SetBackgroundColour('White')

        self.button1 = wx.Button(id=wxID_FPRIMEBUTTON1, label='Wavelength',
              name='button1', parent=self, pos=wx.Point(150, 255),style=0)
        self.button1.SetToolTipString('Switch between wavelength and energy scale')
        self.button1.Bind(wx.EVT_BUTTON, self.OnButton1, id=wxID_FPRIMEBUTTON1)

        self.button2 = wx.Button(id=wxID_FPRIMEBUTTON2, label='sin(theta)/lambda',
              name='button2', parent=self, pos=wx.Point(250, 255), style=0)
        self.button2.SetToolTipString('Switch between sin(theta)/lambda, q and 2-theta scale')
        self.button2.Bind(wx.EVT_BUTTON, self.OnButton2, id=wxID_FPRIMEBUTTON2)

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.ffplot = pylab.figure(self.ffpfignum,facecolor='white')
        self.fpplot = pylab.figure(self.fppfignum,facecolor='white')
        self.ffplot.canvas.set_window_title('X-ray Form Factors')
        self.fpplot.canvas.set_window_title('X-Ray Resonant Scattering Factors')
        self.fpplot.canvas.mpl_connect('pick_event', self.OnPick)
        self.fpplot.canvas.mpl_connect('button_release_event', self.OnRelease)
        self.fpplot.canvas.mpl_connect('motion_notify_event', self.OnMotion)
        mpl.rcParams['axes.grid'] = True
        mpl.rcParams['legend.fontsize'] = 10
        self.Bind(wx.EVT_CLOSE, self.ExitMain)
        self.Lines = []
        self.linePicked = None

    def ExitMain(self, event):
        sys.exit()
        
    def OnFPRIMEExitMenu(self, event):
        pylab.close('all')
        self.Close()

    def OnFPRIMENewMenu(self, event):
        PE = Element.PickElement(self)
        ElList = []
        for Elem in self.Elems: ElList.append(Elem[0])
        Elem = ()
        if PE.ShowModal() == wx.ID_OK:
            ElemSym = PE.Elem.strip().upper()
            if ElemSym not in ElList:
                FormFactors = Element.GetFormFactorCoeff(ElemSym)
                for FormFac in FormFactors:
                    FormSym = FormFac['Symbol'].strip()
                    if FormSym == ElemSym:
                        Z = FormFac['Z']
                        Orbs = Element.GetXsectionCoeff(ElemSym)
                        Elem += (ElemSym,Z,FormFac,Orbs)
                Fprime.Elems.append(Elem)
            self.Delete.Enable(True)
            self.CalcFPPS()
            self.SetWaveEnergy(Fprime.Wave)
        PE.Destroy()
            
    def OnFPRIMEDeleteMenu(self, event):
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
                Fprime.Elems = S
                self.CalcFPPS()
                if not self.Elems:
                    self.Delete.Enable(False)
                self.SetWaveEnergy(self.Wave)
        
    def OnKALPHACrkaMenu(self, event):
        self.SetWaveEnergy(2.28962)

    def OnKALPHAMnkaMenu(self, event):
        self.SetWaveEnergy(2.10174)

    def OnKALPHAFekaMenu(self, event):
        self.SetWaveEnergy(1.93597)

    def OnKALPHACokaMenu(self, event):
        self.SetWaveEnergy(1.78896)

    def OnKALPHANikaMenu(self, event):
        self.SetWaveEnergy(1.65784)

    def OnKALPHACukaMenu(self, event):
        self.SetWaveEnergy(1.54052)

    def OnKALPHAZnkaMenu(self, event):
        self.SetWaveEnergy(1.43510)

    def OnKALPHAMokaMenu(self, event):
        self.SetWaveEnergy(0.70926)

    def OnKALPHAAgkaMenu(self, event):
        self.SetWaveEnergy(0.55936)
        
    def OnSpinText1(self, event):
        self.SetWaveEnergy(float(self.SpinText1.GetValue()))
        
    def OnSpinText2(self, event):
        self.SetWaveEnergy(self.Kev/(float(self.SpinText2.GetValue())))
       
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
        
    def UpDateFPPlot(self,Wave):
        """Plot f' & f" vs wavelength 0.05-3.0A"""
        ax = self.fpplot.add_subplot(111)
        if not self.NewFPPlot:
            xlim = ax.get_xlim()
            ylim = ax.get_ylim()
        ax.clear()
        ax.set_title('X-ray resonant scattering factors')
        ax.set_ylabel("f',"+' f", e-',fontsize=12)
        if self.ifWave: 
            ax.set_xlabel(r'$\mathsf{wavelength, \AA}$',fontsize=14)
            ax.set_xlim(self.Wmin,self.Wmax)
            ax.axvline(x=Wave,picker=3)
        else:
            ax.set_xlabel(r'$\mathsf{Energy, keV}$',fontsize=14)
            ax.set_xscale('log')
            ax.set_xlim(self.Kev/self.Wmax,self.Kev/self.Wmin)
            ax.axvline(x=self.Kev/Wave,picker=3)
        Ymin = 0.0
        Ymax = 0.0
        if self.FPPS: 
            for Fpps in self.FPPS:
                Ymin = min(Ymin,min(Fpps[2]),min(Fpps[3]))
                Ymax = max(Ymax,max(Fpps[2]),max(Fpps[3]))
                ax.plot(Fpps[1],Fpps[2],label=Fpps[0]+" f'")
                ax.plot(Fpps[1],Fpps[3],label=Fpps[0]+' f"')
        ax.set_ylim(Ymin,Ymax)
        if self.NewFPPlot:
            self.NewFPPlot = False
        else:
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)
        ax.legend(loc='best',numpoints=2)
        pylab.figure(self.fppfignum)
        pylab.draw()
        
    def OnPick(self, event):
        self.linePicked = event.artist
        
    def OnMotion(self,event):
        if self.linePicked:
            xpos = event.xdata
            if xpos and hasattr(self.fpplot.canvas,'SetToolTipString'):
                self.fpplot.canvas.SetToolTipString('%9.3f'%(xpos))
    def OnRelease(self, event):
        if self.linePicked is None: return
        xpos = event.xdata
        if xpos:
            if self.ifWave:
                Wave = xpos
            else:
                Wave = self.Kev/xpos               
            self.SetWaveEnergy(Wave)
            
        self.linePicked = None

    def UpDateFFPlot(self):
        "generate a set of form factor curves & plot them vs sin-theta/lambda or q or 2-theta"
        StlMax = math.sin(80.0*math.pi/180.)/self.Wave
        if StlMax > 2.0:StlMax = 2.0
        Stl = pylab.arange(0.,StlMax,.01)
        ax = self.ffplot.add_subplot(111)
        ax.clear()
        ax.set_title('X-ray form factors')
        if self.FFxaxis == 'S':
            ax.set_xlabel(r'$\mathsf{sin(\theta)/\lambda}$',fontsize=14)
        elif self.FFxaxis == 'T':
            ax.set_xlabel(r'$\mathsf{2\theta}$',fontsize=14)
        else:
            ax.set_xlabel(r'$Q, \AA$',fontsize=14)
        ax.set_ylabel('f, e-',fontsize=12)
        E = self.Energy
        DE = E*self.Eres                         #smear by defined source resolution
        Ymax = 0.0
        for Elem in self.Elems:
            Els = Elem[0]
            Els = Els = Els.ljust(2).lower().capitalize()
            Ymax = max(Ymax,Elem[1])
            res1 = Element.FPcalc(Elem[3],E+DE)
            res2 = Element.FPcalc(Elem[3],E-DE)
            res = (res1[0]+res2[0])/2.0
            if Elem[1] > 78 and self.Energy > self.Kev/0.16: res = 0.0
            if Elem[1] > 94 and self.Energy < self.Kev/2.67: res = 0.0
            Els = Elem[0]
            Els = Els.ljust(2).lower().capitalize()
            X = []
            ff = []
            for S in Stl: 
                ff.append(Element.ScatFac(Elem[2],S)+res)
                if self.FFxaxis == 'S':
                    X.append(S)
                elif self.FFxaxis == 'T':
                    X.append(360.0*math.asin(S*self.Wave)/math.pi)
                else:
                    X.append(4.0*S*math.pi)
            ax.plot(X,ff,label=Els)
        ax.legend(loc='best',numpoints=2,)
        ax.set_ylim(0.0,Ymax+1.0)
        pylab.figure(self.ffpfignum)
        pylab.draw()

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
        for Elem in Fprime.Elems:
            r1 = Element.FPcalc(Elem[3],E+DE)
            r2 = Element.FPcalc(Elem[3],E-DE)
            Els = Elem[0]
            Els = Els.ljust(2).lower().capitalize()
            if Elem[1] > 78 and self.Energy+DE > self.Kev/0.16:
                Text += "%s\t%s%6s\t%s%6.3f  \t%s%10.2f \n" %    (
                    'Element= '+str(Els)," f'=",'not valid',
                    ' f"=',(r1[1]+r2[1])/2.0,' mu=',(r1[2]+r2[2])/2.0)
            elif Elem[1] > 94 and self.Energy-DE < self.Kev/2.67:
                Text += "%s\t%s%6s\t%s%6s\t%s%10s\n" %    (
                    'Element= '+str(Els)," f'=",'not valid',
                    ' f"=','not valid',' mu=','not valid')
            else:
                Text += "%s\t%s%6.3f   \t%s%6.3f  \t%s%10.2f \n" %    (
                    'Element= '+str(Els)," f'=",(r1[0]+r2[0])/2.0,
                    ' f"=',(r1[1]+r2[1])/2.0,' mu=',(r1[2]+r2[2])/2.0)
        self.Results.SetValue(Text)
        self.Results.Update()
        self.UpDateFPPlot(Wave)
        self.UpDateFFPlot()
        pylab.show()

    def CalcFPPS(self):
        """generate set of f' & f" curves for selected elements
           does constant delta-lambda/lambda steps over defined range
        """
        FPPS = []
        if self.Elems:
            wx.BeginBusyCursor()
            try:
                for Elem in self.Elems:
                    Els = Elem[0]
                    Els = Els = Els.ljust(2).lower().capitalize()
                    Wmin = self.Wmin
                    Wmax = self.Wmax
                    Z = Elem[1]
                    if Z > 78: Wmin = 0.16        #heavy element high energy failure of Cromer-Liberman
                    if Z > 94: Wmax = 2.67        #heavy element low energy failure of Cromer-Liberman
                    lWmin = math.log(Wmin)
                    N = int(round(math.log(Wmax/Wmin)/self.Wres))    #number of constant delta-lam/lam steps
                    I = range(N+1)
                    Ws = []
                    for i in I: Ws.append(math.exp(i*self.Wres+lWmin))
                    fps = []
                    fpps = []
                    Es = []
                    for W in Ws:
                        E = self.Kev/W
                        DE = E*self.Eres                         #smear by defined source resolution
                        res1 = Element.FPcalc(Elem[3],E+DE)
                        res2 = Element.FPcalc(Elem[3],E-DE)
                        fps.append((res1[0]+res2[0])/2.0)
                        fpps.append((res1[1]+res2[1])/2.0)
                        Es.append(E)
                    if self.ifWave:
                        Fpps = (Els,Ws,fps,fpps)
                    else:
                        Fpps = (Els,Es,fps,fpps)
                    FPPS.append(Fpps)
            finally:
                wx.EndBusyCursor()
        self.FPPS = FPPS

    def OnButton1(self, event):
        if event.GetEventObject().GetLabel() == "Energy":
            event.GetEventObject().SetLabel("Wavelength")
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
            event.GetEventObject().SetLabel("Energy")
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
        self.UpDateFPPlot(self.Wave)
        pylab.show()

    def OnButton2(self, event):
        if event.GetEventObject().GetLabel() == "sin(theta)/lambda":
            event.GetEventObject().SetLabel("Q")
            self.FFxaxis = 'Q'
        elif event.GetEventObject().GetLabel() == 'Q':
            event.GetEventObject().SetLabel('2-theta')
            self.FFxaxis = 'T'
        else:
            event.GetEventObject().SetLabel("sin(theta)/lambda")
            self.FFxaxis = 'S'
        self.UpDateFFPlot()
        pylab.show()

    def OnABOUTItems0Menu(self, event):
        info = wx.AboutDialogInfo()
        info.Name = 'pyFprime'
        info.Version = __version__
        info.Copyright = '''
Robert B. Von Dreele, 2008(C)
Argonne National Laboratory
This product includes software developed 
by the UChicago Argonne, LLC, as 
Operator of Argonne National Laboratory.        '''
        info.Description = '''
For calculating real and resonant X-ray scattering factors to 250keV;       
based on Fortran program of Cromer & Liberman corrected for 
Kissel & Pratt energy term; Jensen term not included
        '''
        wx.AboutBox(info)

