SELECT id,username,enable FROM user_master WHERE username='接続設定のユーザーID';
SELECT id,user_id,name,twitter_user_id,display_name,auth_token,user_agent,sec_ch_ua,inpersonate,is_cookie_expired FROM account_master ORDER BY id DESC LIMIT 20;
