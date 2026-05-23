from oauth2client.client import OAuth2WebServerFlow
from googleapiclient.discovery import build
import httplib2

CLIENT_ID = ''
CLIENT_SECRET =''
OAUTH_SCOPE = ''
REDIRECT_URI = ""
flow = OAuth2WebServerFlow(CLIENT_ID, CLIENT_SECRET, OAUTH_SCOPE, REDIRECT_URI)

authorize_url = flow.step1_get_authorize_url()
print(authorize_url)

auth_code = ''

credentials = flow.step2_exchange(auth_code)

http = httplib2.Http()
creds = credentials.authorize(http)

webmasters_service = build('searchconsole', 'v1', http=creds)

response = webmasters_service.sites().list().execute()
print(response)

