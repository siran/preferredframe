.PHONY: serve clean

serve:
	echo "removing site/"
	rm -r site || true
	echo "building ..."
	.scripts/build_site/build_site.py
	echo "serving ..."
	python3 -m http.server -d site 8000

clean:
	rm -rf site
