from iqoptionapi.stable_api import IQ_Option
import time, json
from datetime import datetime, timedelta
from colorama import init, Fore, Back
from dateutil import tz # pip install python-dateutil
import sys
import fileinput
import os
import getpass

error_password="""{"code":"invalid_credentials","message":"You entered the wrong credentials. Please check that the login/password is correct."}"""

API = IQ_Option
############################################################################################
# Banner do CLI
############################################################################################
def bannerProject():
	os.system("cls")
	print("""


  __        __   __   ______     ______      ______    ______    	 ______      ______    ______     ______    ________
 |  \      /  | |  | |   _  \   |   _  \    /  __  \  |   _  \   	|   _  \    /  __  \  |   _  \   /  __  \  |__    __|
 |   \    /   | |  | |  |_)  |  |  |_)  |  |  |  |  | |  |_)  |  	|  |_)  |  |  |  |  | |  |_)  | |  |  |  |    |  |
 |  |\\\  //|  | |  | |      /   |      /   |  |  |  | |      /   	|      /   |  |  |  | |   _  <  |  |  |  |    |  |
 |  | \\\// |  | |  | |  |\  \__ |  |\  \__ |  `--'  | |  |\  \__ 	|  |\  \__ |  `--'  | |  |_)  | |  `--'  |    |  |
 |__|  \/  |__| |__| | _| `.___|| _| `.___| \______/  | _| `.___|	| _| `.___| \______/  |______/   \______/     |__|
""")
############################################################################################
# Pergunta o Email e Senha do Usuário
############################################################################################
def consultInformation():
	print("""[] Seja bem vindo ao MIRROR ROBOT SINAIS.
[] Por favor, preencha os dados abaixo. \n""")

	print("\n[ LOGIN ] Seu email:", end="")
	email = input()

	print("\n[ LOGIN ] Sua senha:", end="")
	password = getpass.getpass('')


	return email, password
############################################################################################
# Conecta o Usuário com a API
############################################################################################
def apiConnect(email, password):
	API = IQ_Option(email, password)
	while_run_time=10
	check,reason=API.connect()	

	API.change_balance("PRACTICE")

	return API, while_run_time, check, reason
############################################################################################
# Consulta informações do usuário na API (Copiei do MAV mesmo KKKKKKKKKK)
############################################################################################
def perfil():
	perfil = json.loads(json.dumps(API.get_profile_ansyc()))
	
	return perfil
	
	'''
		name
		first_name
		last_name
		email
		city
		nickname
		currency
		currency_char 
		address
		created
		postal_index
		gender
		birthdate
		balance		
	'''
############################################################################################
# Função para pegar o Payout pago no momento pela corretora
############################################################################################
def payout(par, tipo, timeframe = 1):
	if tipo == 'turbo':
		a = API.get_all_profit()
		return int(100 * a[par]['turbo'])

	elif tipo == 'digital':

		API.subscribe_strike_list(par, timeframe)
		while True:
			d = API.get_digital_current_profit(par, timeframe)
			if d != False:
				d = int(d)
				break
			time.sleep(1)
		API.unsubscribe_strike_list(par, timeframe)
		return d
############################################################################################
# Martingale
############################################################################################
def martingale(valor, fatorgale):
	lucro_esperado = valor * fatorgale
	return round(lucro_esperado, 2)
############################################################################################
# Carrega a lista de sinais com o arquivo (sinais.txt)
############################################################################################
def carregar_sinais():
	arquivo = open(caminho, encoding='UTF-8')
	
	lista = arquivo.read()
	arquivo.close

	lista = lista.split('\n')

	for index,a in enumerate(lista):
		if not a.rstrip():
			del lista[index]

	return lista
############################################################################################
# Painel de Controle Principal
############################################################################################
def painelControle(credencialPerfil):
	print("""\n\n

                                                                 
	         _         _      _                    _           _     
	 ___ ___|_|___ ___| |   _| |___    ___ ___ ___| |_ ___ ___| |___ 
	| . | .'| |   | -_| |  | . | -_|  |  _| . |   |  _|  _| . | | -_|
	|  _|__,|_|_|_|___|_|  |___|___|  |___|___|_|_|_| |_| |___|_|___|
	|_|                                                              
""")

	print("""	---------------------------------------------------------------------""")
	print("  			Seja bem vindo " + str(credencialPerfil['name']) + ".	")
	print("  			Você tem um total de $ " + str(round(credencialPerfil['balance'], 2)) + " na sua conta.")
	print("  			Atualmente sua moeda é " + str(credencialPerfil['currency']) + ".\n")
	print("""  			CARREGANDO LISTA DE SINAIS ... """)
	print("""	---------------------------------------------------------------------""")
	time.sleep(5)
