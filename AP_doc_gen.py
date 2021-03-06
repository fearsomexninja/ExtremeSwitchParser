import exsh
import re
import datetime

OUIList =['00:0[bB]:86','00:1[aA]:1[eE]','00:24:6[cC]','04:[bB][dD]:88','18:64:72','20:4[cC]:03','24:[dD][eE]:[cC]6','40:[eE]3:[dD]6','6[cC]:[fF]3:7[fF]','70:3[aA]:0[eE]','84:[dD]4:7[eE]','94:[bB]4:0[fF]','9[cC]:1[cC]:12','[aA][cC]:[aA]3:1[eE]','[bB]4:5[dD]:50','[dD]8:[cC]7:[cC]8','[fF]0:5[cC]:19']
date = datetime.datetime.now()

filename = "/usr/local/cfg/{0}-{1}-{2}_AP_doc_gen.csv".format(date.year, date.month,date.day)
f = open(filename,'w')
f.write('port,MAC,Vlan,Vlan Tag,port description,switch\n')

showswitch = exsh.clicmd("sho switch",True)
SysName=re.search(r'SysName:\s*(.*)',showswitch)
switchName = SysName.group(1)

showvlan = exsh.clicmd("sho fdb", True)
mac_entry=re.findall(r'\b((?:[0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})\s*\S*\(.* (\d{1,2})',showvlan)

for item in mac_entry:
#	powercommand = 'show inline-power info ports '+item[1]
#	showpower = exsh.clicmd(powercommand,True)
#	inline_entry= re.search(r'delivering',showpower)
#	if inline_entry:
	i=0
	while i<len(OUIList):
		ouistring = OUIList[i]+':(?:[0-9a-fA-F]{2}:){2}[0-9a-fA-F]{2}'
		ouicheck = re.search(ouistring,item[0], re.IGNORECASE)
		if ouicheck:
			print "port "+item[1]+" is a WAP"
			
			info_detail_command= "show port "+item[1]+" info detail"
			info_detail_string=exsh.clicmd(info_detail_command,True)
			info_detail_match= re.search('Name: (.*), Internal Tag = (\d*),',info_detail_string)
			port_desc_string=re.search(r'Port:\s*\d*\((.*)\)',info_detail_string)
			lock_learning_command = "conf port "+item[1]+" vlan "+info_detail_match.group(1)+" lock-learning"
			print lock_learning_command
			if port_desc_string:
				f.write(item[1]+','+item[0]+','+info_detail_match.group(1)+','+info_detail_match.group(2)+','+port_desc_string.group(1)+','+switchName+'\n')
			else:
				f.write(item[1]+','+item[0]+','+info_detail_match.group(1)+','+info_detail_match.group(2)+','+'No Port Description'+','+switchName+'\n')
			#lock_learning_string = exsh.clicmd(lock_learning_command, True)
			break
		i += 1
	if i==len(OUIList):
#			print "port "+ item[1]+" is not a WAP but is delivering power"
			#f.write("port "+ item[1]+" is not a WAP but is delivering power\n")
#	else:
		print "port "+ item[1]+" is not a WAP"
		#f.write("port "+ item[1]+" is not a WAP\n")
f.close()
#exsh.clicmd("tftp put 172.16.1.8 vr vr-def "+filename,False) 
#exsh.clicmd("rm "+filename,False)