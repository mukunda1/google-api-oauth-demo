#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#	Simple demo of Google Data API 
#	working with multiple scoops
#
#	Written by: Kristofer Källsbo
#	http://www.hackviking.com
#
import webapp2
from google.appengine.ext.webapp.util import run_wsgi_app
from urlparse import urlparse #Nedded for parsing URLS
import gdata.photos.service #In this example where contacting Google Picasa Web API
import gdata.client #Needed to get the user info
import gdata.gauth # Needed to export the session token from the gdata client
import json # Needed to parse the input

class MainHandler(webapp2.RequestHandler):
    def get(self):
		oauthURL = urlparse(self.request.url) #Parsing the requesting url
		oauthURL = oauthURL.scheme + '://' + oauthURL.netloc + oauthURL.path + "oauth" #Removing any querystrings and appending the oauth path
		scope = ['https://picasaweb.google.com/data/', 'https://www.googleapis.com/auth/userinfo.email'] #Requesting the Picasa scope and the user profile
		secure = False 
		session = True
		gd_client = gdata.photos.service.PhotosService() #Fireing up the gdata client to build the login url
		oauthLoginURL = gd_client.GenerateAuthSubURL(oauthURL, scope, secure, session)
		self.response.write('<a href="{0}">Log in...</a>'.format(oauthLoginURL))

class oAuthHandler(webapp2.RequestHandler): #Actuall handler for the oauth callback from Google API
	def get(self):
		# Check if there is any querystring
		token = self.request.get("token", default_value='none')	
		
		if (token != 'none'):
			# We have a token upgrade to session token
		
			#Get the gdata client up and running
			gd_client = gdata.photos.service.PhotosService()
			
			#Set the one time token
			gd_client.SetAuthSubToken(token)
			
			#Try to upgrade it to a session token
			gd_client.UpgradeToSessionToken()
			
			#Test access
			self.response.write("We have access to your picasa albums<br/>")
			albums = gd_client.GetUserFeed() #Get album list
			
			#Dsiplay album list
			for album in albums.entry:
				self.response.write('{0} ({1})<br/>'.format(album.title.text,album.numphotos.text))
			
			#Setup a basic gdata client
			userClient = gdata.client.GDClient()
			
			#Create a gauth sub token object from the session token we allready have in the gd_client
			oauthToken = gdata.gauth.AuthSubToken(gd_client.GetAuthSubToken())
			
			#Get the request, this userinfo is in json
			response = userClient.request('GET','https://www.googleapis.com/userinfo/v2/me', oauthToken)
			
			#Parse the webresponse
			jobj = json.loads(response.read())
			
			#Display
			self.response.write('Your email is: {0}'.format(jobj['email']))
		else:
			self.response.write('ERROR: NOTOKEN')
		
app = webapp2.WSGIApplication([
	('/oauth', oAuthHandler), #Handler for the oauth callback
    ('/', MainHandler)
], debug=True)

def main():
	run_wsgi_app(app)

if __name__ == '__main__':
	main()
