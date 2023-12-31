.PHONY: run, test, install

run:
	( \
      rm -rf src/db.sqlite; \
       . venv/bin/activate; \
       export ENV=dev           ; \
       cd src                   ; \
       uvicorn main:app --reload; \
    )

test:
	( \
       . venv/bin/activate; \
       pytest -s; \
    )

install:
	( \
       python3 -m venv venv; \
       . venv/bin/activate; \
       pip install -r requirements.txt; \
    )
