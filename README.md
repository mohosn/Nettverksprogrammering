# Network-Programming_Prosjekt


Milepæl 1 

Dere skal i første milepæl programmere en webtjener med programmeringspråket C. Ta gjerne utgangspunkt i eksemplet hallotjener. 

Funksjonskrav 

1.	Tjeneren skal leverere "as-is"-filer. 

"As-is"-filer er filer som inneholder både http-hode og http-kropp, og sendes "som de er", uten å legge til eller trekke fra noe. Enklere blir det ikke: Tjeneren åpner fila og skriver den til til socket'en som er forbundet med klienten. 
Disse filene skal ende på .asis og skal inneholde både http-hode og http-kropp, som i eksemplet under. 

./eksempler/index.asis 
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 16
Hallo verden :-)

2.	Dersom det kommer en http-forespørsel etter en fil som ikke finnes, eller til en fil av en type som ikke støttes, så skal korrekt http-feilmeling returneres til klienten.
3.	Siden tjeneren skal være demonisert (se Sikkerhets-/robusthets-krav under), så har den ingen kontroll-terminal å skrive ut til. 
Åpne derfor en fil og koble den til stderr, slik at du kan få skrevet ut feil- og avlusnings-info. 

Sikkerhets-/robusthets-krav

1.	Programmet skal ikke binde seg til porten en gang pr. forespørsel, men kun ved programstart.
2.	Hver klient-forsepørsel skal behandles i en egen tråd eller prosess.
3.	Tjeneren skal være demonisert slik at den er uavhengig av kontroll-terminal.
4.	Tjeneren den lytte på port 80 uten at den kjører som brukeren root.
5.	Katalogen som inneholder filene som skal være tilgjengelige via http skal befinne seg på web root. Tjener-prosessene skal også (ved hjelp av chroot(2)) ha endret sin rot-katalog til denne denne webroten..
Merk at punktene 1. og 2. allerede er tilfrestillt i hallotjener. 



Milepæl 2 

•  Utvid tjeneren fra MP1, slik at den (i tillegg til asis-filer) kan levere alle filtyper som er oppført i flien /etc/mime.types. 
Identifiseringen av type skal gjøres ved hjelp av filendelsen. Hvis f.eks. fila ender på .txt så blir Content-type satt til text/plain. 
•  Lag en web-side for gruppa som 
•	har minst ett bilde,
•	er være stilsatt med en CSS-fil og
•	har en hyperlenke til en XML fil som viser info om gruppemedlemmmene
Alle filene (HTML-, CSS-, XML- og bilde-filene) som websiden består av skal være lagret i webroten, eller en underkatalog av denne. 
•  Sørg for at tjeneren kjører i en busybox-basert container som skal opprettes ved hjelp av chroot(8) og unshare(1), slik at tilgang til filer og prosesser begrenses. Ta gjerne utgangspunkt i eksempelet 6.2 eller unshare-container II. Det skal fremdeles også være mulig å kjøre tjeneren som en demon direkte på verts-systemet – altså utenfor containeren. 
Filtreet i containeren skal inneholde minst mulig. Det kan f.eks se omtrent slik ut: 


    Navneforslag	                                     Kommentar

       /bin/	                                Her kommer busybox-lenkene og webtjeneren
      /proc/	                                Et virtuelt filsystem for prosess-informasjon
    /var/www/	                                En katalog som skal være webroten.
    /var/log/debug.log	                        Logg-fila som skal være koblet til STDERR. Denne bør ikke ligge i webrota
    /etc/mime.types	                                For å identifisere mime-type utfra fil-etternavn


For å kjøre web-tjeneren i en container er det lurt å ha en init-prosess kørende som prosess 1. Web tjenestene kan da kjøres som et barn av init (f.eks. med PID=2). 
Noen av sikkerhets-/robusthetskravene fra MP1, er unødvendige, når tjeneren kjøres i containeren. Dere kan derfor legge inn en test, slik at unødvendige sikkerhets-/robusthets-tiltak ikke utføres dersom foreldreprosessen er init. F.eks. slik: 

if (1!=getppid()) {
  tiltak(); 
}
Slik vil prosessen utføre tiltaket dersom den den startes normalt fra kommandolinja utenfor containeren. Inne i containeren vil skal tiltaket allerede være gjort. 


Milepæl 3 


I denne milepælen skal det lages en database, og et CGI-skript. Merk at: i neste milepæl (MP4) vil det komme krav om om at skriptet skal kjøres av webtjeneren Apache i en Docker-container. 

Arkitektur-/system-krav

Alle statiske filer (CSS, DTD, etc.) skal befinne seg på web-tjener-containeren fra MP2 – altså ikke på webtjeneren som kjører CGI-skriptet. 

Funksjonskrav:

