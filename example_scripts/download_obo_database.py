#!/usr/bin/env python

import os
import re
import shutil
import subprocess
import sys
import tempfile
from argparse import ArgumentParser

"""Download all versions of the psidev OBO for mzML files"""

CVS_SERVER = ":pserver:anonymous:" "@psidev.cvs.sourceforge.net:/cvsroot/psidev"


class CVSClient(object):
    def __init__(self, root, client_dir=None, verbose=False):
        self.root = root

        self.client_dir = client_dir
        self.cleanup = False
        self.verbose = verbose

    def __enter__(self):
        if not self.client_dir or not os.path.isdir(self.client_dir):
            self.client_dir = tempfile.mkdtemp(prefix="cvs")
            self.cleanup = True

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.cleanup:
            shutil.rmtree(self.client_dir, ignore_errors=True)

    def __call__(self, *args, **kwargs):
        command = ["cvs", "-d" + self.root] + list(args)

        # Default args for subprocess
        processkwargs = dict(cwd=self.client_dir)

        if not self.verbose:
            command.insert(1, "-Q")
            processkwargs["stderr"] = open(os.devnull, "w")

        # Override defaults with provided args
        processkwargs.update(kwargs)

        if self.verbose:
            print(">>> " + " ".join(command), file=sys.stderr)

        return subprocess.check_output(command, **processkwargs)


def get_version_map(cvs):
    filename = "psi/psi-ms/mzML/controlledVocabulary/psi-ms.obo"

    # Download the OBO file and get its revision log
    cvs("-z3", "co", filename)
    revisions = parse_revisions(cvs("-z3", "log").split("\n"))

    version_map = {}
    for revision in revisions:
        file_at_revision = cvs("-z3", "co", "-p", "-r", revision, filename)
        version = parse_version(file_at_revision)

        # Revisions go from newest to oldest, so if a version exists in the
        # dictionary, it's already the newest revision of that version
        if version and version not in version_map:
            version_map[version] = file_at_revision

    return version_map


def parse_revisions(revision_log):
    revisions = []
    revision_regexp = re.compile(r"revision (\d+\.\d+)")
    for line in revision_log:
        match = revision_regexp.match(line)
        if match:
            revisions.append(match.group(1))
    return revisions


def parse_version(file_string):
    version_regexp = re.compile(r"remark:\s+version: (\d+\.\d+\.\d+\S*)")
    version = None
    for line in file_string.split("\n"):
        match = version_regexp.match(line)
        if match:
            version = match.group(1)

    return version


def save_versions(version_map, destination):
    for version, file_at_version in version_map.iteritems():
        destination_path = os.path.join(destination, "psi-ms-{0}.obo".format(version))
        with open(destination_path, "w+") as destination_file:
            destination_file.write(file_at_version)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("destination", help="directory into which the OBO files go")
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="show extra logging information"
    )
    args = parser.parse_args()

    # Sanity checking
    assert os.path.isdir(args.destination), "destination must be a valid directory"

    with CVSClient(CVS_SERVER, verbose=args.verbose) as cvs:
        cvs("login")
        revision_map = get_version_map(cvs)
        save_versions(revision_map, args.destination)

# vim: ts=4:sw=4:sts=4
