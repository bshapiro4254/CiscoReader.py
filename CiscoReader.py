#!/usr/bin/python
### Cisco config reader Copyright 2018 Benjamin Shapiro
from threading import Thread
import paramiko
import sys
import paramiko
import threading
import re
import time
import string
import datetime
import csv
import re
import os

#	###############################################################################################
#	############ Main Script to execute device collection loop.                           #########
#	###############################################################################################


def main():
	if len(sys.argv) > 1:
		dev_list = read_list(sys.argv[1])
		print dev_list
		for device_num, dev_data in dev_list.items():
			print dev_data

			Data_Collect(dev_data)

			time.sleep(15)

#	###############################################################################################
#	############ Read device data CSV function for reading csv list of target devices     #########
#	###############################################################################################

def read_list(dd_file):
		P_Var = 'Reading device cfg file...' ; print P_Var
		cwd = os.getcwd()

		if os.path.isfile(dd_file):
			with open(dd_file) as device_data_file:
				device_reader = csv.reader(device_data_file)
				deviceData = list(device_reader)
				print deviceData
		else:
			P_Var = 'You did not supply a device list. Please check your device file. \n {0}'.format(dd_file)
			print P_Var
		csv_mcount2 = len(deviceData)
		print(csv_mcount2)
		csv_step2 = 0
		device_list_dict = dict()

		while csv_step2 < csv_mcount2:
			hostname = deviceData[csv_step2][0]
			MGMT_IP = deviceData[csv_step2][1]
			Username = deviceData[csv_step2][2]
			Password = deviceData[csv_step2][3]
			device_list_dict.update({csv_step2 : {"hostname": hostname , "IP": MGMT_IP, "Username":  Username, "Password": Password, "port" : 22 }})
			csv_step2 = csv_step2 + 1

		print(device_list_dict)
		return device_list_dict

#	###############################################################################################
#	############ Main data collection logic function.                                     #########
#	###############################################################################################

def Data_Collect(dev_data):
	My_SSH_Dev = dev_data
	My_SSH_Session = BKGD_SSH()
	My_SSH_Session.load_dev(My_SSH_Dev)
	My_SSH_Session.enter_enable()
	time.sleep(1)
	My_SSH_Session.send_cmd('show hostname')
	time.sleep(1)
	hostname = My_SSH_Session.return_output()
	time.sleep(1)
	My_SSH_Session.send_cmd('show run')
	time.sleep(1)
	Write_Raw_Results(My_SSH_Session.return_output(),"show_run",hostname)
	Write_CSV_Results(process_show_run(hostname,Read_Raw_Results("show_run",hostname)),"show_run",hostname)
	time.sleep(1)
	My_SSH_Session.send_cmd('show vlan')
	time.sleep(1)
	Write_Raw_Results(My_SSH_Session.return_output(),"show_vlan",hostname)
	Write_CSV_Results(process_show_run(hostname,Read_Raw_Results("show_vlan",hostname)),"show_vlan",hostname)
	time.sleep(1)
	My_SSH_Session.send_cmd('show ip interface brief')
	time.sleep(1)
	Write_Raw_Results(My_SSH_Session.return_output(),"show_ip_int_br",hostname)
	Write_CSV_Results(process_show_run(hostname,Read_Raw_Results("show_ip_int_br",hostname)),"show_ip_int_br",hostname)
	time.sleep(1)
	My_SSH_Session.send_cmd('show run interface')
	time.sleep(1)
	Write_Raw_Results(My_SSH_Session.return_output(),"show_run_int",hostname)
	Write_CSV_Results(process_show_run(hostname,Read_Raw_Results("show_run_int",hostname)),"show_run_int",hostname)
	time.sleep(1)
	My_SSH_Session.send_cmd('show interface trunk')
	time.sleep(1)
	Write_Raw_Results(My_SSH_Session.return_output(),"show_int_trunk",hostname)
	Write_CSV_Results(process_show_run(hostname,Read_Raw_Results("show_int_trunk",hostname)),"show_int_trunk",hostname)

#	###############################################################################################
#	############ Write raw console data to file function for writing command results      #########
#	###############################################################################################

def Write_Raw_Results(raw_data,data_type,hostname):
		cwd = os.getcwd()
		raw_file = '{0}/{3}-{1}-{2}'.format(cwd,data_type,Get_Date(),hostname)
		if os.path.isfile(raw_file):
			fh = open(raw_file, 'a')
		else:
			fh = open(raw_file, 'w')
		raw_output = '{0}'.format(raw_data)
		fh.write(raw_output)
		fh.close()

#	###############################################################################################
#	############ Write raw console data to file function for writing command results      #########
#	###############################################################################################

def Write_CSV_Results(CSV_data,data_type,hostname):
		cwd = os.getcwd()
		csv_file = '{0}/{3}-{1}-{2}.csv'.format(cwd,data_type,Get_Date(),hostname)
		if os.path.isfile(raw_file):
			fh = open(raw_file, 'a')
		else:
			fh = open(raw_file, 'w')
		CSV_data = '{0}'.format(CSV_data)
		fh.write(CSV_data)
		fh.close()

