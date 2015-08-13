import csv
import re

from django.core.management.base import BaseCommand

def clean_advance_reservation(text):
    """ The advance reservation field identifies whether or not advance
    reservations are required to use these facilities (day use areas). If there
    is not recorded answer (blank) we default to 'no reservation required'.
    Returns 'True' if reservation required, False otherwise. """

    text = text.lower()
    if text in ['yes']:
        return True
    if 'registration required' in text:
        return True
    if 'tour request form' in text:
        return True
    if 'call ahead' in text:
        return True
    return False
    
def clean_agency(agency_name):
    """ Clean up the agency names in the dataset to make them consistent. """

    agency_name = agency_name.strip()
    if 'Oceanic' in agency_name:
        return 'National Oceanic and Atmospheric Administration'
    return agency_name

def replace(f):
    exists = [
        'picnic', 'trail', 'day use', 'beach', 'fishing', 'lake', 'hiking']

    for word in exists:
        if word in f:
            return word

    replacements = [
        ('bicyc', 'bicycling'),
        ('bathroom', 'restrooms'),
        ('observation', 'observation area'),
        ('historic', 'historic structures'),
        ('coast', 'coastal areas'),
        ('outdoor classroom', 'outdoor classroom'),
        ('outdoor education', 'outdoor classroom'),
        ('outdoor school', 'outdoor classroom'),
        ('environmental education', 'environmental education facility'),
        (' ee ', ''),
        (' wetl', ''),
        ('advance reservation', ''),
        ('mobile game', ''),
        (' isl', ''),
        ('bilingual', ''),
        ('education guide', ''),
        ('s live', ''),
        ('hmu', ''),
    ]

    for key, rephrased in replacements:
        if key in f:
            return rephrased

    if 'visitor' in f or 'contact station' in f:
        return 'visitor center'
    elif 'auto' in f or 'driving' in f:
        return 'auto tour route'
    elif 'river' in f and not 'museum' in f:
        return 'river'
    elif ' water ' in f or 'waterway' in f:
        return 'water access'
    elif 'camp' in f and not 'spy' in f and not 'primitive' in f:
        return 'camping'
    else:
        return f


def clean_youth_facilities(facilities):
    
    facilities = facilities.lower()
    facilities = re.split('[;,]|and|&', facilities)
    facilities = [f.strip() for f in facilities]
    facilities = [f.replace('(a.k.a.', '') for f in facilities]
    facilities = [replace(f) for f in facilities]

    return facilities

def process_site(row):
    facilities = clean_youth_facilities(row['YOUTH_FACI'])
    for f in facilities:
        print(f)

def read_site_list(filename):
    with open(filename, 'r', encoding='latin-1') as site_csv:
        site_reader = csv.DictReader(site_csv, delimiter=',', quotechar='"')
        for l in site_reader:
            process_site(l)

class Command(BaseCommand):
    """ Read and import a list of field trip sites (also known as the FICOR
    list)."""

    def add_arguments(self, parser):
        parser.add_argument('filename', nargs=1)

    def handle(self, *args, **options):
        filename = options['filename'][0]
        read_site_list(filename)
