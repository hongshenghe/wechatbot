#!/usr/bin/env python    
#encoding: utf-8  
import sys  
reload(sys)  
sys.setdefaultencoding('utf8')  #微信编码是utf-8,所以一次性初始化时重载
import datetime,time
import re,simplejson
from WXBizMsgCrypt import WXBizMsgCrypt
import xml.etree.cElementTree as ET

import web
web.config.debug = False
from utility import *
from config import *  # 参数配置文件

urls = (
    '/', 'index',
    '/wxservice/', 'wxService',
    '/sendMsg/targets=(.*)','sendMessage',
)


class index:
    def GET(self):
	return u'INVALID REQUEST'

class wxService:
    def GET(self):
	# 微信校验端口，确认回调模式时要求就绪
	flag_parameter=True
	form=web.input(msg_signature="none",timestamp="none",nonce="none",echostr="none",flag_parameter="True")
	sVerifyMsgSig=form.msg_signature
	sVerifyTimeStamp=form.timestamp
	sVerifyNonce=form.nonce
	sVerifyEchoStr=form.echostr
	
	if flag_parameter:
		wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
		ret,sEchoStr=wxcpt.VerifyURL(sVerifyMsgSig, sVerifyTimeStamp,sVerifyNonce,sVerifyEchoStr)
		if(ret!=0):
			 return "ERR: VerifyURL ret: " + str(ret)
		else:
			return sEchoStr
	else:
		return "ERR: Invalid parameter"
		

    def POST(self):
	form=web.input()
        sReqMsgSig=form.msg_signature
	sReqTimeStamp=form.timestamp
	sReqNonce=form.nonce
	sReqData=web.data()
	wxcpt=WXBizMsgCrypt(sToken,sEncodingAESKey,sCorpID)
	ret,sMsg=wxcpt.DecryptMsg( sReqData, sReqMsgSig, sReqTimeStamp, sReqNonce)
	if( ret!=0 ):
		return "ERR: DecryptMsg ret: " + str(ret)
	xml_tree = ET.fromstring(sMsg)

	fromUserName=xml_tree.find("ToUserName").text
	toUserName=xml_tree.find("FromUserName").text
	content=xml_tree.find("Content").text
	content=GetAnswer(content)
	#print type(content)
	#print content
	#print chardet.detect(content)
	msgType = xml_tree.find("MsgType").text
	agentID = xml_tree.find("AgentID").text
	msgId = xml_tree.find("MsgId").text
	createTime=str(int(time.time()))
	sRespData = """<xml><ToUserName><![CDATA[%s]]></ToUserName>
<FromUserName><![CDATA[%s]]></FromUserName>
<CreateTime>%s</CreateTime>
<MsgType><![CDATA[%s]]></MsgType>
<Content><![CDATA[%s]]></Content>
<MsgId>%s</MsgId>
<AgentID>%s</AgentID></xml>""" %(toUserName,fromUserName,createTime,msgType,content.encode('utf-8'),msgId,agentID)
	ret,sEncryptMsg=wxcpt.EncryptMsg(sRespData, sReqNonce, sReqTimeStamp)
	if( ret!=0 ):
		return 'Error'
		#print ret
		#return "ERR:EncryptMsg ret: " % str(ret)	
	
	return sEncryptMsg

def GetAnswer(msg):
	result='未知指令'
	result=GetCommands()
	now=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
	result='%s \n\n %s' %(result,now)
	command=msg.encode('utf-8')
	
	
	m=re.search('重启实例\s+(\d+)',command)
	if m:
		result='好的，正在重启实例: %s' %(m.groups()[0])
	
	m=re.search('你叫什么',command)
	if m:
		result='少年'
	
	m=re.search('谁是运维第一前端选手',command)
	if m:	
		result='王佳明'

	m=re.search('作者',command)
 	if m:
		result='hongsheng,哥在上海，有两个可爱的宝贝'
	
	return result
	
def GetCommands():
	cmds='''
使用帮助

1.查询实例列表 
2.查询应用实例应用 
3.查询应用主机 + 主机名
4.重启实例 + 实例编号
5.Dump实例 + 实例编号
6.发布
7.还没想好
8.紧急联系方式

	'''
	return cmds


class sendMessage:
	def GET(self):
		return 'INVALID REQUEST'

	def POST(self,targets):
		message=web.data()
		token=simplejson.loads(getAccessToken(sCorpID,appSecret))['access_token'] 
		result=senddata(token,message,targets)
		print result
		return result

if __name__ == "__main__":
    app = web.application(urls, globals())
    app.run()
