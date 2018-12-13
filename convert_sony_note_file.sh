#!/bin/bash

XSLT_STYLESHEET="sonynotepad2svg.xsl"

if [ "$#" -eq 0 -o "x$1" = "x--help" ]
then
    cat <<EOF
Usage: $0 [[[note-file0] note-file1] ...]

or: $0 --help
to display this help message.

This script is a tool to convert drawings made on a Sony PRS T2 Ebook reader to svg format.

This script call xsltproc with an appropriate xslt stylesheet on each of the files given as argument.
The files are expected to be those of the Sony_Reader/media/notepads folder on the Readers internal memory.

EXAMPLE:
./convert_sony_note_file.sh /media/\$USER/READER/Sony_Reader/media/notepads/*

NOTE:
This script needs the program xsltproc and the stylesheet $XSLT_STYLESHEET to work.

EOF

    exit 0
fi

#check if it is there:
which xsltproc > /dev/null

if [ $? -ne 0 ]
then
    echo "The program xsltproc cannot be found. Please install it or apply the XSLT stylesheet $XSLT_STYLESHEET with a different tool."
    exit 1
fi

for file in $@
do
    if expr match "$file" '.*\.note' > /dev/null
    then
        if grep --quiet 'notepad type="drawing"' "$file"
        then
            outfile="${file%.note}.svg"
            echo "Applying $XSLT_STYLESHEET on $file to produce $outfile"
            xsltproc --output "$outfile" $XSLT_STYLESHEET "$file"
            echo "return value: $?"
        fi
    fi
done

