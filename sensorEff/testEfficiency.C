// -*- C++ -*-
#include <iostream>
#include <fstream>
#include <algorithm>
#include <numeric>
#include <cmath>
#include <map>

#include "TH1.h"
#include "TH2.h"
#include "TFile.h"
#include "TChain.h"
#include "TGraph.h"
#include "TBranch.h"

using namespace std;

template<typename... Ts>
inline void plot1d(string name, float xval, map<string,TH1*> &allhistos, Ts... args)
{
  auto iter = allhistos.find(name);
  if (iter == allhistos.end()) {
    TH1D* currentHisto= new TH1D(name.c_str(), args...);
    // currentHisto->Sumw2();
    currentHisto->Fill(xval);
    allhistos.insert( pair<string, TH1D*>(name, currentHisto) );
  } else {
    iter->second->Fill(xval);
  }
}

template<typename... Ts>
inline void plot2d(string name, float xval, float yval, map<string,TH1*> &allhistos, Ts... args) {
  auto iter = allhistos.find(name);
  if (iter == allhistos.end()) {
    TH2D* currentHisto= new TH2D(name.c_str(), args...);
    // currentHisto->Sumw2();
    currentHisto->Fill(xval, yval);
    allhistos.insert( pair<string,TH2D*>(name, currentHisto) );
  } else {
    ((TH2D*) iter->second)->Fill(xval, yval);
  }
}

template<typename... Ts>
inline void graph1d(string name, map<string,TGraph*> &allgraphs, Ts... args) {
  auto iter = allgraphs.find(name);
  if (iter != allgraphs.end()) {
    cout << "[makeGraph]: TGraph with name: " << name << " already exist!\n";
  } else {
    TGraph* thisgraph = new TGraph(args...);
    thisgraph->SetName(name.c_str());
    allgraphs.insert( pair<string,TGraph*>(name, thisgraph) );
  }
}

inline TGraph* graphPulse(const int n, float* time, short* channel, string title = "", string name = "", map<string,TGraph*>* allgraphs = nullptr) {
  float* chan = new float[n];
  std::copy(channel, channel+n, chan);
  TGraph* thisgraph = new TGraph(n, time, chan);
  thisgraph->SetTitle(title.c_str());
  if (name != "") thisgraph->SetName(name.c_str());
  if (allgraphs) allgraphs->insert( pair<string,TGraph*>(name, thisgraph) );
  return thisgraph;
}

// Make a constant array of time bins
const auto tbins = []() {
  float* tbins = new float[1024];
  std::iota(tbins, tbins+1024, 0);
  return tbins;
} ();

