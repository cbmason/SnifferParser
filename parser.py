#!/usr/bin/python3
################################################################################
#
# parser.py
#
# Description: Parses the output.txt files that Stratus Engineering's EZ-View
#	RS232 sniffer program outputs.
#
# Author: Chris Mason <chrismason285@gmail.com>
#
################################################################################

import os
import sys
import binascii

def extract_msg_from_line(line):
	""" Returns the transmitted char logged by a line, and whether it was
	a Tx or an Rx. Returned char is in bytes format

	>>> extract_msg_from_line("78 08/21/13 17:10:37.007.295 2c , 1 0  0 0 0 0")
	(2c, tx)
	>>> extract_msg_from_line("83 08/21/13 17:10:37.071.151 0 0 0d < CR> 0 0 0 0")
	(0d, rx)
	"""

	myline = line.split()
	if len(myline[3]) == 2:
		return (binascii.unhexlify(myline[3]), "tx")
	elif(len(myline[5] == 2)):
		return (binascii.unhexlify(myline[5]), "rx")
	else:
		return (b'', "null")


def parse_file(txtfile):
	"""Parses an EZ-View output textfile into a text file containing a 
	chronological list of command / response pairs between master and slave.  
	File also contains a set of all commands / responses.  The output file
	is named after the base of the input with _parsed.txt appended. """

	#open file
	try:
		inhandle = open(txtfile, 'r')
	except: IOError as err:
		print("Infile I/O error: {0}".format(err))
		return

	#open output file or die
	try:
		outfile = str(os.path.splitext(txtfile)[0] + "_parsed.txt")
		outhandle = open(outfile, 'x')
	except IOError as err:
		print("Outfile I/O error: {0}".format(err))
		return

	#throw away first line since it is just header garbage
	curline = inhandle.readline()

	curdirection = "null"
	allcmds = set()
	curmsg = bytearray()

	#while not end of file:
	for line in inhandle:
		(txbyte, direction) = extract_msg_from_line(inhandle.readline())

		#if message is done, reset message vars
		if direction != curdirection:
			if curmsg != b'':
				outhandle.write(curmsg.decode())
				outhandle.write('\n')
				allcmds.add(curmsg.decode())
				curmsg = b''
			curdirection = direction
			#see if tx or rx, print to output accordingly
			if ("null" == direction):
				#do nothing
				pass

			elif ("rx" == direction):
				outhandle.write("Slave transmitted: ")
				while direction == "rx":
					curmsg += txbyte

			elif ("tx" == direction):
				outhandle.write("Master transmitted: ")

		curmsg += txbyte

	outhandle.write('\n\n')
	outhandle.write("List of all commands seen:\n")
	outhandle.write(str(allcmds))
	outhandle.close()
	inhandle.close()

if __name__ == "__main__":
	parse_file(sys.argv[1])

