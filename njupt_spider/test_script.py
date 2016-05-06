# -*- coding: utf-8 -*-
import pickle
from items import NjuptSpiderItem

DictReadFileName = 'DictReadFileName'
testdict = dict()
item = NjuptSpiderItem()
item['depart'] = '南京邮电大学保卫处治安动态'
item['timestamp'] = 4006
item['title'] = '治安通报——违反“禁摩”规定通报'
testdict['南京邮电大学保卫处治安动态'] = item
item2 = NjuptSpiderItem()
item2['depart'] = '南京邮电大学党委宣传部 信息中心通知通告' 
item2['timestamp'] = 1002
item2['title'] = '关于报送宣传思想工作创新成果的通知'
testdict['南京邮电大学党委宣传部 信息中心通知通告'] = item2
fp = open(DictReadFileName, 'wb')
pickle.dump(testdict, fp)
