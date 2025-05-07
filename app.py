from wsgiref.simple_server import make_server

def application(environ, start_response):
    print("Custom WSGI app is running...")
    status = '200 OK'
    headers = [('Content-Type', 'text/plain')]
    start_response(status, headers)
    return [b'hi']

if __name__ == '__main__':
    with make_server('', 8000, application) as httpd:
        print("Serving on port 8000...")
        httpd.serve_forever()
