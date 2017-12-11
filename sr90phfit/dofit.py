import os
import sys
import math
import json
import ROOT as r
r.gROOT.SetBatch(1)
r.gROOT.ProcessLine(".L langaus.C++")
from ROOT import langaufit, langaupro
from array import array

def generateHists(infn, chnum=0, phcut_max=350, phcut_min=0, *args, **kwargs):
    ''' ch1, ch2 will be lists as of pulse heights '''

    xmax = 200 if phcut_max < 200 else phcut_max + 50

    hph1 = r.TH1F("h_ph1", "Pulse height distribution for Sr90;Pulse hieght [mV];Events", 100, 0, xmax)
    hpa1 = r.TH1F("h_pa1", "Pulse area distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 2)

    hph2 = r.TH1F("h_ph2", "Pulse height distribution for Sr90;Pulse hieght [mV];Events", 100, 0, xmax)
    hpa2 = r.TH1F("h_pa2", "Pulse area distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 2)

    lines = open("data/"+infn+".ant").readlines()
    for line in lines:
        line = line.split()
        ph1 = float(line[3])
        ph2 = float(line[7])

        pa1 = float(line[4])
        pa2 = float(line[8])

        if ph1 < phcut_max and ph1 > phcut_min:
            hph1.Fill(ph1)
        if ph2 < phcut_max and ph2 > phcut_min:
            hph2.Fill(ph2)

        hpa1.Fill(pa1)
        hpa2.Fill(pa2)

    hph1.SetLineColor(r.kRed)
    hpa1.SetLineColor(r.kRed)
    hph2.SetLineColor(r.kBlue)
    hpa2.SetLineColor(r.kBlue)

    if chnum == 1:
        return hph1, hpa1
    elif chnum == 2:
        return hph2, hpa2
    else:
        return hph1, hph2

def generateHists2(infn, phcut_max=350, phcut_min=0, chnum=0, *args, **kwargs):
    ''' ch1, ch2 will be lists as of pulse heights '''

    hph1 = r.TH1F("h_ph1", "Pulse height distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 200)
    hph2 = r.TH1F("h_ph2", "Pulse height distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 200)

    # hpa1 = r.TH1F("h_pa1", "Pulse area distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 2)
    # hpa2 = r.TH1F("h_pa2", "Pulse area distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 2)

    lines = open("data2/"+infn+".ant").readlines()
    for line in lines:
        line = line.split()
        ph1 = float(line[2])
        ph2 = float(line[11])

        if ph1 > ph2 and ph1 < phcut_max and ph1 > phcut_min:
            hph1.Fill(ph1)
        elif ph2 > ph1 and ph2 < phcut_max and ph2 > phcut_min:
            hph2.Fill(ph2)

        # pa1 = float(line[3])
        # pa2 = float(line[12])
        # hpa1.Fill(pa1)
        # hpa2.Fill(pa2)

    hph1.SetLineColor(r.kRed)
    hph2.SetLineColor(r.kBlue)

    # hpa1.SetLineColor(r.kRed)
    # hpa2.SetLineColor(r.kBlue)

    if chnum == 1:
        return hph1, hpa1
    elif chnum == 2:
        return hph2, hpa2
    else:
        return hph1, hph2

def generateHistsFromJSON(infn, chnum=1, phcut_max=350, phcut_min=0, *args, **kwargs):
    ''' ch1, ch2 will be lists as of pulse heights '''

    hph1 = r.TH1F("h_ph1", "Pulse height distribution for Sr90;Pulse hieght [mV];Events", 50, 0, 300)
    hpa1 = r.TH1F("h_pa1", "Pulse area distribution for Sr90;Pulse hieght [mV];Events", 50, 0, 2)

    # hph2 = r.TH1F("h_ph2", "Pulse height distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 200)
    # hpa2 = r.TH1F("h_pa2", "Pulse area distribution for Sr90;Pulse hieght [mV];Events", 100, 0, 2)

    with open("data_drs/"+infn+".json", "r") as fhin:
        js = json.load(fhin)
        for line in js.values():
            ch1 = line['channels'][0]
            if not ch1['has_peak']: continue
            ph1 = ch1['pulse_height']
            pa1 = ch1['pulse_area']
            if ph1 < phcut_max and ph1 > phcut_min:
                hph1.Fill(ph1)
            hpa1.Fill(pa1)

            # ch2 = line['channels'][1]
            # if not ch2['has_peak']: continue
            # ph2 = ch2['pulse_height']
            # pa2 = ch2['pulse_area']
            # if ph2 < phcut_max and ph2 > phcut_min:
            #     hph2.Fill(ph2)
            # hpa2.Fill(pa2)

    hph1.SetLineColor(r.kRed)
    hpa1.SetLineColor(r.kRed)

    # hph2.SetLineColor(r.kBlue)
    # hpa2.SetLineColor(r.kBlue)

    if chnum == 1:
        return hph1, hpa1
    # elif chnum == 2:
    #     return hph2, hpa2
    # else:
    #     return hph1, hph2

def dofitLandau(hch1, plotname="", doDraw=False):

    if plotname != "": doDraw = True

    hch1.Fit("landau","0")
    fr1 = hch1.GetFunction("landau")
    # fr1.Draw()
    print fr1.GetParameter(0), fr1.GetParameter(1), fr1.GetParameter(2)

    if doDraw:

        r.gStyle.SetOptStat(0)

        c1 = r.TCanvas("c1", "c1", 600, 400)

        fr1.SetLineColor(r.kAzure)
        hch1.Draw()
        fr1.Draw("same")

        c1.SetTitle("Landau fit to Pulse Height for " + fn)
        c1.Print("plots/h_fit"+plotname+".pdf")

    return fr1.GetParameter(1), fr1.GetParameter(2)

def dofitLandGaus(hph, plotname="", *args, **kwargs):

    fr   = array('d', [kwargs.get('frmin', 20), kwargs.get('frmax', 140)])
    fp   = array('d', [0, 0, 0, 0])
    fpe  = array('d', [0, 0, 0, 0])
    pllo = array('d', [  0.5,    10,      1,  0.0])
    plhi = array('d', [10000,  1000, 100000,  100])
    sv   = array('d', [  1.8,    40,     50,    3])
    
    fitr = langaufit(hph,fr,sv,pllo,plhi,fp,fpe);

    if plotname != "":
        r.gStyle.SetOptStat(0)
        c1 = r.TCanvas("c1", "c1", 600, 400)
        fitr.SetLineColor(r.kAzure)
        hph.Draw()
        fitr.Draw("same")

        c1.SetTitle("Landau * Gauss fit to Pulse Height")
        c1.Print("plots/h_fit"+plotname+".pdf")

    maxx = r.Double()
    fwhm = r.Double()
    langaupro(fp, maxx, fwhm)

    print "Results:", maxx, fp[1], fpe[1], fp[3]
    # return maxx, fp[3]
    return fp[1], fpe[1]

def dofitLandGaus2(hph, plotname="", *args, **kwargs):

    fr   = array('d', [kwargs.get('xmin', 0), kwargs.get('xmax', 1.6)])
    fp   = array('d', [0, 0, 0, 0])
    fpe  = array('d', [0, 0, 0, 0])
    pllo = array('d', [  0.0, 0.001,      0,    0])
    plhi = array('d', [  100,  1000,  10000,  100])
    sv   = array('d', [ 0.01,   0.4,     40,  0.1])
    
    fitr = langaufit(hph,fr,sv,pllo,plhi,fp,fpe);

    if plotname != "":
        r.gStyle.SetOptStat(0)
        c1 = r.TCanvas("c1", "c1", 600, 400)
        fitr.SetLineColor(r.kAzure)
        hph.Draw()
        fitr.Draw("same")

        c1.SetTitle("Landau * Gauss fit to Pulse Height")
        c1.Print("plots/h_fit"+plotname+".pdf")

    maxx = r.Double()
    fwhm = r.Double()
    langaupro(fp, maxx, fwhm)

    return maxx, fp[3]

def dofitPolExp(hch1):

    fitf = r.TF1("f1", "([0] + [1]*x + [2]*x^2)*exp([3]*x) + [4]", 50, 700)
    fitf.SetParameter(0, 3)
    fitf.SetParameter(1, -0.01)
    fitf.SetParameter(2, 1e-5)
    fitf.SetParameter(3, 0.01)
    fitf.SetParameter(4, 17)

    c1 = r.TCanvas("c1", "c1", 530, 350)

    hch1.Fit("f1","0")
    hch1.Fit("f1","0")
    print "Fit result for ch1:"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2), fitf.GetParameter(3), fitf.GetParameter(4)
    fit1 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    hch2.SetLineColor(r.kGreen+3)
    fit1.SetLineColor(r.kAzure)

    hch1.GetYaxis().SetRangeUser(0, 200)
    hch1.Draw()
    fit1.Draw("same")

    c1.SetTitle("poly * exp fit to the Sr90 runs")
    c1.Print("hpole_test.pdf")

def dofitExpExp(hch1):

    fitf = r.TF1("f2", "[0]*exp([1]*x) + [2]", 150, 700)
    fitf.SetParameter(0, 0.3)
    fitf.SetParameter(1, 0.004)
    fitf.SetParameter(2, 1.4)

    c1 = r.TCanvas("c2", "c2", 530, 350)

    hch1.Fit("f2", "0")
    hch1.Fit("f2", "0")
    print "Fit result for exp * exp(x):"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit1 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    fit1.SetLineColor(r.kAzure)

    hch1.GetYaxis().SetRangeUser(0, 5)
    hch1.Draw()
    fit1.Draw("same")

    c1.SetTitle("exp * exp fit to the Sr90 runs")
    c1.Print("hee_test.pdf")

def dofitExpExpInv(hch1):

    fitf = r.TF1("f3", "[0]*exp(-[1]/x) + [2]", 150, 700)
    fitf.SetParameter(0, 0.3)
    fitf.SetParameter(1, 0.004)
    fitf.SetParameter(2, 1.4)

    c1 = r.TCanvas("c3", "c3", 530, 350)

    hch1.Fit("f3", "0")
    hch1.Fit("f3", "0")
    print "Fit result for exp * exp(-1/x):"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit1 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    fit1.SetLineColor(r.kAzure)

    hch1.GetYaxis().SetRangeUser(0, 5)
    hch1.Draw()
    fit1.Draw("same")

    c1.SetTitle("exp * exp(-a/x) fit to the Sr90 runs")
    c1.Print("hei_test.pdf")

def dofitExpExpInvSft(hch1):

    fitf = r.TF1("f4", "[0]*exp([1]/([2]-x)) + [3]", 150, 700)
    fitf.SetParameter(0, 0.3)
    fitf.SetParameter(1, 0.004)
    fitf.SetParameter(2, 700)
    fitf.SetParameter(3, 1.4)

    c1 = r.TCanvas("c3", "c3", 530, 350)

    hch1.Fit("f4", "0")
    hch1.Fit("f4", "0")
    print "Fit result for exp * exp(-1/x):"
    print fitf.GetParameter(0), fitf.GetParameter(1), fitf.GetParameter(2)
    fit1 = fitf.Clone()

    hch1.SetMarkerSize(0.8)
    fit1.SetLineColor(r.kAzure)

    hch1.GetYaxis().SetRangeUser(0, 5)
    hch1.Draw()
    fit1.Draw("same")

    c1.SetTitle("exp * exp(-a/x) fit to the Sr90 runs")
    c1.Print("hesi_test.pdf")

def dofitLine(hch1):

    c1 = r.TCanvas("c3", "c3", 530, 350)

    hch1.Fit("pol1", "0")
    fit1 = hch1.GetFunction("pol1")

    hch1.SetMarkerSize(0.8)
    fit1.SetLineColor(r.kAzure)

    hch1.GetYaxis().SetRangeUser(0, 5)
    hch1.Draw()
    fit1.Draw("same")

    c1.SetTitle("linear fit to log-linear plots")
    c1.Print("hlin_test.pdf")


if __name__ == "__main__":

    sch1_flist = ["Run247","Run257","Run258","Run261","Run274"]
    sch1_BVlist = [500, 500, 500, 500, 500]
    sch1_Tlist = [20.6, 11.5, 11.5, 11.5, 20.6]

    sch2_flist = ["Run248", "Run252", "Run262","Run275"]
    sch2_BVlist = [500, 500, 500, 500]
    sch2_Tlist = [20.6, 20.6, 11.5, 20.6]


    coinc_list = ["Run253", "Run256"]
    coinc_BVlist = [500,500]
    coinc_Tlist = [20.6,15,]

    coinc_list = ["Run253", "Run256"]
    coinc_BVlist = [500,500]
    coinc_Tlist = [20.6,15,]

    '''
    Set of points taken by David  on Sr90, with Kansas board 
    Information can be found at http://fixels.physics.ucsb.edu/Lgbk/pub/E521.dir/E521.html
    '''
    ch1_lrunlist1 = ["Run289","Run286","Run300","Run305","Run308","Run310","Run313","Run317","Run320","Run322",]
    ch1_lrBVlist1 = [    520 ,    500 ,    480 ,    460 ,    440 ,    420 ,    400 ,    380 ,    360 ,    340 ,]
    ch1_lrdivlst1 = [     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,]
    ch1_frminlst1 = [     35 ,     35 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     10 ,     10 ,]
    ch1_frmaxlst1 = [    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,]

    ch2_lrunlist1 = ["Run293","Run294","Run297","Run306","Run307","Run311","Run314","Run316","Run319","Run323",]
    ch2_lrBVlist1 = [    520 ,    500 ,    480 ,    460 ,    440 ,    420 ,    400 ,    380 ,    360 ,    340 ,]
    ch2_lrdivlst1 = [     50 ,     50 ,     50 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,]
    ch2_frminlst1 = [     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,     20 ,]
    ch2_frmaxlst1 = [    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,    140 ,]

    ch1_lrunlist2 = ["Run325","Run328","Run334","Run355","Run360",] # "Run363",
    ch1_lrBVlist2 = [    320 ,    300 ,    280 ,    260 ,    240 ,] #     200 ,
    ch1_lrdivlst2 = [     10 ,     10 ,     10 ,     10 ,     10 ,] #      10 ,
    ch1_frminlst2 = [     10 ,     10 ,     10 ,     10 ,     10 ,] #      10 ,
    ch1_frmaxlst2 = [     65 ,     65 ,     65 ,     65 ,     65 ,] #      65 ,


    '''
    Set of points taken by David during last week of October on Sr90, with Fermilab board 
    sensor on ch1 has guard-ring and ch2 no guard-ring 
    '''
    ch1_lrunlist3 = ["Run389","Run402","Run406","Run407","Run410","Run411",]
    ch1_lrBVlist3 = [    400 ,    500 ,    550 ,    600 ,    600 ,    650 ,]
    ch1_lrdivlst3 = [     10 ,     10 ,     10 ,     10 ,     20 ,     20 ,]
    ch1_frminlst3 = [     10 ,     10 ,     10 ,     20 ,     20 ,     25 ,]
    ch1_frmaxlst3 = [     70 ,     75 ,     75 ,     75 ,    100 ,    135 ,]

    ch2_lrunlist3 = ["Run388","Run404","Run405","Run408","Run409","Run412",] # "Run403","Run387",
    ch2_lrBVlist3 = [    400 ,    500 ,    550 ,    600 ,    600 ,    650 ,] #     500 ,    400 ,
    ch2_lrdivlst3 = [      5 ,     10 ,     10 ,     10 ,     20 ,     20 ,] #      20 ,     10 ,
    ch2_frminlst3 = [      8 ,     10 ,     10 ,     20 ,     25 ,     40 ,] #      10 ,     10 ,
    ch2_frmaxlst3 = [     30 ,     65 ,     65 ,     65 ,    100 ,    100 ,] #     100 ,     65 ,


    '''
    Set of points taken with the broken fnal sensor, 
    '''
    ch1_lrunlist4 = ["Run436","Run431","Run432","Run433","Run434",] # "Run426",
    ch1_lrBVlist4 = [    450 ,    475 ,    500 ,    525 ,    550 ,] #     550 ,
    ch1_lrdivlst4 = [      5 ,      5 ,     10 ,     10 ,     20 ,] #      20 ,
    ch1_frminlst4 = [     10 ,     10 ,     10 ,     10 ,     20 ,] #      25 ,
    ch1_frmaxlst4 = [     30 ,     30 ,     65 ,     65 ,    120 ,] #     145 ,

    '''
    Set of points taken with the last fnal sensor (FS4), with guard ring, mounted on a carrier board.
    '''
    ch1_lrunlist5 = ["Run658","Run659","Run660","Run661","Run662",]
    ch1_lrBVlist5 = [    400 ,    500 ,    540 ,    580 ,    680 ,]
    ch1_lrdivlst5 = [     20 ,     20 ,     20 ,     20 ,     50 ,]
    ch1_frminlst5 = [     14 ,     14 ,     14 ,     14 ,     50 ,]
    ch1_frmaxlst5 = [    150 ,    150 ,    150 ,    150 ,    600 ,]

    '''
    Retake of set of points taken with the last fnal sensor (FS4), with guard ring, mounted on a carrier board.
    '''
    ch1_lrunlist5 = ["Run726","Run727","Run728","Run729","Run730","Run731","Run732",]
    ch1_lrBVlist5 = [    620 ,    640 ,    660 ,    680 ,    560 ,    500 ,    470 ,]
    ch1_lrdivlst5 = [     50 ,     50 ,     50 ,     50 ,     50 ,     50 ,     50 ,]
    ch1_frminlst5 = [     20 ,     20 ,     20 ,     20 ,     15 ,     15 ,     10 ,]
    ch1_frmaxlst5 = [    350 ,    350 ,    350 ,    350 ,    150 ,    150 ,    150 ,]

    # ch1_lrunlist = ch1_lrunlist1 + ch1_lrunlist2
    # ch1_lrBVlist = ch1_lrBVlist1 + ch1_lrBVlist2
    # ch1_lrdivlst = ch1_lrdivlst1 + ch1_lrdivlst2
    # ch1_frminlst = ch1_frminlst1 + ch1_frminlst2
    # ch1_frmaxlst = ch1_frmaxlst1 + ch1_frmaxlst2

    ch1_lrunlist = ch1_lrunlist5
    ch1_lrBVlist = ch1_lrBVlist5
    ch1_lrdivlst = ch1_lrdivlst5
    ch1_frminlst = ch1_frminlst5
    ch1_frmaxlst = ch1_frmaxlst5

    ch2_lrunlist = ch2_lrunlist1
    ch2_lrBVlist = ch2_lrBVlist1
    ch2_lrdivlst = ch2_lrdivlst1
    ch2_frminlst = ch2_frminlst1
    ch2_frmaxlst = ch2_frmaxlst1

    # ch2_lrunlist = ch2_lrunlist1
    # ch2_lrBVlist = ch2_lrBVlist1
    # ch2_lrdivlst = ch2_lrdivlst1

    ch2_lrunlist = []

    hch1 = r.TH1F("h_ph1s", "Pulse height MPV distribution for Sr90;Bias Voltage [V];Pulse hieght MPV [mV]", 700, 0, 700)
    hch2 = r.TH1F("h_ph2s", "Pulse height MPV distribution for Sr90;Bias Voltage [V];Pulse hieght MPV [mV]", 700, 0, 700)

    hlog1 = r.TH1F("h_logph1s", "Pulse height MPV distribution for Sr90;Bias Voltage [V]; log(Pulse hieght MPV) [+lnmV]", 700, 0, 700)
    hlog2 = r.TH1F("h_logph2s", "Pulse height MPV distribution for Sr90;Bias Voltage [V]; log(Pulse hieght MPV) [+lnmV]", 700, 0, 700)

    for i, fn in enumerate(ch1_lrunlist):
        bv = ch1_lrBVlist[i]
        frmin = ch1_frminlst[i]
        frmax = ch1_frmaxlst[i]

        hph1, hpa1 = generateHists(fn, 1, frmax, frmin)
        v, e = dofitLandGaus(hph1, '_{}_ph1_{}'.format(fn, bv), frmin=frmin, frmax=frmax)
        hch1.SetBinContent(bv, v)
        hch1.SetBinError  (bv, e)
        hlog1.SetBinContent(bv, math.log(v))
        hlog1.SetBinError  (bv, math.log(v)*e/v)

        # fargs = {'frmin': 0, 'frmax': 1.2}
        # v, e = dofitLandGaus2(hpa1, '_{}_pa_{}'.format(fn, bv), **fargs)
        # hch2.SetBinContent(ibin, v)
        # hch2.SetBinError  (ibin, e)

    for i, fn in enumerate(ch2_lrunlist):
        bv = ch2_lrBVlist[i]
        frmin = ch2_frminlst[i]
        frmax = ch2_frmaxlst[i]

        hph2, hpa2 = generateHists(fn, 2, frmax, frmin)
        v, e = dofitLandGaus(hph2, '_{}_ph2_{}'.format(fn, bv), frmin=frmin, frmax=frmax)
        hch2.SetBinContent(bv, v)
        hch2.SetBinError  (bv, e)
        hlog2.SetBinContent(bv, math.log(v))
        hlog2.SetBinError  (bv, math.log(v)*e/v)


    drs_flist = [  "Run1",  "Run2",]
    drs_BVlst = [    300 ,    500 ,]
    drs_frmin = [     10 ,     10 ,]
    drs_frmax = [    180 ,    180 ,]

    # for i, fn in enumerate(drs_flist):
    #     bv = drs_BVlst[i]
    #     frmin = drs_frmin[i]
    #     frmax = drs_frmax[i]

    #     hph1, hph2 = generateHists2(fn, frmax, frmin)
    #     print hph1.Integral(), hph2.Integral()
    #     v, e = dofitLandGaus(hph1, '_{}_ph1_{}'.format(fn, bv), frmin=frmin, frmax=frmax)
    #     hch1.SetBinContent(bv, v)
    #     hch1.SetBinError  (bv, e)
    #     hlog1.SetBinContent(bv, math.log(v))
    #     hlog1.SetBinError  (bv, math.log(v)*e/v)
    #     v, e = dofitLandGaus(hph2, '_pp{}_ph2_{}'.format(fn, bv), frmin=frmin, frmax=frmax)
    #     hch2.SetBinContent(bv, v)
    #     hch2.SetBinError  (bv, e)
    #     hlog2.SetBinContent(bv, math.log(v))
    #     hlog2.SetBinError  (bv, math.log(v)*e/v)

    drs_jsonlist = ["FS4_BV450","FS4_BV500","FS4_BV550","FS4_BV600", ]
    drs_jsBVlist = [       450 ,       500 ,       550 ,       600 , ]
    drs_jsdivlst = [        50 ,        50 ,        50 ,        50 , ]
    drs_jsminlst = [        14 ,        14 ,        14 ,        14 , ]
    drs_jsmaxlst = [       200 ,       200 ,       200 ,       200 , ]

    # for i, fn in enumerate(drs_jsonlist):
    #     bv = drs_jsBVlist[i]
    #     frmin = drs_jsminlst[i]
    #     frmax = drs_jsmaxlst[i]

    #     hph1, hpa1 = generateHistsFromJSON(fn, 1, frmax, frmin)
    #     v, e = dofitLandGaus(hph1, '_{}_ph1_{}'.format(fn, bv), frmin=frmin, frmax=frmax)
    #     hch1.SetBinContent(bv, v)
    #     hch1.SetBinError  (bv, e)
    #     hlog1.SetBinContent(bv, math.log(v))
    #     hlog1.SetBinError  (bv, math.log(v)*e/v)

    r.gStyle.SetOptStat(0)

    hch1.SetMarkerStyle(4)
    hch2.SetMarkerStyle(4)
    hlog1.SetMarkerStyle(4)
    hlog2.SetMarkerStyle(4)

    c1 = r.TCanvas("c0", "c0", 600, 400)
    hch1.Draw()
    c1.Print("hch1_test.pdf")

    c1.Clear()
    hch2.Draw()
    c1.Print("hch2_test.pdf")

    # f = r.TFile("drsData_Sr90response.root","RECREATE")
    f = r.TFile("FS4_Sr90response.root","RECREATE")
    hch1.Write()
    hch2.Write()
    hlog1.Write()
    hlog2.Write()
    f.Close()

    dofitExpExp(hch1)
    dofitPolExp(hch1)
    dofitExpExp(hlog1)
    dofitExpExpInv(hlog1)
    dofitExpExpInvSft(hlog1)
    dofitLine(hlog1)
