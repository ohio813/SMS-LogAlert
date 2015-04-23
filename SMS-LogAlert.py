#!/usr/bin/python

# Quick script that alerts on iptable logs
# You must set these things:
#------------------------------
# (1) User and password of SMTP Server, if using GMAIL insure using unsecure app settings
# (2) Recipients of the SMS need to be in list format
# (3) Email addr must use proper SMS format per company .. ex ATT= txt.att.net

import smtplib
import os 
import time
import argparse
import sys

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

#HTML needs to be un "#""


def cli_parser():
	 parser = argparse.ArgumentParser(add_help=False, description="This script will monito a iptables log and aler by SMS")
	 parser.add_argument("-t", metavar="10", type=int, default=10, help="Will tell how long between log checks in Secs, defaults to 10 Secs.")
	 parser.add_argument("-sms", metavar="10", type=int, default=100, help="Max SMS texts that can recived before it shuts down, default is 100.")
	 parser.add_argument("-e", metavar="email@eamil.com", help="Set required email addr user, ex ale@email.com")
	 parser.add_argument("-p", metavar="1234", help="Set required email password")
	 parser.add_argument('-h', '-?', '--h', '-help', '--help', action="store_true", help=argparse.SUPPRESS)
	 args = parser.parse_args()
	 if args.h: 
			parser.print_help()
			sys.exit()
	 return args.t, args.sms, args.e, args.p


def mail(text_alert, max_sms, senders_email, senders_password): 
	recipient = ['213xxxxxx@txt.att.net']

	# Create message container - the correct MIME type is multipart/alternative.
	msg = MIMEMultipart('alternative')
	msg['Subject'] = "YOU HAVE MAIL"
	msg['From'] = senders_email
	msg['To'] = ", ".join(recipient)

# Create the body of the message (a plain-text and an HTML version).
	text = text_alert
	
	#HTML SUPPORT LIVES HERE
	#html = """\
	#<html>
	 # <head></head>
		#<body>
		 # <p>BECON HAS LANDEDbr>
			#</p>
		#</body>
	#</html>
	#"""

# Record the MIME types of both parts - text/plain and text/html.
	part1 = MIMEText(text, 'plain')
	#part2 = MIMEText(html, 'html')

# Attach parts into message container.
# According to RFC 2046, the last part of a multipart message, in this case
# the HTML message, is best and preferred.
	msg.attach(part1)
	#msg.attach(part2)

# Send the message via local SMTP server.
	mail = smtplib.SMTP('smtp.gmail.com', 587)
	mail.ehlo()
	mail.starttls()
	mail.login(senders_email, senders_password)
	mail.sendmail(senders_email, recipient, msg.as_string())
	mail.quit()
	print "[*] Message has been sent!"
	max_sms = max_sms - 1
	return max_sms


#This function monitors the log file 
def syslog_mon(sleep_time, max_sms, senders_email, senders_password):
	#Use log_file to point to the log you need to monitor
		log_file = "/var/log/iptables.log"
		while True:
			try:
				f = open(log_file, "r")
				try:
				# OR read one line at a time.
					log_data = f.readlines()
					f.close()	
					Alert_on = ''	
					for Alert_on in log_data:
						trigger = "CALLBACK"
						if trigger in Alert_on:
							Listed_data = str(Alert_on)
							Listed_data  = Listed_data.split()
							data=''
						for element in Listed_data:
							if "SRC" in element:
								SRC_IP=element
								print "[*] We Have a CALLBACK at:", element
								mail(SRC_IP, max_sms, senders_email, senders_password)
								clear_file() 
								break
				except IOError:
					pass
			except IOError:
				pass
			sleep(sleep_time)
			sms_check(max_sms)


#Open and clear th file for future Alets
def clear_file():
	try:
		f = open("/var/log/iptables.log", "w+")
		f.write("")
		f.close()
		print "[*] File has been cleared"
	except IOError:
		pass  

def sms_check(max_sms):
	if max_sms > 0:
		return
	if max_sms < 1:
		print "[*] Reached max SMS count"
		exit()


 #Sleep so you wont block file   
def sleep(how_long):
	 print "[*] Sleeping for:", how_long, "second(s)"
	 time.sleep(how_long)
	

def title():
	print "\n\
		##############################\n\
		#     SCRIPT  KID  THING     #\n\
		#        KiLlSwiTch-GUI      #\n\
		##############################\n\
This tools is for SMS log alerting on target Log \n "



def main():
	#assign CLI vars
	cli_time, cli_sms, cli_user, cli_pass = cli_parser()
	if cli_user is None:
		print "[*] missing User-Name for SMTP login.. Now quiting"
		exit()
	if cli_pass is None:
		print "[*] missing Password for SMTP login.. Now quiting"
		exit()
	#call title menu
	title()
	
	#call log monitoring
	syslog_mon(cli_time, cli_sms, cli_user, cli_pass)

if __name__ == "__main__":
	try:	
		main()
	except KeyboardInterrupt:
		print 'Interrupted'
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)