############################################################################################
# A opção do menu abaixo do Painel de Controle
############################################################################################
def switchControlPainel():
	print("	PREENCHER ATENTAMENTE SUAS CONFIGURAÇÕES DE GERENCIAMENTO !!!")
	print("			BOAS OPERAÇÕES !!!.\n")
	time.sleep(5)
	switchControlPainelOption = 1 

	return switchControlPainelOption
############################################################################################
# Função para verificar a tendência
############################################################################################
def tendenciadasvelas(qtd_velas, timeframe, par):
	
	velasT = API.get_candles(par, (int(timeframe) * 60), int(qtd_velas),  time.time())
	ultimo = round(velasT[0]['close'], 4)
	primeiro = round(velasT[-1]['close'], 4)

	diferenca = abs( round( ( (ultimo - primeiro) / primeiro ) * 100, 3) )
	tendencia = "call" if ultimo < primeiro and diferenca > 0.01 else "put" if ultimo > primeiro and diferenca > 0.01 else 'Lateralizado'
	return tendencia
############################################################################################
# OPERA NA BINARIA 
# Abre o arquivo sinais.txt e lê, transforma em JSON
############################################################################################
def lerSinaisBinaria(lista):
	json.dumps(carregar_sinais(), indent=1)

	lista = carregar_sinais()

	contLine = 0
	lucrototal = 0
	perdatotal = 0
	win = 0
	loss = 0
	wingale = 0
	doji = 0
	entrou = 0
	#cont = 0
	opcancelada = 0
	stopoperacao = 0

	menu = True
	# Menu----------------------------------------
	while menu: 
		print('	[GERENCIAMENTO] QUAL O VALOR DA MÃO ?', end='')
		valormao = float(input())
		print('	[GERENCIAMENTO] QUANTIDADE DE VELAS PARA ANALISE DE TENDÊNCIA ?', end='')
		qtvela = int(input())
		print('	[GERENCIAMENTO] INFORME O STOP WIN ?', end='')
		stopwin = float(input())
		print('	[GERENCIAMENTO] INFORME O STOP LOSS ?', end='')
		stoploss = float(input())
		print('	[GERENCIAMENTO] PAYOUT MINIMO :', end='')
		ptminimo = int(input())
		print('	[GERENCIAMENTO] QUANTIDADE DE GALE :', end='')
		qtgale = int(input())
		print('	[GERENCIAMENTO] FATOR DO GALE :', end='')
		ftgale = float(input())
		print("""---------------------------------------------------------------------""")
		##---------------------------------------------------------------------------------------
		os.system("cls || clear")
		print('--------------------------------------------\n')
		print('\nQuantidade de Velas => ',qtvela,
			  '\nStop Win $ ',stopwin,
			  '\nStop Loss $ ',stoploss,
			  '\nPayout minimo => ',ptminimo,'%',
			  '\nQuantidade de Gales => ',qtgale,
			  '\nFator do Gale => ',ftgale)
		print('--------------------------------------------\n')
		print('	\nSALVAR AS CONFIGURAÇÕES E COMEÇAR AS OPERAÇÕES: [1] - SIM / [0] - NÃO.')
		opcao = int(input())
		os.system("cls || clear")
		if opcao == 1:
    			menu = False
		else:
    			menu = True
	# Menu----------------------------------------
	# 01/09/2020,21:20,EURUSD,5,PUT	
	#while cont < len(lista): 
	for sinal in lista:
		dados = sinal.split(',')
		data = dados[0]
		hora = dados[1]
		par = str(dados[2])
		timeframe = int(dados[3])
		mao = valormao	#float(dados[4])
		novamao = mao
		direcao = dados[4]
		agora = datetime.now()
		data_atual = agora.strftime('%d/%m/%Y')
		contLine +=1
		while data >= data_atual:
			entrou = 1
			ptoperadora = payout(par,'digital', timeframe)
			dirTendencia = tendenciadasvelas(qtvela, timeframe, par)
			now = datetime.now()
			hora_atual = now.strftime("%H:%M")
			direction = direcao.lower()
			if hora_atual == hora:

				if ptoperadora >= ptminimo and dirTendencia == direction: 
				
					# Contador de Linhas

					os.system("cls || clear")
					print("\n\n[ TUDO CERTO ] Lendo arquivo....\n\n")
					time.sleep(2)
					print('Tendência de Mercado => ',dirTendencia, '\n')
					print("Informações do " + str(contLine) + "º sinal. \n")
					print("Você selecionou para comprar no dia " + str(data) + ".")
					print("Na hora " + str(hora) + ".") 
					print("Com a paridade " + str(par) + ".") 
					print("Duração de " + str(timeframe) + " min.") 
					print("Com $ ",round((mao), 2), " de entrada.") 
					print("Com direção " + str(direction) + ".")
					

					status,id = API.buy(mao, par, direction, timeframe) #API.buy_digital_spot(par, mao, direction, timeframe) <=Digital
																		#API.buy(mao, par, direction, timeframe) <= Binaria
					if status:
						print('Aguardando o final da operação...')
						while True:
							status,lucro = API.check_win_v3_1(id) #API.check_win_v3_1(id) <=Binaria
																#API.check_win_digital_v2(id) <=Digital
							
							if status:	
								if lucro > 0:
									lucrototal += lucro
									win += 1
								elif lucro == 0:
									perdatotal += lucro
									doji += 1
								else:
									perdatotal += lucro
									loss += 1
									# ------------------------------------------MARTIGALE
									mao = novamao
									novaentrada = True
									for i in range(int(qtgale) if int(qtgale) > 0 else 1):
									
										mao = martingale(mao, ftgale)

										if novaentrada == True:			
											status,id = API.buy(mao, par, direction, timeframe)
											if status:
												while True:
													status,lucro = API.check_win_v3_1(id)
													if status:	
														if lucro > 0:
															lucrototal += lucro
															win += 1
															wingale += 1
															novaentrada = False 
															break
														elif lucro == 0:
															perdatotal += lucro
															doji += 1
															break
														else :
															perdatotal += lucro
															loss += 1
															break
											
									# ------------------------------------------MARTIGALE
								break
					stopoperacao = float(lucrototal) + float(perdatotal)
					
					if float(stopoperacao) >= stopwin:
						os.system("cls || clear")
						print('STOP GAIN BATIDO...!!!\n')
						print('***********************************************')
						print('Relatorio de Operações do MIRROR ROBOT SINAIS')
						print(	'Valor de encerramento das Operações $ ',round(stopoperacao, 2),
								'\nGanhos Totais da Operação $ ', round(lucrototal, 2),
								'\nPerdas Totais da Operação $ ', round(perdatotal, 2),
								'\nHoráro de encerramento: ',hora_atual,
								'\nTotal de WIN: ',win,
								'\nTotal de LOSS: ',loss,
								'\nTotal de DOJI: ',doji,
								'\nWIN com GALE: ',wingale,
								'\nOperações canceladas: ',opcancelada)
						print('***********************************************')
						time.sleep(60)
						sys.exit()

					if float(abs(stopoperacao)) >= stoploss:
						os.system("cls || clear")
						print('STOP LOSS BATIDO...!!!\n')
						print('***********************************************')
						print('Relatorio de Operações do MIRROR ROBOT SINAIS')
						print(	'Valor de encerramento das Operações $ ',round(stopoperacao, 2),
								'\nGanhos Totais da Operação $ ', round(lucrototal, 2),
								'\nPerdas Totais da Operação $ ', round(perdatotal, 2),
								'\nHoráro de encerramento: ',hora_atual,
								'\nTotal de WIN: ',win,
								'\nTotal de LOSS: ',loss,
								'\nTotal de DOJI: ',doji,
								'\nWIN com GALE: ',wingale,
								'\nOperações canceladas: ',opcancelada)
						print('***********************************************')
						time.sleep(60)
						sys.exit()
				else:
					os.system("cls || clear")
					print("\n\n[ TUDO CERTO ] Lendo arquivo....\n\n")
					time.sleep(2)
					print('Tendência de Mercado => ',dirTendencia, '\n')
					print("Informações do " + str(contLine) + "º sinal. \n")
					print("Você selecionou para comprar no dia " + str(data) + ".")
					print("Na hora " + str(hora) + ".") 
					print("Com a paridade " + str(par) + ".") 
					print("Duração de " + str(timeframe) + " min.") 
					print("Com $ ",round((mao), 2), " de entrada.") 
					print("Com direção " + str(direction) + ".")	
					print('\n**********************************************************************')
					print('OPERAÇÃO NÃO REALIZADA -> PROBABILIDADE DE 98% DE PERDA !!!\n')
					print('MOTIVOS PARA CANCELAR A OPERAÇÃO !')
					print('PAYOUT PAGO: ',ptoperadora, ' ==> PAYOUT MININO: ',ptminimo)
					print('TENDÊNCIA DO MERCADO: ',dirTendencia, ' ==> DIREÇÃO DA OPERAÇÃO: ',direction)
					print('***********************************************************************')
					time.sleep(5)
					opcancelada +=1
				break
			if entrou == 0:
				print('NÃO FOI POSSÍVEL EXECUTAR A OPERAÇÃO!')
	#	cont += 1
		#break
	
	os.system("cls || clear")
	print("\nFinal da lista de sinais. Obrigado por usar o MIRROR ROBOT SINAIS.\n")
	print('***********************************************')
	print('Relatorio de Operações do MIRROR ROBOT SINAIS')
	print(	'Valor de encerramento das Operações $ ',round(stopoperacao, 2),
			'\nGanhos Totais da Operação $ ', round(lucrototal, 2),
			'\nPerdas Totais da Operação $ ', round(perdatotal, 2),
			'\nHoráro de encerramento: ',hora_atual,
			'\nTotal de WIN: ',win,
			'\nTotal de LOSS: ',loss,
			'\nTotal de DOJI: ',doji,
			'\nWIN com GALE: ',wingale,
			'\nOperações canceladas: ',opcancelada)
	print('***********************************************')
	
	time.sleep(60)
	exit()
