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

    if self.request.get('Key') != "": # パラメタあり？
      Key = self.request.get('Key')   # パラメタ取得
    else:
      Key = ""  # 追加はキー無し
    cookieStr = 'Key=' + Key + ';'     # Cookie保存
    self.response.headers.add_header('Set-Cookie', cookieStr.encode('shift-jis'))

    if Key == "":
      DataRec = DatSeikyu()
      DataRec.Hizuke = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d')
    else:
      DataRec = DatSeikyu().GetRec(Key)

#    for DataRec in DataRecs:
#      if RecSeikyu == {}:
#        setattr(DataRec,"Suryo","")
#      else:
#        setattr(DataRec,"Suryo",RecSeikyu.Suryo)
#        setattr(DataRec,"Bikou",RecSeikyu.Bikou)

    template_values = { 'DataRec'  :DataRec,
                        'LblMsg'    : ""}

    path = os.path.join(os.path.dirname(__file__), 'haitsu110.html')
    self.response.out.write(template.render(path, template_values))

  def val(self,value):
    if value == "":
      RetVal = None
    else:
      RetVal = int(value)

    return RetVal
  
  def post(self):

    Key      = self.request.cookies.get('Key', '') # Cookieより
    Nengetu  = self.request.cookies.get('Nengetu', '')  # Cookieより

    if self.request.get('BtnEnd')  != '': # 決定ボタン
      
      if Key == "": # 新規追加
        Rec = DatSeikyu()
      else: # 更新
        Rec = DatSeikyu().GetRec(Key) 
      Rec.Hizuke     = datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d')
      Rec.Room       = self.val(self.request.get('Room'))
      Rec.KanaName   = self.request.get('KanaName')
      Rec.Name       = self.request.get('Name')
      Rec.Futan      = self.val(self.request.get('Futan'))
      Rec.Haitu2Kei  = self.val(self.request.get('Haitu2Kei'))
      Rec.Byouin     = self.val(self.request.get('Byouin'))
      Rec.Yakkyoku   = self.val(self.request.get('Yakkyoku'))
      if  self.request.get('Ryosyubi') == "":
        Rec.Ryosyubi   = None
      else:
        Rec.Ryosyubi   = datetime.datetime.strptime(self.request.get('Ryosyubi'), '%Y-%m-%d') 
      Rec.put()
        
      self.redirect("/haitsu100/?Nengetu=" + Nengetu )
      return

    for param in self.request.arguments(): 


      if "BtnSel" in param:  # 更新ボタン？
        Parm = "?BusyoCode=" + BusyoCD # Cookieより
        Parm += "&Code=" + param.replace("BtnSel","") # 押下ボタン名
        Parm += "&Hizuke=" + Hizuke.replace("/","-")  # 日付
        self.redirect("/item110/" + Parm) #
        return

    Rec["BusyoName"] = MstBusyo().GetRec(BusyoCD).Name
    Rec["Hizuke"] = DatHizuke().GetNext(datetime.datetime.now()).strftime('%Y/%m/%d') # 今日の日付

    LblMsg = ""
    template_values = { 'Rec'       :Rec,
                        'MstBuppin' :MstBuppin().GetAll(),
                        'LblMsg'   : LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'item100.html')
    self.response.out.write(template.render(path, template_values))
    return

app = webapp2.WSGIApplication([
    ('/haitsu110/', MainHandler)
], debug=True)
