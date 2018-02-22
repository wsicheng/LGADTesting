// -*- C++ -*-
// Simple ROOT macro to check between hits from strip data and pixel data

struct FTBFPixelEvent {
  double xSlope;
  double ySlope;
  double xIntercept;
  double yIntercept;
  double chi2;
  int trigger;
  int runNumber;
  Long64_t timestamp;
};

template<typename... Ts>
inline void plot1d(string name, float xval, double weight, map<string,TH1*> &allhistos, Ts... args) {
  auto iter = allhistos.find(name);
  if (iter == allhistos.end()) {
    TH1D* currentHisto= new TH1D(name.c_str(), args...);
    currentHisto->Sumw2();
    currentHisto->Fill(xval, weight);
    allhistos.insert( pair<string,TH1D*>(name, currentHisto) );
  } else {
    iter->second->Fill(xval, weight);
  }
}

template<typename... Ts>
inline void plot2d(string name, float xval, float yval, double weight, map<string,TH1*> &allhistos, Ts... args) {
  auto iter = allhistos.find(name);
  if (iter == allhistos.end()) {
    TH2D* currentHisto= new TH2D(name.c_str(), args...);
    currentHisto->Sumw2();
    currentHisto->Fill(xval, yval, weight);
    allhistos.insert( pair<string,TH2D*>(name, currentHisto) );
  } else {
    ((TH2D*) iter->second)->Fill(xval, yval, weight);
  }
}

void compareHits() {

  // Histograms
  map<string,TH1*> hvec;

  TFile* pixelDataFile = TFile::Open("pixel_Run1655.root" ,"READ");
  TFile* stripDataFile = TFile::Open("strip_Run1655.root" ,"READ");

  TFile* outfile = new TFile("hists.root", "RECREATE");

  TH1D* test = new TH1D("h_test", "test", 100, 0, 100);

  TTree* pixelTree = (TTree*) pixelDataFile->Get("MAPSA");
  TTree* stripTree = (TTree*) stripDataFile->Get("MAPSA");

  TBranch* pixelBranch = pixelTree->GetBranch("event");
  TBranch* stripBranch = stripTree->GetBranch("eventUpstream");

  if (!pixelTree || !stripTree) { cout << "Error: Pixel Tree not found!\n"; return; }

  FTBFPixelEvent pixelEvent;
  FTBFPixelEvent stripEvent;

  pixelBranch->SetAddress(&pixelEvent);
  stripBranch->SetAddress(&stripEvent);

  int nEventsPixel = pixelTree->GetEntries();
  int nEventsStrip = stripTree->GetEntries();

  for (int ipixel = 0, istrip = 0; ipixel < nEventsPixel && istrip < nEventsStrip; ) {
    stripTree->GetEntry(istrip);

    // Ignore multiple trigger events for now, coming back later
    pixelTree->GetEntry(ipixel+1);
    int nexttrig = pixelEvent.trigger;
    pixelTree->GetEntry(ipixel);
    if (pixelEvent.trigger == nexttrig) {
      if (stripEvent.trigger == nexttrig) {
        ++istrip;
        plot1d("nMultiTrig", 0, 1, hvec, "", 1, 0, 1);
      }
      ipixel += 2;
      continue;
    }
      
    if (pixelEvent.trigger == stripEvent.trigger) {
      
      float diff_x = fabs(pixelEvent.xIntercept - stripEvent.xIntercept);
      float diff_y = fabs(pixelEvent.yIntercept - stripEvent.yIntercept);

      float diff_xSlope = fabs(pixelEvent.xSlope - stripEvent.xSlope);
      float diff_ySlope = fabs(pixelEvent.ySlope - stripEvent.ySlope);

      // if (diff_x > 780 && diff_x < 880 && diff_y > 100 && diff_y < 200) {
      if (true) {

        plot2d("pixel_hits", pixelEvent.xIntercept, pixelEvent.yIntercept, 1, hvec, "Pixel;pixel_x; pixel_y", 70, 14000, 28000, 70, 12000, 26000);
        plot2d("strip_hits", stripEvent.xIntercept, stripEvent.yIntercept, 1, hvec, "Strip;strip_x; strip_y", 70, 13000, 27000, 70, 12000, 26000);

        plot1d("strip_xSlope", stripEvent.xSlope, 1, hvec, "", 100, -4e-4, 4e-4);
        plot1d("strip_ySlope", stripEvent.ySlope, 1, hvec, "", 100, -3e-4, 3e-4);
        plot1d("pixel_xSlope", pixelEvent.xSlope, 1, hvec, "", 100, -2e-4, 2e-4);
        plot1d("pixel_ySlope", pixelEvent.ySlope, 1, hvec, "", 100, -2e-4, 2e-4);

        plot1d("diff_xIntercept", diff_x, 1, hvec, "", 200, 500, 1300);
        plot1d("diff_yIntercept", diff_y, 1, hvec, "", 200, 0, 400);

        diff_x -= 836;
        diff_y -= 159;
        plot1d("diff_dist", sqrt(diff_y*diff_y+diff_x*diff_x), 1, hvec, "", 200, 0, 400);

        plot1d("diff_xSlope", diff_xSlope, 1, hvec, "", 100, 0, 3e-4);
        plot1d("diff_ySlope", diff_ySlope, 1, hvec, "", 100, 0, 3e-4);
      }
      ++ipixel;
      ++istrip;
    } else if (pixelEvent.trigger < stripEvent.trigger) {
      ++ipixel;
    } else {
      ++istrip;
    }

  }

  outfile->cd();
  for (auto& h : hvec) {
    int nbin = h.second->GetNbinsX();
    int uf = h.second->GetBinContent(0);
    int of = h.second->GetBinContent(nbin+1);
    if (uf > 0) h.second->SetBinContent(1, h.second->GetBinContent(1) + uf);
    if (of > 0) h.second->SetBinContent(nbin, h.second->GetBinContent(nbin) + of);
    h.second->Write();
  }


}
