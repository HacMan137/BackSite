curl -X POST http://localhost:8080/api/user/session -H 'Content-Type: application/json' -k -d '{"username":"admin", "password":"admin"}' --cookie-jar ./cookies