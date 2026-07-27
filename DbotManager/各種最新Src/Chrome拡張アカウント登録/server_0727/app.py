from __future__ import annotations
import json, logging, os
from contextlib import contextmanager
from typing import Any, Iterator
import pymysql
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
load_dotenv(); logging.basicConfig(level=os.getenv('LOG_LEVEL','INFO'),format='%(asctime)s %(levelname)s %(message)s'); logger=logging.getLogger('x-account-sync')
API_TOKEN=os.getenv('API_TOKEN',''); DB_HOST=os.getenv('DB_HOST','127.0.0.1'); DB_PORT=int(os.getenv('DB_PORT','3306')); DB_USER=os.getenv('DB_USER',''); DB_PASSWORD=os.getenv('DB_PASSWORD',''); DB_NAME=os.getenv('DB_NAME',''); DEFAULT_VPS_ID=int(os.getenv('DEFAULT_VPS_ID','2'))
class XAccountData(BaseModel):
    twitter_id:str=''; screen_name:str=Field(min_length=1,max_length=100); display_name:str=''; twitter_user_id:str=Field(min_length=1,max_length=45); auth_token:str=Field(min_length=1,max_length=100); ct0:str=Field(min_length=1); twid:str=''; cookies:dict[str,str]=Field(default_factory=dict); cookie_string:str=''; user_agent:str=''; sec_ch_ua:str=''; impersonate:str='chrome'; exported_at:str|None=None; source_url:str|None=None
class AccountRequest(BaseModel):
    username:str=Field(min_length=1,max_length=45); password:str=Field(min_length=1,max_length=45); account:XAccountData
app=FastAPI(title='X Account Sync API',version='2.0.0'); app.add_middleware(CORSMiddleware,allow_origins=['*'],allow_credentials=False,allow_methods=['GET','POST','OPTIONS'],allow_headers=['Authorization','Content-Type'])
def require_api_token(authorization:str|None=Header(default=None))->None:
    if not API_TOKEN: raise HTTPException(500,'サーバーのAPI_TOKENが未設定です。')
    if authorization!=f'Bearer {API_TOKEN}': raise HTTPException(401,'APIトークンが正しくありません。')
@contextmanager
def db_connection()->Iterator[pymysql.connections.Connection]:
    c=pymysql.connect(host=DB_HOST,port=DB_PORT,user=DB_USER,password=DB_PASSWORD,database=DB_NAME,charset='utf8mb4',cursorclass=pymysql.cursors.DictCursor,autocommit=False,connect_timeout=10,read_timeout=20,write_timeout=20)
    try: yield c
    finally: c.close()
def get_user(c,username,password):
    with c.cursor() as cur: cur.execute('SELECT id,username,enable FROM user_master WHERE username=%s AND password=%s LIMIT 1',(username,password)); u=cur.fetchone()
    if not u: raise HTTPException(401,'ユーザーIDまたはパスワードが正しくありません。')
    if int(u.get('enable') or 0)!=1: raise HTTPException(403,'このユーザーは無効です。')
    return u
def norm_name(v): return v.strip().lstrip('@')
def cookie_json(a): return json.dumps(a.cookies,ensure_ascii=False,separators=(',',':'))
@app.get('/health')
def health(): return {'status':'ok'}
@app.post('/api/account/add',dependencies=[Depends(require_api_token)])
def add_account(req:AccountRequest):
    a=req.account; name=norm_name(a.screen_name or a.twitter_id)
    try:
        with db_connection() as c:
            u=get_user(c,req.username,req.password); uid=u['id']
            with c.cursor() as cur:
                cur.execute('SELECT id FROM account_master WHERE user_id=%s AND twitter_user_id=%s LIMIT 1',(str(uid),a.twitter_user_id))
                if cur.fetchone(): raise HTTPException(409,'このXアカウントは既に登録されています。')
                cur.execute('SELECT id FROM account_master WHERE name=%s LIMIT 1',(name,))
                if cur.fetchone(): raise HTTPException(409,'同じXユーザー名のアカウントが既に登録されています。')
                cur.execute("""INSERT INTO account_master (vps_id,user_id,name,twitter_user_id,login_id,account_name,display_name,auth_token,cookies,user_agent,sec_ch_ua,inpersonate,ct0,regist_type,enable,is_cookie_expired) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,0)""",(DEFAULT_VPS_ID,str(uid),name,a.twitter_user_id,name,a.display_name or name,a.display_name,a.auth_token,cookie_json(a),a.user_agent[:200],a.sec_ch_ua[:100],a.impersonate[:45],a.ct0,'chrome_extension')); aid=cur.lastrowid
            c.commit(); logger.info('Account added account_id=%s user_id=%s twitter_user_id=%s',aid,uid,a.twitter_user_id); return {'status':'ok','action':'added','account_id':aid,'message':f'@{name} を追加しました。'}
    except HTTPException: raise
    except pymysql.err.IntegrityError as e: logger.exception('Integrity error'); raise HTTPException(409,f'重複データのため追加できませんでした。({e.args[0]})') from e
    except pymysql.MySQLError as e: logger.exception('DB error'); raise HTTPException(500,f'データベース処理に失敗しました。({e.args[0]})') from e
@app.post('/api/account/update',dependencies=[Depends(require_api_token)])
def update_account(req:AccountRequest):
    a=req.account; name=norm_name(a.screen_name or a.twitter_id)
    try:
        with db_connection() as c:
            u=get_user(c,req.username,req.password); uid=u['id']
            with c.cursor() as cur:
                cur.execute('SELECT id,name FROM account_master WHERE user_id=%s AND twitter_user_id=%s LIMIT 1',(str(uid),a.twitter_user_id)); target=cur.fetchone()
                if not target: raise HTTPException(404,'更新対象のXアカウントが見つかりません。先にアカウント追加を実行してください。')
                cur.execute('SELECT id FROM account_master WHERE name=%s AND id<>%s LIMIT 1',(name,target['id']))
                if cur.fetchone(): raise HTTPException(409,'変更後のXユーザー名が別アカウントで使用されています。')
                cur.execute("""UPDATE account_master SET name=%s,login_id=%s,account_name=%s,display_name=%s,auth_token=%s,cookies=%s,user_agent=%s,sec_ch_ua=%s,inpersonate=%s,ct0=%s,is_cookie_expired=0 WHERE id=%s AND user_id=%s""",(name,name,a.display_name or name,a.display_name,a.auth_token,cookie_json(a),a.user_agent[:200],a.sec_ch_ua[:100],a.impersonate[:45],a.ct0,target['id'],str(uid)))
                if cur.rowcount!=1: raise HTTPException(409,'アカウントを更新できませんでした。')
            c.commit(); logger.info('Account updated account_id=%s user_id=%s twitter_user_id=%s',target['id'],uid,a.twitter_user_id); return {'status':'ok','action':'updated','account_id':target['id'],'message':f'@{name} を更新しました。'}
    except HTTPException: raise
    except pymysql.err.IntegrityError as e: logger.exception('Integrity error'); raise HTTPException(409,f'重複データのため更新できませんでした。({e.args[0]})') from e
    except pymysql.MySQLError as e: logger.exception('DB error'); raise HTTPException(500,f'データベース処理に失敗しました。({e.args[0]})') from e
