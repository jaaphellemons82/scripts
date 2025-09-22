# 📊 DSE Voetbal Data Project

Interactieve topscorerspagina in **DSE-stijl**, automatisch gegenereerd vanuit Google Sheets en voetbal.nl data.  
De HTML wordt direct naar GitHub gepusht zodat deze online te bekijken is.  

![Voorbeeld weergave](assets/screenshot.png)

---

## ⚙️ Vereisten

### Software
- [Python 3.10+](https://www.python.org/downloads/)  
- [Google Chrome](https://www.google.com/chrome/)  
- [ChromeDriver](https://chromedriver.chromium.org/downloads) (zelfde versie als je Chrome)  
- [Git](https://git-scm.com/downloads)  

---

## 📦 Installatie

### Python dependencies installeren
Gebruik het meegeleverde `requirements.txt` bestand:

```bash
pip install -r requirements.txt
```
Handmatig installeren kan ook:

```bash
pip install selenium gspread oauth2client plotly
```

--- 

## 🔑 Google API credentials

1. Ga naar Google Cloud Console
2. Maak een nieuw project aan en activeer:
3. Google Sheets API
4. Google Drive API
5. Maak een Service Account aan en download de credentials.json
6. Zet credentials.json in de hoofdmap van dit project
7. Deel de juiste Google Sheets met het service account e-mailadres (meestal iets als xxxx@xxxx.iam.gserviceaccount.com) met bewerkerrechten

## ⚙️ Configuratie
config.json

Hierin staat de login- en teamconfiguratie:

```json
{
  "chrome": {
    "chromedriver_path": "C:/Data/voetbal/chromedriver.exe",
    "chrome_binary_path": "C:/Program Files/Google/Chrome/Application/chrome.exe"
  },
  "teams": [
    {
      "name": "JO13-1",
      "username": "xxxxxxx",
      "password": "xxxxxxx",
      "spreadsheet_id": "xxxxxxxxxxxxxxxxxxxx",
      "sheet_name_uitslagen": "Uitslagen",
      "sheet_name_aanwezigheid": "Aanwezigheid",
      "team_url": "https://www.voetbal.nl/team/T123456789/uitslagen"
    }
  ]
}
```

git_config.py

Bevat de GitHub configuratie voor automatisch uploaden:
```python
GIT_REPO_PATH = r"C:/Data/git/scripts"
GIT_BRANCH = "main"
GITHUB_USERNAME = "jouw-gebruikersnaam"
GITHUB_PAT = "github_pat_xxx"
GITHUB_REPO = "voetbal-scripts"
```

## 🚀 Gebruik
1. Voetbal.nl scraper starten
```bash
python get-data.py
```
- Opent Chrome
- Logt in op voetbal.nl
- Scrapet uitslagen & programma
- Schrijft nieuwe wedstrijden en tegenstanders naar Google Sheets

2. Topscorers genereren
```bash
python topscorers_plot.py
```
- Leest data uit Google Sheet
- Genereert interactieve HTML (topscorers_plot.html)
- Uploadt automatisch naar GitHub

## 📂 Belangrijke bestanden

- get-data.py → scraper voor voetbal.nl
- topscorers_plot.py → genereert HTML grafieken
- config.json → configuratie per team
- git_config.py → GitHub instellingen
- credentials.json → Google API credentials
- dselogo.png → clublogo (wordt in de HTML getoond)
- assets/screenshot.png → voorbeeldweergave van de HTML pagina

## 📱 Mobiele weergave

- Grafieken schalen automatisch mee
- Tabel kan horizontaal gescrold worden
- Extra witruimte tussen secties voor betere leesbaarheid

## ✅ Checklist voor nieuwe pc

 - Python geïnstalleerd
 - Chrome + juiste ChromeDriver geïnstalleerd
 - Git geïnstalleerd
 - Dependencies geïnstalleerd met pip install -r requirements.txt
 - credentials.json toegevoegd
 - Google Sheet gedeeld met service account
 - config.json en git_config.py ingevuld
 - Scripts starten met python get-data.py en python topscorers_plot.py

 ⚽ Klaar! Met deze setup kun je het project overal draaien en automatisch je topscorers publiceren.