1.	Lag en sqlite-database som har følgende skjema: 

          Bruker	    ( e-postadresse , passordhash, fornavn, etternavn)
          Sesjon	    ( sesjonsID , e-postadresse*)
          Dikt	            ( diktID, dikt, e-postadresse*)
          
          
2.	Lag et CGI-program som: 

o	er et shell-skript
o	gir et RESTful API mot sqlite-databasen fra punkt 1. over.
o	Med API'et skal det være mulig å: 

	logge inn (sjekke passord mot e-postadresse, og sette sesjsonsID)
	logge ut (slette sesjonsID for innlogget bruker)
	dersom brukeren/webklienten er innlogget, er det mulig å gjøre følgende: 

           1. hente ut ett bestemt dikt (gitt diktID)
           2.      hente alle dikt,
           3.      legge til nytt dikt,
           4. endre egne dikt,
           5. 	slette eget dikt (gitt diktID) og
           6.   slette alle egne dikt

	dersom brukeren/webklienten ikke er logget inn skal det bare være mulig å gjøre leseoperasjonene – ikke endringer.
o	bruker XML ved overføring av data i http-kroppen både ved forespørsel og respons.
o	sørger for at XML-dokumentene, som overføres, har korrekt referanse til et dokument som: 

	ved hjelp av DTD (eller XML-Schema) definerer XML-dataenes gyldige struktur,
	reflekterer database-skjemaet (mulige og obligatoriske elementer/attributter)
o	bruker XSL Transformations og CSS for å stilsette XML-dokumentene dersom de vises direkte i en nettleser – slik som i eksempelet XPATH, CGI, Database, XSLT og CSS.


Milepæl 4 

I denne milepælen skal det lages to Docker-containere. Følgende sikkerhetskrav skal gjelde begge: 
•	root-brukeren i containeren skal være upriviligert i vertssystemet (ved hjelp av namespaces(7)).
•	Prosessorbruken til containeren skal begrenses med cgroups(7).
•	Sikkerheten skal økes ved hjelp av capabilities(7).

Arkitekturkrav

1.	Lag et Docker-bilde (Docker og namespaces) som skal være: 
o	basert på det offisielle Docker-bildet httpd:alpine (som er Apache på Alpine).
o	satt opp slik at web-tjeneren Apache støtter CGI-standarden.
o	definert i egen Dockerfile.

2.	Lag to Docker-containere (Docker-container) kalt konteiner-2 og konteiner-3 
o	Disse containerne skal være basert på hver sin Dockerfile
o	Containernes Dockerfiler skal være basert på bildet på Docker-bildet fra punkt 1. over. Se forøvrig arkitekturskissen. 

Funksjonskrav

1.	Funksjonskrav for Konteiner_2: 

o	Dikt-databasen med REST-APIet fra mp3, skal kjøres i denne containeren.

2.	Funksjonskrav for Konteiner_3 

konteiner-3 skal gi et web-grensensittt til dikt-databasen i Konteiner_2. Web-grensesnittet …

0.	kjøres av CGI-program som er et shell-skript;
1.	kan brukes i en nettleser uten javascript (f.eks. lynx);
2.	kommuniserer med Diktdatabasens via REST-API-et;
3.	bruker HTML skjema til å hente data fra bruker;
4.	gir mulighet til å utføre alle operasjonene som APIet tilbyr (og som er ramset opp i funksjonskrav 2. i mp3);
5.	tydelig viser om brukeren er innlogget eller ikke;
6.	er stilsatt ved hjelp av en CSS-fil som skal befinne seg på i web-tjener-containeren fra MP2. Evt. andre statiske filer skal også befinne seg der;
7.	inneholder en hyperlenke til gruppas hjemmeside på containeren fra MP2.


Milepæl 5 

Det skal lages en web-applikasjon som gir et webgrensesnitt mot dikt-databasen i Konteiner_2 (se Arkitekturskisse for fullført prosjekt). Web-applikasjonen skal … 

1.	kunne kjøres i de mest brukte nettleserne;
2.	være kodet i ren javascript (uten bruk av eksterne kodebibliotek);
3.	kommunisere med diktdatabasens REST-API ved hjelp av XMLHttpRequest (AJAX) eller Fetch;
4.	skal gi brukere samme funksjonalitet som det CGI-baserte web-grensesnittet fra funksjonskravene for konteiner_3 i mp4 – bortsett fra punkt 1 og 2. 
5.	ha alle filene som den består av, levert av den C-baserte tjeneren fra milepæl MP1 og MP2;
6.	når klienten brukes med en nettleser som støtter Service workers, gi brukeren tilgang til lese-operasjonener på alle diktene selv når den ikke har tilgang til tjeneren. 

Dette skal besørges av en service worker som, ved første mulighet, lagrer følgende i et mellomlager (cache): 

o	alle filene den trenger (HTML, js, css, etc.) og
o	alle diktene i databasen.




