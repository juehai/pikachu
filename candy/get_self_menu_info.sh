#!/bin/bash
token='195ZWfkVYnbDT-rxPhMMvZ8DrXmTsN2xzwFEQGzXkV5teP6o1IThHgZ2karVVPspQYJaLLaKKTen1_RNhY8zhXT_1K1rt4wkz8ni2PuW3XwPSVjAIAGJM'
API='https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=ACCESS_TOKEN'

URL=$(echo $API | sed -e "s/ACCESS_TOKEN/$token/")

curl -s $URL

API='https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN'
URL=$(echo $API | sed -e "s/ACCESS_TOKEN/$token/")
