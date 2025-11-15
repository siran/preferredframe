.PHONY: serve clean

serve:
	echo "removing site/"
	rm -r site || true
	git restore .scripts/build_site.py
	echo "building ..."
	touch site/.keep
	echo "serving ..."
	python3 -m http.server -d site 8000

clean:
	rm -rf site
