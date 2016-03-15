######################################################################
#
# File: utils.py
#
# Copyright 2016 Backblaze Inc. All Rights Reserved.
#
# License https://www.backblaze.com/using_b2_code.html
#
######################################################################

from __future__ import division

import hashlib
import shutil
import tempfile

import six


def choose_part_ranges(content_length, minimum_part_size):
    """
    Returns a list of (offset, length) for the parts of a large file.
    """

    # If the file is at least twice the minimum part size, we are guaranteed
    # to be able to break it into multiple parts that are all at least
    # the minimum part size.
    assert minimum_part_size * 2 <= content_length

    # How many parts can we make?
    part_count = content_length // minimum_part_size
    assert 2 <= part_count

    # All of the parts, except the last, are the same size
    part_size = content_length // part_count
    last_part_size = content_length - (part_size * (part_count - 1))
    assert minimum_part_size <= last_part_size

    # Make all of the parts except the last
    parts = [(i * part_size, part_size) for i in six.moves.range(part_count - 1)]

    # Add the last part
    start_of_last = (part_count - 1) * part_size
    last_part = (start_of_last, content_length - start_of_last)
    parts.append(last_part)

    return parts


def hex_sha1_of_stream(input_stream, content_length):
    """
    Returns the 40-character hex SHA1 checksum of the first content_length
    bytes in the input stream.
    """
    remaining = content_length
    block_size = 1024 * 1024
    digest = hashlib.sha1()
    while remaining != 0:
        to_read = min(remaining, block_size)
        data = input_stream.read(to_read)
        if len(data) != to_read:
            raise ValueError(
                'content_length(%s) is more than the size of the file' % content_length
            )
        digest.update(data)
        remaining -= to_read
    return digest.hexdigest()


class TempDir(object):
    """
    Context manager that creates and destroys a temporary directory.
    """

    def __enter__(self):
        self.dirpath = tempfile.mkdtemp()
        return self.dirpath

    def __exit__(self, exc_type, exc_val, exc_tb):
        shutil.rmtree(self.dirpath)
        return None  # do not hide exception