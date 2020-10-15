# -*- coding: utf-8 -*-
# @Author: yongfanmao
# @Date:   2020-08-19 16:30:39
# @E-mail: maoyongfan@163.com
# @Last Modified by:   yongfanmao
# @Last Modified time: 2020-08-26 11:07:56

from robot.api import logger
from HelloBikeLibrary.request import Request
from HelloBikeLibrary.con_mysql import UseMysql
import json


"""
采集第三方信息
"""

class ThirdInfo(object):

	def get_container_ip(self,service_name,env="uat",tag="group1"):

		"""
			获取指定服务容器的对应IP地址,没有容器时,返回ecs ip地址
			env 不传默认为uat
			tag 不传默认为group1
			
			返回内容为:
				ip地址

			例:
			|$(ip) |get container ip | AppHellobikeOpenlockService | env="uat" | tag="group1"
		"""
		try:
			ttGetEcsIpUrl = "https://tt.hellobike.cn/v1/api/{}".format(service_name)
			if env == "fat":
				groupsUrl = "https://gaia.hellobike.cn/container-business-service/api/v1/apps/groups/appname/{}/env/6".format(service_name)
				containerUrl = "https://gaia.hellobike.cn/container-business-service/api/v1/apps/pods/appname/{service_name}/env/6/group/{tag}".format(
				service_name=service_name,tag=tag)
			else:
				groupsUrl = "https://gaia.hellobike.cn/container-business-service/api/v1/apps/groups/appname/{}/env/2".format(service_name)
				containerUrl = "https://gaia.hellobike.cn/container-business-service/api/v1/apps/pods/appname/{service_name}/env/2/group/{tag}".format(
				service_name=service_name,tag=tag)
			# print(groupsUrl)
			us = UseMysql()
			headerInfos = us.getTokenInfos()
			headers = {"token": headerInfos[0],"user-agent":headerInfos[1]}
			grRep = Request().request_client(url=groupsUrl,method='get',headers=headers)
			# print(grRep)
			if grRep[0] == 200:
				dataResult = grRep[1].get('data')
				if dataResult:
					groupList = dataResult.get('groupList',[])
					for group in groupList:
						if group == tag:
							break
					else:
						raise Exception("传入的tag信息不存在")
				else:

					data = {"page":1,
					"env":env.upper(),
					"action":"tt.application.info.resource",
					"page_size":20,
					"type":"ECS"}
					ttRep = Request().request_client(url=ttGetEcsIpUrl,method='post',data=data,headers=headers)
	
					if ttRep[0] == 200:
						# 没有容器时 ，返回ecs_ip
						ip = ttRep[1].get('data',[])[0].get('ip',{}).get('intranet','') 
						print(ip)
						return ip 


			# print(containerUrl)

			cnRep = Request().request_client(url=containerUrl,method='get',headers=headers)
			# print (cnRep)

			if cnRep[0] == 200:
				ip = cnRep[1].get('data').get('appPodList',[])[0].get("ipAddress")
				print(ip)
				return ip

			return False
		except Exception as e:
			raise Exception("请联系管理员")


	def exe_redis(self,name,command,env="uat",database=None):

		"""
			执行redis 命令
			env 不传默认为uat
			自动分区的redis可不传database 
			
			返回内容为:
				执行结果

			例:
			|$(result) |exe redis | bikeAlias | get bikeServiceIp:2100170725 | env="uat"
		"""
		try:
			getAllRedisNamesUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisConf/getAllRedisNames".format(env)
			getSelfRedisUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisQuery/getRedisList".format(env)
			addRedisTokenUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisQuery/addRedisTokenApplication".format(env)
			executeRedisUrl = "https://{}-basicconf-admin-server.hellobike.cn/redisQuery/execute".format(env)
			
			selfHaveRedis = False

			us = UseMysql()
			headerInfos = us.getTokenInfos()
			headers = {"token": headerInfos[0],"user-agent":headerInfos[1]}

			allRedisRep = Request().request_client(url=getAllRedisNamesUrl,method='get',headers=headers)

			if allRedisRep[0] == 200:
				redisList = allRedisRep[1].get('data',[])
				for redisName in redisList:
					if name == redisName:
						break
				else:
					return  False#("没有传入的redis信息,请联系管理员")


			getSelfRedisRep = Request().request_client(url=getSelfRedisUrl,method='get',headers=headers)

			if getSelfRedisRep[0] == 200:
				selfRedisList = getSelfRedisRep[1].get('data',[])
				for selfRedis in selfRedisList:
					if selfRedis.get("redisName","") == name:
						selfHaveRedis = True

			if not selfHaveRedis:

				data = {"redisNameList":[name],
						"expireTime":2160,
						"commandList":["set","setnx","setex","psetex","del","incr","decr","lpush","lpop","rpush","rpop","lrem","sadd","srem","zadd","zrem","hset","hmset","hdel","hkeys","incrby","incrbyfloat","geoadd","get","exists","lrange","lindex","sismember","scard","smembers","zrange","zrangebyscore","hget","hmget","hkeys","hgetall","georadius","ttl","pttl","pexpire","pexpireat","persist","expire","expireat","scriptexists","eval","evalsha","scriptload","sadd","scard","sdiff","sdiffstore","sinter","sinterstore","sismember","smembers","spop","srandmember","srem","sscan","sunion","sunionstore","append","decrby","decr","del","exists","getrange","get","getset","incrbyfloat","incrby","incr","mget","msetnx","mset","psetex","scanbatch","scan","setex","setnx","setrange","set","strlen","geoadd","geodist","geohash","geopos","georadiusbymember","georadius","publish","type","info","lindex","llen","lrange","brpoplpush","blpop","brpop","linsert","lpop","lpush","lpushx","lrem","lset","ltrim","rpoplpush","rpop","rpush","rpushx","hexists","hgetall","hget","hkeys","hlen","hmget","hvals","hdel","hincrbyfloat","hincrby","hmset","hsetnx","hset","hscan","zadd","zcard","zcount","zincrby","zinterstore","zlexcount","zrangebylex","zrangebyscore","zrangebyscorewithscores","zrange","zrank","zremrangebylex","zremrangebyrank","zremrangebyscore","zrem","zrevrangebylex","zrevrangebyscore","zrevrangebyscorewithscores","zrevrange","zrevrank","zscan","zscore","zunionstore","pfadd","pfcount","pfmerge"]
						}

				addRedisRep = Request().request_client(url=addRedisTokenUrl,method='patch',data=data,headers=headers)

				print(addRedisRep)

				if addRedisRep[0] == 200:
					if addRedisRep[1]['code'] == 0:
						pass
					else:
						return False # 添加redis权限失败

			if database:
				executData = {"database":database,"redisName":name,"command":command}
			else:
				executData = {"redisName":name,"command":command}

			executRep = Request().request_client(url=executeRedisUrl,method='post',data=executData,headers=headers)

			print(executRep)

			if executRep[0] == 200:
				return executRep[1]

			return False
		except Exception as e:
			raise Exception("请联系管理员")



if __name__ == '__main__':
	td = ThirdInfo()
	print(td.get_container_ip("AppHellobikeOpenlockService",env="uat"))
	print(td.get_container_ip("AppHellobikeRideApiService",env="uat"))
	# print(td.get_container_ip("AppHellobikeBikeStateService",env="uat")) #没有容器的服务
	# print(td.exe_redis("bikeAlias","get bikeServiceIp:2100170725",env="fat"))




