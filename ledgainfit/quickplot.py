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

    # h1 = createHistogram(ch1_BVlist3, ch1_PHlist3, "gain")
    # h2 = createHistogram(ch1_BVlist3, ch2_PHlist3, "nogain")

    # LED scan on Fermilab board, source morderate close, no filter, source pulse at 6V (3V passed over)
    # Data taken on 2017/10/31 Tue morning
    ch1_BVlist4 = [  0,  30,  50,  70, 100, 200, 250, 300,  350,  400,  440,  470,  500,  520,  540,  560,  580,  590,  600,  610,  620,  630,  640,  650,  660,  670,  680,   690,   700, ]
    ch1_PHlist4 = [2.1, 2.2, 4.5, 5.7, 6.7, 8.0, 8.8, 9.9, 11.3, 13.3, 15.2, 17.0, 19.5, 21.4, 24.0, 26.9, 28.3, 30.6, 33.2, 36.6, 40.6, 45.3, 50.4, 56.9, 66.1, 77.7, 94.5, 119.4, 162.4, ]
    ch2_PHlist4 = [1.3, 1.5, 3.6, 4.8, 5.8, 7.0, 7.7, 8.7, 10.0, 11.7, 13.6, 15.3, 17.5, 19.4, 21.6, 24.4, 26.9, 29.2, 31.6, 34.5, 38.0, 42.4, 47.3, 53.9, 62.8, 74.5, 91.9, 117.9, 165.6, ]


    # h1 = createHistogram(ch1_BVlist4, ch1_PHlist4, "ch1")
    # h2 = createHistogram(ch1_BVlist4, ch2_PHlist4, "ch2")


    # Quick LED scan on 2017/11/3 Fri afternoon, on Fermilab board, for the purpose of testing the satuation hypothesis
    BVlist5 = [ 160, 200, 250, 300, 350, 400, 450, 500, 550, 600, 650, 680, 700]
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

    ch1_PH_6V10Filter_1 = [ 2.5, 2.6, 0, 0, 0, 0, 0, 3.5, 0, 4.6, 6.9, 10.4, 17.2, ]
    ch2_PH_6V10Filter_1 = [ 1.9, 1.9, 0, 0, 0, 0, 0, 2.7, 0, 3.5, 5.3, 8.3, 14.1, ]


    h1 = createHistogram(BVlist5, ch1_PH_6VnoFilter, "6VnoFilter")
    h2 = createHistogram(BVlist5, ch1_PH_4VnoFilter, "4VnoFilter")
    h3 = createHistogram(BVlist5, ch1_PH_6Vp3Filter, "6Vp3Filter")
    h4 = createHistogram(BVlist5, ch1_PH_4Vp3Filter, "4Vp3Filter")

    h5 = createHistogram(BVlist5, ch1_PH_6V10Filter_1, "6V10Filter")

    c1 = r.TCanvas("c1", "c1")
    r.gStyle.SetOptStat(0)

    h1.SetMarkerStyle(8)
    h2.SetMarkerStyle(4)
    h1.SetMarkerSize(0.8)
    h2.SetMarkerSize(0.8)
    h1.SetMarkerColor(r.kOrange+3)
    h2.SetMarkerColor(r.kRed)

    h3.SetMarkerStyle(8)
    h4.SetMarkerStyle(4)
    h3.SetMarkerSize(0.8)
    h4.SetMarkerSize(0.8)
    h3.SetMarkerColor(r.kTeal)
    h4.SetMarkerColor(r.kAzure)

    h5.SetMarkerStyle(8)
    h5.SetMarkerSize(0.8)
    h5.SetMarkerColor(r.kGray)

    # h2.Scale(ch1_PH_6VnoFilter[1] / ch1_PH_4VnoFilter[1])
    # h3.Scale(ch1_PH_6VnoFilter[1] / ch1_PH_6Vp3Filter[1])
    # h4.Scale(ch1_PH_6VnoFilter[1] / ch1_PH_4Vp3Filter[1])
    # h5.Scale(ch1_PH_6VnoFilter[1] / ch1_PH_6V10Filter_1[1])

    h2.Scale(ch1_PH_6VnoFilter[7] / ch1_PH_4VnoFilter[7])
    h3.Scale(ch1_PH_6VnoFilter[7] / ch1_PH_6Vp3Filter[7])
    h4.Scale(ch1_PH_6VnoFilter[7] / ch1_PH_4Vp3Filter[7])
    h5.Scale(ch1_PH_6VnoFilter[7] / ch1_PH_6V10Filter_1[7])

    h1.Draw("P")
    h2.Draw("Psame")
    h3.Draw("Psame")
    h4.Draw("Psame")
    h5.Draw("Psame")

    leg = r.TLegend(0.2, 0.7, 0.44, 0.86)
    leg.AddEntry(h1, "ch1 6VnoFilter")
    leg.AddEntry(h2, "ch1 4VnoFilter")
    leg.AddEntry(h3, "ch1 6Vp3Filter")
    leg.AddEntry(h4, "ch1 4Vp3Filter")
    leg.AddEntry(h5, "ch1 6V10Filter")

    leg.Draw()

    # c1.SetLogy()
    c1.SaveAs("scan_ch1_Nov6.pdf")


    c1.Clear()
    leg.Clear()

    hr13 = h1.Clone()
    hr13.Divide(h3)
    hr24 = h2.Clone()
    hr24.Divide(h4)
    hr12 = h1.Clone()
    hr12.Divide(h2)
    hr34 = h3.Clone()
    hr34.Divide(h4)

    hr13.SetMarkerStyle(2)
    hr24.SetMarkerStyle(2)
    hr12.SetMarkerStyle(2)
    hr34.SetMarkerStyle(2)
    hr13.SetMarkerSize(2)
    hr24.SetMarkerSize(2)
    hr12.SetMarkerSize(2)
    hr34.SetMarkerSize(2)
    hr13.SetMarkerColor(r.kRed)
    hr24.SetMarkerColor(r.kAzure)
    hr12.SetMarkerColor(r.kOrange+2)
    hr34.SetMarkerColor(r.kGreen)

    hr13.GetYaxis().SetRangeUser(0, 3)
    hr13.Draw("P")
    hr24.Draw("Psame")
    hr12.Draw("Psame")
    hr34.Draw("Psame")

    leg.AddEntry(hr13, "6V, noFilter/p3Filter")
    leg.AddEntry(hr24, "4V, noFilter/p3Filter")
    leg.AddEntry(hr12, "noFilter, 6V/4V")
    leg.AddEntry(hr34, "p3Filter, 6V/4V")
    leg.Draw()


    c1.SaveAs("scan_ratios_Nov3.pdf")