############################################################################################
# OPERA NA DIGITAL 
# Abre o arquivo sinais.txt e lê, transforma em JSON
############################################################################################
def lerSinaisDigital(lista):
	json.dumps(carregar_sinais(), indent=1)

	lista = carregar_sinais()

	contLine = 0
	lucrototal = 0
	perdatotal = 0
	win = 0
	loss = 0
	wingale = 0
	doji = 0
	entrou = 0
	cont = 0
	opcancelada = 0
	stopoperacao = 0

	menu = True
	# Menu----------------------------------------
	while menu: 
		print('	[GERENCIAMENTO] QUAL O VALOR DA MÃO ?', end='')
		valormao = float(input())
		print('	[GERENCIAMENTO] QUANTIDADE DE VELAS PARA ANALISE DE TENDÊNCIA ?', end='')
		qtvela = int(input())
		print('	[GERENCIAMENTO] INFORME O STOP WIN ?', end='')
		stopwin = float(input())
		print('	[GERENCIAMENTO] INFORME O STOP LOSS ?', end='')
		stoploss = float(input())
		print('	[GERENCIAMENTO] PAYOUT MINIMO :', end='')
		ptminimo = int(input())
		print('	[GERENCIAMENTO] QUANTIDADE DE GALE :', end='')
		qtgale = int(input())
		print('	[GERENCIAMENTO] FATOR DO GALE :', end='')
		ftgale = float(input())
		print("""---------------------------------------------------------------------""")
		##---------------------------------------------------------------------------------------
		os.system("cls || clear")
		print('--------------------------------------------\n')
		print('\nQuantidade de Velas => ',qtvela,
			  '\nStop Win $ ',stopwin,
			  '\nStop Loss $ ',stoploss,
			  '\nPayout minimo => ',ptminimo,'%',
			  '\nQuantidade de Gales => ',qtgale,
			  '\nFator do Gale => ',ftgale)
		print('--------------------------------------------\n')
		print('	\nSALVAR AS CONFIGURAÇÕES E COMEÇAR AS OPERAÇÕES: [1] - SIM / [0] - NÃO.')
		opcao = int(input())
		os.system("cls || clear")
		if opcao == 1:
    			menu = False
		else:
    			menu = True
	# Menu----------------------------------------
	# 01/09/2020,21:20,EURUSD,5,PUT	
	#while cont < len(lista): 
	for sinal in lista:
		dados = sinal.split(',')
		data = dados[0]
		hora = dados[1]
		par = str(dados[2])
		timeframe = int(dados[3])
		mao = valormao	#float(dados[4])
		novamao = mao
		direcao = dados[4]
		agora = datetime.now()
		data_atual = agora.strftime('%d/%m/%Y')
		contLine +=1
		while data >= data_atual:
			entrou = 1
			ptoperadora = payout(par,'digital', timeframe)
			dirTendencia = tendenciadasvelas(qtvela, timeframe, par)
			now = datetime.now()
			hora_atual = now.strftime("%H:%M")
			direction = direcao.lower()
			if hora_atual == hora_atual:#hora:

				if ptoperadora >= ptminimo and dirTendencia == direction: 
				
					# Contador de Linhas

					os.system("cls || clear")
					print("\n\n[ TUDO CERTO ] Lendo arquivo....\n\n")
					time.sleep(2)
					print('Tendência de Mercado => ',dirTendencia, '\n')
					print("Informações do " + str(contLine) + "º sinal. \n")
					print("Você selecionou para comprar no dia " + str(data) + ".")
					print("Na hora " + str(hora) + ".") 
					print("Com a paridade " + str(par) + ".") 
					print("Duração de " + str(timeframe) + " min.") 
					print("Com $ ",round((mao), 2), " de entrada.") 
					print("Com direção " + str(direction) + ".")
					

					status,id = API.buy_digital_spot(par, mao, direction, timeframe) #API.buy_digital_spot(par, mao, direction, timeframe) <=Digital
					
					if status:
						print('Aguardando o final da operação...')
						while True:
							status,lucro = API.check_win_digital_v2(id) #API.check_win_v3_1(id) <=Binaria
																#API.check_win_digital_v2(id) <=Digital
							
							if status:	
								if lucro > 0:
									lucrototal += lucro
									win += 1
								elif lucro == 0:
									perdatotal += lucro
									doji += 1
								else:
									perdatotal += lucro
									loss += 1
									# ------------------------------------------MARTIGALE
									mao = novamao
									novaentrada = True
									for i in range(int(qtgale) if int(qtgale) > 0 else 1):
									
										mao = martingale(mao, ftgale)

										if novaentrada == True:			
											status,id = API.buy_digital_spot(par, mao, direction, timeframe)
											if status:
												while True:
													status,lucro = API.check_win_digital_v2(id)
													if status:	
														if lucro > 0:
															lucrototal += lucro
															win += 1
															wingale += 1
															novaentrada = False 
															break
														elif lucro == 0:
															perdatotal += lucro
															doji += 1
															break
														else :
															perdatotal += lucro
															loss += 1
															break
											
									# ------------------------------------------MARTIGALE
								break
					stopoperacao = float(lucrototal) + float(perdatotal)
					
					if float(stopoperacao) >= stopwin:
						os.system("cls || clear")
						print('STOP GAIN BATIDO...!!!\n')
						print('***********************************************')
						print('Relatorio de Operações do MIRROR ROBOT SINAIS')
						print(	'Valor de encerramento das Operações $ ',round(stopoperacao, 2),
								'\nGanhos Totais da Operação $ ', round(lucrototal, 2),
								'\nPerdas Totais da Operação $ ', round(perdatotal, 2),
								'\nHoráro de encerramento: ',hora_atual,
								'\nTotal de WIN: ',win,
								'\nTotal de LOSS: ',loss,
								'\nTotal de DOJI: ',doji,
								'\nWIN com GALE: ',wingale,
								'\nOperações canceladas: ',opcancelada)
						print('***********************************************')
						time.sleep(60)
						sys.exit()

					if float(abs(stopoperacao)) >= stoploss:
						os.system("cls || clear")
						print('STOP LOSS BATIDO...!!!\n')
						print('***********************************************')
						print('Relatorio de Operações do MIRROR ROBOT SINAIS')
						print(	'Valor de encerramento das Operações $ ',round(stopoperacao, 2),
								'\nGanhos Totais da Operação $ ', round(lucrototal, 2),
								'\nPerdas Totais da Operação $ ', round(perdatotal, 2),
								'\nHoráro de encerramento: ',hora_atual,
								'\nTotal de WIN: ',win,
								'\nTotal de LOSS: ',loss,
								'\nTotal de DOJI: ',doji,
								'\nWIN com GALE: ',wingale,
								'\nOperações canceladas: ',opcancelada)
						print('***********************************************')
						time.sleep(60)
						sys.exit()
				else:
					os.system("cls || clear")
					print("\n\n[ TUDO CERTO ] Lendo arquivo....\n\n")
					time.sleep(2)
					print('Tendência de Mercado => ',dirTendencia, '\n')
					print("Informações do " + str(contLine) + "º sinal. \n")
					print("Você selecionou para comprar no dia " + str(data) + ".")
					print("Na hora " + str(hora) + ".") 
					print("Com a paridade " + str(par) + ".") 
					print("Duração de " + str(timeframe) + " min.") 
					print("Com $ ",round((mao), 2), " de entrada.") 
					print("Com direção " + str(direction) + ".")	
					print('\n**********************************************************************')
					print('OPERAÇÃO NÃO REALIZADA -> PROBABILIDADE DE 98% DE PERDA !!!\n')
					print('MOTIVOS PARA CANCELAR A OPERAÇÃO !')
					print('PAYOUT PAGO: ',ptoperadora, ' ==> PAYOUT MININO: ',ptminimo)
					print('TENDÊNCIA DO MERCADO: ',dirTendencia, ' ==> DIREÇÃO DA OPERAÇÃO: ',direction)
					print('***********************************************************************')
					time.sleep(5)
					opcancelada +=1
				break
			if entrou == 0:
				print('NÃO FOI POSSÍVEL EXECUTAR A OPERAÇÃO!')
	#	cont += 1
		#break

	os.system("cls || clear")
	print("\nFinal da lista de sinais. Obrigado por usar o MIRROR ROBOT SINAIS.\n")
	print('***********************************************')
	print('Relatorio de Operações do MIRROR ROBOT SINAIS')
	print(	'Valor de encerramento das Operações $ ',round(stopoperacao, 2),
			'\nGanhos Totais da Operação $ ', round(lucrototal, 2),
			'\nPerdas Totais da Operação $ ', round(perdatotal, 2),
			'\nHoráro de encerramento: ',hora_atual,
			'\nTotal de WIN: ',win,
			'\nTotal de LOSS: ',loss,
			'\nTotal de DOJI: ',doji,
			'\nWIN com GALE: ',wingale,
			'\nOperações canceladas: ',opcancelada)
	print('***********************************************')
	
	time.sleep(60)
	exit()
