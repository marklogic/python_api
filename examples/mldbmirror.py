#!/usr/bin/python3
#
# Copyright 2016 MarkLogic Corporation
#
# This script mirrors the contents of a directory into a database. It reads
# a .mldbmirror-config.json file containing configuration data.
#
# For example:
#
# python3 mldbmirror.py [--cred credentials] --host host[:port] [--path path] \
#                       [--upload|--download] database
#

"""Script for uploading or downloading a database"""

from __future__ import unicode_literals, print_function, absolute_import

import argparse
import io
import json
import logging
import os
import re
import sys
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from marklogic.connection import Connection
from requests.auth import HTTPDigestAuth
from marklogic.client.clientutils import ClientUtils
from marklogic.client.documents import Documents
from marklogic.client.bulkloader import BulkLoader
from marklogic.client.transactions import Transactions
from requests_toolbelt import MultipartDecoder

CONFIGFILE = ".mldbmirror-config.json"
BULKTHRESHOLD = 10 * 1000 * 1024      # 10Mb
BATCHSIZE = 1000

class MarkLogicDatabaseMirror:
    def __init__(self):
        self.batchsize = BATCHSIZE
        self.cdir = None
        self.config = None
        self.connection = None
        self.database = None
        self.dryrun = False
        self.hostname = None
        self.list = None
        self.mdir = None
        self.mirror = False
        self.path = None
        self.port = None
        self.regex = []
        self.root = None
        self.threshold = BULKTHRESHOLD
        self.ucdir = None
        self.umdir = None
        self.utils = None
        self.verbose = False
        self.logger = logging.getLogger("marklogic.examples.mldbmirror")

    def connect(self, args):
        """Connect to the server"""
        self.path = os.path.abspath(args['path'])
        self.loadconfig(self.path)

        if args['credentials'] is not None:
            cred = args['credentials']
        else:
            if 'user' in self.config and 'pass' in self.config:
                cred = self.config['user'] + ":" + self.config['pass']
            else:
                cred = None

        try:
            adminuser, adminpass = re.split(":", cred)
        except ValueError:
            raise RuntimeError("Invalid credentials (must be user:pass): {}" \
                                   .format(args['credentials']))

        if args['debug']:
            logging.basicConfig(level=logging.WARNING)
            logging.getLogger("requests").setLevel(logging.INFO)
            logging.getLogger("marklogic").setLevel(logging.DEBUG)

        self.batchsize = args['batchsize']
        self.database = args['database']
        self.dryrun = args['dryrun']
        self.list = args['list']
        self.mirror = args['mirror']
        self.regex = args['regex']
        self.root = args['root']
        self.threshold = args['threshold']
        self.verbose = args['verbose']

        if self.list and self.regex:
            raise RuntimeError("You must not specify both --regex and --list")

        if self.root.endswith("/"):
            self.root = self.root[0:len(self.root)-1]

        if args['hostname'] is None:
            if 'host' in self.config:
                self.hostname = self.config['host']
                if 'port' in self.config:
                    self.port = self.config['port']
                else:
                    self.port = 8000
        else:
            self.hostname = args['hostname'].split(":")[0]
            try:
                self.port = args['hostname'].split(":")[1]
            except IndexError:
                self.port = 8000

        self.connection \
          = Connection(self.hostname, HTTPDigestAuth(adminuser, adminpass), \
                           port=self.port)

        self.utils = ClientUtils(self.connection)

    def upload(self):
        """Upload data"""
        trans = Transactions(self.connection)
        if not self.dryrun:
            trans.set_database(self.database)
            trans.create()
            txid = trans.txid()

        mirror = True
        for name in os.listdir(self.path):
            if not name in ['content', 'metadata', 'ucontent', 'umetadata']:
                mirror = False

        if self.mirror and not mirror:
            raise RuntimeError("Path doesn't point to a mirror directory")

        try:
            if mirror:
                self._upload_mirror(trans)
            else:
                self._upload_directory(trans)
        except KeyboardInterrupt:
            if not self.dryrun:
                trans.rollback()
        except:
            if not self.dryrun:
                trans.rollback()
            raise
        else:
            if not self.dryrun:
                trans.commit()

    def _upload_mirror(self, trans):
        """Internal method for uploading a mirror."""

        upload_map = {}

        # Before we start, make sure the mirror isn't corrupted.
        # We check that every content file has a corresponding metadata file.
        # We don't check the other way around; if you delete some content, you
        # don't have to delete the corresponding metadata.
        print("Reading files from filesystem...")

        cpath = "{}/content".format(self.path)
        mpath = "{}/metadata".format(self.path)
        missing = []
        if os.path.exists(cpath):
            files = self.scan(cpath, root=cpath)
            for check in files:
                if os.path.exists(mpath + check):
                    upload_map[check] = {"content": cpath + check, \
                                             "metadata": mpath + check}
                else:
                    missing.append(mpath + check)

        cpath = "{}/ucontent".format(self.path)
        mpath = "{}/umetadata".format(self.path)
        if os.path.exists(cpath):
            files = self.scan(cpath, root=cpath)
            for check in files:
                if os.path.exists(mpath + check):
                    upload_map[check] = {"content": cpath + check, \
                                             "metadata": mpath + check, \
                                             "uuid": True}
                else:
                    missing.append(mpath + check)

        if missing:
            print("Missing files:", missing)
            raise RuntimeError("Mirror corrupt")

        self._upload_map(trans, upload_map)

    def _upload_directory(self, trans):
        """Internal method for uploading a directory."""

        print("Reading files from filesystem...")
        allfiles = self.scan(self.path)

        if self.regex:
            files = self.regex_filter(allfiles)
        elif self.list:
            files = self.list_filter(allfiles)
        else:
            files = allfiles

        if len(files) != len(allfiles):
            print("Selected {} of {} files from filesystem..."\
                      .format(len(files),len(allfiles)))

        upload_map = {}
        for check in files:
            upload_map[check] = {"content": self.path + check}

        self._upload_map(trans, upload_map)

    def _upload_map(self, trans, upload_map):
        """Upload from an internally constructed map."""
        print("Reading URIs from server...")
        uris = self.utils.uris(self.database)
        urihash = {}
        for uri in uris:
            urihash[uri] = 1

        print("Getting timestamps from server...")
        stamps = self.get_timestamps(list(upload_map))
        if not stamps:
            print("No timestamps, assuming all files newer.")
        else:
            uptodate = []
            for key in upload_map:
                if key in stamps:
                    source = upload_map[key]['content']
                    statinfo = os.stat(source)
                    stamp = stamps[key]
                    stamp = stamp[0:len(stamp)-1] + "+0000"
                    stamp = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S%z")
                    if statinfo.st_mtime < stamp.timestamp():
                        uptodate.append(key)

            if uptodate:
                print("{} documents are up-to-date...".format(len(uptodate)))
                for key in uptodate:
                    del upload_map[key]
                    del urihash[key]    # remove it from this list so we don't delete it

        upload_count = len(upload_map)
        print("Uploading {} files...".format(upload_count))

        docs = Documents(self.connection)

        bulk = BulkLoader(self.connection)
        bulk.set_database(self.database)
        bulk.set_txid(trans.txid())

        files = list(upload_map.keys())
        done = not files
        upload_size = 0
        ulcount = 0
        while not done:
            doc = files.pop(0)
            done = not files

            docs.clear()

            source = upload_map[doc]['content']
            target = self.root + doc

            body_content_type = "application/octet-stream"

            if 'metadata' in upload_map[doc]:
                metasource = upload_map[doc]['metadata']
                metaxml = ET.parse(metasource)
                root = metaxml.getroot()

                txml = root \
                  .find("{http://marklogic.com/ns/mldbmirror/}content-type")
                if txml is not None:
                    body_content_type = txml.text
                    root.remove(txml)

                if 'uuid' in upload_map[doc] and upload_map[doc]['uuid']:
                    txml = root \
                      .find("{http://marklogic.com/ns/mldbmirror/}uri")
                    if txml is None:
                        raise RuntimeError("No URI provided in metadata.")
                    else:
                        target = txml.text
                        root.remove(txml)

                text = ET.tostring(root, encoding="unicode", method="xml")
                docs.set_metadata(text, "application/xml")
            else:
                metasource = None
                collections = []
                permissions = []

                for cfg in self.config["config"]:
                    if type(cfg["match"]) is list:
                        matches = cfg["match"]
                    else:
                        matches = [cfg["match"]]

                    for match in matches:
                        if re.match(match, target):
                            if "content-type" in cfg:
                                body_content_type = cfg["content-type"]
                            if "permissions" in cfg:
                                permissions = cfg["permissions"]
                            if "permissions+" in cfg:
                                permissions = permissions + cfg["permissions+"]
                            if "collections" in cfg:
                                collections = cfg["collections"]
                            if "collections+" in cfg:
                                collections = collections + cfg["collections+"]

                docs.set_collections(collections)
                docs.set_permissions(None)
                for perm in permissions:
                    for key in perm:
                        docs.add_permission(key, perm[key])

            if target in urihash:
                del urihash[target]

            ulcount += 1
            statinfo = os.stat(source)
            upload_size += statinfo.st_size

            docs.set_uri(target)

            datafile = open(source, "rb")
            docs.set_content(datafile.read(), body_content_type)
            datafile.close()

            bulk.add(docs)

            if self.verbose:
                print("-> {}".format(target))

            if upload_size > self.threshold:
                perc = (float(ulcount) / upload_count) * 100.0
                print("{0:.0f}% ... {1} files, {2} bytes" \
                          .format(perc, bulk.size(), upload_size))
                if self.dryrun:
                    bulk.clear_content()
                else:
                    bulk.post()
                upload_size = 0

        if bulk.size() > 0:
            perc = (float(ulcount) / upload_count) * 100.0
            print("{0:.0f}% ... {1} files, {2} bytes" \
                      .format(perc, bulk.size(), upload_size))
            if self.dryrun:
                bulk.clear_content()
            else:
                bulk.post()

        docs.clear()
        docs.set_txid(trans.txid())
        docs.set_database(self.database)
        delcount = 0
        for uri in urihash:
            if uri.startswith(self.root):
                if self.verbose:
                    print("DEL {}".format(uri))
                docs.add_uri(uri)
                delcount += 1

        if delcount > 0:
            if self.regex or self.list:
                print("Limited download, not deleting {} files..." \
                          .format(delcount))
            else:
                print("Deleting {} URIs...".format(delcount))
                if not self.dryrun:
                    docs.delete()

    def download(self):
        """Download data"""
        trans = Transactions(self.connection)
        if not self.dryrun:
            trans.set_database(self.database)
            trans.create()

        try:
            if self.mirror:
                self._download_mirror(trans)
            else:
                self._download_directory(trans)
        except KeyboardInterrupt:
            if not self.dryrun:
                trans.rollback()
        except:
            if not self.dryrun:
                trans.rollback()
            raise
        else:
            if not self.dryrun:
                trans.commit()

    def _download_mirror(self, trans):
        """Download mirror"""
        if not os.path.isdir(self.path):
            print("Target directory must exist: {}".format(self.path))
            sys.exit(1)

        if os.listdir(self.path):
            print("Target directory must be empty: {}".format(self.path))
            sys.exit(1)

        self.logger.debug("Starting download_mirror")

        print("Reading URIs from server...")
        alluris = self.utils.uris(self.database, self.root)

        if self.regex:
            uris = self.regex_filter(alluris, download=True)
        elif self.list:
            uris = self.list_filter(alluris, download=True)
        else:
            uris = alluris

        cdir = "{}/content".format(self.path)
        mdir = "{}/metadata".format(self.path)
        ucdir = "{}/ucontent".format(self.path)
        umdir = "{}/umetadata".format(self.path)
        down_map = {}

        for uri in uris:
            if self.can_store_on_filesystem(uri):
                down_map[uri] = {"content": cdir + uri, \
                                     "metadata": mdir + uri}
            else:
                pos = uri.rfind(".")
                if pos > 0:
                    ext = uri[pos:]
                else:
                    ext = ""

                # Put some path segments at the front so that we don't wind up
                # with a single directory containing a gazillion files
                fnuuid = str(uuid.uuid4())
                fnuuid = fnuuid[0:2] + "/" + fnuuid[2:4] + "/" + fnuuid[4:]
                filename = "/{}{}".format(fnuuid, ext)

                down_map[uri] = {"content": ucdir + filename, \
                                     "metadata": umdir + filename, \
                                     "uuid": True}

        self._download_map(trans, down_map)

    def _download_directory(self, trans):
        """Download directory"""
        if not os.path.isdir(self.path):
            print("Target directory must exist: {}".format(self.path))
            sys.exit(1)

        self.logger.debug("Starting download_directory")

        print("Reading URIs from server...")
        alluris = self.utils.uris(self.database, self.root)

        if self.regex:
            uris = self.regex_filter(alluris, download=True)
        elif self.list:
            uris = self.list_filter(alluris, download=True)
        else:
            uris = alluris

        print("Getting timestamps from server...")
        stamps = self.get_timestamps(alluris)

        down_map = {}

        for uri in uris:
            if not self.can_store_on_filesystem(uri):
                raise RuntimeError("Cannot save URI:", uri)

            down_map[uri] = {"content": self.path + uri}
            if uri in stamps:
                down_map[uri]['timestamp'] = stamps[uri]

        self._download_map(trans, down_map)

    def _download_map(self, trans, down_map):
        """Download from an internally constructed map."""
        filehash = {}
        if not self.mirror:
            print("Reading files from filesystem...")
            for path in self.scan(self.path):
                filehash[path] = 1

        self.logger.debug("Downloading map")
        self.logger.debug(down_map)

        download_count = len(down_map)

        print("Downloading {} documents...".format(download_count))

        docs = Documents(self.connection)
        docs.set_database(self.database)
        docs.set_txid(trans.txid())
        docs.set_format('xml')
        docs.set_accept("multipart/mixed")
        if self.mirror:
            docs.set_categories(['content', 'metadata'])
        else:
            docs.set_category('content')

        dlprog = 0
        dlcount = 0
        for uri in down_map.keys():
            dlcount += 1
            docs.add_uri(uri)

            if uri in filehash:
                del filehash[uri]

            if dlcount >= self.batchsize:
                dlprog += dlcount
                perc = (float(dlprog) / download_count) * 100.0
                print("{0:.0f}% ... {1}/{2} files" \
                          .format(perc, dlprog, download_count))

                self._download_batch(docs, down_map)
                docs.clear()
                docs.set_database(self.database)
                docs.set_txid(trans.txid())
                docs.set_format('xml')
                docs.set_accept("multipart/mixed")
                if self.mirror:
                    docs.set_categories(['content', 'metadata'])
                else:
                    docs.set_category('content')
                dlcount = 0

        if dlcount > 0:
            perc = (float(dlcount) / download_count) * 100.0
            print("{0:.0f}% ... {1} files".format(perc, dlcount))
            self._download_batch(docs, down_map)

        delfiles = []
        for path in filehash.keys():
            delfiles.append(self.path + path)

        if not self.mirror and delfiles:
            if self.regex or self.list:
                print("Limited download, not deleting {} files..." \
                          .format(len(delfiles)))
            else:
                print("Deleting {} files...".format(len(delfiles)))
                if not self.dryrun:
                    for path in delfiles:
                        os.remove(path)
                    self._remove_empty_dirs(self.path)

    def _download_batch(self, docs, down_map):
        """Download a batch of files"""
        if self.dryrun:
            return

        self.logger.debug("Downloading batch")
        self.logger.debug(docs)

        resp = docs.get()
        decoder = MultipartDecoder.from_response(resp)

        self.logger.debug("Downloaded {} bytes in {} parts" \
                              .format(len(resp.text), len(decoder.parts)))

        meta_part = None
        content_part = None
        splitregex = re.compile(';\\s*')

        if not decoder.parts:
            raise RuntimeError("FAILED TO GET ANY PARTS!?")

        for mimepart in decoder.parts:
            disp = mimepart.headers[b'Content-Disposition'].decode('utf-8')
            if 'category=metadata' in disp:
                if meta_part is not None:
                    raise RuntimeError("More than one metadata part!?")
                meta_part = mimepart
            else:
                content_part = mimepart

                disp = content_part.headers[b'Content-Disposition'].decode('utf-8')
                dispositions = splitregex.split(disp)
                filename = None
                for disp in dispositions:
                    if disp.startswith("filename="):
                        filename = disp[10:len(disp)-1]

                body_content_type = content_part.headers[b'Content-Type'].decode('utf-8')

                if filename is None:
                    raise RuntimeError("Multipart without filename!?")

                #print("FN:",filename)

                last_modified = None
                stanza = down_map[filename]
                if meta_part is not None:
                    last_modified = self._store_metadata(meta_part, down_map[filename], \
                                                             body_content_type, filename)
                    if last_modified is not None:
                        stanza['timestamp'] = last_modified
                self._store_content(content_part, stanza)
                meta_part = None
                content_part = None

    def _store_metadata(self, meta_part, stanza, body_content_type, uri):
        # fromstring() doesn't return an an xml.etree.ElementTree and
        # doesn't have a write method that we're going to need later
        fakeio = io.StringIO(meta_part.content.decode('utf-8'))
        metaxml = ET.parse(fakeio)
        root = metaxml.getroot()
        fakeio.close()

        last_mod = None
        properties = root.find('{http://marklogic.com/xdmp/property}properties')
        if properties is not None:
            last_mod = properties.find('{http://marklogic.com/xdmp/property}last-modified')
            if last_mod is not None:
                last_mod = last_mod.text

        txml = ET.Element("{http://marklogic.com/ns/mldbmirror/}content-type")
        txml.text = body_content_type
        root.insert(0, txml)

        metafn = stanza['metadata']
        if 'uuid' in stanza:
            txml = ET.Element("{http://marklogic.com/ns/mldbmirror/}uri")
            txml.text = uri
            root.insert(1, txml)

        if not self.dryrun:
            if not os.path.exists(os.path.dirname(metafn)):
                os.makedirs(os.path.dirname(metafn))

            metaxml.write(metafn)
        else:
            if self.verbose:
                print("Meta:", metafn)

        return last_mod

    def _store_content(self, content_part, stanza):
        contfn = stanza['content']

        #print(stanza)

        stamp = None
        if 'timestamp' in stanza:
            stamp = stanza['timestamp']

        if stamp is not None:
            stamp = stamp[0:len(stamp)-1] + "+0000"
            stamp = datetime.strptime(stamp, "%Y-%m-%dT%H:%M:%S%z")

        if not self.dryrun:
            if not os.path.exists(os.path.dirname(contfn)):
                os.makedirs(os.path.dirname(contfn))

            dataf = open(contfn, 'wb')
            dataf.write(content_part.content)
            dataf.close()
            if stamp is not None:
                os.utime(contfn, (stamp.timestamp(), stamp.timestamp()))
        else:
            if self.verbose:
                print("Data:", contfn)

    def can_store_on_filesystem(self, filename):
        """Returns true if the filename can be stored.

        Many MarkLogic URIs (e.g, /path/to/file.xml) can be stored on the filesystem.
        Many others (e.g., http://...) can not. This method returns true iff the
        filename is a legitimate filesystem name.

        N.B. If a filename does not begin with "/", it cannot be stored on the
        filesystem because if it's ever uploaded, it'll get a leading /.
        """
        if (not filename.startswith("/")) or ("//" in filename) \
          or (":" in filename) or ('"' in filename) or ('"' in filename) \
          or ("\\" in filename):
            return False
        else:
            return True

    def list_filter(self, alluris, download=False):
        if self.list:
            uris = []
            print("Reading list from {}...".format(self.list))
            listfile = open(self.list, "r")
            for line in listfile:
                line = line.rstrip()
                if line in alluris:
                    if self.dryrun and self.verbose:
                        print("INCL:", line)
                    uris.append(line)
                else:
                    print("Not available:", line)

            if download:
                cat = "files"
            else:
                cat = "URIs"

            print("File list reduced {} {} to {}." \
                      .format(len(alluris), cat, len(uris)))

            return uris
        else:
            return alluris

    def get_timestamps(self, uris):
        """Get the database timestamp for these URIs"""
        stamps = []
        for seg in self._chunks(uris, 10):
            stamps += self.utils.last_modified(self.database, seg)

        # FIXME: make the XQuery return a single object
        stamp_hash = {}
        for stamp in stamps:
            stamp_hash[stamp["uri"]] = stamp["dt"]
        return stamp_hash

    def _chunks(self, uris, n):
        """Chop a long list into a list of lists"""
        for index in range(0, len(uris), n):
            yield uris[index:index+n]

    def regex_filter(self, alluris, download=False):
        if self.regex:
            uris = []
            cregex = []
            for exp in self.regex:
                cregex.append(re.compile(exp))

            for uri in alluris:
                match = False
                for exp in cregex:
                    match = match or exp.match(uri)

                if match:
                    if self.dryrun and self.verbose:
                        print("INCL:", uri)
                    uris.append(uri)
                else:
                    if self.dryrun and self.verbose:
                        print("EXCL:", uri)

            if download:
                cat = "URIs"
            else:
                cat = "files"

            if len(self.regex) == 1:
                print("Regex filter reduced {} {} to {}." \
                          .format(len(alluris), cat, len(uris)))
            elif len(self.regex) > 1:
                print("{} regex filters reduced {} {} to {}." \
                          .format(len(self.regex), cat, len(alluris), len(uris)))

            return uris
        else:
            return alluris

    def _remove_empty_dirs(self, directory):
        """Remove empty directories recursively"""
        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isdir(path):
                self._remove_empty_dirs(path)

        if not os.listdir(directory):
            os.rmdir(directory)

    def scan(self, directory, root=None, files=None):
        """Scan a directory recursively, returning all of the files"""
        if files is None:
            files = []
        if root is None:
            root = directory
        skip = "/" + CONFIGFILE

        for name in os.listdir(directory):
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                if not path.endswith(skip):
                    path = path[len(root):]
                    files.append(path)
            else:
                self.scan(path, root, files)
        return files

    def loadconfig(self, path):
        """Load the configuration file that determines document properties"""
        config = {}
        localconfig = {}

        home = os.path.expanduser("~")
        cfgfile = home + "/" + CONFIGFILE
        if os.path.isfile(cfgfile):
            data = open(cfgfile).read()
            config = json.loads(data)

        cfgfile = path + "/" + CONFIGFILE
        if os.path.isfile(cfgfile):
            data = open(cfgfile).read()
            localconfig = json.loads(data)

        for key in localconfig:
            if key != 'config':
                config[key] = localconfig[key]

        if 'config' not in config:
            config['config'] = []

        if 'config' in localconfig:
            config['config'] = config["config"] + localconfig['config']

        self.config = config

