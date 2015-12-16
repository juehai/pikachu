#!/bin/bash
token='PZUa3XneLZuQ5kH5N7GDnKO9D8I413NOcpeW9w0DCm4gy_nI0h0DgYUpr2PbvsQ8llXa1ZkNjxpAD9ZvQIC1E1NjHcANXlHF3KUZqiYQngkARDiAIAMDP'
API='https://api.weixin.qq.com/cgi-bin/get_current_selfmenu_info?access_token=ACCESS_TOKEN'

URL=$(echo $API | sed -e "s/ACCESS_TOKEN/$token/")

curl -s $URL

API='https://api.weixin.qq.com/cgi-bin/menu/create?access_token=ACCESS_TOKEN'
URL=$(echo $API | sed -e "s/ACCESS_TOKEN/$token/")
