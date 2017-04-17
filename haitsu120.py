#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# 注文者ＥＸＣＥＬ出力
#

import webapp2

#import os
from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

import datetime
import time
from calendar import monthrange
import locale

import xlwt # EXCEL 出力ライブラリ
import StringIO
import copy

from MstUser   import *   # 使用者マスタ
from DatSeikyu  import *   # 請求データ

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return


    WorkBook =  self.ExcelSet(self.request.get('Nengetu'))

    self.response.headers['Content-Type'] = 'application/ms-excel'
    self.response.headers['Content-Transfer-Encoding'] = 'Binary'
    self.response.headers['Content-disposition'] = 'attachment; filename="Haitu120.xls"'
    WorkBook.save(self.response.out)

  def ExcelSet(self,Hizuke):

    WorkBook = xlwt.Workbook()  # 新規Excelブック

    Style = self.SetStyle("THIN","THIN","THIN","THIN",xlwt.Alignment.VERT_CENTER,xlwt.Alignment.HORZ_CENTER) 
    font = xlwt.Font() # Create the Font
    font.height = 230
    Style.font = font

    WorkSheet = WorkBook.add_sheet(u"請求一覧")  # シート追加
    self.SetPrintParam(WorkSheet) # 用紙サイズ等セット

    DataRec = DatSeikyu().GetMonth(Hizuke)
    Row = 0
    Col = 1
    for Rec in DataRec: # データループ
      self.SetColSize(WorkSheet,Col) # 行,列サイズセット
      self.SetTitle(WorkSheet,Row,Col,Hizuke,Rec.Name,Style)      # 固定部分セット
      self.SetData(WorkSheet,Rec,Row,Col,Style)      # データセット
      if Col == 1:
        Col = 5   # 右側
      else:
        Col = 1   # 左に戻す
        Row += 9  # 9行追加
        
    return  WorkBook
  
  def SetPrintParam(self,WorkSheet): # 用紙サイズ・余白設定
    WorkSheet.set_paper_size_code(9) # A4
    WorkSheet.set_portrait(1) # 縦
    WorkSheet.top_margin = 0.9 / 2.54    # 1インチは2.54cm
    WorkSheet.bottom_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.left_margin = 0.8 / 2.54    # 1インチは2.54cm
    WorkSheet.right_margin = 0.5 / 2.54    # 1インチは2.54cm
    WorkSheet.header_str = ''
    WorkSheet.footer_str = ''
