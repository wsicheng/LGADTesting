#!/usr/bin/python

import os
import sys
import math
import ROOT as r
r.gROOT.SetBatch(1)

def generateHists(ch1, ch2, outfn, *args, **xargs):
    ''' ch1, ch2 will be dict with {BiasVoltage: PulseHeight} as items '''

    

    xmax = max(ch1.keys()) + 30

    hch1 = r.TH1F("h_ch1", "Pulse height vs bias voltage;Bias voltage [V]; Pulse hieght [mV]", xmax, 0, xmax)
    hch2 = r.TH1F("h_ch2", "Pulse height vs bias voltage;Bias voltage [V]; Pulse hieght [mV]", xmax, 0, xmax)

    hlog1 = r.TH1F("h_log1", "Pulse height vs bias voltage;Bias voltage [V]; log(Pulse hieght) [+lnmV]", xmax, 0, xmax)
    hlog2 = r.TH1F("h_log2", "Pulse height vs bias voltage;Bias voltage [V]; log(Pulse hieght) [+lnmV]", xmax, 0, xmax)

    hll1 = r.TH2F("h_ll1", "Pulse height vs bias voltage;log(Bias voltage) [+lnV]; log(Pulse hieght) [+lnmV]", 200, 5, 7, 300, 3, 6)
    hll2 = r.TH2F("h_ll2", "Pulse height vs bias voltage;log(Bias voltage) [+lnV]; log(Pulse hieght) [+lnmV]", 200, 5, 7, 300, 3, 6)

    hlla1 = r.TH2F("h_lla1", "Pulse height vs bias voltage;log(Bias voltage) [+lnV]; log(Pulse hieght) [+lnmV]", 600, 2, 8, 400, 2, 6)
    hlla2 = r.TH2F("h_lla2", "Pulse height vs bias voltage;log(Bias voltage) [+lnV]; log(Pulse hieght) [+lnmV]", 600, 2, 8, 400, 2, 6)

    for bv, ph in ch1.items():
        sft = 20 - abs(ch1[160]); 
        bv = abs(bv)
        ph = abs(ph) + sft
        if bv < 70: continue
        hch1.SetBinContent(bv, ph)
        hch1.SetBinError(bv, 0.2)
        # bv = bv-40
        # lph = math.log(ph+ch1[-40])
        lph = math.log(ph)
        lbv = math.log(bv)
        hlla1.Fill(lbv, lph)

        if bv < 170: continue
        hlog1.SetBinContent(bv, lph)
        hlog1.SetBinError(bv, 0.2*lph/ph)
        if bv < 200: continue
        hll1.Fill(lbv, lph)

    for bv, ph in ch2.items():
        sft = 20 - abs(ch2[160]); 
        bv = abs(bv)
        ph = abs(ph) + sft
        if bv < 70: continue
        hch2.SetBinContent(bv, ph)
        hch2.SetBinError(bv, 0.2)
        # bv = bv-40
        # lph = math.log(ph+ch2[-40])
        lph = math.log(ph)
        lbv = math.log(bv)
        hlla2.Fill(lbv, lph)

        if bv < 170: continue
        hlog2.SetBinContent(bv, lph)
        hlog2.SetBinError(bv, 0.2*lph/ph)
        if bv < 200: continue
        hll2.Fill(lbv, lph)

    r.gStyle.SetOptStat(0)
    # c = r.TCanvas("c","c",900,600)
    hch1.SetMarkerStyle(4)
    hch1.SetMarkerColor(r.kAzure+3)
    hch2.SetMarkerStyle(4)
    hch2.SetMarkerColor(r.kAzure+3)

    hlog1.SetMarkerStyle(4)
    hlog1.SetMarkerColor(r.kAzure+3)
    hlog2.SetMarkerStyle(4)
    hlog2.SetMarkerColor(r.kAzure+3)

    hll1.SetMarkerStyle(4)
    hll1.SetMarkerColor(r.kAzure+3)
    hll2.SetMarkerStyle(4)
    hll2.SetMarkerColor(r.kAzure+3)

    hlla1.SetMarkerStyle(4)
    hlla1.SetMarkerColor(r.kAzure+3)
    hlla2.SetMarkerStyle(4)
    hlla2.SetMarkerColor(r.kAzure+3)

    ofile = r.TFile(outfn+".root", "RECREATE")
    hch1.Write()
    hch2.Write()

    hlog1.Write()
    hlog2.Write()

    hll1.Write()
    hll2.Write()

    hlla1.Write()
    hlla2.Write()