#	######################################################################################################
#	############ Read raw console data to memory function for processing console command results #########
#	######################################################################################################

def Read_Raw_Results(data_type,hostname):
		cwd = os.getcwd()
		raw_file = '{0}/{3}-{1}-{2}'.format(cwd,data_type,Get_Date(),hostname)
		if os.path.isfile(raw_file):
			fh = open(raw_file, 'r')
			raw_data = fh.read()
		return pre_process_raw_data(raw_data)

#	#######################################################################################################
#	### preprocess console data function for pre processing console command results and clean data ########
#	#######################################################################################################

def pre_process_raw_data(raw_data):
	processed_data = raw_data
	for x in range(0,20):
		processed_data = re.sub(r'\ \ ',' ',processed_data)
	split_data = processed_data.split('\n')
	return split_data

#   ######################################################################################################
#   ###############################################################     #      ##       #      ###########
#   ##### Functions to process raw data and export to Excel/CSV ###    ###    ####     ###     ###########
#   ###############################################################     #     ####      #      ###########
#   ######################################################################################################

		#	###############################################################
		#	############ Function for processing Show vlan output #########
		#	###############################################################

def process_show_vlan(hostname,split_data):
	formated_data = ""
	for line in split_data:
		if "VLAN Name" in line:
			continue
		elif "---" in line:
			continue
		elif "VLAN Type" in line:
			break
		else:
			line = re.sub(r",",".",line)
			line = re.sub(r"\ ",",",line)
			line = "{0},{1}".format(hostname,line)
			formated_data = "{0} \n {1}".format(formated_data,line)
	return formated_data

		#	################################################################
		#	############ Function for processing Show interfaces trunk #####
		#	################################################################

def process_show_int_trunk(hostname,split_data):
	count = 0
	formated_data = ""
	for line in split_data:
		if "Port" in line:
			continue
		line = re.sub(",",".",line)
		line = re.sub("\ ",",",line)
		line = line.split('\n')
		port = line[0]
		if count ==- 0:
			Mode =  line[1]
			Encap = line[2]
			Native = line[3]
			count += 1
		elif count == 1:
			vl_on_trnk = line[1]
			count += 1
		elif count == 2:
			vl_in_domain = line[1]
			count += 1
		elif count == 3:
			vl_in_stree = line[1]
			trunk_info = "{0},{1},{2},{3},{4},{5},{6},{7}".format(hostname,port,Mode,Encap,Native,vl_on_trnk,vl_in_domain,vl_in_stree)
			formated_data = "{0} \n{1}".format(formated_data,trunk_info)
			count = 0

		#	###############################################################
		#	############ Function for processing Show ip interface brief ##
		#	###############################################################

def process_sh_ip_br(hostname,split_data):
	formated_data = ""
	for line in split_data:
		if "Interface" in line:
			continue
		else:
			line = re.sub(r",",".",line)
			line = re.sub(".\ ",".",line)
			line = re.sub(r"\ ",",",line)
			line = "{0},{1}".format(hostname,line)
			formated_data = "{0} \n {1}".format(formated_data)
	return formated_data

		#	###############################################################
		#	############ Function for processing Show run interface   #####
		#	###############################################################

def process_sh_run_int(hostname,split_data):
	count = 0
	formated_data = ""
	for line in split_data:
		if "Current" in line:
			continue
		elif "!" in line:
			continue
		line = re.sub(",",".",line)
		line = re.sub(".\ ",".",line)
		line = re.sub("\ ",",",line)
		line = line.split('\n')
		port = line[0]
		if count == 0:
			port = line[1]
			count += 1
		elif count == 1:
			access_vl = line[3]
			count += 1
		elif count == 2:
			voice_vl = line[3]
			port_info = "{0},{1},{2},{3}".format(hostname,port,access_vl,voice_vl)
			formated_data = "{0} \n{1}".format(formated_data,port_info)
			count += 1
		elif count == 3:
			count += 1
		elif count == 4:
			count += 1
		elif count == 5:
			count += 1
		elif count == 6:
			count = 0

		#	###############################################################
		#	############ Function for processing Show run             #####
		#	###############################################################

def process_show_run(hostname,raw_data):
	raw_data = """-------------------------------------------------------------------------------------------------
				  ----------------------- Show Run results from: {0} ---------------------------
				  -------------------------------------------------------------------------------------------------


				  {1}""".format(hostname,raw_data)
	Write_Raw_Results(raw_data,'show_run_capture',hostname)

#	###############################################################################################
#	############ BKGD SSH function for maintaining single ssh session for device/commands #########
#	###############################################################################################


