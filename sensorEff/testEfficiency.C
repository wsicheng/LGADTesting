// -*- C++ -*-

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

inline TGraph* graphPulse(const int n, float* time, short* channel, string name = "", map<string,TGraph*>* allgraphs = nullptr) {
  float* chan = new float[n];
  copy(channel, channel+n, chan);
  TGraph* thisgraph = new TGraph(n, time, chan);
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
    
    if (amp[10] > 0.01)
      plot2d("h2d_pix[10]", x1, y1, hvec, ";x1[#mum];y1[#mum]", 120, 17000, 23000, 120, 21000, 27000);

    int exptbin0 = gauspeak[0] * 5.12;
    int exptbin_lo = exptbin0 - 69 - 30;
    int exptbin_hi = exptbin0 - 69 + 30;

    if (amp[10] < 0.002 && gpocnt < 15) {
      short* chptr = channel[10];  // ptr to channel
      short* twinmin = std::min_element(chptr+exptbin_lo, chptr+exptbin_hi); // ptr to min in the expected time window
      int minidx = twinmin - chptr;
      // float twinint = std::accumulate(twinmin-20, twinmin+20, 0); // integral in the time window
      float twinint = std::accumulate(chptr+exptbin_lo, chptr+exptbin_hi, 0); // integral in the time window
      float twinamp = *twinmin * (1.0/4096);
      cout << __LINE__ << ": " << ++gpocnt << ": event = " << event << ", base = " << base[10] << ", integral = " << integral[10] << ", xmin= " << xmin[10];
      cout <<  "   :  twinint= " << twinint << ", twinamp = " << twinamp << ", minidx = " << minidx << ", tdiff = " << exptbin0 - minidx << endl;
      graphPulse(1024, time[0], chptr, Form("h2d_shape_%d", event), &gvec);
      graphPulse(1024, tbins, chptr, Form("h2d_pulse_vs_tbins_%d", event), &gvec);
    }

    if (gpocnt == 15) break;

  }

  outfile->cd();
  for (auto& h : hvec) {
    int nbin = h.second->GetNbinsX();
    float uf = h.second->GetBinContent(0);
    float of = h.second->GetBinContent(nbin+1);
    if (uf > 0) h.second->SetBinContent(1, h.second->GetBinContent(1) + uf);
    if (of > 0) h.second->SetBinContent(nbin, h.second->GetBinContent(nbin) + of);
    h.second->Write();
  }
  for (auto& g : gvec) {
    g.second->Write();
  }

  return 0;
}