def combinePlots(hch1, fit1, hph1, fixpt1, fixpt2, suf):

    c1 = r.TCanvas("cb", "cb", 600, 400)

    hch1.Draw()
    fit1.Draw("same")

    scale = 1.0 * hch1.GetBinContent(fixpt1) / hph1.GetBinContent(fixpt2)
    hph1.Scale(scale)
    hph1.SetMarkerStyle(33)
    hph1.SetMarkerSize(1.4)
    hph1.SetMarkerColor(r.kRed-7)
    hph1.Draw("same")
    leg = r.TLegend(0.2, 0.7, 0.36, 0.8)
    leg.AddEntry(hch1, "LED Source")
    leg.AddEntry(hph1, "Sr90 Source")
    leg.Draw()
    scaletxt = r.TLatex(0.2, 0.67, "Sr90 scaled by  %2.1f" % scale)
    scaletxt.SetNDC()
    scaletxt.SetTextAlign(11)
    scaletxt.SetTextFont(61)
    scaletxt.SetTextSize(0.034)
    scaletxt.Draw()

    if suf != "": suf = "_"+suf
    c1.Print("combined{}.pdf".format(suf))


def dofitPolExp(fname):

    f1 = r.TFile(fname+".root")
    hch1 = f1.Get("h_ch1")
    hch2 = f1.Get("h_ch2")

    xmax = 720

    fitf = r.TF1("f1", "([0] + [1]*x + [2]*x^2)*exp([3]*x) + [4]", 50, xmax)
    fitf.SetParameter(0, 3)
    fitf.SetParameter(1, -0.01)
    fitf.SetParameter(2, 1e-5)
    fitf.SetParameter(3, 0.01)
    fitf.SetParameter(4, 17)

    # fr1 = hch1.GetFunction("f1")
    c1 = r.TCanvas("c1", "c1", 600, 400)

    hch1.Fit("f1","0")
    hch1.Fit("f1","0")
    print "Fit result for " +fname+ " ch1:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2), fitf.GetParameter(3), fitf.GetParameter(4)
    fit1 = fitf.Clone()

    hch2.Fit("f1","0")
    hch2.Fit("f1","0")
    print "Fit result for " +fname+ " ch2:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2), fitf.GetParameter(3), fitf.GetParameter(4)
    fit2 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    hch2.SetMarkerSize(0.8)
    hch2.SetLineColor(r.kGreen+3)
    fit1.SetLineColor(r.kAzure)
    fit2.SetLineColor(r.kTeal)

    hch1.GetYaxis().SetRangeUser(0, 200)
    hch2.GetYaxis().SetRangeUser(0, 200)
    hch1.Draw()
    hch2.Draw("same")
    fit1.Draw("same")
    fit2.Draw("same")

    leg = r.TLegend(0.2, 0.7, 0.36, 0.8)
    # leg.AddEntry(fit1, "T = 20 #circC")
    # leg.AddEntry(fit2, "T = 11 #circC")
    leg.AddEntry(fit1, "CH1 \"gain\"")
    leg.AddEntry(fit2, "CH2 \"no gain\"")
    leg.Draw()

    c1.Print("hpole_"+fname+".pdf")

    f_sr90 = r.TFile("../sr90phfit/Sr90_response.root")
    hph1 = f_sr90.Get("h_ph1s")
    hph2 = f_sr90.Get("h_ph2s")
    # print hch1.GetXaxis().FindBin(400), hch1.GetBinContent(400), hph1.GetBinContent(4)
    combinePlots(hch1, fit1, hph1, 500, 17, "1")
    combinePlots(hch2, fit2, hph2, 500, 17, "2")

    return fit1, fit2
    # print fr1.GetParameter(0), fr1.GetParameter(1), fr1.GetParameter(2), fr1.GetParameter(3), fr1.GetParameter(4)

def dofitPowExp(fname):

    f1 = r.TFile(fname+".root")
    hch1 = f1.Get("h_ll1")
    hch2 = f1.Get("h_ll2")

    fitf = r.TF1("f3", "[0]*x + [1]*exp(x) + [2]", 5.2, 6.4)
    fitf.SetParameter(0, 0.3)
    fitf.SetParameter(1, 0.01)
    fitf.SetParameter(2, 5)

    c1 = r.TCanvas("c3", "c3", 600, 400)

    hch1.Fit("f3", "0")
    hch1.Fit("f3", "0")
    print "Fit result for " +fname+ " ch1:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit1 = fitf.Clone()

    hch2.Fit("f3", "0")
    hch2.Fit("f3", "0")
    print "Fit result for " +fname+ " ch2:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit2 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    hch2.SetMarkerSize(0.8)
    hch2.SetLineColor(r.kGreen+3)
    fit1.SetLineColor(r.kAzure)
    fit2.SetLineColor(r.kTeal)

    hch1.GetYaxis().SetRangeUser(0, 6)
    hch1.Draw()
    hch2.Draw("same")
    fit1.Draw("same")
    fit2.Draw("same")

    leg = r.TLegend(0.2, 0.7, 0.36, 0.8)
    leg.AddEntry(fit1, "T = 20 #circC")
    leg.AddEntry(fit2, "T = 11 #circC")
    leg.Draw()

    c1.Print("hpowe_"+fname+".pdf")

    return fit1, fit2


