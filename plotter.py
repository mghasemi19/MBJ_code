import ROOT
import glob, os
import sys
import numpy as np
from array import array
import random

#ROOT.gStyle.SetErrorX(0.)
ROOT.gStyle.SetOptStat(0)
ROOT.gStyle.SetOptTitle(0)

def getSampleColor(sample):
   if sample == "ttbar":         return ROOT.kAzure+8  
   if sample == "W_jets":       return ROOT.kOrange-3
   if sample == "Z_jets":     return ROOT.kYellow-4
   if sample == "singletop":     return ROOT.kGreen-9
   if sample == "topEW":     return ROOT.kGreen+2
   if sample == "diboson":     return ROOT.kRed+1

  
def plotter_0L(var, bkgs_name, xlable, leg_0L, bkg_data_file, QCD_file, Signal_file):
  
  # Initialize all the histograms  
  hdata_tmp = bkg_data_file.Get("h_obsData")
  hbkg_list = []
  for bkg in bkgs_name: 
    hbkg = bkg_data_file.Get(bkg)
    hbkg.SetFillColor(getSampleColor(bkg))
    hbkg_list.append(bkg_data_file.Get(bkg))

  for QCD_name in QCD_file.GetListOfKeys():
    if "QCD_"+var in QCD_name.GetName(): 
       hQCD = QCD_file.Get(QCD_name.GetName())
       overflow = hQCD.GetBinContent(hQCD.GetNbinsX()+1);
       value = overflow + hQCD.GetBinContent(hQCD.GetNbinsX())
       hQCD.SetBinContent(hQCD.GetNbinsX(), value)
       
  stack = ROOT.THStack("stack","stack")
  stack.Add(hQCD)
  for hist in hbkg_list: stack.Add(hist)

  i = 0
  htot_list = []
  htot_list.append(hQCD)
  for hist in hbkg_list:
    if i == 0:
      htot = hbkg_list[0].Clone()
    else:     
      htot.Add(hist)
    i+=1  
    htot_list.append(hist)
  htot.Add(hQCD)

  htot.SetLineColor(1)
  SM_tot = htot.Clone("SM_tot")
  SM_tot.SetFillStyle(3001)
  SM_error = htot.Clone("SM_error")
  SM_tot.SetLineWidth(3)
  ROOT.gStyle.SetHatchesSpacing(0.8)
  SM_error.SetFillStyle(3354)
  SM_error.SetFillColorAlpha(1, 0.4)
  
  for sig_name in Signal_file.GetListOfKeys():
    if "Gtt_1900_5000_1_nominal_"+var in sig_name.GetName(): 
       #print sig_name.GetName()
       hGtt = Signal_file.Get(sig_name.GetName())
       overflow = hGtt.GetBinContent(hGtt.GetNbinsX()+1);
       value = overflow + hGtt.GetBinContent(hGtt.GetNbinsX())
       hGtt.SetBinContent(hGtt.GetNbinsX(), value)       
       hGtt.SetLineColor(51)
       hGtt.SetLineStyle(9)
       hGtt.SetLineWidth(3)
    if "Gbb_1900_5000_1_nominal_"+var in sig_name.GetName():
       #print sig_name.GetName()
       hGbb = Signal_file.Get(sig_name.GetName())
       overflow = hGbb.GetBinContent(hGbb.GetNbinsX()+1);
       value = overflow + hGbb.GetBinContent(hGbb.GetNbinsX())
       hGbb.SetBinContent(hGbb.GetNbinsX(), value)
       hGbb.SetLineColor(ROOT.kMagenta)
       hGbb.SetLineStyle(2)
       hGbb.SetLineWidth(3)

  hdata = hbkg_list[0].Clone("data")
  grdata = ROOT.TGraphErrors()
  grdata.SetMarkerStyle(20)
  
  for i in range(0,hdata_tmp.GetN()):
    x=hdata_tmp.GetX()[i]
    y=hdata_tmp.GetY()[i]
    #Ex=hdata_RF.GetErrorX(i)
    Ey=hdata_tmp.GetErrorY(i)
    hdata.SetBinContent(i+1,y)
    hdata.SetBinError(i+1, Ey)  
    grdata.SetPoint(i+1, x, y)
    grdata.SetPointError(i+1, 0, Ey)

  c1 = ROOT.TCanvas("c1", "Test plotter", 600, 600)
  c1.SetLogy()
  c1.SetLeftMargin(0.15)
  pad1 = ROOT.TPad("pad1", "pad1", 0, 0.29, 1, 1.0)
  pad1.SetBottomMargin(0)  # joins upper and lower plot
  pad1.SetLogy()
  pad1.SetTicky()
  pad1.SetTickx()
  #pad1.SetTickx()
  pad1.Draw()
  # Lower ratio plot is pad2
  c1.cd()  # returns to main canvas before defining pad2
  pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.27)
  pad2.SetTopMargin(0)  # joins upper and lower plot
  pad2.SetBottomMargin(0.3)
  pad2.SetTicky()
  pad2.SetTickx()
  pad2.SetFillColor(0)
  pad2.Draw()

  pad1.cd()
  hdata.SetMarkerStyle(20)
  hdata.SetMarkerColor(1)
  SM_tot.GetYaxis().SetTitle("Events")
  #SM_tot.GetYaxis().SetTitleSize(0.1)
  histo_max=hdata.GetMaximum()
  SM_tot.SetMaximum(400*histo_max)
  SM_tot.SetMinimum(0.2)
  if var == "jets_n":
    SM_tot.GetXaxis().SetNdivisions(8)
  if var == "bjets_n":
    SM_tot.GetXaxis().SetNdivisions(4)

  #ROOT.gStyle.SetErrorX(0.);
  SM_tot.Draw("hist")
  stack.Draw("hist same")
  hGtt.Draw("hist same")
  hGbb.Draw("hist same")
  SM_error.Draw("same E2")
  #hdata.Draw("same E0")  
  grdata.Draw("same PZ")
 
  leg=ROOT.TLegend(0.65,0.5,0.9,0.85)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)  
  leg.AddEntry(grdata, "Data", "p")
  leg.AddEntry(SM_error, "Total background", "lf")
  for index, h in enumerate(reversed(htot_list)):
    leg.AddEntry(h, leg_0L[index], "f")
  leg.Draw()

  leg_sig=ROOT.TLegend(0.15,0.6,0.5,0.7)
  leg_sig.SetFillStyle(0)
  leg_sig.SetLineColor(0)  
  leg_sig.AddEntry(hGtt, "Gtt: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 1900, 1 (x50)", "l")
  leg_sig.AddEntry(hGbb, "Gbb: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 1900, 1 (x50)", "l")
  leg_sig.Draw()

  write=["#bf{#it{ATLAS}}    Internal","#sqrt{s} = 13 TeV, 139 fb^{-1}","0L Preselection "]
  text =  ROOT.TLatex()
  text.SetNDC()
  text.SetTextAlign( 11 )
  text.SetTextFont( 42 )
  text.SetTextSize( 0.04 )
  text.SetTextColor( 1 )
  y = 0.83
  for t in write:
     #if "79.9" in t or '36' in t or '43.8' in t:
        #y = y-0.08
     #else:
     text.DrawLatex(0.15,y, t)
     y = y-0.055

  ROOT.gPad.Modified()
  ROOT.gPad.Update()
  pad1.RedrawAxis()
  pad1.Update()
  
  pad2.cd()
  hratio = hdata.Clone("hratio")  
  hratio.Divide(htot)
  grratio = ROOT.TGraphErrors()
  grratio.SetMarkerStyle(20)
  for i in range(0,hratio.GetNbinsX()):
    Ygr=hratio.GetBinContent(i+1)
    errYgr=hratio.GetBinError(i+1)
    Xgr=hratio.GetXaxis().GetBinCenter(i+1)    
    grratio.SetPoint(i+1, Xgr, Ygr)
    grratio.SetPointError(i+1, 0, errYgr)

  nbin = hratio.GetNbinsX()
  low_bin = hratio.GetXaxis().GetBinLowEdge(1)
  high_bin = hratio.GetXaxis().GetBinUpEdge(nbin)

  hline=ROOT.TH1D("hline", "hline", 1, low_bin, high_bin)
  hline.SetLineColor(1)
  hline.SetBinContent(1,1)
  hline.SetLineStyle(2)
  hline.SetLineWidth(1)

  hline.SetMinimum(0.4)
  hline.SetMaximum(1.7)  
  hline.GetYaxis().SetNdivisions(3)
  if var == "jets_n":
    hline.GetXaxis().SetNdivisions(8)
  if var == "bjets_n":
    hline.GetXaxis().SetNdivisions(4)

  hline.GetYaxis().SetTitle("Data/SM")
  hline.GetXaxis().SetTitle(xlable)
  hline.GetYaxis().CenterTitle()

  hline.GetXaxis().SetLabelSize(hline.GetXaxis().GetLabelSize()*2.9)
  hline.GetXaxis().SetLabelOffset(0.02)
  hline.GetXaxis().SetTickSize(0.08)
  hline.GetYaxis().SetLabelSize(hline.GetYaxis().GetLabelSize()*2.5)
  hline.GetYaxis().SetLabelOffset(0.01)
  hline.GetYaxis().SetTitleSize(hline.GetYaxis().GetTitleSize()*3)
  hline.GetXaxis().SetTitleSize(hline.GetXaxis().GetTitleSize()*3.5)
  hline.GetXaxis().SetTitleOffset(1)
  hline.GetYaxis().SetTitleOffset(0.4)

  # Make Error band in the ratio panel
  err_band = bkg_data_file.Get("h_rel_error_band")
  herror = hdata.Clone("herror")
  x = array('d', [0.])
  y = array('d', [0.])
  
  for i in range(1, herror.GetNbinsX()+1):
    Error = 1
    err_band.GetPoint(2*i+1, x, y)
    Error = abs(Error - y[0])
    herror.SetBinContent(i, 1)    
    herror.SetBinError(i, Error)    
    #if (var=="jets_n"): print "{}  Npoint:{}  x:{}  y:{}".format(i, err_band.GetN(),x[0],y[0])
    if (var=="jets_n"): print "Bin:{}  Y:{}  EY:{}".format(i,1,Error)
  herror.SetMarkerSize(0)
  herror.SetFillStyle(3354)
  herror.SetFillColorAlpha(1, 0.4)
  

  hline.Draw("hist")
  grratio.Draw("same Pz")
  herror.Draw("same E2")

  pad2.RedrawAxis("g")
  pad2.Update()  
  
  #raw_input("stop")
  if var == "bjets_n" or var == "jets_n":
    raw_input("stop")
    #sys.exit()
  c1.SaveAs(var+"_presel0L.pdf")

    