int testEfficiency()
{

  // TFile* ifile = new TFile("../rootfiles/Run1563.root");
  TChain* ch = new TChain("pulse");
  // ch->Add("/eos/uscms/store/user/cmstestbeam/ETL/MT6Section1Data/122017/OTSDAQ/DRSPixelMerged_ReProcess-08-03-18/Run1537.root");
  // ch->Add("/eos/uscms/store/user/cmstestbeam/ETL/MT6Section1Data/122017/OTSDAQ/DRSPixelMerged_ReProcess-08-03-18/Run154[0-9].root");
  // ch->Add("/eos/uscms/store/user/cmstestbeam/ETL/MT6Section1Data/122017/OTSDAQ/DRSPixelMerged_ReProcess-08-03-18/Run155[0-8].root");
  // ch->Add("/eos/uscms/store/user/cmstestbeam/ETL/MT6Section1Data/122017/OTSDAQ/DRSPixelMerged_ReProcess-08-03-18/Run156[0-3].root");
  ch->Add("../rootfiles/Run1563.root");


  TBranch* pixel_branch = ch->GetBranch("");

  // Define variales and set branches
  int event;
  short tc[4]; // trigger counter bin
  float time[4][1024]; // calibrated time
  short raw[36][1024]; // ADC counts
  short channel[36][1024]; // calibrated input (in V)
  double channelFilter[36][1024]; // calibrated input (in V)
  float xmin[36]; // location of peak
  float base[36]; // baseline voltage
  float amp[36]; // pulse amplitude
  float integral[36]; // integral in a window
  float integralFull[36]; // integral over all bins
  float gauspeak[36]; // time extracted with gaussian fit
  float sigmoidTime[36];//time extracted with sigmoid fit
  float fullFitTime[36];//time extracted with sigmoid fit
  float linearTime0[36]; // constant fraction fit coordinates
  float linearTime15[36];
  float linearTime30[36];
  float linearTime45[36];
  float linearTime60[36];
  float fallingTime[36]; // falling exponential timestamp
  float risetime[36];
  float constantThresholdTime[36];
  float FFTtime[36];
  int HV[36];
  // float xIntercept, yIntercept;
  float xSlope, ySlope;
  float x1, y1, x2, y2;
  int nTracks;
  float chi2;

  ch->SetBranchAddress("event", &event);
  ch->SetBranchAddress("time", &time);
  ch->SetBranchAddress("channel", &channel);
  ch->SetBranchAddress("xmin", &xmin);
  ch->SetBranchAddress("amp", &amp);
  ch->SetBranchAddress("base", &base);
  ch->SetBranchAddress("integral", &integral);
  ch->SetBranchAddress("gauspeak", &gauspeak);
  ch->SetBranchAddress("xSlope", &xSlope);
  ch->SetBranchAddress("ySlope", &ySlope);
  ch->SetBranchAddress("x1", &x1);
  ch->SetBranchAddress("x2", &x2);
  ch->SetBranchAddress("y1", &y1);
  ch->SetBranchAddress("y2", &y2);
  ch->SetBranchAddress("chi2", &chi2);
  ch->SetBranchAddress("nTracks", &nTracks);

  // Histograms for output
  map<string,TH1*> hvec;
  map<string,TGraph*> gvec;
  TFile* outfile = new TFile("histos.root", "RECREATE");
  ofstream ofile("printout.txt");

  int gpocnt = 0;  // global print out count

  int nEventsTotal = ch->GetEntries();
  for (int ievt = 0; ievt < nEventsTotal; ++ievt) {
    ch->GetEntry(ievt);

    // Analysis code
    if (x1 < 10000 || y1 < 10000) continue;
    if (nTracks > 1 || chi2 > 7) continue;

    // plot1d("h_amp[0]", amp[0], hvec, "", 100, 0, 0.5);
    if (amp[0] < 0.01 || amp[0] > 0.1) continue;

    plot1d("gauspeak[0]", gauspeak[0], hvec, "", 100, 60, 160);
    if (gauspeak[0] < 103 || gauspeak[0] > 114) continue;

    plot1d("h_amp[7]",  amp[7] , hvec, "amp[7] [mV]" , 100, 0, 0.1);
    plot1d("h_amp[10]", amp[10], hvec, "amp[10] [mV]", 100, 0, 0.1);
    plot1d("h_amp[13]", amp[13], hvec, "amp[13] [mV]", 100, 0, 0.1);
    plot1d("h_amp[14]", amp[14], hvec, "amp[14] [mV]", 100, 0, 0.1);

    plot1d("h_xSlope_all", xSlope, hvec, "xSlope", 100, -0.0006, 0.0004);
    plot1d("h_ySlope_all", ySlope, hvec, "ySlope", 100, -0.0006, 0.0004);
    if (fabs(xSlope+0.00016) > 0.0003 || fabs(ySlope+0.00011) > 0.0003) continue;

    if (amp[10] > 0.008)
      plot2d("h2d_pix[10]", x1, y1, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);

    int exptbin0 = gauspeak[0] * 5.12;
    int exptbin_lo = exptbin0 - 69 - 30;
    int exptbin_hi = exptbin0 - 69 + 30;

    bool inarea10 = (x1>19800 && x1<21300 && y1>22900 && y1<24600);
    bool intrga10 = (x1>19600 && x1<21000 && y1>22700 && y1<24600);

    bool inarea13 = (x1>17600 && x1<19200 && y1>22800 && y1<24500);
    bool intrga13 = (x2>17400 && x2<19100 && y2>22500 && y2<24500);

    float theta = -0.03;
    float x1r = x1*cos(theta) - y1*sin(theta);
    float y1r = x1*sin(theta) + y1*cos(theta);

    bool areaW6_bot2 = (x1r>18000 && x1r<22200 && y1r>22000 && y1r<24200);
    bool areaW6_all4 = (x1r>17800 && x1r<22400 && y1r>21800 && y1r<26600);

    if (!areaW6_all4) continue;

    plot2d("hden2d_pix_W6all4_150", x1r, y1r, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);
    plot1d("hden_xboth_150", x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
    plot1d("hden_yboth_150", y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);

    plot2d("hden2d_pix_W6all4_200", x1r, y1r, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);
    if (y1r>22300 && y1r<24000)
      plot1d("hden_xboth_200", x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
    if (x1r>20300 && x1r<22100)
      plot1d("hden_yboth_200", y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);

    short* chptr;   // ptr to channel
    short* twinmin; // ptr to min in the expected time window

    for (int idx : {10, 13, 14, 7}) {
      if ((idx == 10 || idx == 13) && (y1r>22300 && y1r<24000)) {
        plot1d(Form("hden_pixx_ch[%d]_200", idx), x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
        plot1d(Form("hden_pixx_ch[%d]_150", idx), x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
      }
      if ((idx == 10 || idx == 14) && (x1r>20300 && x1r<22100)) {
        plot1d(Form("hden_pixy_ch[%d]_200", idx), y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);
        plot1d(Form("hden_pixy_ch[%d]_150", idx), y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);
      }

      chptr = channel[idx];  // ptr to channel
      twinmin = std::min_element(chptr+exptbin_lo, chptr+exptbin_hi); // ptr to min in the expected time window
      float twinamp = *twinmin * (-1.0/4096);  // move to unit V
      float twinint = -1.0 * std::accumulate(twinmin-20, twinmin+20, 0);
      float fwinint = -1.0 * std::accumulate(chptr+exptbin_lo, chptr+exptbin_hi, 0); // integral in the time window
      int minidx = twinmin - chptr;

      if (twinint > 200) {
        if ((idx == 10 || idx == 13) && (y1r>22300 && y1r<24000)) {
          plot1d(Form("hnum_pixx_ch[%d]_200", idx), x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
          plot1d("hnum_xboth_200", x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
        }
        if ((idx == 10 || idx == 14) && (x1r>20300 && x1r<22100)) {
          plot1d(Form("hnum_pixy_ch[%d]_200", idx), y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);
          plot1d("hnum_yboth_200", y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);
        }

        plot2d("hnum2d_pix_W6all4_200", x1r, y1r, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);
      }
      if (twinint > 150) {
        if ((idx == 10 || idx == 13) && (y1r>22300 && y1r<24000)) {
          plot1d(Form("hnum_pixx_ch[%d]_150", idx), x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
          plot1d("hnum_xboth_150", x1r, hvec, ";x^#prime(rotated) [#mum]", 200, 17500, 22500);
        }
        if ((idx == 10 || idx == 14) && (x1r>20300 && x1r<22100)) {
          plot1d(Form("hnum_pixy_ch[%d]_150", idx), y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);
          plot1d("hnum_yboth_150", y1r, hvec, ";y^#prime(rotated) [#mum]", 200, 21500, 26500);
        }

        plot2d("hnum2d_pix_W6all4_150", x1r, y1r, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);
      }

    }

    if (false) {
      if (inarea10) {
        int idx = 10;
        short* chptr = channel[idx];  // ptr to channel
        // Redo minimum finding
        short* twinmin = std::min_element(chptr+exptbin_lo, chptr+exptbin_hi); // ptr to min in the expected time window
        float twinamp = *twinmin * (-1.0/4096);  // move to unit V
        float twinint = -1.0 * std::accumulate(twinmin-20, twinmin+20, 0);
        float fwinint = -1.0 * std::accumulate(chptr+exptbin_lo, chptr+exptbin_hi, 0); // integral in the time window
        int minidx = twinmin - chptr;

        plot1d(Form("h_amp[%d]", idx), amp[idx], hvec, ";amp [V]", 100, 0, 0.05);
        plot2d(Form("h2d_area%d", idx), x1, y1, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);

        plot1d(Form("h_twinamp[%d]", idx), twinamp, hvec, ";amp [V]", 100, 0, 0.05);
        plot1d(Form("h_twinint[%d]", idx), twinint, hvec, ";time win integral", 120, -200, 1000);
        plot1d(Form("h_fwinint[%d]", idx), fwinint, hvec, ";fix win integral", 120, -200, 1000);

        if (amp[10] < 0.001) {
          plot1d(Form("h_twinamp[%d]_amp0", idx), twinamp, hvec, ";amp [V]", 100, 0, 0.05);
          plot1d(Form("h_twinint[%d]_amp0", idx), twinint, hvec, ";time win integral", 100, 0, 1000);
          if (gpocnt < 15) {
            ofile << __LINE__ << ": " << ++gpocnt << ": event = " << event << ", base = " << base[10] << ", integral = " << integral[10] << ", xmin= " << xmin[10];
            ofile <<  "   :  twinint= " << twinint << ", twinamp = " << twinamp << ", minidx = " << minidx << ", tdiff = " << exptbin0 - minidx << endl;
            auto title = Form("amp=%.3f, xmin=%.0f | minidx=%d, twinamp=%.4f, twinint=%.0f", amp[idx], xmin[idx], minidx, twinamp, twinint);
            graphPulse(1024, tbins, chptr, title, Form("g_pulse_vs_tbins_evt%d", event), &gvec);
          }
        }

        if (twinint > 100 && twinint < 200) {
          plot1d(Form("h_twinamp[%d]_int100to200", idx), twinamp, hvec, ";amp [V]", 100, 0, 0.05);
          if (gpocnt >= 15 && gpocnt < 30) {
            ofile << __LINE__ << ": " << ++gpocnt << ": event = " << event << ", base = " << base[10] << ", integral = " << integral[10] << ", xmin= " << xmin[10];
            ofile <<  "   :  twinint= " << twinint << ", twinamp = " << twinamp << ", minidx = " << minidx << ", tdiff = " << exptbin0 - minidx << endl;
            auto title = Form("amp=%.3f, xmin=%.0f | minidx=%d, twinamp=%.4f, twinint=%.0f", amp[idx], xmin[idx], minidx, twinamp, twinint);
            graphPulse(1024, time[0], chptr, title, Form("g_pulse_vs_time_evt%d", event), &gvec);
          }
        }
      }
      else if (inarea13) {
        int idx = 13;
        plot2d(Form("h2d_area%d", idx), x1, y1, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);
        short* absmin = std::min_element(channel[idx]+100, channel[idx]+900); // ptr to min in the expected time window

        if (*absmin > -0.006*4096) continue;

        idx = 10;
        short* chptr = channel[idx];  // ptr to channel
        // Redo minimum finding
        short* twinmin = std::min_element(chptr+exptbin_lo, chptr+exptbin_hi); // ptr to min in the expected time window
        float twinamp = *twinmin * (-1.0/4096);  // move to unit mV
        float twinint = -1.0 * std::accumulate(twinmin-20, twinmin+20, 0);
        float fwinint = -1.0 * std::accumulate(chptr+exptbin_lo, chptr+exptbin_hi, 0); // integral in the time window
        int minidx = twinmin - chptr;

        plot1d(Form("hfake_amp[%d]", idx), amp[idx], hvec, ";amp [V]", 100, 0, 0.05);
        plot1d(Form("hfake_twinamp[%d]", idx), twinamp, hvec, ";amp [V]", 100, 0, 0.05);
        plot1d(Form("hfake_twinint[%d]", idx), twinint, hvec, ";time win integral", 120, -200, 1000);
        plot1d(Form("hfake_fwinint[%d]", idx), fwinint, hvec, ";fix win integral", 120, -200, 1000);

        if (twinint > 100) {
          plot1d(Form("hfake_twinamp[%d]_int100", idx), twinamp, hvec, ";amp [V]", 100, 0, 0.05);
          plot1d(Form("hfake_fwinint[%d]_int100", idx), fwinint, hvec, ";fix win integral", 100, 0, 1000);
          if (gpocnt >= 40 && gpocnt < 50) {
            ofile << __LINE__ << ": fake " << ++gpocnt << ": event = " << event << ", base = " << base[10] << ", integral = " << integral[10] << ", xmin= " << xmin[10];
            ofile <<  "   :  twinint= " << twinint << ", twinamp = " << twinamp << ", minidx = " << minidx << ", tdiff = " << exptbin0 - minidx << endl;
            auto title = Form("fake: amp=%.3f, xmin=%.0f | minidx=%d, twinamp=%.4f, twinint=%.0f", amp[idx], xmin[idx], minidx, twinamp, twinint);
            graphPulse(1024, tbins, chptr, title, Form("gfake_pulse_vs_tbins_evt%d", event), &gvec);
          }
        } else if (gpocnt >= 30 && gpocnt < 40) {
          ofile << __LINE__ << ": fake " << ++gpocnt << ": event = " << event << ", base = " << base[10] << ", integral = " << integral[10] << ", xmin= " << xmin[10];
          ofile <<  "   :  twinint= " << twinint << ", twinamp = " << twinamp << ", minidx = " << minidx << ", tdiff = " << exptbin0 - minidx << endl;
          auto title = Form("fake: amp=%.3f, xmin=%.0f | minidx=%d, twinamp=%.4f, twinint=%.0f", amp[idx], xmin[idx], minidx, twinamp, twinint);
          graphPulse(1024, time[0], chptr, title, Form("gfake_pulse_vs_time_evt%d", event), &gvec);
        }
      }
    }

  }

  outfile->cd();
  for (auto& h : hvec) {
    int nbin = h.second->GetNbinsX();
    float uf = h.second->GetBinContent(0);
    float of = h.second->GetBinContent(nbin+1);
    if (uf > 0) h.second->SetBinContent(1, h.second->GetBinContent(1) + uf);
    if (of > 0) h.second->SetBinContent(nbin, h.second->GetBinContent(nbin) + of);
    h.second->SetLineWidth(2);
    h.second->Write();

    if (h.first.find("hnum") == 0) {
      string hname = h.first;
      hname.erase(0, 4);
      TH1F* h_ratio = (TH1F*) h.second->Clone(("ratio"+hname).c_str());
      h_ratio->Divide(h_ratio, hvec.at("hden"+hname), 1, 1, "B");
      h_ratio->Write();
    }
  }
  for (auto& g : gvec) {
    g.second->Write();
  }

  // // Print out:
  // ofile << Form("Efficiency for ch10 after int > 200: %.2f%%", 100.0*hvec["h_twinint[10]"]->Integral(20, -1)/hvec["h_twinint[10]"]->Integral(0, -1)) << endl;
  // ofile << Form("Fake rate for ch10 after int > 200: %.2f%%", 100.0*hvec["hfake_twinint[10]"]->Integral(20, -1)/hvec["hfake_twinint[10]"]->Integral(0, -1)) << endl << endl;
  // ofile << Form("Efficiency for ch10 after int > 150: %.2f%%", 100.0*hvec["h_twinint[10]"]->Integral(15, -1)/hvec["h_twinint[10]"]->Integral(0, -1)) << endl;
  // ofile << Form("Fake rate for ch10 after int > 150: %.2f%%", 100.0*hvec["hfake_twinint[10]"]->Integral(15, -1)/hvec["hfake_twinint[10]"]->Integral(0, -1)) << endl << endl;
  // ofile << Form("Efficiency for ch10 after int > 100: %.2f%%", 100.0*hvec["h_twinint[10]"]->Integral(10, -1)/hvec["h_twinint[10]"]->Integral(0, -1)) << endl;
  // ofile << Form("Fake rate for ch10 after int > 100: %.2f%%", 100.0*hvec["hfake_twinint[10]"]->Integral(10, -1)/hvec["hfake_twinint[10]"]->Integral(0, -1)) << endl << endl;

  // cout << Form("Efficiency for ch10 after int > 200: %.2f%%", 100.0*hvec["h_twinint[10]"]->Integral(20, -1)/hvec["h_twinint[10]"]->Integral(0, -1)) << endl;
  // cout << Form("Fake rate for ch10 after int > 200: %.2f%%", 100.0*hvec["hfake_twinint[10]"]->Integral(20, -1)/hvec["hfake_twinint[10]"]->Integral(0, -1)) << endl << endl;
  // cout << Form("Efficiency for ch10 after int > 150: %.2f%%", 100.0*hvec["h_twinint[10]"]->Integral(15, -1)/hvec["h_twinint[10]"]->Integral(0, -1)) << endl;
  // cout << Form("Fake rate for ch10 after int > 150: %.2f%%", 100.0*hvec["hfake_twinint[10]"]->Integral(15, -1)/hvec["hfake_twinint[10]"]->Integral(0, -1)) << endl << endl;
  // cout << Form("Efficiency for ch10 after int > 100: %.2f%%", 100.0*hvec["h_twinint[10]"]->Integral(10, -1)/hvec["h_twinint[10]"]->Integral(0, -1)) << endl;
  // cout << Form("Fake rate for ch10 after int > 100: %.2f%%", 100.0*hvec["hfake_twinint[10]"]->Integral(10, -1)/hvec["hfake_twinint[10]"]->Integral(0, -1)) << endl << endl;

  return 0;
}