def dofitExpExp(fname):

    f1 = r.TFile(fname+".root")
    hch1 = f1.Get("h_log1")
    hch2 = f1.Get("h_log2")

    xmax = 720

    fitf = r.TF1("f2", "[0]*exp([1]*x) + [2]", 150, xmax)
    fitf.SetParameter(0, 0.3)
    fitf.SetParameter(1, 0.004)
    fitf.SetParameter(2, 1.4)

    # fr1 = hch1.GetFunction("f2")
    c1 = r.TCanvas("c2", "c2", 600, 400)

    hch1.Fit("f2", "0")
    hch1.Fit("f2", "0")
    print "Fit result for " +fname+ " ch1:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit1 = fitf.Clone()

    hch2.Fit("f2", "0")
    hch2.Fit("f2", "0")
    print "Fit result for " +fname+ " ch2:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit2 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    hch2.SetMarkerSize(0.8)
    hch2.SetLineColor(r.kGreen+3)
    fit1.SetLineColor(r.kAzure)
    fit2.SetLineColor(r.kTeal)

    hch1.GetYaxis().SetRangeUser(2.6, 6)
    hch1.Draw()
    hch2.Draw("same")
    fit1.Draw("same")
    fit2.Draw("same")

    leg = r.TLegend(0.2, 0.7, 0.36, 0.8)
    leg.AddEntry(fit1, "T = 20 #circC")
    leg.AddEntry(fit2, "T = 11 #circC")
    leg.Draw()

    c1.Print("hee_"+fname+".pdf")

    return fit1, fit2

def dofitExpExpInv(fname):

    f1 = r.TFile(fname+".root")
    hch1 = f1.Get("h_log1")
    hch2 = f1.Get("h_log2")

    xmax = 720

    fitf = r.TF1("f4", "[0]*exp(-[1]/(x-[2])) + [3]", 150, xmax)
    fitf.SetParameter(0, 0.3)
    fitf.SetParameter(1, 0.004)
    fitf.SetParameter(2, 700)
    fitf.SetParameter(3, 1.4)

    # fr1 = hch1.GetFunction("f3")
    c1 = r.TCanvas("c3", "c3", 600, 400)

    hch1.Fit("f4", "0")
    hch1.Fit("f4", "0")
    print "Fit result for " +fname+ " ch1:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit1 = fitf.Clone()

    hch2.Fit("f4", "0")
    hch2.Fit("f4", "0")
    print "Fit result for " +fname+ " ch2:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit2 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    hch2.SetMarkerSize(0.8)
    hch2.SetLineColor(r.kGreen+3)
    fit1.SetLineColor(r.kAzure)
    fit2.SetLineColor(r.kTeal)

    hch1.GetYaxis().SetRangeUser(2.6, 6)
    hch1.Draw()
    hch2.Draw("same")
    fit1.Draw("same")
    fit2.Draw("same")

    leg = r.TLegend(0.2, 0.7, 0.36, 0.8)
    leg.AddEntry(fit1, "CH1 \"gain\"")
    leg.AddEntry(fit2, "CH2 \"no gain\"")
    leg.Draw()

    c1.Print("hei_"+fname+".pdf")

    return fit1, fit2

def readFrom511(fname):
    ch1 = {}
    ch2 = {}

    lines = open("E511.dir/"+fname+".ant").readlines()
    for line in lines:
        line = line.split()
        if line[0] == '#': continue
        ch1[abs(int(line[0]))] = abs(float(line[1]))
        ch2[abs(int(line[0]))] = abs(float(line[3]))
    
    return ch1, ch2

def readFrom523(run1, run2):
    ch1 = {}
    ch2 = {}

    lines = open("E523.dir/runs.ant").readlines()

    for line in lines:
        line = line.split()
        if line[0] == '#': continue
        if line[0] == run1:
            ch1[abs(int(line[2]))] = abs(float(line[1]))
        if line[0] == run2:
            ch2[abs(int(line[2]))] = abs(float(line[1]))

    return ch1, ch2

