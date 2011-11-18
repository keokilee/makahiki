from django.core import management

import re
from apps.components.analytics.models import ApacheLog, MakahikiLog

def load_apache_log(filename, format):

    pattern_str = '(?P<ip>\d+\.\d+\.\d+\.\d+) \- \- \[(?P<time>.*)\] "(?P<request>.*) (?P<url>.*) (?P<http>.*)" (?P<status>\d+) (?P<size>.*)'

    if format == 'combined':
      pattern_str = pattern_str + ' "(?P<referral>.*)" "(?P<agent>.*)"'

    pattern = re.compile(pattern_str)

    file = open(filename)
    count = 0
    for line in file:
      m = pattern.match(line)
      if m:
          res = m.groupdict()

          res["status"] = int(res["status"])
          if res["size"] == "-":
            res["size"] = 0
          else:
            res["size"] = int(res["size"])

          #print res

          log = ApacheLog()
          log.host = res["ip"]
          log.request_time = res["time"]
          log.request = res["request"]
          log.url = res["url"]
          log.status = res["status"]
          log.response_size = res["size"]
          log.http = res["http"]
          if format == 'combined':
            log.referral = res["referral"]
            log.agent = res["agent"]

          log.save()
          count = count + 1
          if count % 1000 == 0:
              print "%d records loaded" % count

    print "-- total %d records loaded" % count

    file.close()

def load_makahiki_log(filename):

    pattern_post = re.compile('(?P<level>.*) (?P<date>.*) (?P<time>.*) (?P<ip>\d+\.\d+\.\d+\.\d+) (?P<user>.*) POST (?P<url>.*) (?P<status>\d+) \<QueryDict: \{(?P<content>.*)\}\>')
    pattern_get = re.compile('(?P<level>.*) (?P<date>.*) (?P<time>.*) (?P<ip>\d+\.\d+\.\d+\.\d+) (?P<user>.*) GET (?P<url>.*) (?P<status>\d+)')

    file = open(filename)
    count = 0

    for line in file:
      request = None
      m = pattern_get.match(line)
      if m:
          request = 'GET'
      else:
          m = pattern_post.match(line)
          if m:
            request = 'POST'

      if request:
          res = m.groupdict()

          res["status"] = int(res["status"])

          #print res

          log = MakahikiLog()
          log.host = res["ip"]
          log.request_time = res["date"] + ' ' + res["time"]
          log.request = request
          log.url = res["url"]
          log.status = res["status"]
          log.level = res["level"]
          log.remote_user = res["user"]

          if request == 'POST':
              log.post_content = res["content"]

          log.save()

          count = count + 1
          if count % 1000 == 0:
              print "%d records loaded" % count

    print "-- total %d records loaded" % count

    file.close()

def clear_apache_log():
    ApacheLog.objects.all().delete()

def clear_makahiki_log():
    MakahikiLog.objects.all().delete()

class Command(management.base.BaseCommand):
  help = 'Load the logs files into analytics tables.'

  def handle(self, *args, **options):
    if len(args) < 2:
      self.stderr.write("Usage: 'python manage.py load_log apache|makahiki <log_filename> [common]\n")
      return

    type = args[0]
    filename = args[1]

    format = "combined"
    if len(args) == 3:
        format = args[2]

    if type == "apache":
        if format == "combined":
            clear_apache_log()

        load_apache_log(filename, format)
    if type == "makahiki":
        clear_makahiki_log()
        load_makahiki_log(filename)