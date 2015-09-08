#coding:utf-8

from config import *
from utility import *  
import simplejson 
import requests
import httplib2

def getAccessToken(corpid,corpsecret):
    http = httplib2.Http(".cache")
    url="https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=%s&corpsecret=%s" %(corpid,corpsecret)
    resp, content = http.request(url, "GET")
    return content


def senddata(access_token,send_content,to_user='hongshenghe'):
    url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + access_token
    send_values = {
        "touser":'%s' % to_user,
        "msgtype":"text",
        "agentid":"6",
        "text":{
            "content":send_content
            },
        "safe":"0"
        }
    data = simplejson.dumps(send_values,ensure_ascii=False)
    ret= requests.post(url, data=data)
    result=ret.json() 
    return result
