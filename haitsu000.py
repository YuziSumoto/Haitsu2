#!/usr/bin/env python
# -*- coding: UTF-8 -*-
import webapp2

import os

from google.appengine.ext.webapp import template

from google.appengine.ext.webapp.util import login_required
from google.appengine.api import users

import datetime
from MstUser   import *   # 使用者マスタ

class MainHandler(webapp2.RequestHandler):

  @login_required

  def get(self):

    LblMsg = ""

    user = users.get_current_user() # ログオン確認
    if MstUser().ChkUser(user.email().lower()) == False:
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnLogout')  != '':
      self.redirect(users.create_logout_url(self.request.uri))
      return

    if self.request.get('BtnMENU000')  != '':
      self.redirect("/")
      return

# 入居者別個人別請求一覧
    if self.request.get('BtnHaitsu100')  != '': # (2016/04まで)
      self.redirect("/haitsu100/?Nengetu=" + self.request.get('CmbNengetu') )
      return

    PrintParam = "?Nengetu="
    if self.request.get('CmbNengetu') == "":
      Zengetu = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Zengetu -= datetime.timedelta(days=1) # 前月末日
      SelHizuke = Zengetu.strftime('%Y/%m') # 前月１日
      PrintParam += SelHizuke.replace("/","%2F")
    else:
      PrintParam += self.request.get('CmbNengetu').replace("/","%2F")

    template_values = {'PrintParam' : PrintParam,
                       'StrNengetu' : self.StrNengetuSet(),
                       'LblMsg': LblMsg}
    path = os.path.join(os.path.dirname(__file__), 'haitsu000.html')
    self.response.out.write(template.render(path, template_values))

  def StrNengetuSet(self):

    Hizuke = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日

    if self.request.get('CmbNengetu') == "":
      Zengetu = datetime.datetime.strptime(datetime.datetime.now().strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Zengetu -= datetime.timedelta(days=1) # 前月末日
#      SelHizuke = datetime.datetime.now().strftime('%Y/%m') # 当月１日
      SelHizuke = Zengetu.strftime('%Y/%m') # 当月１日
    else:
      SelHizuke = self.request.get('CmbNengetu')
    
    retStr = ""

    while  Hizuke > datetime.datetime.strptime('2014/01/01', '%Y/%m/%d'):
      retStr += "<option value='"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "'"
      if SelHizuke == Hizuke.strftime('%Y/%m'):  # 選択？
        retStr += " selected "
        Flg = False
      retStr += ">"
      retStr += Hizuke.strftime('%Y/%m')
      retStr += "</option>"
      Hizuke = datetime.datetime.strptime(Hizuke.strftime('%Y/%m') + "/01", '%Y/%m/%d') # 当月１日
      Hizuke -= datetime.timedelta(days=1) # 前月末日

    return retStr

app = webapp2.WSGIApplication([
    ('/haitsu000/', MainHandler),
    ('/', MainHandler)
], debug=True)
