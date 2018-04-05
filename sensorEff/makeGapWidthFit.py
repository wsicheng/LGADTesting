import os
import ROOT as r
r.gROOT.SetBatch(1)

os.system('mkdir -p plots')

def fitWidthY(fin):
    c1 = r.TCanvas("c1", "c1", 800, 600)

    h1 = fin.Get("ratio_pixy_ch[10]_200")
    h2 = fin.Get("ratio_pixy_ch[14]_200")
    h2.SetLineColor(r.kRed)
    h1.Draw()
    h2.Draw("same")
    c1.Print("plots/hrat_yboth_ch10_ch14.pdf")

    f1 = r.TF1("f1", "[0]*TMath::Erf((x-[1])/[2])+[3]", 24100, 25000)
    f1.SetParameters(0.3, 24100, 100, 0.01)
    h2.Fit(f1,'QNR')
    f1.SetLineColor(r.kBlue)

    print f1.GetParameter(0), f1.GetParameter(1), f1.GetParameter(2), f1.GetParameter(3)

    f2 = r.TF1("f2", "[0]*TMath::Erf(([1]-x)/[2])+[3]", 23200, 24300)
    f2.SetParameters(0.3, 24100, 100, 0.01)
    h1.Fit(f2,'QNR')

    print f2.GetParameter(0), f2.GetParameter(1), f2.GetParameter(2), f2.GetParameter(3)

    r.gStyle.SetOptStat(0)

    h1.Draw()
    h2.Draw("same")
    f1.Draw("same")
    f2.Draw("same")

    p1 = 0.90*(f2.GetParameter(0)+f2.GetParameter(3))
    p2 = 0.90*(f1.GetParameter(0)+f1.GetParameter(3))
    e1 = f2.GetX(p1)
    e2 = f1.GetX(p2)
    print "e1 = {}, e2 = {}".format(e1, e2)
    print "Width =", e2 - e1

    arr = r.TArrow(e1, p1, e2, p2, 0.02, "<|>")
    arr.SetAngle(35);
    arr.SetLineWidth(3);
    arr.SetLineColor(1);
    arr.SetFillColor(1);
    arr.Draw();

    tex = r.TLatex(0.6, 0.8,"width = {:.1f} #mum".format(e2-e1))
    tex.SetNDC();
    tex.SetTextSize(0.05);
    tex.Draw()

    c1.Print("plots/hrat_yboth_testfit90_ch10_ch14.pdf")

def fitWidthX(fin):
    c1 = r.TCanvas("c1", "c1", 800, 600)


    h1 = fin.Get("ratio_pixx_ch[13]_200")
    h2 = fin.Get("ratio_pixx_ch[10]_200")
    h2.SetLineColor(r.kRed)
    h1.Draw()
    h2.Draw("same")
    c1.Print("plots/hrat_xboth_ch10_ch13.pdf")

    # f1 = r.TF1("f1", "[0]*TMath::Erf(([1]-x)/[2])+[3]", 19500, 20500)
    f1 = r.TF1("f1", "[0]*TMath::Erf((x-[1])/[2])+[3]", 19900, 21200)
    f1.SetParameters(0.3, 20100, 100, 0.01)
    h2.Fit(f1,'QNR')
    f1.SetLineColor(r.kBlue)

    print f1.GetParameter(0), f1.GetParameter(1), f1.GetParameter(2), f1.GetParameter(3)

    f2 = r.TF1("f2", "[0]*TMath::Erf(([1]-x)/[2])+[3]", 19000, 20300)
    f2.SetParameters(0.3, 20100, 100, 0.01)
    h1.Fit(f2,'QNR')

    print f2.GetParameter(0), f2.GetParameter(1), f2.GetParameter(2), f2.GetParameter(3)

    r.gStyle.SetOptStat(0)

    h2.Draw()
    h1.Draw("same")
    f1.Draw("same")
    f2.Draw("same")

    p1 = 0.90*(f2.GetParameter(0)+f2.GetParameter(3))
    p2 = 0.90*(f1.GetParameter(0)+f1.GetParameter(3))
    e1 = f2.GetX(p1)
    e2 = f1.GetX(p2)
    print "e1 = {}, e2 = {}".format(e1, e2)
    print "Width =", e2 - e1

    arr = r.TArrow(e1, p1, e2, p2, 0.02, "<|>")
    arr.SetAngle(35);
    arr.SetLineWidth(3);
    arr.SetLineColor(1);
    arr.SetFillColor(1);
    arr.Draw();

    tex = r.TLatex(0.24, 0.77,"width = {:.1f} #mum".format(e2-e1))
    tex.SetNDC();
    tex.SetTextSize(0.05);
    tex.Draw()

    c1.Print("plots/hrat_xboth_testfit90_ch10_ch13.pdf")


if __name__ == '__main__':
    
    fin = r.TFile("histos.root")
    
    fitWidthX(fin)
    fitWidthY(fin)




