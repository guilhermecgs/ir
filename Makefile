export DROPBOX_FILE_LOCATION=/Finance/GCGS/export_operacoes_gcgs.txt
export DROPBOX_API_KEY=jOznaw_xxxxxxxxxxxxxxxxxxxxtkw9ox_a9I_8-_aU2xw1xxxxxxxxxxKWek69Z
export GMAIL_FROM=emailremetente@gmail.com
export GMAIL_PASSWORD=minha_senha_gmail
export SEND_TO=emaildestinatario@gmail.com
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
	- python ./ir.py --do busca_trades_e_faz_merge_operacoes
	- python ./ir.py --do calculo_ir --numero_de_meses 99