def plotter_1L(var, bkgs_name, xlable, leg_1L, bkg_data_file_wRW, bkg_data_file_noRW, Signal_file):
  
  # Initialize all the histograms for RW files
  hdata_tmp_wRW = bkg_data_file_wRW.Get("h_obsData")
  hbkg_list_wRW = []
  for bkg in bkgs_name: 
    hbkg_wRW = bkg_data_file_wRW.Get(bkg)
    hbkg_wRW.SetFillColor(getSampleColor(bkg))
    hbkg_list_wRW.append(hbkg_wRW)
      
  stack = ROOT.THStack("stack","stack")
  for hist in hbkg_list_wRW: stack.Add(hist)

  i = 0
  htot_list_wRW = []
  for hist in hbkg_list_wRW:
    if i == 0:
      htot_wRW = hbkg_list_wRW[0].Clone()
    else:     
      htot_wRW.Add(hist)
    i+=1  
    htot_list_wRW.append(hist)

  htot_wRW.SetLineColor(1)
  SM_tot = htot_wRW.Clone("SM_tot")
  SM_tot.SetFillStyle(3001)
  SM_error = htot_wRW.Clone("SM_error")
  SM_tot.SetLineWidth(3)
  ROOT.gStyle.SetHatchesSpacing(0.8)
  SM_error.SetFillStyle(3354)
  SM_error.SetFillColorAlpha(1, 0.4)
  
  for sig_name in Signal_file.GetListOfKeys():
    if "Gtt_1900_5000_1_nominal_"+var in sig_name.GetName(): 
       #print sig_name.GetName()
       hGtt = Signal_file.Get(sig_name.GetName())
       overflow = hGtt.GetBinContent(hGtt.GetNbinsX()+1);
       value = overflow + hGtt.GetBinContent(hGtt.GetNbinsX())
       hGtt.SetBinContent(hGtt.GetNbinsX(), value)       
       hGtt.SetLineColor(51)
       hGtt.SetLineStyle(9)
       hGtt.SetLineWidth(3)
    if "Gtt_1800_5000_1200_nominal_"+var in sig_name.GetName():
       #print sig_name.GetName()
       hGbb = Signal_file.Get(sig_name.GetName())
       overflow = hGbb.GetBinContent(hGbb.GetNbinsX()+1);
       value = overflow + hGbb.GetBinContent(hGbb.GetNbinsX())
       hGbb.SetBinContent(hGbb.GetNbinsX(), value)
       hGbb.SetLineColor(ROOT.kMagenta)
       hGbb.SetLineStyle(2)
       hGbb.SetLineWidth(3)

  hdata = hbkg_list_wRW[0].Clone("data")
  grdata = ROOT.TGraphErrors()
  grdata.SetMarkerStyle(20)
  
  for i in range(0,hdata_tmp_wRW.GetN()):
    x=hdata_tmp_wRW.GetX()[i]
    y=hdata_tmp_wRW.GetY()[i]
    #Ex=hdata_RF.GetErrorX(i)
    Ey=hdata_tmp_wRW.GetErrorY(i)
    hdata.SetBinContent(i+1,y)
    hdata.SetBinError(i+1, Ey)  
    grdata.SetPoint(i+1, x, y)
    grdata.SetPointError(i+1, 0, Ey)

  c1 = ROOT.TCanvas("c1", "Test plotter", 600, 600)
  c1.SetLogy()
  c1.SetLeftMargin(0.15)
  pad1 = ROOT.TPad("pad1", "pad1", 0, 0.29, 1, 1.0)
  pad1.SetBottomMargin(0)  # joins upper and lower plot
  pad1.SetLogy()
  pad1.SetTicky()
  pad1.SetTickx()
  pad1.Draw()
  # Lower ratio plot is pad2
  c1.cd()  # returns to main canvas before defining pad2
  pad2 = ROOT.TPad("pad2", "pad2", 0, 0, 1, 0.27)
  pad2.SetTopMargin(0)  # joins upper and lower plot
  pad2.SetBottomMargin(0.3)
  pad2.SetTicky()
  pad2.SetTickx()
  pad2.SetFillColor(0)
  pad2.Draw()

  pad1.cd()
  hdata.SetMarkerStyle(20)
  hdata.SetMarkerColor(1)
  SM_tot.GetYaxis().SetTitle("Events")
  histo_max=hdata.GetMaximum()
  SM_tot.SetMaximum(400*histo_max)
  SM_tot.SetMinimum(0.2)
  if var == "jets_n":
    SM_tot.GetXaxis().SetNdivisions(8)
  if var == "bjets_n":
    SM_tot.GetXaxis().SetNdivisions(4)

  #ROOT.gStyle.SetErrorX(0.);
  SM_tot.Draw("hist")
  stack.Draw("hist same")
  hGtt.Draw("hist same")
  hGbb.Draw("hist same")
  SM_error.Draw("same E2")
  grdata.Draw("same PZ")
 
  leg=ROOT.TLegend(0.61,0.5,0.86,0.85)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)  
  leg.AddEntry(grdata, "Data", "p")
  leg.AddEntry(SM_error, "Total background", "lf")
  for index, h in enumerate(reversed(htot_list_wRW)):
    leg.AddEntry(h, leg_1L[index], "f")
  leg.Draw()

  leg_sig=ROOT.TLegend(0.15,0.6,0.5,0.7)
  leg_sig.SetFillStyle(0)
  leg_sig.SetLineColor(0)  
  leg_sig.AddEntry(hGtt, "Gtt: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 1900, 1 (x50)", "l")
  leg_sig.AddEntry(hGbb, "Gtt: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 1800, 1200 (x50)", "l")
  leg_sig.Draw()

  write=["#bf{#it{ATLAS}}    Internal","#sqrt{s} = 13 TeV, 139 fb^{-1}","0L Preselection "]
  text =  ROOT.TLatex()
  text.SetNDC()
  text.SetTextAlign( 11 )
  text.SetTextFont( 42 )
  text.SetTextSize( 0.04 )
  text.SetTextColor( 1 )
  y = 0.83
  for t in write:
     #if "79.9" in t or '36' in t or '43.8' in t:
        #y = y-0.08
     #else:
     text.DrawLatex(0.15,y, t)
     y = y-0.055

  ROOT.gPad.Modified()
  ROOT.gPad.Update()
  pad1.RedrawAxis()
  pad1.Update()

  #raw_input("stop")
  #sys.exit()
   
  pad2.cd()

  # Initialize all the histograms for noRW files
  hdata_tmp_noRW = bkg_data_file_noRW.Get("h_obsData")
  hbkg_list_noRW = []
  for bkg in bkgs_name:
    hbkg_noRW = bkg_data_file_noRW.Get(bkg)
    hbkg_noRW.SetFillColor(getSampleColor(bkg))
    hbkg_list_noRW.append(hbkg_noRW)

  i = 0
  for hist in hbkg_list_noRW:
    if i == 0:
      htot_noRW = hbkg_list_noRW[0].Clone()
    else:
      htot_noRW.Add(hist)
    i+=1

  hdata_noRW = hbkg_list_noRW[0].Clone("data")

  for i in range(0,hdata_tmp_noRW.GetN()):
    x=hdata_tmp_noRW.GetX()[i]
    y=hdata_tmp_noRW.GetY()[i]
    #Ey=hdata_tmp_wRW.GetErrorY(i)
    hdata_noRW.SetBinContent(i+1,y)
    hdata_noRW.SetBinError(i+1, Ey)

  hratio = hdata.Clone("hratio")  
  hratio.Divide(htot_wRW)
  grratio = ROOT.TGraphErrors()
  grratio.SetMarkerStyle(20)
  for i in range(0,hratio.GetNbinsX()):
    Ygr=hratio.GetBinContent(i+1)
    errYgr=hratio.GetBinError(i+1)
    Xgr=hratio.GetXaxis().GetBinCenter(i+1)    
    grratio.SetPoint(i+1, Xgr, Ygr)
    grratio.SetPointError(i+1, 0, errYgr)

  nbin = hratio.GetNbinsX()
  low_bin = hratio.GetXaxis().GetBinLowEdge(1)
  high_bin = hratio.GetXaxis().GetBinUpEdge(nbin)

  hratio_noRW = hdata_noRW.Clone("hratio_noRW")
  hratio_noRW.Divide(htot_noRW)
  grratio_noRW = ROOT.TGraph()
  grratio_noRW.SetMarkerStyle(25)
  #grratio_noRW.SetLineWidth(5)
  #grratio_noRW.SetMarkerSize(5)
  grratio_noRW.SetMarkerColor(ROOT.kRed)  
  for i in range(0,hratio_noRW.GetNbinsX()):
    Ygr=hratio_noRW.GetBinContent(i+1)
    errYgr=hratio_noRW.GetBinError(i+1)
    Xgr=hratio_noRW.GetXaxis().GetBinCenter(i+1)
    grratio_noRW.SetPoint(i+1, Xgr, Ygr)
    #grratio_noRW.SetPointError(i+1, 0, errYgr)

  hratio = hdata.Clone("hratio")
  hratio.Divide(htot_wRW)
  grratio = ROOT.TGraphErrors()
  grratio.SetMarkerStyle(20)
  for i in range(0,hratio.GetNbinsX()):
    Ygr=hratio.GetBinContent(i+1)
    errYgr=hratio.GetBinError(i+1)
    Xgr=hratio.GetXaxis().GetBinCenter(i+1)
    grratio.SetPoint(i+1, Xgr, Ygr)
    grratio.SetPointError(i+1, 0, errYgr)

  nbin = hratio.GetNbinsX()
  low_bin = hratio.GetXaxis().GetBinLowEdge(1)
  high_bin = hratio.GetXaxis().GetBinUpEdge(nbin)
  hline=ROOT.TH1D("hline", "hline", 1, low_bin, high_bin)
  hline.SetLineColor(1)
  hline.SetBinContent(1,1)
  hline.SetLineStyle(2)
  hline.SetLineWidth(1)

  hline.SetMinimum(0.4)
  hline.SetMaximum(1.7)  
  hline.GetYaxis().SetNdivisions(3)
  if var == "jets_n":
    hline.GetXaxis().SetNdivisions(8)
  if var == "bjets_n":
    hline.GetXaxis().SetNdivisions(4)

  hline.GetYaxis().SetTitle("Data/SM")
  hline.GetXaxis().SetTitle(xlable)
  hline.GetYaxis().CenterTitle()

  hline.GetXaxis().SetLabelSize(hline.GetXaxis().GetLabelSize()*2.9)
  hline.GetXaxis().SetLabelOffset(0.02)
  hline.GetXaxis().SetTickSize(0.08)
  hline.GetYaxis().SetLabelSize(hline.GetYaxis().GetLabelSize()*2.5)
  hline.GetYaxis().SetLabelOffset(0.01)
  hline.GetYaxis().SetTitleSize(hline.GetYaxis().GetTitleSize()*3)
  hline.GetXaxis().SetTitleSize(hline.GetXaxis().GetTitleSize()*3.5)
  hline.GetXaxis().SetTitleOffset(1)
  hline.GetYaxis().SetTitleOffset(0.4)

  # Make Error band in the ratio panel
  err_band = bkg_data_file_wRW.Get("h_rel_error_band")
  herror = hdata.Clone("herror")
  x = array('d', [0.])
  y = array('d', [0.])
  
  for i in range(1, herror.GetNbinsX()+1):
    Error = 1
    err_band.GetPoint(2*i+1, x, y)
    Error = abs(Error - y[0])
    herror.SetBinContent(i, 1)    
    herror.SetBinError(i, Error)    
    #if (var=="jets_n"): print "{}  Npoint:{}  x:{}  y:{}".format(i, err_band.GetN(),x[0],y[0])
    if (var=="jets_n"): print "Bin:{}  Y:{}  EY:{}".format(i,1,Error)
  herror.SetMarkerSize(0)
  herror.SetFillStyle(3354)
  herror.SetFillColorAlpha(1, 0.4)

  leg_RW=ROOT.TLegend(0.15,0.75,0.5,0.94)
  leg_RW.SetFillStyle(0)
  leg_RW.SetLineColor(0)
  leg_RW.AddEntry(grratio,"With reweighting", "p")
  leg_RW.AddEntry(grratio_noRW,"Without reweighting", "p")

  hline.Draw("hist")
  grratio.Draw("same PZ")
  grratio_noRW.Draw("same P")
  herror.Draw("same E2")
  leg_RW.Draw()

  pad2.RedrawAxis("g")
  pad2.Update()  
 
  #raw_input("stop")
  #sys.exit() 
  #raw_input("stop")
  #if var == "bjets_n" or var == "jets_n":
    #raw_input("stop")
    #sys.exit()
  c1.SaveAs(var+"_presel1L.pdf")  

