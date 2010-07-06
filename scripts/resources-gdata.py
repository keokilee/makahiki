try: 
  from xml.etree import ElementTree
except ImportError:  
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import string
from django.core.management import setup_environ
import settings
from django.core.exceptions import ObjectDoesNotExist
import datetime

setup_environ(settings)

import sys
from os.path import join

sys.path.insert(0, join(settings.PINAX_ROOT, "apps"))
sys.path.insert(0, join(settings.PROJECT_ROOT, "apps"))

from resources.models import Topic, Resource

RESOURCE_KEY="0An9ynmXUoikYdGZfXzRXM1l3aV9NUV9xb1JqcFAxQXc"
last_resource = Resource.objects.order_by("-created_at")[0]
last_date = last_resource.created_at


def printFeed(feed):
  for i, entry in enumerate(feed.entry):
    if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
      print '%s %s\n' % (entry.title.text, entry.content.text)
    elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
      print '%s %s %s' % (i, entry.title.text, entry.content.text)
      # Print this row's value for each column (the custom dictionary is
      # built from the gsx: elements in the entry.) See the description of
      # gsx elements in the protocol guide.
      print 'Contents:'
      for key in entry.custom:
        print '  %s: %s' % (key, entry.custom[key].text)
      print '\n',
    else:
      print '%s %s\n' % (i, entry.title.text)
      
def updateResources(worksheet_feed):
  for i, entry in enumerate(worksheet_feed.entry):
    print 'Resource:'
    for key in entry.custom:
      print '  %s: %s' % (key, entry.custom[key].text)
    print '\n'
    if datetime.datetime.strptime(entry.custom["timestamp"].text, "%m/%d/%Y %H:%M:%S") > last_date:
      createResource(entry)
    else:
      print "Skipping old entry."
    
def createResource(entry):
  resource = Resource()
  resource.title = entry.custom["title"].text
  resource.created_at = datetime.datetime.strptime(entry.custom["timestamp"].text, "%m/%d/%Y %H:%M:%S")
  resource.abstract = entry.custom["abstract"].text
  resource.media_type = entry.custom["mediatype"].text
  resource.added_by = entry.custom["enteredby"].text
  resource.url = entry.custom["link"].text

  try:
    resource.length = int(entry.custom["length"].text)
  except ValueError:
    print "This resource has length %s" % entry.custom["length"].text
  except TypeError:
    print "This resource has no length."
    
  resource.save()
  
  topics = entry.custom["topictypes"].text.split(",")
  for topic_string in topics:
    topic_string = topic_string.strip()
    try:
      topic = Topic.objects.get(topic=topic_string)
    except ObjectDoesNotExist:
      topic = Topic(topic = topic_string)
      topic.save()
      
    resource.topics.add(topic)

def promptForSpreadsheet(gd_client):
  # Get the list of spreadsheets
  feed = gd_client.GetSpreadsheetsFeed()
  printFeed(feed)
  input = raw_input('\nSelection: ')
  return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]
  
def promptForWorksheet(gd_client, key):
  # Get the list of worksheets
  feed = gd_client.GetWorksheetsFeed(key)
  printFeed(feed)
  input = raw_input('\nSelection: ')
  return feed.entry[string.atoi(input)].id.text.rsplit('/', 1)[1]
  
def stringToDictionary(row_data):
  result = {}
  for param in row_data.split():
    name, value = param.split('=')
    result[name] = value
  return result

def main():
  gd_client = gdata.spreadsheet.service.SpreadsheetsService()
  gd_client.email = settings.GDATA_EMAIL
  gd_client.password = settings.GDATA_PASSWORD
  gd_client.source = 'makahiki'
  gd_client.ProgrammaticLogin()

  spreadsheet = promptForSpreadsheet(gd_client)
  worksheet = promptForWorksheet(gd_client, spreadsheet)
  feed = gd_client.GetListFeed(spreadsheet, worksheet)
  updateResources(feed)
  
if __name__ == '__main__':
  main()
