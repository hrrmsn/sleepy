#!/usr/bin/env python


# Helper functions are defined here.
def get_response_headers(content_type):
  return [('Content-Type', content_type)]

def readfile(filepath):
  file_content = 'Error when reading from the file: ' + filepath + '.'
  with open(filepath, 'r') as f:
    file_content = f.read()
  return file_content


# URL dispatching is here.
def static(environ, start_response):

urls = [
  (r'/$', index),
  (r'/static/.*', static)
]


def not_found(environ, start_response):
  


# Main function of WSGI application.
def application(environ, start_response):
  response_body = """
    <!DOCTYPE>
    <html>
      <body>
        Hello. My name is Kotolina.
      </body>
    </html>"""

  response_headers = [
    ('Content-Type', 'text/html')
  ]

  start_response('200 OK', response_headers)
  return [response_body.encode('utf-8')]