## Stand van zaken thesis Simon Vansuyt 27/03/2023

* Vignetting correctie:
  * De correctie is verwerkt in de pipeline en wordt toegepast op de gestackte beelden. Eerst worden de beelden gecropt van 9,21 x 9,21 mm naar 7,6 x 7,6 mm. Daarna wordt de flat field correctie op de gecropte beelden uitgevoerd. De gestitchte beelden zijn beter, maar er is nog steeds een klein visueel verschil merkbaar.
* GUI:
  * Behalve het kalibratietabblad is alles uitgewerkt in de GUI. 
  * De GUI bevat nog een aantal bugs die moeten weg gewerkt worden:
    * Het genereren van de ruwe scan faalt soms.
    * Stitching start soms niet automatisch.
    * ...
* Kalibratie:
  * In GUI tabblad uitwerken
  * Mogelijkheid onderzoeken om een kalibratieplaatje te ontwikkelen
* Scriptie:
  * Extended Abstract: Begonnen maar nog niet af
  * Hoofdstuk 4: Softwarearchitectuur: verder uitbreiden met vignetting correctie, en sequentie diagrams voor de communicatie tussen containers.
  * Hoofdstuk 6: Analyse: verder aan schrijven: EFI en Stitching zijn klaar maar er moet nog over vignetting geschreven worden
  * Hoofdstuk 7: Grafische User Interface: begonnen maar nog verder aan werken
  * Hoofdstuk 8: Evaluatie en reflectie: Nog aan te beginnen
  * Conclusie: Nog aan te beginnen
* Overdracht van code:
  * Code documenteren -> meer commentaar en tabel van REST API per container maken.
  * Voor ieder container python requirements.txt finaal genereren (pip freeze) en containers opnieuw builden.
  * Finale containers op Docker Hub plaatsen
  * Dependencies voor project verder uitschrijven [zie github wiki](https://github.ugent.be/UGent-Woodlab-master-theses/SimonVansuyt/wiki)
  * Docker-compose aanpassen zodat alles automatisch start. Op dit moment is dit niet het geval omdat dit gemakkelijker is voor ontwikkeling.
  * Resultaatbeelden plaatsen op Zenodo, Drive, etc.