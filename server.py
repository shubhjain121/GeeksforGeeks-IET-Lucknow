import http.server
import json
import os

PORT = int(os.environ.get("PORT", 8000))


class CustomHandler(http.server.SimpleHTTPRequestHandler):
def do_GET(self):
    if self.path == '/':
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        html = """
        <!doctype html>
        <html>
        <head><meta name="viewport" content="width=device-width,initial-scale=1"></head>
        <body>
        <h2>Register</h2>
        <form id="regForm">
          <input name="fullName" placeholder="Full name" required><br><br>
          <input name="rollNumber" placeholder="13-digit roll number" required><br><br>
          <input name="password" placeholder="Password" required><br><br>
          <button type="submit">Register</button>
        </form>
        <pre id="result"></pre>
        <script>
        document.getElementById('regForm').addEventListener('submit', async function(e){
          e.preventDefault();
          const form = e.target;
          const data = {
            fullName: form.fullName.value,
            rollNumber: form.rollNumber.value,
            password: form.password.value
          };
          try {
            const res = await fetch('/register', {
              method: 'POST',
              headers: {'Content-Type': 'application/json'},
              body: JSON.stringify(data)
            });
            const json = await res.json();
            document.getElementById('result').textContent = JSON.stringify(json, null, 2);
          } catch (err) {
            document.getElementById('result').textContent = 'Error: ' + err;
          }
        });
        </script>
        </body>
        </html>
        """
        self.wfile.write(html.encode('utf-8'))
    else:
        self.send_response(404)
        self.end_headers()

    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_POST(self):
        if self.path == '/register':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            try:
                data = json.loads(post_data.decode('utf-8'))
                
                full_name = data.get('fullName', '')
                roll_number = data.get('rollNumber', '')
                password = data.get('password', '')
                
                if any(char.isdigit() for char in full_name):
                    self.send_error_response("Name must not contain numbers.")
                    return
                
                if len(roll_number) != 13 or not roll_number.isdigit():
                    self.send_error_response("Roll number must be exactly 13 digits.")
                    return
                
                if len(password) < 5 or not any(char.isupper() for char in password):
                    self.send_error_response("Password must be at least 5 characters and contain an uppercase letter.")
                    return
                
                filepath = 'registrations.json'
                registrations = []
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            registrations = json.load(f)
                            if not isinstance(registrations, list):
                                registrations = []
                    except Exception:
                        registrations = []
                
                registrations.append(data)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(registrations, f, indent=4)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                response = {"success": True}
                self.wfile.write(json.dumps(response).encode('utf-8'))
                
            except json.JSONDecodeError:
                self.send_error_response("Invalid JSON data.")
            except Exception as e:
                self.send_error_response(f"Server error: {str(e)}")
        else:
            self.send_response(404)
            self.end_headers()
            
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        response = {"success": False, "message": message}
        self.wfile.write(json.dumps(response).encode('utf-8'))

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server_address = ('', PORT)
    httpd = http.server.HTTPServer(server_address, CustomHandler)
    print(f"Serving custom HTTP server with POST support on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        httpd.server_close()