if __name__ == "__main__":

    # # flist511 = ["LEDTest1","LEDTest2","LEDTest3","LEDTest4",]
    # flist511 = []
    # for fn in flist511:
    #     ch1, ch2 = readFrom511(fn)
    #     generateHists(ch1, ch2, fn)
    #     dofitPolExp(fn)
    #     dofitExpExp(fn)
        
    # if True:
    #     r1, r2 = readFrom523('1', '2')
    #     generateHists(r1, r2, 'test')
    #     # dofitPolExp("test")
    #     # dofitPowExp("test")
    #     # dofitExpExp("test")

    #     # r1, r2 = readFrom523('1', '3')
    #     # generateHists(r1, r2, 'T20C')
    #     # dofitPolExp("T20C")
    #     # dofitPowExp("T20C")
    #     # dofitExpExp("T20C")

    #     r1, r2 = readFrom523('2', '4')
    #     generateHists(r1, r2, 'T11C')
    #     dofitPolExp("T11C")
    #     # dofitPowExp("T11C")
    #     # dofitExpExp("T11C")

    # # LED scan on Fermilab board, source morderate close, no filter, source pulse at 6V (3V passed over)
    # # Data taken on 2017/10/31 Tue morning
    # BVlist     = [  0,  30,  50,  70, 100, 200, 250, 300,  350,  400,  440,  470,  500,  520,  540,  560,  580,  590,  600,  610,  620,  630,  640,  650,  660,  670,  680,   690,   700, ]
    # ch1_PHlist = [2.1, 2.2, 4.5, 5.7, 6.7, 8.0, 8.8, 9.9, 11.3, 13.3, 15.2, 17.0, 19.5, 21.4, 24.0, 26.9, 28.3, 30.6, 33.2, 36.6, 40.6, 45.3, 50.4, 56.9, 66.1, 77.7, 94.5, 119.4, 162.4, ]
    # ch2_PHlist = [1.3, 1.5, 3.6, 4.8, 5.8, 7.0, 7.7, 8.7, 10.0, 11.7, 13.6, 15.3, 17.5, 19.4, 21.6, 24.4, 26.9, 29.2, 31.6, 34.5, 38.0, 42.4, 47.3, 53.9, 62.8, 74.5, 91.9, 117.9, 165.6, ]

    # Quick LED scan on 2017/11/3 Fri afternoon, on Fermilab board, for the purpose of testing the satuation hypothesis
    BVlist = [ 160, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 680, 700]
    ch1_PH_4VnoFilter = [ 3.7, 4.0, 4.6, 5.0, 5.7, 6.6, 7.9, 9.9, 12.9, 18.1, 30.0, 48.6, 81.5, ]
    ch2_PH_4VnoFilter = [ 2.8, 3.0, 3.4, 3.9, 4.6, 5.3, 6.3, 7.8, 10.4, 14.7, 25.0, 41.8, 72.1, ]
    ch1_PH_6VnoFilter = [ 7.2, 7.9, 8.8, 10.0, 11.4, 13.4, 16.1, 19.7, 25.7, 36.6, 61.1, 100, 171, ]
    ch2_PH_6VnoFilter = [ 5.8, 6.3, 7.1, 9.1, 9.2, 10.8, 12.9, 16.1, 21.0, 30.3, 51.0, 66.2, 153.5, ]


    ch1_PH_4Vp3Filter = [ 2.4, 2.6, 2.8, 3.1, 3.5, 3.9, 4.5, 5.4, 6.8, 9.1, 14.7, 23.3, 38.5, ]
    ch2_PH_4Vp3Filter = [ 1.8, 1.9, 2.1, 2.4, 2.6, 2.9, 3.4, 4.1, 5.3, 7.3, 12.1, 20.1, 34.7, ]

    ch1_PH_5Vp3Filter = [ 3.7, 3.9, 4.3, 4.7, 5.0, 5.8, 6.6, 8.0, 10.0, 13.9, 22.2, 35.3, 58.7, ]
    ch2_PH_5Vp3Filter = [ 2.6, 3.0, 3.2, 3.5, 3.9, 4.5, 5.2, 6.4, 8.0, 11.1, 18.4, 30.5, 52.3, ]

    ch1_PH_6Vp3Filter = [ 4.7, 5.2, 5.6, 5.9, 6.7, 7.4, 8.7, 10.6, 13.2, 18.4, 29.6, 47.3, 79.0, ]
    ch2_PH_6Vp3Filter = [ 3.6, 3.8, 4.3, 4.7, 5.1, 6.0, 6.9, 8.2, 10.7, 15.0, 24.7, 41.2, 70.6, ]


    ch1 = {}
    ch2 = {}
    for i in range(0, len(BVlist)):
        # ch1[BVlist[i]] = ch1_PHlist[i]
        # ch2[BVlist[i]] = ch2_PHlist[i]
        ch1[BVlist[i]] = ch1_PH_6VnoFilter[i]
        ch2[BVlist[i]] = ch1_PH_6VnoFilter[i]

    
    fn = "fnalboard"
    generateHists(ch1, ch2, fn)
    dofitPolExp(fn)
    # dofitExpExp(fn)
    # dofitPowExp(fn)
    dofitExpExpInv(fn)