def main():
    """Main"""
    mirror = MarkLogicDatabaseMirror()

    parser = argparse.ArgumentParser(
        description="MarkLogic database mirror")

    parser.add_argument('--debug', action='store_true',
                        help='Turn on debug logging')
    parser.add_argument('--verbose', action='store_true',
                        help='Print more messages')
    parser.add_argument('--mirror', action='store_true',
                        help='Download a mirror of the database')
    parser.add_argument('--dryrun', action='store_true',
                        help='Print what would be done, but don\'t do anything')
    parser.add_argument('--credentials',
                        metavar='USER:PASS',
                        help='The user:pass for the host')
    parser.add_argument('--hostname', metavar='host',
                        help='The MarkLogic host')
    parser.add_argument('--path', default='.', metavar="path",
                        help='The filesystem path from which to mirror')
    parser.add_argument('--root', default='/', metavar="root",
                        help='The module root to which you want to mirror')
    parser.add_argument('--upload', action='store_true',
                        help='Upload local path to database?')
    parser.add_argument('--threshold', type=int, default=BULKTHRESHOLD,
                        help='Size of upload batches (bytes)')
    parser.add_argument('--batchsize', type=int, default=BATCHSIZE,
                        help='Size of download batches (number of files)')
    parser.add_argument('--regex', action='append',
                        help='Regex(es) to match for URIs')
    parser.add_argument('--list', default=None,
                        help='File containing list of filenames/URIs to transfer')
    parser.add_argument('--download', action='store_true',
                        help='Download database to local path?')
    parser.add_argument('database',
                        help='The database to mirror into')

    args = vars(parser.parse_args())

    if args['upload'] == args['download']:
        print("Exactly one of --upload or --download must be specified.")
        sys.exit(1)

    mirror.connect(args)

    if args['upload']:
        mirror.upload()
    else:
        mirror.download()

    if args['dryrun']:
        print("(DRY RUN)")

if __name__ == '__main__':
    main()
