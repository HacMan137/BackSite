curl -X PATCH http://localhost:8080/api/user/1 -H 'Content-Type: application/json' -k -d '{"username":"superadmin", "old_password":"admin", "password": "admin123", "email":""}' --cookie ./cookies