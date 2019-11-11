import os, sys, csv
import json
import requests
import urllib

AUTH_TOKEN = "ENTER PHANTOM REST API TOKEN"
PHANTOM_SERVER = "ENTER PHANTOM IP ADDRESS"
ARTIFACT_LABEL = "ENTER TARGET LABEL"
URL = "ENTER HTTP SERVER WITH RESPONSE CSV"

headers = {
  "ph-auth-token": AUTH_TOKEN
}

container_common = {
    "description" : "Test container added via REST API call",
}

# disable certificate warnings for self signed certificates
requests.packages.urllib3.disable_warnings()

def add_container(name, sid):
  url = 'https://{}/rest/container'.format(PHANTOM_SERVER)

  post_data = container_common.copy()
  post_data['name'] = '{} ({})'.format(name, sid)
  post_data['source_data_identifier'] = sid
  json_blob = json.dumps(post_data)

  # set verify to False when running with a self signed certificate
  r = requests.post(url, data=json_blob, headers=headers, verify=False)
  if (r is None or r.status_code != 200):
    if r is None:
      print('error adding container')
    else:
      print('error {} {}'.format(r.status_code,json.loads(r.text)['message']))
    return False

  return r.json().get('id')

def add_artifact(row, container_id):
  url = 'https://{}/rest/artifact'.format(PHANTOM_SERVER)

  post_data = {}
  post_data['name'] = 'artifact for {}'.format(row[1])
  post_data['label'] = ARTIFACT_LABEL
  post_data['container_id'] = container_id
  post_data['source_data_identifier'] = "source data primary key for artifact or other identifier"

  # The cef key is intended for structured data that can be used when
  # dealing with product agnostic apps or playbooks. Place any standard
  # CEF fields here.
  cef = {
    'ip': row[0],
    'host': row[1],
  }

  # The "data" key can contain arbitrary json data. This is useful for
  # keeping data that does not comfortably fit into CEF fields or is highly
  # product specific
  data = cef.copy()

  post_data['cef'] = cef
  post_data['data'] = data

  json_blob = json.dumps(post_data)

  # set verify to False when running with a self signed certificate
  r = requests.post(url, data=json_blob, headers=headers, verify=False)

  if (r is None or r.status_code != 200):
    if (r is None):
      print('error adding artifact')
    else:
      error = json.loads(r.text)
      print('error {} {}'.format(r.status_code, error['message']))
    return False

  resp_data = r.json()
  return resp_data.get('id')

def load_data():
    webpage = urllib.urlopen(URL)
    datareader = csv.reader(webpage)
    csvdata  = []
    for row in datareader:
	csvdata.append(row)

	container_id = add_container(row[0], row[1])
	if not container_id:
		continue
	print 'added container {}'.format(container_id)
	artifact_id = add_artifact(row, container_id)

if __name__ == '__main__':
  load_data()
  sys.exit(0)
    
