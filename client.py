# client.py
import requests

tokenUrl = "http://localhost:8001/realms/myorg/protocol/openid-connect/token"

client_id = "testapiclient1"
client_secret = "0QGeXxVys5dWzJvJ1vpsUnm2ML0ZFxNe"
requiredScopes = "".join(["test_api_access"])

#to get token do the http POST REQ and get the token
# request the access token from OAuth server
post_body = {"grant_type": "client_credentials",
             "client_id": client_id,
             "client_secret": client_secret,
             "scope": requiredScopes#have to give this thing explicityl 
             }
headers = {'content-type': "application/x-www-form-urlencoded"}

accessTokenResp = requests.post(tokenUrl,
                    data=post_body,
                    headers=headers)

# derive the access token from OAuth server response
if not accessTokenResp.ok:
    print("server token response status not ok")
    quit()

accessTokenRespJson = accessTokenResp.json()

if not "access_token" in accessTokenRespJson:
    print("access_token not found in token response")
    quit()

accessToken = accessTokenRespJson["access_token"]
print(accessToken)

# request data from resource server with access token in the request header
apiReqHeaders = {
    'content-type': "application/json",
    'authorization': f"Bearer {accessToken}"
}
apiResp = requests.get("http://localhost:50100/api/private-scoped", headers=apiReqHeaders)

# parse the response from resource server
if not apiResp.ok:
    print("ok response not received from resource API call")
    print("Status:", apiResp.status_code)               
    print("Body:", apiResp.text)
    quit()

print("printing API response...")
print(apiResp.json())
print("execution complete...!")