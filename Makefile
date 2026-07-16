.PHONY: test validate

validate:
	python3 -m drcet_validator.validate examples/synthetic_pass/drcet_submission.json
	python3 -m drcet_validator.validate examples/synthetic_withheld/drcet_submission.json

test:
	python3 -m unittest discover -s tests -v