############################################################################################
# Chama as funções acima, isso aqui é a parte do Login e verificação dos Dados
############################################################################################
bannerProject()
email, password = consultInformation()
API, while_run_time, check, reason = apiConnect(email, password)
############################################################################################
# Se a conexão com a API for True, ele obedece esse bloco.
############################################################################################
caminho = os.path.abspath('sinais.txt') # <=== Pega o caminho correto do arquivo 'sinais.txt'

if check:
	os.system("cls || clear")
	print("\n\n[ CONECTADO ] Bem vindo! Aguarde....")
	time.sleep(3)
while True: 
	if API.check_connect()==False:#detect the websocket is close
		print("Tentando reconectar...")
		check,reason=API.connect()         
	if check:
		os.system("cls || clear")
		# Parâmetros pós conectado

		credencialPerfil = perfil()
		painelControle(credencialPerfil)

		time.sleep(2)

		switchControlPainelOption = switchControlPainel()

		if switchControlPainelOption == 1:
			time.sleep(3)
			# Chama a função
			lista = carregar_sinais()
			#lerSinais(lista)
			print('	Escolhar qual tipo de PARES deseja operar => 1 - Digital / 2 - Binaria ', end='')
			escolha = int(input())
			if escolha == 1:
				lerSinaisDigital(lista)
			elif escolha == 2:
				lerSinaisBinaria(lista)
			else:
				print('*** OPÇÃO INVALIDA !!! ***\n')
				print('OBRIGADO POR UTILIZAR O MIRROR ROBOT SINAIS!')		
				time.sleep(10)
				sys.exit()
		
	else:
		if reason==error_password:
			print("Erro! Senha inválida.")
			exit()
		else:
			print("Sem conexão com internet!")
			exit()

else:

	if reason=="[Errno -2] Name or service not known":
		print("Sem conexão com internet!")
	elif reason==error_password:
		print("Erro! Senha inválida.")

