export PYTHONPATH=`pwd`:$PYTHONPATH
sphinx-apidoc gillespy --full -o build_docs -H 'GillesPy' -A 'John H. Abel, Brian Drawert, Andreas Hellander' -V '0.1'
cd build_docs && make html
sed -i '' 's/gillespy.gillespy/gillespy/g' _build/html/*.html
cp -r _build/html/* ../docs/
