#!/usr/bin/env python

import re
import os

from urlparse import parse_qs


PASSPORT_INFO_REGEX = r'\s*(\d{4})\s*(\d{6})\s*'
PROBLEM_ANSWER_REGEX = r'\s*(\d+)\s*'
VERIFIED = False

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
  global VERIFIED

  response_body = ''
  if VERIFIED:
    response_body = readfile('static/html/verified.html')
    start_response('200 OK', get_response_headers('text/html'))
    return [response_body.encode('utf-8')]
  elif environ['REQUEST_METHOD'].lower() != 'post':
    return not_found(environ, start_response)

  request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  request_body = environ['wsgi.input'].read(request_body_size)
  parsed_qs = parse_qs(request_body)
  passport_info = parsed_qs['passport_info'].pop()

  matched = re.match(PASSPORT_INFO_REGEX, passport_info)
  passport_series = matched.group(1)
  passport_number = matched.group(2)

  if passport_series + passport_number == '9211198283':
    VERIFIED = True
    response_body = readfile('static/html/verified.html')
  else:
    response_body = readfile('static/html/not-verified.html')

  start_response('200 OK', get_response_headers('text/html'))
  return [response_body.encode('utf-8')]

def check_answer(environ, start_response):
  request_body_size = int(environ.get('CONTENT_LENGTH', 0))
  request_body = environ['wsgi.input'].read(request_body_size)
  parsed_qs = parse_qs(request_body)
  problem_info = parsed_qs['problem_answer'].pop()

  matched = re.match(PROBLEM_ANSWER_REGEX, problem_info)
  problem_answer = matched.group(1)

  response_body = ''
  if problem_answer == '4':
    response_body = readfile('static/html/congrats.html')
  else:
    response_body = readfile('static/html/sorry.html')

  start_response('200 OK', get_response_headers('text/html'))
  return [response_body.encode('utf-8')]


url_managers = [
  (r'/$', index),
  (r'/static/.*', static),
  (r'/verify$', verify)
]


# Main function of WSGI application.
def application(environ, start_response):
  for key in environ:
    print key + '->' + str(environ[key])

  if environ['REQUEST_METHOD'].lower() == 'post':
    if environ['PATH_INFO'].lower().strip('/') == 'verify':
      return verify(environ, start_response)
    elif environ['PATH_INFO'].lower().strip('/') == 'check-answer':
      return check_answer(environ, start_response)

  for regex, func in url_managers:
    if re.match(regex, environ['PATH_INFO']):
      return func(environ, start_response)
  return not_found(environ, start_response)