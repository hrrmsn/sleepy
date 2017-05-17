#!/usr/bin/env python

import re
import os

from urlparse import parse_qs


PASSPORT_INFO_REGEX = r'\s*(\d{4})\s*(\d{6})\s*'

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
  path_info = environ['PATH_INFO'].strip('/')
  response_body = ''
  if os.path.exists(path_info):
    response_body = readfile(path_info)
  
  content_type = 'application/octet-stream'
  if path_info.endswith('.css'):
    content_type = 'text/css'
  elif path_info.endswith('.jpg'):
    content_type = 'image/jpeg'
  elif path_info.endswith('.ico'):
    content_type = 'image/x-icon'

  start_response('200 OK', get_response_headers(content_type))
  return [response_body]

def index(environ, start_response):
  response_body = readfile('static/html/index.html')
  start_response('200 OK', get_response_headers('text/html'))
  return [response_body.encode('utf-8')]

def not_found(environ, start_response):
  response_body = readfile('static/html/not-found.html')
  start_response('200 OK', get_response_headers('text/html'))
  return [response_body.encode('utf-8')]

def verify(environ, start_response):
  request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  request_body = environ['wsgi.input'].read(request_body_size)
  parsed_qs = parse_qs(request_body)
  passport_info = parsed_qs['passport_info'].pop()

  matched = re.match(PASSPORT_INFO_REGEX, passport_info)
  passport_series = matched.group(1)
  passport_number = matched.group(2)

  if passport_series + passport_number == '9211198283':
    title = 'Hello, Ilya!'
    body_content = """<p>It seems that you aren't Ilya Salnikov. You need to stop look this page in such case. 
      Otherwise please take a new <a href="/">attempt</a>.</p>"""
  else:
    title = 'stranger'
    body_content = """<p>Yeah! You proved us that you're Ilya Salnikov. Now you need to solve a simple problem if you 
      want to receive your gift. Good luck buddy!</p>"""

  response_body = readfile('static/html/verify.html')
  response_body = response_body.format(
    **{'title': title, 'body_content': body_content}
  )

  start_response('200 OK', get_response_headers('text/html'))
  return [response_body.encode('utf-8')]


url_managers = [
  (r'/$', index),
  (r'/static/.*', static)
]


# Main function of WSGI application.
def application(environ, start_response):
  for key in environ:
    print key + '->' + str(environ[key])
  print '***\n\n'

  if environ['REQUEST_METHOD'].lower() == 'post':
    return verify(environ, start_response)

  for regex, func in url_managers:
    if re.match(regex, environ['PATH_INFO']):
      return func(environ, start_response)
  return not_found(environ, start_response)