#    WorkSheet.fit_num_pages = 1
    return

  def SetColSize(self,WorkSheet,Col):  # 行,列サイズセット

    ColWidth = ["列の幅",2,10,10,9,2]
    for i in range(1,len(ColWidth)):
      WorkSheet.col(Col + i - 2).width = int(ColWidth[i] * 400)

    return

  def SetTitle(self,WorkSheet,Row,Col,Hizuke,Name,Style):  # 固定部分セット

    StyleNoline = copy.deepcopy(Style)
    Border = xlwt.Borders()
    StyleNoline.borders = Border

    StyleNolineUnder = copy.deepcopy(Style)
    Border = xlwt.Borders()
    StyleNolineUnder.borders = Border
    StyleNolineUnder.font.underline = True

    WorkSheet.write(Row,Col,Hizuke[5:7] + u"月分",StyleNoline)
    WorkSheet.write_merge(Row,Row,Col + 1 ,Col + 2,u"　" + Name + u"　様",StyleNolineUnder)
    Row += 1
    OutStr =  u"ふたばハイツⅡ使用料\n"
    OutStr += u"【ふたばハイツⅡ・特定】"
    WorkSheet.write_merge(Row,Row+1,Col  ,Col + 1,OutStr,Style)
    Row += 2
    WorkSheet.write_merge(Row,Row,Col  ,Col + 1,u"ふたば病院受診代",Style)
    Row += 1
    WorkSheet.write_merge(Row,Row,Col  ,Col + 1,u"診断書・自立支援申請等",Style)
    Row += 1
    WorkSheet.write_merge(Row,Row,Col  ,Col + 1,u"アイセイ薬局",Style)
    Row += 1
    WorkSheet.write_merge(Row,Row,Col  ,Col + 1,u"　",Style)
    Row += 1
    WorkSheet.write_merge(Row,Row,Col  ,Col + 1,u"合計",Style)

    return

  def SetData(self,WorkSheet,Rec,Row,Col,Style):  # データ部分セット

    if Col == 1:
      for i in range(0,9):
        WorkSheet.row(Row + i).height_mismatch = 1
        WorkSheet.row(Row + i).height = 600

    Goukei = 0
    if Rec.Haitu2Kei != None:
      Goukei += Rec.Haitu2Kei
      OutStr = u"￥" + "{:,d}".format(int(Rec.Haitu2Kei))
    else:
      OutStr = ""
    WorkSheet.write_merge(Row+1,Row+2,Col+2  ,Col + 2,OutStr,Style)

    if Rec.Byouin != None:
      Goukei += Rec.Byouin
      OutStr = u"￥" + "{:,d}".format(int(Rec.Byouin))
    else:
      OutStr = ""
    WorkSheet.write(Row + 3,Col + 2,OutStr,Style)

    if Rec.Yakkyoku != None:
      Goukei += Rec.Yakkyoku
      OutStr = u"￥" + "{:,d}".format(int(Rec.Yakkyoku))
    else:
      OutStr = ""
    WorkSheet.write(Row + 4,Col + 2,OutStr,Style)
    WorkSheet.write(Row + 5,Col + 2,"",Style)
    WorkSheet.write(Row + 6,Col + 2,"",Style)
    WorkSheet.write(Row + 7,Col + 2,u"￥" + "{:,d}".format(int(Goukei)),Style)

    return

  def SetDataGoukei(self,WorkSheet,DataRecs,GoukeiOutCol,Style):  # データ部分セット

    OutStyle = copy.deepcopy(Style)
    OutStyle.pattern.pattern = xlwt.Pattern.SOLID_PATTERN
    OutStyle.pattern.pattern_fore_colour = xlwt.Style.colour_map['gray50']
    OutStyle.font.colour_index = xlwt.Style.colour_map['white']
    
    WorkSheet.write(3,GoukeiOutCol,u"合計",OutStyle)

    OutRow = 4
    for DataRec in DataRecs:
      WorkSheet.write(OutRow,GoukeiOutCol,getattr(DataRec,"Goukei",0),Style)
      OutRow += 1

    return

  def SetStyle(self,Top,Bottom,Right,Left,Vert,Horz):  # セルスタイルセット

    Style = xlwt.XFStyle()
    Border = xlwt.Borders()
    if Top == "THIN":
      Border.top     = xlwt.Borders.THIN
    elif Top == "DOTTED":
      Border.top     = xlwt.Borders.DOTTED

    if Bottom == "THIN":
      Border.bottom  = xlwt.Borders.THIN
    elif Bottom == "DOTTED":
      Border.bottom     = xlwt.Borders.DOTTED

    if   Left == "THIN":
      Border.left    = xlwt.Borders.THIN
    elif Left == "DOTTED":
      Border.left    = xlwt.Borders.DOTTED

    if   Right == "THIN":
      Border.right   = xlwt.Borders.THIN
    elif Right == "DOTTED":
      Border.right   = xlwt.Borders.DOTTED

    Style.borders = Border

    Alignment      = xlwt.Alignment()

    Alignment.wrap = 1 # これないとセル内改行が効かない

    if Vert != False:
      Alignment.vert = Vert

    if Horz != False:
      Alignment.horz = Horz

    Style.alignment = Alignment

    return Style

app = webapp2.WSGIApplication([
    ('/haitsu120/', MainHandler)
], debug=True)