class BKGD_SSH():
	def __init__(self):
		self.Device_info = {}
		self.SSH_C_Signal = 0
		self.SSH_R_Signal = 0
		self.SSH_CMD = None
		self.SSH_Result = None

	def load_dev(self,DI):
		self.Device_info = DI
		self.init_session()

	def set_c_sig(self, v):
		self.SSH_C_Signal = int(v)

	def set_r_sig(self, v):
		self.SSH_R_Signal = int(v)

	def ret_c_sig(self):
		return self.SSH_C_Signal

	def ret_r_sig(self):
		return self.SSH_R_Signal

	def init_session(self):
		#Create bkgd process to run capture
		ssh_session = Thread(target=self.bkgd_ssh, args=())
		#Initiate and start backgroun capture.
		ssh_session.isDaemon()
		ssh_session.start()
		time.sleep(15)
		print 'back from thread'

	def send_cmd(self,cmd):
		self.SSH_CMD = '{}\n'.format(cmd)
		self.clear_output()
		self.set_c_sig(1)
		time.sleep(3)

	def collect_result(self,Result):
		self.SSH_Result = Result
		self.clear_output()

	def return_output(self):
		self.set_c_sig(2)
		r_sig = self.ret_r_sig()
		while self.SSH_R_Signal != 1:
			r_sig = self.ret_r_sig()
			#print 'waiting on r'
			time.sleep(1)
		self.set_r_sig(0)
		return self.clean_control(self.SSH_Result)

	def clear_output(self):
		self.set_c_sig(2)
		time.sleep(2)

	def enter_enable(self):
		self.set_c_sig(3)
		time.sleep(2)

	def enter_conf(self):
		self.set_c_sig(4)
		time.sleep(2)

	def exit_conf(self):
		self.set_c_sig(5)
		time.sleep(2)

	def close(self):
		self.set_c_sig(99)

	def clean_control(self,s):
		compiled_output=''''''
		for line in s.splitlines():
			all_bytes = string.maketrans('', '')
			line = line.translate(all_bytes, all_bytes[:32])
			#print '{0}'.format(line)
			if line == '':
				line = line
			elif line == ' ':
				line = line
			else:
				compiled_output = '''{0}
	{1}'''.format(compiled_output, line)
		return(compiled_output)

	def bkgd_ssh(self):
		#print 'SSH commands running in background.'
		host = self.Device_info['IP']
		port = self.Device_info['port']
		user = self.Device_info['Username']
		password = self.Device_info['Password']
		if 'rpw' in self.Device_info.keys():
			rpw = self.Device_info['RPW']
		else:
			rpw = None
		# Creates a new SSH client.
		ssh = paramiko.SSHClient()
		# Allows for connections to hosts with unknown fingerprints.
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		# Connects to the specified host.
		ssh.connect(hostname=host, port=port, username=user, password=password)
		# Creates a new shell to allow the sending of commands.
		ssh_sess = ssh.invoke_shell()
		time.sleep(5)
		# Set terminal to not pAGE
		ssh_sess.send('terminal length 0\n')
		ssh_sess.send('terminal pager 0\n')
		# Remove whatever is currently in the buffer.
		ssh_sess.recv(100000)
		c_sig = self.ret_c_sig()
		while c_sig != 99:
			c_sig = self.ret_c_sig()
			if c_sig == 1:
				cmd = self.SSH_CMD
				print 'issuing command'
				ssh_sess.send(cmd)
				time.sleep(2)
				# run while loop until kill signal is received.
				self.set_c_sig(0)

			elif c_sig == 2:
				print 'collecting output'
				# Set output equal to whatever is currently in the buffer.
				#print ssh_sess.recv(100000)
				ssh_output = ssh_sess.recv(100000)
				#print 'ssh output : {}'.format(ssh_output)
				self.collect_result(ssh_output)
				self.set_c_sig(0)
				self.set_r_sig(1)

			elif c_sig == 2:
				# Remove whatever is currently in the buffer.
				ssh_sess.recv(100000)
				self.set_c_sig(0)


		# Enter CLI Mode
			elif c_sig == 3:
				print 'Entering Enable mode.'
				enter_enable = 'enable\n'
				ssh_sess.send(enter_enable)
				time.sleep(1)
				self.set_c_sig(0)

		# Enter Conf Mode
			elif c_sig == 4:
				print 'Entering Configuration mode.'
				enterconf = 'configure terminal\n'
				ssh_sess.send(enterconf)
				time.sleep(1)
				self.set_c_sig(0)

		# Exit Conf
			elif c_sig == 5:
				print 'Exiting Configuration mode.'
				exitmode = 'exit\n'
				ssh_sess.send(exit)
				time.sleep(1)
				self.set_c_sig(0)


		if c_sig == 99:
			print 'Kill signal recieved. Ending Capture'
			ssh_sess.send('^c\n')
			# Set output equal to whatever is currently in the buffer.
			ssh_output = ssh_sess.recv(100000)
			# close ssh session
			ssh_sess.close()
			# reset daemon flag for next instance of function.
			self.set_c_sig(0)

main()