def plotter_SR(region, var, bkgs_name, xlable_SR, leg_SR, bkg_data_file, Signal_file):
  
  # Initialize all the histograms  
  hdata_tmp = bkg_data_file.Get("h_obsData")
  hbkg_list = []
  for bkg in bkgs_name: 
    hbkg = bkg_data_file.Get(bkg)
    hbkg.SetFillColor(getSampleColor(bkg))
    hbkg_list.append(bkg_data_file.Get(bkg))
      
  stack = ROOT.THStack("stack","stack")
  for hist in hbkg_list: stack.Add(hist)
  #raw_input("stop")

  i = 0
  htot_list = []
  for hist in hbkg_list:
    if i == 0:
      htot = hbkg_list[0].Clone()
    else:     
      htot.Add(hist)
    i+=1  
    htot_list.append(hist)

  htot.SetLineColor(1)
  #SM_tot = htot.Clone("SM_tot")
  SM_tot = bkg_data_file.Get("SM_total")
  SM_tot.SetFillStyle(3001)
  #SM_error = htot.Clone("SM_error")
  SM_error = bkg_data_file.Get("SM_total")
  SM_tot.SetLineWidth(3)
  ROOT.gStyle.SetHatchesSpacing(0.8)
  SM_error.SetFillStyle(3354)
  SM_error.SetFillColorAlpha(1, 0.4)
  
  for sig_name in Signal_file.GetListOfKeys():
    
    if "Gbb_2000_5000_1_nominal_"+var[0] in sig_name.GetName(): 
       #print sig_name.GetName()
       hGbb_B = Signal_file.Get(sig_name.GetName())
       overflow = hGbb_B.GetBinContent(hGbb_B.GetNbinsX()+1);
       value = overflow + hGbb_B.GetBinContent(hGbb_B.GetNbinsX())
       hGbb_B.SetBinContent(hGbb_B.GetNbinsX(), value)       
       hGbb_B.SetLineColor(51)
       hGbb_B.SetLineStyle(9)
       hGbb_B.SetLineWidth(3)
    if "Gbb_2000_5000_1000_nominal_"+var[0] in sig_name.GetName():
       #print sig_name.GetName()
       hGbb_M = Signal_file.Get(sig_name.GetName())
       overflow = hGbb_M.GetBinContent(hGbb_M.GetNbinsX()+1);
       value = overflow + hGbb_M.GetBinContent(hGbb_M.GetNbinsX())
       hGbb_M.SetBinContent(hGbb_M.GetNbinsX(), value)
       hGbb_M.SetLineColor(ROOT.kMagenta)
       hGbb_M.SetLineStyle(2)
       hGbb_M.SetLineWidth(3)
    if "Gbb_2000_5000_1800_nominal_"+var[0] in sig_name.GetName():
       #print sig_name.GetName()
       hGbb_C = Signal_file.Get(sig_name.GetName())
       overflow = hGbb_C.GetBinContent(hGbb_C.GetNbinsX()+1);
       value = overflow + hGbb_C.GetBinContent(hGbb_C.GetNbinsX())
       hGbb_C.SetBinContent(hGbb_B.GetNbinsX(), value)
       hGbb_C.SetLineColor(51)
       hGbb_C.SetLineStyle(9)
       hGbb_C.SetLineWidth(3)     

  
  hdata = hbkg_list[0].Clone("data")
  grdata = ROOT.TGraphErrors()
  grdata.SetMarkerStyle(20)
  
  for i in range(0,hdata_tmp.GetN()):
    x=hdata_tmp.GetX()[i]
    y=hdata_tmp.GetY()[i]
    if y < 0.000000000000000000001: continue
    #Ex=hdata_RF.GetErrorX(i)
    Ey=hdata_tmp.GetErrorY(i)
    hdata.SetBinContent(i+1,y)
    hdata.SetBinError(i+1, Ey)  
    grdata.SetPoint(i+1, x, y)
    grdata.SetPointError(i+1, 0, Ey)

  c1 = ROOT.TCanvas("c1", "Test plotter", 700, 600)
  c1.SetLogy()
  c1.SetLeftMargin(0.15)
  pad1 = ROOT.TPad("pad1", "pad1", 0, 0.0, 1, 1.0)
  #pad1.SetBottomMargin(0) 
  pad1.SetTicky()
  pad1.SetTickx()
  pad1.Draw()
 
  pad1.cd()
  hdata.SetMarkerStyle(20)
  hdata.SetMarkerColor(1)
  SM_tot.GetYaxis().SetTitle("Events")
  #SM_tot.GetYaxis().SetTitleSize(0.1)
  histo_max=hdata.GetMaximum()
  #SM_tot.SetMaximum(2*histo_max)
  SM_tot.GetXaxis().SetTitle(xlable_SR[0])
  if "Gbb_B" in region:
    SM_tot.SetMaximum(8)
  if "Gbb_M" in region:
    SM_tot.SetMaximum(12)
  if "Gbb_C" in region:
    SM_tot.SetMaximum(15)
  #SM_tot.SetMinimum(0.2)
  #if var[0] == "jets_n":
  #  SM_tot.GetXaxis().SetNdivisions(8)
  #if var[0] == "bjets_n":
  #  SM_tot.GetXaxis().SetNdivisions(4)

  SM_tot.Draw("hist")
  stack.Draw("hist same")
  #hGbb_C.Draw("hist same")
  hGbb_M.Draw("hist same")
  hGbb_B.Draw("hist same")
  SM_error.Draw("same E2")
  #hdata.Draw("same E0")
  grdata.Draw("same PZ")

  leg=ROOT.TLegend(0.55,0.55,0.88,0.85)
  leg.SetFillStyle(0)
  leg.SetLineColor(0)  
  leg.AddEntry(grdata, "Data", "p")
  leg.AddEntry(SM_error, "Total background", "lf")
  for index, h in enumerate(reversed(htot_list)):
    leg.AddEntry(h, leg_0L[index], "f")
  leg.Draw()

  leg_sig=ROOT.TLegend(0.15,0.6,0.5,0.7)
  leg_sig.SetFillStyle(0)
  leg_sig.SetLineColor(0)  
  leg_sig.AddEntry(hGbb_B, "Gbb: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 2000, 1800", "l")
  leg_sig.AddEntry(hGbb_M, "Gbb: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 2000, 1000", "l")
  #leg_sig.AddEntry(hGbb_B, "Gbb: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 2000, 1", "l")
  #leg_sig.AddEntry(hGbb_C, "Gbb: m(#tilde{g}), m(#tilde{#chi}_{1}^{0}) = 2000, 1800", "l")
  leg_sig.Draw()

  write=["#bf{#it{ATLAS}}","#sqrt{s} = 13 TeV, 139 fb^{-1}", region]
  text =  ROOT.TLatex()
  text.SetNDC()
  text.SetTextAlign( 11 )
  text.SetTextFont( 42 )
  text.SetTextSize( 0.035 )
  text.SetTextColor( 1 )
  y = 0.83
  for t in write:
     #if "79.9" in t or '36' in t or '43.8' in t:
        #y = y-0.08
     #else:
     text.DrawLatex(0.15,y, t)
     y = y-0.055

  ROOT.gPad.Modified()
  ROOT.gPad.Update()
  pad1.RedrawAxis()
  pad1.Update()
   
  #raw_input("stop")
  #if var == "bjets_n" or var == "jets_n":
    #raw_input("stop")
    #sys.exit()

  raw_input("stop")
  c1.SaveAs(region+"_"+var[0]+".pdf")



