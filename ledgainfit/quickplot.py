import os
import sys
import math
import ROOT as r
r.gROOT.SetBatch(1)


def createHistogram(bvs, phs, hname):
    div = 10
    xmax = max(bvs) + 30
    # xmin = min(bvs) if min(bvs) < 0 else 0
    xmin = 0
    nbins = (xmax - xmin) / div
    hist = r.TH1F("h_"+hname, "Pulse Height vs BV for "+hname+"; BV [V]; PH [mV]", nbins, xmin, xmax)
    hist.SetMarkerStyle(4)
    bins = [(x-xmin)/div for x in bvs]
    return fillHistogram(bins, phs, hist)

def fillHistogram(bins, phs, hist):
    for i in range(0, len(bins)):
        hist.SetBinContent(bins[i], phs[i])
        hist.SetBinError(bins[i], 0)
    hist.GetYaxis().SetRangeUser(0, phs[-1]*1.2)
    return hist

if __name__ == "__main__":

    ch1_BVlist1 = [400, 390, 380, 370, 360, 350, 340, 330, 320, 310, 300, 290, 280, 270, 260, 250, 240, 230, 220, 210, 200, 190, 180, 170, 160, 150, 140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0,]
    ch1_PHlist1 = [5.5, 5.3, 5.1, 5.0, 4.9, 4.7, 4.6, 4.5, 4.4, 4.4, 4.3, 4.1, 4.0, 3.9, 3.8, 3.7, 3.6, 3.5, 3.5, 3.4, 3.3, 3.2, 3.2, 3.1, 3.1, 3.0, 3.0, 2.9, 2.8, 2.8, 2.7, 2.7, 2.6, 2.3, 2.1, 1.9, 1.5, 0.9, 0.9, 0.9, 0.9, ]

    ch2_BVlist1 = [400, 390, 380, 370, 360, 350, 340, 330, 320, 310, 300, 290, 280, 270, 260, 250, 240, 230, 220, 210, 200, 190, 180, 170, 160, 150, 140, 130, 120, 110, 100, 90, 80, 70, 60, 50, 40, 30, 20, 10, 0,]
    ch2_PHlist1 = [4.4, 4.2, 4.1, 4.0, 3.8, 3.8, 3.7, 3.5, 3.5, 3.5, 3.2, 3.1, 3.0, 3.0, 3.0, 2.9, 2.9, 2.8, 2.8, 2.7, 2.6, 2.5, 2.5, 2.5, 2.4, 2.3, 2.2, 2.1, 2.1, 2.1, 2.1, 2.0, 1.9, 1.7, 1.5, 1.2, 0.9, 0.5, 0.4, 0.4, 0.4, ]


    hch1 = r.TH1F("h_ch1", "Pulse Height vs BV for ch1; BV [V]; PH [mV]", 42, 0, 420)
    hch2 = r.TH1F("h_ch2", "Pulse Height vs BV for ch2; BV [V]; PH [mV]", 42, 0, 420)


    ch1_BVlist3 = [ 450, 500, 550, 570, 590, 610, 620, 630, 640, 660, 675, 700]
    ch1_PHlist3 = [ 16.5, 21.2, 28.2, 32.8, 38.5,   45,   49, 53.7, 58.8, 74, 87.6, 137]
    ch2_PHlist3 = [ 15.0, 18.5, 23.0, 25.5, 28.7, 33.1, 36.3, 39.7,   46, 69,   83, 134]
 
    # ch1_BVlist4 = [  0,  30,  50,  70, 100, 200, 250, 300,  350,  400,  440,  470,  500,  520,  540,  550,  560,  570,  580,  590,  600,  610,  620,  630,  640,  650,  660,  670,  680,   690,   700, ]
    # ch1_PHlist4 = [2.1, 2.2, 4.5, 5.7, 6.7, 8.0, 8.8, 9.9, 11.3, 13.3, 15.2, 17.0, 19.5, 21.4, 24.0, 25.4, 26.9, 27.4, 28.3, 30.6, 33.2, 36.6, 40.6, 45.3, 50.4, 56.9, 66.1, 77.7, 94.5, 119.4, 162.4, ]
    # ch2_PHlist4 = [1.3, 1.5, 3.6, 4.8, 5.8, 7.0, 7.7, 8.7, 10.0, 11.7, 13.6, 15.3, 17.5, 19.4, 21.6, 22.9, 24.4, 25.0, 26.9, 29.2, 31.6, 34.5, 38.0, 42.4, 47.3, 53.9, 62.8, 74.5, 91.9, 117.9, 165.6, ]

    ch1_BVlist4 = [  0,  30,  50,  70, 100, 200, 250, 300,  350,  400,  440,  470,  500,  520,  540,  560,  580,  590,  600,  610,  620,  630,  640,  650,  660,  670,  680,   690,   700, ]
    ch1_PHlist4 = [2.1, 2.2, 4.5, 5.7, 6.7, 8.0, 8.8, 9.9, 11.3, 13.3, 15.2, 17.0, 19.5, 21.4, 24.0, 26.9, 28.3, 30.6, 33.2, 36.6, 40.6, 45.3, 50.4, 56.9, 66.1, 77.7, 94.5, 119.4, 162.4, ]
    ch2_PHlist4 = [1.3, 1.5, 3.6, 4.8, 5.8, 7.0, 7.7, 8.7, 10.0, 11.7, 13.6, 15.3, 17.5, 19.4, 21.6, 24.4, 26.9, 29.2, 31.6, 34.5, 38.0, 42.4, 47.3, 53.9, 62.8, 74.5, 91.9, 117.9, 165.6, ]

    # h1 = createHistogram(ch1_BVlist3, ch1_PHlist3, "gain")
    # h2 = createHistogram(ch1_BVlist3, ch2_PHlist3, "nogain")

    h1 = createHistogram(ch1_BVlist4, ch1_PHlist4, "ch1")
    h2 = createHistogram(ch1_BVlist4, ch2_PHlist4, "ch2")

    c1 = r.TCanvas("c1", "c1")
    r.gStyle.SetOptStat(0)

    h1.SetMarkerStyle(8)
    h2.SetMarkerStyle(8)
    h1.SetMarkerSize(0.8)
    h2.SetMarkerSize(0.8)
    h1.SetMarkerColor(r.kOrange+3)
    h2.SetMarkerColor(r.kRed)
    h1.Draw("P")
    h2.Draw("Psame")

    leg = r.TLegend(0.2, 0.7, 0.36, 0.8)
    leg.AddEntry(h1, "ch1(gain)")
    leg.AddEntry(h2, "ch2(\"no gain\")")
    leg.Draw()

    c1.SaveAs("gaincurve_1031.pdf")
