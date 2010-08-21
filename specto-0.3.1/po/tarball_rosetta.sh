#!/bin/bash
echo "WARNING. This script is only for creating a Rosetta-compliant upload tarball. It assumes that you properly generated the specto.pot template beforehand with generate_template.py"
mkdir po
for i in *
	do cp $i/specto.po po/$i.po
done
cp specto.pot po/specto.pot
tar -cvf rosetta_po.tar.gz po
rm -R po
