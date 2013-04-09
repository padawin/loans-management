#!/bin/bash
echo "rm existing db"
rm loan.db

echo "creating db structure"
sqlite3 -init structure.sql loan.db '.quit'

[ ! -f values.sql ] && exit 0

echo "inserting db values"
sqlite3 -init values.sql loan.db '.quit'

