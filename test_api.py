import urllib.request
import urllib.error
import json
import time

base_url = "http://127.0.0.1:8000/api"

def request(url, data=None):
    req = urllib.request.Request(url)
    req.add_header('Content-Type', 'application/json')
    if data:
        data = json.dumps(data).encode('utf-8')
    try:
        with urllib.request.urlopen(req, data=data) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} - {e.read().decode()}")
        raise
    except Exception as e:
        print(f"Error: {e}")
        raise

print("1. Cloning voice...")
res = request(f"{base_url}/voice/clone", data={})
voice_id = res["voice_id"]
print(f"Voice ID: {voice_id}")

print("2. Creating job (requesting infinitetalk)...")
res = request(f"{base_url}/jobs", data={
    "voice_id": voice_id,
    "avatar_url": "test",
    "script_mode": "manual",
    "script_input": "hello",
    "preferred_engine": "infinitetalk"
})
job_id = res["job_id"]
print(f"Job ID: {job_id}")

print("3. Polling status until completion/failure...")
while True:
    time.sleep(1)
    status = request(f"{base_url}/jobs/{job_id}")
    print(status)
    if status["status"] in ["completed", "failed"]:
        break

print("Test complete.")
