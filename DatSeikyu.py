# -*- coding: UTF-8 -*-
from google.appengine.ext import db

import datetime # 日付モジュール

class DatSeikyu(db.Model):
  Hizuke            = db.DateTimeProperty(auto_now_add=False) # 日付
  Room              = db.IntegerProperty()                    # 部屋番号
  KanaName          = db.StringProperty(multiline=False)      # 利用者カナ名
  Name              = db.StringProperty(multiline=False)      # 利用者名
  Futan             = db.IntegerProperty()                    # 利用者負担額
  Haitu2Kei         = db.IntegerProperty()                    # ハイツⅡ計
  Byouin            = db.IntegerProperty()                    # ふたば病院額
  Yakkyoku          = db.IntegerProperty()                    # 薬局額
  Byouin2           = db.IntegerProperty()                    # 石井外科額
  Ryosyubi          = db.DateTimeProperty(auto_now_add=False) # 領収日

  def GetMonth(self,Nengetu): # 月データ取得

    Sql =  "SELECT * FROM DatSeikyu"
    Sql += " Where Hizuke = DATE('" + Nengetu.replace("/","-") + "-01')"
    Sql += "    Order By KanaName,Room DESC"
    Snap = db.GqlQuery(Sql)
    Rec  = Snap.fetch(Snap.count())
    return Rec

  def GetRec(self,Key): # 指定キーのデータ取得

    Sql =  "SELECT * FROM DatSeikyu"
    Sql +=  " Where __key__ = KEY('" + str(Key) + "')"
    Snap = db.GqlQuery(Sql)
    Rec = Snap.fetch(Snap.count())

    return Rec[0]

  def DelRec(self,Key): # 指定患者,指定日,指定Seq削除

    Sql =  "SELECT * FROM DatSeikyu"
    Sql +=  " Where __key__ = KEY('" + str(Key) + "')"
    Snap = db.GqlQuery(Sql)
    for Rec in Snap:
       Rec.delete()

    return

  def CopyRecs(self,Nengetu): # 指定患者,指定日,指定Seq削除

    if int(Nengetu[5:7]) == 1: # 1月?
      Zengetu = str(int(Nengetu[0:4])-1) # 全年
      Zengetu += "/12" # 12月
    else:
      Zengetu  = Nengetu[0:5] # 当年
      Zengetu += str(int(Nengetu[5:7])-1) # 前月

    Sql =  "SELECT * FROM DatSeikyu"
    Sql += " Where Hizuke = DATE('" + Zengetu.replace("/","-") + "-01')"
    Sql += "    Order By KanaName,Room DESC"

    Snap = db.GqlQuery(Sql)
    for Rec in Snap:
      AddRec = DatSeikyu() # 新規レコード
      AddRec.Hizuke    =  datetime.datetime.strptime(Nengetu + "/01", '%Y/%m/%d')
      AddRec.Room      =  Rec.Room       # 部屋番号
      AddRec.KanaName  =  Rec.KanaName   # 利用者カナ名
      AddRec.Name      =  Rec.Name       # 利用者名
      AddRec.Futan     =  Rec.Futan      # 利用者負担額
      AddRec.Haitu2Kei =  Rec.Haitu2Kei  # ハイツⅡ計
      AddRec.Byouin    =  Rec.Byouin     # 病院額
      AddRec.Yakkyoku  =  Rec.Yakkyoku   # 薬局額
      AddRec.Ryosyubi  =  Rec.Ryosyubi   # 領収日
      AddRec.Byouin2   =  Rec.Byouin2    # 石井外科額
      AddRec.put()

    return