if __name__ == "__main__":

  # Name of variables need to be plotted in 0L and 1L channels
  name_0L = ["jets_n", "bjets_n", "met", "meff_incl", "mTb_min", "MJSum_rc"]
  leg_0L = ["Multijet","diboson","Z+jets","W+jets","t#bar{t}+X","single top","t#bar{t}"]
  leg_0L.reverse()
  name_1L = ["jets_n", "bjets_n", "met", "meff_incl", "mT", "MJSum_rc"]
  leg_1L = ["diboson","Z+jets","W+jets","t#bar{t}+X","single top","t#bar{t}"] 
  leg_1L.reverse()

  name_SR = ["jets_n"]
  leg_SR = ["diboson","Z+jets","W+jets","t#bar{t}+X","single top","t#bar{t}"] 
  leg_SR.reverse()


  bkgs_name = ["diboson", "W_jets", "Z_jets", "topEW", "singletop", "ttbar"]
  xlable_0L = ["Number of jets", "Number of b-jets", "E_{T}^{miss} [GeV]", "m_{eff}^{incl} [GeV]", "m_{T,min}^{b-jets} [GeV]", "M_{J}^{sum} [GeV]"]
  xlable_1L = ["Number of jets", "Number of b-jets", "E_{T}^{miss} [GeV]", "m_{eff}^{incl} [GeV]", "m_{T} [GeV]", "M_{J}^{sum} [GeV]"]
  xlable_SR = ["Number of jets"]

  # Get all files for 0L: Bkg+Data, QCD, Signal
  '''
  QCD_file = ROOT.TFile("./bkg_data/QCD_hist.root")
  Signal_file = ROOT.TFile("./bkg_data/Sig_hist.root")
  bkg_data_list = []
  bkg_data_dir = "./bkg_data/bkg_files"
  for root, dirs, files in os.walk(bkg_data_dir):
    for filename in files:
        link = root+"/"+filename
        bkg_data_list.append(ROOT.TFile(link))
  #bkg_data_list[0].ls()
  
  # Plot all the variables
  for i,var in enumerate(name_0L):
    for f in bkg_data_list:
       if var in f.GetName(): bkg_data_file = f
    plotter_0L(var, bkgs_name, xlable_0L[i], leg_0L, bkg_data_file, QCD_file, Signal_file)
  '''
  '''
  # Get all files for 1L: Bkg (w and w/o RW)+Data, Signal
  Signal_file = ROOT.TFile("./1L_pres/preselection3b_Sig1L.root")  
  bkg_data_list_wRW = []
  bkg_data_list_noRW = []
  bkg_data_dir_wRW = "./1L_pres/wRW"
  bkg_data_dir_noRW = "./1L_pres/noRW"
  for root, dirs, files in os.walk(bkg_data_dir_wRW):
    for filename in files:
        link = root+"/"+filename
        bkg_data_list_wRW.append(ROOT.TFile(link))  
  for root, dirs, files in os.walk(bkg_data_dir_noRW):
    for filename in files:
        link = root+"/"+filename
        bkg_data_list_noRW.append(ROOT.TFile(link))

  for i,var in enumerate(name_1L):
    for fwRW in bkg_data_list_wRW:
       if var in fwRW.GetName(): bkg_data_file_wRW = fwRW
    for fnoRW in bkg_data_list_noRW:
       if var in fnoRW.GetName(): bkg_data_file_noRW = fnoRW
    print var
    plotter_1L(var, bkgs_name, xlable_1L[i], leg_1L, bkg_data_file_wRW, bkg_data_file_noRW, Signal_file)
  '''
  # Get all files for SR plots
  SR = ["SR_Gbb_B", "SR_Gbb_M", "SR_Gbb_C"]
  for region in SR:
    Signal_file = ROOT.TFile("./SR_hist/{}_Sig.root". format(region))
    bkg_data_file = ROOT.TFile("./SR_hist/{}_jets_n_afterFit.root". format(region))   
    #print bkg_data_file.ls()
    #print Signal_file.ls()
    plotter_SR(region, name_SR, bkgs_name, xlable_SR, leg_SR, bkg_data_file, Signal_file)






