#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os

from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

import datetime
from MstUser   import *   # 使用者マスタ
from DatSeikyu  import *   # 請求データ

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    Rec = {} # 画面受け渡し用領域

    if self.request.get('Nengetu') != "": # パラメタあり？
      Nengetu = self.request.get('Nengetu')   # パラメタ取得
      cookieStr = 'Nengetu=' + Nengetu + ';'     # Cookie保存
      self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))
    else:
      Nengetu = self.request.cookies.get('Nengetu', '') # Cookieより

    DataRecs = DatSeikyu().GetMonth(Nengetu)
    for DataRec in DataRecs:
      setattr(DataRec,"Key",DataRec.key())
      if DataRec.Haitu2Kei != None:
        ZihiSeikyu = DataRec.Haitu2Kei
      else:
        ZihiSeikyu = 0
      if DataRec.Futan != None:
        ZihiSeikyu -= DataRec.Futan
      setattr(DataRec,"ZihiSeikyu",ZihiSeikyu)
      Goukei = DataRec.Haitu2Kei
      if DataRec.Byouin != None:
        Goukei += DataRec.Byouin
      if DataRec.Yakkyoku != None:
        Goukei += DataRec.Yakkyoku
      if DataRec.Byouin2 != None:
        Goukei += DataRec.Byouin2
      setattr(DataRec,"Goukei",Goukei)

    template_values = { 'Nengetu'   :Nengetu,
                        'DataRecs'  :DataRecs,
                        'LblMsg'    : ""}

    path = os.path.join(os.path.dirname(__file__), 'haitsu100.html')
    self.response.out.write(template.render(path, template_values))

  def post(self):

    LblMsg = ""

    Nengetu = self.request.cookies.get('Nengetu', '') # Cookieより

    if self.request.get('BtnAdd')  != '': # 新規追加ボタン
      self.redirect("/haitsu110/?Nengetu=" + Nengetu )
      return

    if self.request.get('BtnCopy')  != '': # 前月複写
      DatSeikyu().CopyRecs(Nengetu)
      LblMsg = "複写しました。"

    for param in self.request.arguments(): 
      if "BtnSel" in param:  # 更新ボタン？
        Parm = "?Key=" + param.replace("BtnSel","") # 押下ボタン名
        Parm += "&Nengetu=" + Nengetu  # 日付
        self.redirect("/haitsu110/" + Parm) #
        return
      if "BtnDel" in param:  # 削除ボタン？
        DatSeikyu().DelRec(param.replace("BtnDel","")) # レコード削除
        LblMsg = "削除しました。"

    DataRecs = DatSeikyu().GetMonth(Nengetu)
    for DataRec in DataRecs:
      setattr(DataRec,"Key",DataRec.key())

    template_values = { 'Nengetu'   :Nengetu,
                        'DataRecs'  :DataRecs,
                        'LblMsg'    :LblMsg}

    path = os.path.join(os.path.dirname(__file__), 'haitsu100.html')
    self.response.out.write(template.render(path, template_values))

app = webapp2.WSGIApplication([
    ('/haitsu100/', MainHandler)
], debug=True)
