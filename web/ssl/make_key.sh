#!/usr/bin/env sh

# 実行スクリプトのpath取得
SCRIPT_DIR=$(cd $(dirname $0); pwd)
cd $SCRIPT_DIR

# 鍵、証明書の自動生成
openssl req -batch -new -x509 -newkey rsa:4096 -nodes -sha256 \
  -subj /CN=example.com/O=example -days 3650 \
  -keyout ./server.key \
  -out ./server.crt
