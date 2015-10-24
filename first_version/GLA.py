import sys
import pickle

def novo_stanje(automat):
	automat["br_stanja"] = automat["br_stanja"] + 1
	return automat["br_stanja"] - 1

# nalazi li se ispred znaka neparan broj backslash-ova
def je_operator(izraz, i):
	br = 0
	while i-1>=0 and izraz[i-1]=='\\':
		br = br + 1
		i = i-1
	return br%2 == 0

def pronadi_zagradu(izraz, i):
	broj_zagrada = 0
	i = i+1
	while i < len(izraz):
		if izraz[i] == '(' and je_operator(izraz, i):
			broj_zagrada = broj_zagrada + 1
		elif izraz[i] == ')' and je_operator(izraz, i) and broj_zagrada != 0:
			broj_zagrada = broj_zagrada - 1
		elif izraz[i] == ')' and je_operator(izraz, i) and broj_zagrada == 0:
			return i
		i = i+1
	return -1

def dodaj_epsilon_prijelaz(automat, stanje1, stanje2):
	temp = str(stanje2)
	if str(stanje1)+'|$$' in automat:
		automat[str(stanje1)+'|$$'].append(temp)
	else:
		automat[str(stanje1)+'|$$'] = []
		automat[str(stanje1)+'|$$'].append(temp)
	return 0

def dodaj_prijelaz(automat, stanje1, stanje2, prijelazni_znak):
	if str(stanje1)+'|'+prijelazni_znak in automat:
		automat[str(stanje1)+'|'+prijelazni_znak].append(str(stanje2))
	else:
		automat[str(stanje1)+'|'+prijelazni_znak] = []
		automat[str(stanje1)+'|'+prijelazni_znak].append(str(stanje2))
	return 0

def pretvori(izraz, automat):
	izbori=[]
	prvi_negrupirani = 0
	br_zagrada = 0
	postoji_op_izbora = False
	# !!!!! ako je | prvi znak
	for i in range(len(izraz)):
		if izraz[i]=='(' and je_operator(izraz, i):
			br_zagrada = br_zagrada + 1
		elif izraz[i]==')' and je_operator(izraz, i):
			br_zagrada = br_zagrada - 1
		elif br_zagrada == 0 and izraz[i]=='|' and je_operator(izraz, i):
			izbori.append(izraz[prvi_negrupirani:i])
			postoji_op_izbora = True
			prvi_negrupirani = i+1
	if postoji_op_izbora:
		izbori.append(izraz[prvi_negrupirani:len(izraz)])
	lijevo_stanje = novo_stanje(automat)
	desno_stanje = novo_stanje(automat)
	if postoji_op_izbora:
		for podizraz in izbori:
			privremeno = pretvori(podizraz, automat)
			dodaj_epsilon_prijelaz(automat, lijevo_stanje, privremeno[0])
			dodaj_epsilon_prijelaz(automat, privremeno[1], desno_stanje)
	else:
		prefiksirano = False
		zadnje_stanje = lijevo_stanje
		j = -1
		while j < len(izraz)-1:
			j = j + 1
			if prefiksirano:
				prefiksirano = False
				if izraz[j] == 't':
					prijelazni_znak = '\t'
				elif izraz[j] == 'n':
					prijelazni_znak = '\n'
				elif izraz[j] == '_':
					prijelazni_znak = ' '
				else:
					prijelazni_znak = izraz[j]
				a = novo_stanje(automat)
				b = novo_stanje(automat)
				dodaj_prijelaz(automat, a, b, prijelazni_znak)

			else:
				if izraz[j] == '\\':
					prefiksirano = True
					continue
				if izraz[j] !='(':
					a = novo_stanje(automat)
					b = novo_stanje(automat)
					if izraz[j] == '$':
						dodaj_epsilon_prijelaz(automat, a, b)
					else:
						dodaj_prijelaz(automat, a, b, izraz[j])
				else:
					k = pronadi_zagradu(izraz, j)
					privremeno = pretvori(izraz[j+1:k], automat)
					a = privremeno[0]
					b = privremeno[1]
					j = k

			# provjera ponavljanja
			if j+1<len(izraz) and izraz[j+1]=='*':
				x = a
				y = b
				a = novo_stanje(automat)
				b = novo_stanje(automat)
				dodaj_epsilon_prijelaz(automat, a, x)
				dodaj_epsilon_prijelaz(automat, y, b)
				dodaj_epsilon_prijelaz(automat, a, b)
				dodaj_epsilon_prijelaz(automat, y, x)
				j = j+1

			dodaj_epsilon_prijelaz(automat,zadnje_stanje, a)
			zadnje_stanje = b
		dodaj_epsilon_prijelaz(automat,zadnje_stanje, desno_stanje)
	return (lijevo_stanje, desno_stanje)

def obrada_reg_definicija(reg_def, line):
	regDefName,regExp = line.split(' ')
	for i in reg_def:
		if i in regExp:
			regExp = regExp.replace(i,'('+reg_def[i]+')')
	reg_def[regDefName] = regExp

def obrada_reg_izraza(reg_def, izraz):
	for i in reg_def:
		if i in izraz:
			izraz = izraz.replace(i,'('+reg_def[i]+')')
	return izraz

automat = {}
automat['br_stanja'] = 0
izraz = '\_(\t|$)XYZ'
stanja_automata = {}
reg_def = {}
akcije_konacnih_stanja = {}

prva_faza = True
ulaz = sys.stdin.readlines()

for temp1 in ulaz:
	line = temp1.rstrip()
	if prva_faza:
		check = line.split(' ')[0]
		if check == '%X':
			for i in line.split(' ')[1:]:
				stanja_automata[i] = []
		elif check == '%L':
			prva_faza = False
			continue
		else:
			obrada_reg_definicija(reg_def,line)
	else:
		if line=='{' or line =='}':
			continue
		elif line[0]=='<':
			temp2,regIzraz = line.split('>',1)
			trenutno_stanje = temp2[1:]
			regIzraz = obrada_reg_izraza(reg_def, regIzraz)
			pomVar = pretvori(regIzraz, automat)
			stanja_automata[trenutno_stanje].append(pomVar[0]) #pocetna stanja automata za odredeno STANJE ANALIZATORA
			akcije_konacnih_stanja[pomVar[1]] = []
		else:
			akcije_konacnih_stanja[pomVar[1]].append(line)
pickle.dump(automat, open("analizator/save.p", "wb"))
