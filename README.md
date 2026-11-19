# Windows XP Phone Number Editor

[Deutsch](#deutsch) | [English](#english)

## Deutsch

Ein grafischer Editor für die Länder-Telefonnummern in `PHONE.INF` bzw. der komprimierten `PHONE.IN_` einer Windows-XP-Installationsquelle. Die Oberfläche verwendet wxPython-Steuerelemente und ist auf die Tastaturbedienung mit Screenreadern wie NVDA ausgelegt.

### Funktionen

- `PHONE.INF` und `PHONE.IN_` öffnen (letzteres über Windows `expand.exe`)
- Land aus einer Ausklappliste auswählen und beide Telefonnummern bearbeiten
- Leeres Feld für die kostenlose Nummer wird als `%not_available%` gespeichert
- Als `PHONE.INF` oder komprimierte `PHONE.IN_` speichern (`makecab.exe`)
- Deutsch/Englisch, automatische Erkennung der Windows-Anzeigesprache und manuelle Umschaltung
- Bedienung über Tabulator, Pfeiltasten und Standard-Windows-Dialoge

### Voraussetzungen und Start

Windows 10 oder 11, Python 3 und wxPython. Die fertige EXE benötigt keine separate Python- oder wxPython-Installation. Für komprimierte Dateien werden die Windows-Werkzeuge `expand.exe` und `makecab.exe` verwendet.

```cmd
py -m pip install -r requirements.txt
py phone_inf_editor_bilingual.py
```

### EXE erstellen

```cmd
py -m pip install -r requirements-build.txt
build.bat
```

Ergebnis: `dist\XP-Phone-Editor.exe`. Die Versionsinformationen stehen in `version_info.txt`.

### Installations-CD anpassen

1. Original-CD vollständig in einen beschreibbaren Ordner kopieren.
2. `I386\PHONE.IN_` im Editor öffnen, Land und Nummern ändern.
3. Als `PHONE.IN_` speichern und die Datei in der *Kopie* des `I386`-Ordners ersetzen.
4. Mit nLite eine neue bootfähige ISO aus der angepassten Quelle erzeugen und in einer VM testen.

**Hinweis:** Dieses Programm ändert nur die angezeigten Telefonnummern, nicht die Windows-Aktivierungsprüfung. Es ist kein Produkt von Microsoft und wird nicht von Microsoft unterstützt. Eine Windows-XP-Installationsquelle ist nicht Bestandteil dieses Repositories.

### Mitmachen und Lizenz

MIT-Lizenz, siehe [LICENSE](LICENSE). Forks, private Änderungen und kommerzielle Nutzung sind erlaubt. Änderungen müssen nicht an den ursprünglichen Autor zurückgegeben werden. Bei Weitergabe muss der Lizenz- und Copyright-Hinweis erhalten bleiben. Beiträge sind willkommen, aber freiwillig.

## English

A graphical editor for country-specific telephone numbers in `PHONE.INF` or compressed `PHONE.IN_` from Windows XP installation media. The wxPython interface uses native Windows controls designed for keyboard and screen reader access (including NVDA).

### Features

- Open `PHONE.INF` or `PHONE.IN_` (decompressed with Windows `expand.exe`)
- Select a country from a drop-down list and edit both telephone numbers
- A blank toll-free number becomes `%not_available%`
- Save as `PHONE.INF` or compressed `PHONE.IN_` (using `makecab.exe`)
- German/English interface with automatic Windows UI language detection and manual switching
- Keyboard navigation with Tab, arrow keys and standard Windows dialogs

### Requirements and run

Windows 10 or 11, Python 3 and wxPython. A packaged EXE does not require Python or wxPython to be installed separately. Windows `expand.exe` and `makecab.exe` are used for compressed files.

```cmd
py -m pip install -r requirements.txt
py phone_inf_editor_bilingual.py
```

### Build standalone EXE

```cmd
py -m pip install -r requirements-build.txt
build.bat
```

Output: `dist\XP-Phone-Editor.exe`. Edit `version_info.txt` to update version metadata.

### Modify installation media

1. Copy the original Windows XP CD contents to a writable directory.
2. Open `I386\PHONE.IN_`, choose a country and edit the numbers.
3. Save as `PHONE.IN_` and replace the file in the *copied* `I386` directory.
4. Use nLite to create a bootable ISO from the modified source and test in a VM.

**Note:** This tool only changes displayed phone numbers; it does not change Windows activation validation. Not affiliated with or endorsed by Microsoft. No Microsoft installation files are distributed in this repository.

### Contributing and license

Licensed under the [MIT License](LICENSE). Forking, private modifications and commercial use are permitted. You are not required to share improvements with the original author. Retain the copyright and license notice when redistributing. Contributions are welcome but optional.
