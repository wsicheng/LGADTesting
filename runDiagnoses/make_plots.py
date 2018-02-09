#! /usr/bin/env python

import ROOT
import os
import sys
import time

if len(sys.argv) < 3:
    print "  usage: {0} <input run list> <tag>"
    exit(1)

ROOT.gROOT.SetBatch(1)
#ROOT.TH1.StatOverflows(1)
ROOT.gStyle.SetOptFit()

# Setup langus fit for amp
ROOT.gROOT.ProcessLine(".L langaus.C+")
from ROOT import langaufit, langaupro
from array import array

outdir = sys.argv[2]

os.system("mkdir -p "+outdir)
# os.system("cp index.php "+outdir)

try:
    good_runs = [int(x) for x in sys.argv[1].split(",")]
except:
    good_runs = [int(x) for x in open(sys.argv[1])]

c = ROOT.TChain("pulse")
for run in good_runs:
    fname = os.path.join("/eos/uscms/store/user/cmstestbeam/ETL/MT6Section1Data/122017/OTSDAQ/DRSPixelMerged","Run{0}.root".format(run))
    if os.path.exists(fname):
        print "Adding run {0}...".format(run)
        c.Add(fname)

print "Total events:",c.GetEntries()

def dofitLandGaus(hph, *args, **kwargs):

    fr   = array('d', [kwargs.get('frmin', 0.01), kwargs.get('frmax', 0.14)])
    fp   = array('d', [0, 0, 0, 0])
    fpe  = array('d', [0, 0, 0, 0])
    pllo = array('d', [0, 0, 0, 0])
    plhi = array('d', [10000,  1000, 100000,  100])
    sv   = array('d', [0.018, kwargs.get('mpv', 0.015), 0.05, 0.003])

    fitr = langaufit(hph,fr,sv,pllo,plhi,fp,fpe);
    maxx = ROOT.Double()
    fwhm = ROOT.Double()
    langaupro(fp, maxx, fwhm)

    return fp[1], fpe[1], fitr


can = ROOT.TCanvas()

c.Draw("amp[0]:event>>ptkamp({0},{1},{2},80,0,0.2)".format(max(int(c.GetEntries()/300.),40),0,c.GetEntries()),"","COLZ")
can.SaveAs(os.path.join(outdir,"photek_amp_v_event.png"))
# can.SaveAs(os.path.join(outdir,"photek_amp_v_event.pdf"))

can.Clear()
c.Draw("amp[0]>>ptkamp(40,0,0.14)","","COLZ")
can.SaveAs(os.path.join(outdir,"photek_amp.png"))
# can.SaveAs(os.path.join(outdir,"photek_amp.pdf"))

can.Clear()
pixel_xmin = 15000
pixel_ymin = 21000
c.Draw("y2:x2>>pix(90,{0},{1},80,{2},{3})".format(pixel_xmin,pixel_xmin+9000,pixel_ymin,pixel_ymin+8000),"amp[0]>0.01","COLZ")
# c.Draw("y2:x2>>pix(90,15000,24000,80,21000,29000)","amp[0]>0.01","COLZ")
can.SaveAs(os.path.join(outdir,"pixels.png"))
# can.SaveAs(os.path.join(outdir,"pixels.pdf"))

# sensor_channels = [1,2,3,4,5,6,7,10,11,12,13,14,15,16]
sensor_channels = [15,16]
# sensor_channels = [2,3,7,10,11,12,13,14]
cutstr = "amp[0]>0.010 && amp[{0}]>0.012 && x1>10000 && y1>10000"

for chan in sensor_channels:
    if chan == 3:
        cutstr = "amp[0]>0.010 && amp[{0}]>0.020 && x1>10000 && y1>10000"
    else:
        cutstr = "amp[0]>0.010 && amp[{0}]>0.000 && x1>10000 && y1>10000"

    can.Clear()
    c.Draw("amp[{0}]>>amp(50,0,0.15)".format(chan),cutstr.format(chan),"HIST")    
    hamp = ROOT.gDirectory.Get("amp")
    nevt = hamp.Integral()
    hamp.Fit("landau","Q")
    fit = ROOT.TF1("fit","[0]*TMath::Landau(x,[1],[2])",0.01,0.14)
    fit.SetParameter(0,1)
    fit.SetParameter(1,ROOT.gDirectory.Get("amp").GetMean())
    fit.SetParameter(2,ROOT.gDirectory.Get("amp").GetRMS())
    hamp.Fit(fit,"QNR","goff")
    v, e, lgfit = dofitLandGaus(hamp, mpv=fit.GetParameter(1))
    lgfit.Draw("SAME")
    can.SaveAs(os.path.join(outdir,"amp_{0}.png".format(chan)))
    # can.SaveAs(os.path.join(outdir,"amp_{0}.pdf".format(chan)))

    can.Clear()
    c.Draw("gauspeak[{0}]-gauspeak[0]>>time(400,-100,100)".format(chan),cutstr.format(chan),"HIST")
    mean = ROOT.gDirectory.Get("time").GetBinCenter(ROOT.gDirectory.Get("time").GetMaximumBin())
    c.Draw("gauspeak[{0}]-gauspeak[0]>>time(60,{1},{2})".format(chan,mean-1,mean+1),cutstr.format(chan),"HIST")
    htime = ROOT.gDirectory.Get("time")
    htime.Fit("gaus","Q")
    fit = htime.GetFunction("gaus")
    # fit = ROOT.TF1("fit","[0]*TMath::Gaus(x,[1],[2])",mean-1,mean+1)
    # fit.SetParameter(0,ROOT.gDirectory.Get("time").GetBinContent(ROOT.gDirectory.Get("time").GetMaximumBin()))
    # fit.SetParameter(1,mean)
    # fit.SetParameter(2,0.2)
    # ROOT.gDirectory.Get("time").Fit(fit,"QNR","goff")
    fit.Draw("SAME")
    can.SaveAs(os.path.join(outdir,"time_{0}.png".format(chan)))
    # can.SaveAs(os.path.join(outdir,"time_{0}.pdf".format(chan)))

    can.Clear()
    c.Draw("FFTtime[{0}]-FFTtime[0]>>time(400,-100,100)".format(chan),cutstr.format(chan),"HIST")
    mean = ROOT.gDirectory.Get("time").GetBinCenter(ROOT.gDirectory.Get("time").GetMaximumBin())
    c.Draw("FFTtime[{0}]-FFTtime[0]>>time(60,{1},{2})".format(chan,mean-1,mean+1),cutstr.format(chan),"HIST")
    htime = ROOT.gDirectory.Get("time")
    htime.Fit("gaus","Q")
    fit = htime.GetFunction("gaus")
    fit.Draw("SAME")
    can.SaveAs(os.path.join(outdir,"ffttime_{0}.png".format(chan)))
    # can.SaveAs(os.path.join(outdir,"ffttime_{0}.pdf".format(chan)))

    can.Clear()
    # c.Draw("y2:x2",cutstr.format(chan),"COLZ")
    c.Draw("y2:x2>>pix(90,{0},{1},80,{2},{3})".format(pixel_xmin,pixel_xmin+9000,pixel_ymin,pixel_ymin+8000),cutstr.format(chan),"COLZ")
    can.SaveAs(os.path.join(outdir,"pixels_{0}.png".format(chan)))
    # can.SaveAs(os.path.join(outdir,"pixels_{0}.pdf".format(chan)))

# os.system("scp -r {0} uaf:public_html/plots/LGAD_RunDiagnoses/".format(outdir))
