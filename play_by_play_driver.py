from play_by_play_generator import *
from selenium import webdriver
import requests
import datetime
import sys

if __name__ == "__main__":
	#open browser with Chrome
	browser = webdriver.Chrome()
	
	print("Starting Game ID: " + sys.argv[1] + " " + str(datetime.datetime.now()))
	generate(browser, sys.argv[1])
	print("Finish Game ID: " + sys.argv[1] + " " + str(datetime.datetime.now()))
	
	f = open("results.txt", "a")
	f.write("Success: " + sys.argv[1] + "\n")
	f.close()
	
	#close browser
	browser.close()