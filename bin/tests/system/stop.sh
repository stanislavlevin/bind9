#!/bin/sh
#
# Copyright (C) 2000  Internet Software Consortium.
# 
# Permission to use, copy, modify, and distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND INTERNET SOFTWARE CONSORTIUM DISCLAIMS
# ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES
# OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL INTERNET SOFTWARE
# CONSORTIUM BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL
# DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR
# PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS
# SOFTWARE.

#
# Stop name servers.
#

test $# -gt 0 || { echo "usage: $0 test-directory" >&2; exit 1; }

cd $1

for d in ns*
do
     pidfile="$d/named.pid"
     if [ -f $pidfile ]; then
        kill -TERM `cat $pidfile`
     fi
done

for d in lwresd*
do
     pidfile="$d/lwresd.pid"
     if [ -f $pidfile ]; then
        kill -TERM `cat $pidfile`
     fi
done

sleep 5

for d in ns*
do
     pidfile="$d/named.pid"
     if [ -f $pidfile ]; then
        kill -KILL `cat $pidfile`
     fi
done

for d in lwresd*
do
     pidfile="$d/lwresd.pid"
     if [ -f $pidfile ]; then
        kill -KILL `cat $pidfile`
     fi
done

sleep 10

