import os
os.environ["APP_ENV"]="staging"
import app
c=app.app.test_client()
h=c.get("/health")
cb=c.post("/callback", json={"type":"message_new"})
print("HEALTH", h.status_code, h.json)
print("CALLBACK", cb.status_code, cb.data.decode())
assert h.status_code == 200
assert h.json["environment"] == "staging"
assert h.json["callback_enabled"] is False
assert cb.status_code == 503
print("STAGING_SMOKE_OK")
