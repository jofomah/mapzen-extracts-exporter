#!/usr/bin/python2
# -*- coding: utf-8 -*-

import os
import os.path
import argparse
import copy
import geojson
from rdp import rdp
from zipfile import ZipFile

from settings.mapzen_settings import MapZenSettings


argparser = argparse.ArgumentParser(
    description='Exports given MapZen extracts .zip file'
)

argparser.add_argument(
    '--settings', default='settings.yaml',
    help='path to the settings file, default: settings.yaml'
)


def simplify_geometry(geom, tolerance):
    return rdp(geom, epsilon=tolerance)


def convert_to_polygon(multipoly):
    poly = []
    # for pol


def process_feature(feature):
    properties = feature.get('properties')
    geom = feature.get('geometry')
    simplified_geom = copy.deepcopy(geom)
    coords = geom.get('coordinates')
    test = [[[[3.78, 9.28], [-130.91, 1.52], [35.12, 72.234], [3.78, 9.28]]], [[[23.18, -34.29], [-1.31, -4.61], [3.41, 77.91], [23.18, -34.29]]]]
    simplified_geom['coordinates'] = simplify_geometry(test, 0.5)

    return [
        ('osm_id', feature.get('id')),
        ('name', feature.get('name')),
        ('name_en', properties.get('name:en')),
        ('adminlevel', properties.get('admin_level')),
        ('iso3166', properties.get('ISO3166-1')),
        ('geometry', geom),
        ('simplified_geometry', simplified_geom),
        ('is_in', None)
    ]


def import_file(filename, file):
    admin_json = geojson.loads(file.read())
    for feature in admin_json['features']:
        if 'admin_level_2' in filename:
            print process_feature(feature)[6]
            break


def read_zip(filename):
    filenames = []
    zipfile = None

    if filename.endswith(".zip"):
            zipfile = ZipFile(filename, 'r')
            filenames = zipfile.namelist()

    else:
        print "Not a zip file"

    # sort our filenames to enable import of admin levels in ascending order.
    filenames.sort()

    # for each file they have given us
    for name in filenames:
        # if it ends in json, then it is geojson, try to parse it
        if name.endswith('json'):
            # read the file entirely
            print "=== parsing %s" % name

            # if we are reading from a zipfile, read it from there
            if zipfile:
                with zipfile.open(name) as json_file:
                    import_file(name, json_file)

            # otherwise, straight off the filesystem
            else:
                with open(name) as json_file:
                    import_file(name, json_file)


if __name__ == '__main__':
    args = argparser.parse_args()
    config = MapZenSettings(args.settings)
    settings = config.get_settings()

    filename = settings.get('sources').get('data_file')
    admin_levels_range = settings.get('admin_level_range')

    print admin_levels_range
    read_zip(filename)
    # implement main