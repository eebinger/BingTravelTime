# Import Modules
import urllib2
import json
import time
import schedule

# Your BING API key
KEY = 'INSERT KEY HERE'

# Output File
output_file = 'BingAPI_Corridors.txt'

# A-->B
# Values are a sample of the Boston MPO's 2016 TIP Corridors, which can be found
# here in full: http://www.ctps.org/tip#
corridors = [
	{	
		'TIP': 'Rte 3 from Crosby Drive North to Manning Rd',
		'start_coord': [42.506431,-71.247396],
		'end_coord': [42.528233,-71.271582]
	},
	{	
		'TIP': 'Rte 3 from Manning Rd to Crosby Drive North',
		'start_coord': [42.528016,-71.271914],
		'end_coord': [42.506293,-71.247788]
	},
	{	
		'TIP': 'Rte 126 from Framingham TL to Holliston TL',
		'start_coord': [42.259508,-71.423853],
		'end_coord': [42.236358,-71.431505]
	},
	{	
		'TIP': 'Rte 126 from Holliston TL to Framingham TL',
		'start_coord': [42.236358,-71.431505],
		'end_coord': [42.259508,-71.423853]
	}
]

# Output JSON Object Initialized
bing_result = []

# API call to collect 'travelDistance', 'travelDuration', 'travelDurationTraffic', 
# and 'trafficCongestion' values.
#
# It is currently written to only run during PM Peak Period (3-7PM) on Tuesdays, 
# Wednesdays, and Thursdays, but that can be changed by changing the values in
# the DOW and HOUR lists.
def bing_api_travelDuration(routes, output_file):
	DOW = ['Tuesday', 'Wednesday', 'Thursday']
	HOUR = [15,16,17,18]
	if time.strftime('%A') in DOW:
		if int(time.strftime('%H')) in HOUR:
			# Open output_file
			with open(output_file, 'w') as f:
				# Call API for each route in routes json
				for route in routes:
					# Create base of HTTP request
					http = "http://dev.virtualearth.net/REST/V1/Routes/Driving"
					http += "?key=" + KEY
					http += "&optmz=timeWithTraffic"
					http += "&distanceUnit=mi"
					
					# Call Bing Maps API
					try:
						url = http
						url += "&wp.0=" + str(route['start_coord'][0]) + "," + str(route['start_coord'][1])
						if 'mid_coord' in route:
							url += "&wp.1=" + str(route['mid_coord'][0][0]) + "," + str(route['mid_coord'][0][1])
							url += "&wp.2=" + str(route['mid_coord'][1][0]) + "," + str(route['mid_coord'][1][1])
							url += "&wp.3=" + str(route['end_coord'][0]) + "," + str(route['end_coord'][1])
						else:
							url += "&wp.1=" + str(route['end_coord'][0]) + "," + str(route['end_coord'][1])
						handle = urllib2.urlopen(url)
						response = handle.read()
						api = json.loads(response)
						bingData = api['resourceSets'][0]['resources'][0]
						
						# Append returned data to routes json
						bing_result.append({
							'route': 			route['TIP'],					# The Name of the Corridor (A-->B)
							'dow': 				time.strftime('%A'),				# DOW
							'date':				time.strftime('%x'), 				# Date
							'callTime': 			time.strftime('%X'),				# Time (24-Hour Clock)
							'travelDistance': 		float(bingData['travelDistance']),		# Travel Distance (miles)
							'travelDuration': 		int(bingData['travelDuration']),		# Travel Duration, no Traffic (seconds)
							'travelDurationTraffic': 	int(bingData['travelDurationTraffic']), 	# Travel Duration with Traffic (seconds)
							'trafficCongestion': 		str(bingData['trafficCongestion'])		# The Level of Traffic Congestion
						})
					
					# If failure, print time of error, continue
					except (urllib2.HTTPError, urllib2.URLError) as e:
						print e.code
						print "A-->B, Error at " + time.strftime('%A %X %x')
					
				# Dump output as json to output_file
				json.dump(bing_result, f)
			# Close output_file so next iteration rewrites with appended data
			f.closed
		else:
			# It is not during the PM Peak Period. No need to call API.
			return
	else:
		# DOW not Tuesday, Wednesday, or Thursday. No need to call API.
		return

# Run function and collect travel time data in 5-minute intervals
schedule.every(5).minutes.do(bing_api_travelDuration, corridors, output_file).tag('five_minutes')
while True:
    schedule.run_pending()
