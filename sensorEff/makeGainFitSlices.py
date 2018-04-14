import os
import sys
import ROOT as r
import numpy as np
import matplotlib
import matplotlib.pyplot as plt

r.gROOT.SetBatch(1)
r.gStyle.SetOptFit(0)
r.gStyle.SetOptStat(0)

os.system('mkdir -p plots')

# Setup langus fit for amp
r.gROOT.ProcessLine(".L langaus.C+")
from ROOT import langaufit, langaupro
from array import array

def dofitLandGaus(hph, pltname='', *args, **kwargs):

    fr   = array('d', [kwargs.get('frmin', 50), kwargs.get('frmax', 950)])
    fp   = array('d', [0, 0, 0, 0])
    fpe  = array('d', [0, 0, 0, 0])
    pllo = array('d', [0, 0, 0, 0])
    plhi = array('d', [10000,  1000, 100000,  100])
    sv   = array('d', [150, kwargs.get('mpv', 300), 6000, 30])

    fitr = langaufit(hph,fr,sv,pllo,plhi,fp,fpe);
    maxx = r.Double()
    fwhm = r.Double()
    langaupro(fp, maxx, fwhm)

    if pltname != "":
        c1 = r.TCanvas("c1", "c1", 600, 400)
        fitr.SetLineWidth(2)
        fitr.SetLineColor(r.kOrange+10)
        hph.SetLineColor(r.kAzure-3)
        hph.Draw()
        fitr.Draw("same")

        c1.SetTitle("Landau * Gauss fit to time window integral")
        c1.Print("plots/h_fit"+pltname+".pdf")

    return fp[1], fpe[1], fitr


f1 = r.TFile('./W6_eff_Apr13/histos_w6eff_v7_Apr13.root')

keys = f1.GetListOfKeys()

hnames = [k.GetName() for k in keys if 'slice' in k.GetName() ]

hints = {}
xslis = {}
sumvs = {}

for idx in [10, 13, 14, 7]:
    hints[idx] = [f1.Get(hn) for hn in hnames if 'int[%d]' % idx in hn]

xlis = []
mpvs = []
errs = []

for idx in [10, 13]:
    xslis[idx] = []
    sumvs[idx] = 0
    for h in hints[idx]:
        xslice = int(h.GetName().split('slice')[1][1:-1]) - 200
        xslis[idx].append(xslice)
        xlis.append(xslice)
        v, e, _ = dofitLandGaus(h, '_ch{}_slice{}'.format(idx, xslice))
        # v, e, _ = dofitLandGaus(h)
        mpvs.append(v)
        errs.append(e)
        sumvs[idx] += v

hbot = r.TH1F("h_bot", "twinint MPV slices on W6 2x8 ch10, ch13; x slice [#mum];twinint MPV", 50, 17000, 23000)

for i, x in enumerate(xlis):
    hbot.SetBinContent(hbot.FindBin(x), mpvs[i])
    hbot.SetBinError(hbot.FindBin(x), errs[i])

hbot.GetYaxis().SetRangeUser(0, 400)
hbot.SetMarkerStyle(4)
hbot.SetMarkerSize(1.3)

c1 = r.TCanvas("c1", "c1", 600, 400)
hbot.Fit("pol1", "Q")
hbot.GetFunction("pol1").SetLineColor(46)
hbot.Draw()

avg10 = r.TF1("avg10", "{}".format(sumvs[10]/4), 17000, 23000)
avg10.SetLineStyle(9)
avg10.SetLineColor(14)
avg10.Draw("same")

avg13 = r.TF1("avg13", "{}".format(sumvs[13]/4), 17000, 23000)
avg13.SetLineStyle(9)
avg13.SetLineColor(30)
avg13.Draw("same")

c1.Print("plots/hbot_5.pdf")

c1.Clear()

for idx in [7, 14]:
    xslis[idx] = []
    sumvs[idx] = 0
    for h in hints[idx]:
        xslice = int(h.GetName().split('slice')[1][1:-1]) - 200
        xslis[idx].append(xslice)
        xlis.append(xslice)
        v, e, _ = dofitLandGaus(h, '_ch{}_slice{}'.format(idx, xslice))
        # v, e, _ = dofitLandGaus(h)
        mpvs.append(v)
        errs.append(e)
        sumvs[idx] += v

htop = r.TH1F("h_top", "twinint MPV x slices on W6 2x8 ch7, ch14; x slice [#mum];twinint MPV", 50, 17000, 23000)

for i, x in enumerate(xlis):
    htop.SetBinContent(htop.FindBin(x), mpvs[i])
    htop.SetBinError(htop.FindBin(x), errs[i])

htop.GetYaxis().SetRangeUser(0, 400)
htop.SetMarkerStyle(4)
htop.SetMarkerSize(1.3)

c1 = r.TCanvas("c1", "c1", 600, 400)
htop.Fit("pol1", "Q")
htop.GetFunction("pol1").SetLineColor(46)
htop.Draw()

avg7 = r.TF1("avg7", "{}".format(sumvs[7]/4), 17000, 23000)
avg7.SetLineStyle(9)
avg7.SetLineColor(14)
avg7.Draw("same")

avg14 = r.TF1("avg14", "{}".format(sumvs[14]/4), 17000, 23000)
avg14.SetLineStyle(9)
avg14.SetLineColor(30)
avg14.Draw("same")

c1.Print("plots/htop_5.pdf")

# fig, ax = plt.subplots()
# ax.plot(xlis, mpvs, 'o')

# plt.show()
