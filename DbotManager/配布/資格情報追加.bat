@echo off
:: 資格情報を使ってネットワークドライブを割り当て
net use \\203.137.102.211\upload /user:winserverroot Hashidai00! /persistent:yes

:: 例
:: net use \\192.168.1.100\Shared /user:winserverroot Hashidai00! /persistent:yes

echo 資格情報が追加されました。
pause