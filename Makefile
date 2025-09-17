.PHONY: serve clean

serve:
	.scripts/build_site.py
	python3 -m http.server -d site 8000

clean:
	rm -rf site
