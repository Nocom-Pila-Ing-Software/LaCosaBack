.PHONY: run, test, install

run:
	( \
       source venv/bin/activate; \
       export ENV=dev           ; \
       cd src                   ; \
       uvicorn main:app --reload; \
    )

test:
	( \
       source venv/bin/activate; \
       pytest; \
    )

install:
	( \
       python3 -m venv venv; \
       source venv/bin/activate; \
       pip install -r requirements.txt; \
    )
