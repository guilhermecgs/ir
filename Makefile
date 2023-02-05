export DROPBOX_FILE_LOCATION=/Finance/GCGS/export_operacoes_gcgs.txt
export DROPBOX_API_KEY=jOznaw_xxxxxxxxxxxxxxxxxxxxtkw9ox_a9I_8-_aU2xw1xxxxxxxxxxKWek69Z
export SMTP_USER=smtp_user@abc.com
export SMTP_PASSWORD=smtp_pass
export SEND_TO=emaildestinatario@abc.com
export SMTP_SERVER=smtp.elasticemail.com
export SMTP_PORT=2525
export CPF=00098765434
export SENHA_CEI=minha_senha_cei

deps:
	pip install -r requirements.txt

reqs:
	pip freeze > requirements.txt

coverage:
	python coverage_test.py

test:
	pytest

run:
	- python ./ir.py --do importar_negociacoes
	- python ./ir.py --do calculo_ir --numero_de_meses 99
