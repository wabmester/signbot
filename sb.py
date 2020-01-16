import re
import time
import json
# import psutil
from slackclient import SlackClient
#from subprocess import call
import smbus

botname = "signbot"
api_token = "xoxb-140504451268-672086241472-IsWiHYvPD5uocPOpJzTVFAT6"

DEVICE_BUS = 1
DEVICE_ADDR = 0x15
bus = smbus.SMBus(DEVICE_BUS)

STATE_OFF = 0
STATE_OPEN = 1
STATE_CLASS = 2
STATE_PI = 3
STATE_XMAS = 4

sign_state = STATE_OFF

def sign_off() :
	global sign_state
	LED_array=[0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,0x09,0x0a,0x0b,0x0c,0x0d,0x0e,0x0f,0x10,0x11,0x12,0x13,0x14,0x15,0x16,0x17,0x18]
	sign_state = STATE_OFF
        for i in range(0,24):
		bus.write_byte_data(DEVICE_ADDR, LED_array[i], 0x00)
	return

def sign_open() :
	global sign_state
	LED_array1=[0x01, 0x02, 0x03]	# r g b
	LED_array2=[0x04, 0x05, 0x06]
	if sign_state != STATE_OPEN and sign_state != STATE_OFF:
		sign_off()
        for i in range(0,3):
		bus.write_byte_data(DEVICE_ADDR, LED_array1[i], 0xFF)
        	for j in range(0,3) :
			bus.write_byte_data(DEVICE_ADDR, LED_array2[i], 0xFF)
                	time.sleep(0.5)                               # delay
			bus.write_byte_data(DEVICE_ADDR, LED_array2[i], 0x00)
                time.sleep(0.5)                               # delay
		bus.write_byte_data(DEVICE_ADDR, LED_array1[i], 0x00)
	sign_state = STATE_OPEN
	return

def sign_class():
	global sign_state
	if sign_state != STATE_CLASS and sign_state != STATE_OFF:
		sign_off()
	bus.write_byte_data(DEVICE_ADDR, 0x07, 0xFF)
	bus.write_byte_data(DEVICE_ADDR, 0x0a, 0xFF)
	sign_state = STATE_CLASS
	return

def sign_pi():
	global sign_state
	LED_array=[0x0d,0x0e,0x0f,0x10,0x11,0x12]
	if sign_state != STATE_PI and sign_state != STATE_OFF:
		sign_off()
        for i in range(0,3):
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2], 0xFF)
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2+1], 0xFF)
                time.sleep(0.5)                               # delay
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2], 0x00)
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2+1], 0x00)
	sign_state = STATE_PI
	return

def sign_xmas():
	global sign_state
	LED_array=[0x13,0x16,0x14,0x17]
	if sign_state != STATE_XMAS and sign_state != STATE_OFF:
		sign_off()
        for i in range(0,2):
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2], 0xFF)
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2+1], 0xFF)
                time.sleep(0.5)                               # delay
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2], 0x00)
		bus.write_byte_data(DEVICE_ADDR, LED_array[i*2+1], 0x00)
	sign_state = STATE_XMAS
	return

slack_client = SlackClient(api_token)


# Fetch your Bot's User ID
user_list = slack_client.api_call("users.list")
for user in user_list.get('members'):
    if user.get('name') == botname:
        slack_user_id = user.get('id')
        break


# Start connection
if slack_client.rtm_connect():
    print "Connected!"

    while True:
        for message in slack_client.rtm_read():
            if 'text' in message and message['text'].startswith("<@%s>" % slack_user_id):

                print "Message received: %s" % json.dumps(message, indent=2)

                message_text = message['text'].\
                    split("<@%s>" % slack_user_id)[1].\
                    strip()

                if re.match(r'.*(off).*', message_text, re.IGNORECASE):
                    sign_off()

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="sign is off",
                        as_user=True)

                if re.match(r'.*(open).*', message_text, re.IGNORECASE):

		    sign_open()

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="studio is open",
                        as_user=True)

                if re.match(r'.*(class).*', message_text, re.IGNORECASE):
		    sign_class()

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="class in session",
                        as_user=True)

                if re.match(r'.*(pi).*', message_text, re.IGNORECASE):
		    sign_pi()

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="Taste of Pi",
                        as_user=True)


                if re.match(r'.*(xmas).*', message_text, re.IGNORECASE):
		    sign_xmas()

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="Happy Festivus",
                        as_user=True)

                if re.match(r'.*(patience).*', message_text, re.IGNORECASE):

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="sorry, I don't have the time",
                        as_user=True)


                if re.match(r'.*(cpu).*', message_text, re.IGNORECASE):
                    cpu_pct = psutil.cpu_percent(interval=1, percpu=False)

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="My CPU is at %s%%." % cpu_pct,
                        as_user=True)

                if re.match(r'.*(memory|ram).*', message_text, re.IGNORECASE):
                    mem = psutil.virtual_memory()
                    mem_pct = mem.percent

                    slack_client.api_call(
                        "chat.postMessage",
                        channel=message['channel'],
                        text="My RAM is at %s%%." % mem_pct,
                        as_user=True)

        time.sleep(1)
        #print "Sign state: " + str(sign_state)
	if sign_state == STATE_OPEN:
		sign_open()
	elif sign_state == STATE_PI:
		sign_pi()
	elif sign_state == STATE_XMAS:
		sign_xmas()
	# STATE_OFF and STATE_CLASS don't iterate
