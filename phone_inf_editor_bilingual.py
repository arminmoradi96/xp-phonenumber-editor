#!/usr/bin/env python3
# Windows XP PHONE.INF editor with native Windows controls (wxPython).
# Installation: py -m pip install wxPython
import re
import locale
import shutil
import subprocess
import tempfile
from pathlib import Path
import wx

NOT_AVAILABLE = '%not_available%'


def read_phone(path):
    raw = Path(path).read_bytes()
    if Path(path).suffix.lower() == '.in_':
        expand = shutil.which('expand.exe')
        if not expand:
            raise RuntimeError('EXPAND.EXE wurde nicht gefunden. Bitte unter Windows starten.')
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / 'PHONE.INF'
            result = subprocess.run([expand, str(path), str(target)], capture_output=True,
                                    text=True, errors='replace')
            if result.returncode != 0 or not target.is_file():
                raise RuntimeError('Entpacken fehlgeschlagen: ' + result.stdout + result.stderr)
            raw = target.read_bytes()
    if raw.startswith((b'\xff\xfe', b'\xfe\xff')):
        encoding = 'utf-16'
    elif raw.startswith(b'\xef\xbb\xbf'):
        encoding = 'utf-8-sig'
    else:
        encoding = 'cp1252'
    lines = raw.decode(encoding).splitlines(keepends=True)
    section = ''
    names = {}
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section = stripped[1:-1].lower()
        elif section == 'strings':
            match = re.match(r'^\s*([\w]+)\s*=\s*"(.*?)"', line)
            if match:
                names[match.group(1).lower()] = match.group(2)
    section = ''
    entries = {}
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('[') and stripped.endswith(']'):
            section = stripped[1:-1].lower()
            continue
        if section != 'isocodes' or not stripped or stripped.startswith(';'):
            continue
        parts = line.rstrip('\r\n').split(',', 5)
        if len(parts) != 6 or not re.fullmatch(r'[A-Z]{3}', parts[0]):
            continue
        token = parts[3].strip('%').lower()
        name = names.get(token, token.replace('_', ' '))
        entries[f'{name} ({parts[0]})'] = (index, parts)
    if not entries:
        raise ValueError('In [IsoCodes] wurden keine Länder gefunden.')
    return lines, encoding, entries



TRANSLATIONS = {
 "de": {
  "title":"Windows XP – Telefonnummern-Editor (NVDA)",
  "open":"&Öffnen: PHONE.INF oder PHONE.IN_",
  "language":"&Sprache / Language:", "country":"&Land auswählen:",
  "free":"&Kostenlose Nummer (leer = nicht verfügbar):",
  "paid":"&Weitere oder kostenpflichtige Nummer:",
  "apply":"Änderungen &übernehmen", "inf":"Als &INF speichern",
  "cab":"Als CD-Datei PHONE.IN_ &speichern",
  "ready":"Bereit. Bitte zuerst eine Datei öffnen.",
  "status":"Bereit. Tab-Taste wechselt zwischen den Feldern.",
  "discard":"Ungespeicherte Änderungen verwerfen?", "question":"Rückfrage",
  "open_dialog":"PHONE.INF oder PHONE.IN_ öffnen",
  "filter":"XP-Telefondateien (*.inf;*.in_)|*.inf;*.in_|Alle Dateien|*.*",
  "loaded":"{count} Länder geladen. Land auswählen.",
  "open_error":"Fehler beim Öffnen", "country_status":"Land: {name}",
  "no_file":"Bitte zuerst eine Datei öffnen.", "notice":"Hinweis",
  "invalid":"Telefonnummern dürfen keine Kommas oder Zeilenumbrüche enthalten.",
  "invalid_title":"Ungültige Eingabe",
  "applied":"Änderungen für {name} übernommen.",
  "save_dialog":"Datei speichern", "all_files":"Alle Dateien",
  "missing_makecab":"MAKECAB.EXE wurde nicht gefunden. Bitte unter Windows starten.",
  "makecab_error":"MAKECAB fehlgeschlagen: ",
  "saved":"Gespeichert: {path}", "success":"Erfolg",
  "saved_dialog":"Datei erfolgreich gespeichert:\n{path}",
  "save_error":"Fehler beim Speichern",
  "close_warning":"Es gibt ungespeicherte Änderungen. Trotzdem beenden?"
 },
 "en": {
  "title":"Windows XP – Phone Number Editor (NVDA)",
  "open":"&Open: PHONE.INF or PHONE.IN_",
  "language":"&Language / Sprache:", "country":"Select &country:",
  "free":"&Toll-free number (blank = not available):",
  "paid":"&Other or chargeable number:",
  "apply":"&Apply changes", "inf":"Save as &INF",
  "cab":"Save as CD file PHONE.IN_ (&compressed)",
  "ready":"Ready. Open a file first.",
  "status":"Ready. Use Tab to move between controls.",
  "discard":"Discard unsaved changes?", "question":"Confirmation",
  "open_dialog":"Open PHONE.INF or PHONE.IN_",
  "filter":"XP phone files (*.inf;*.in_)|*.inf;*.in_|All files|*.*",
  "loaded":"{count} countries loaded. Select a country.",
  "open_error":"Error opening file", "country_status":"Country: {name}",
  "no_file":"Please open a file first.", "notice":"Information",
  "invalid":"Phone numbers must not contain commas or line breaks.",
  "invalid_title":"Invalid input",
  "applied":"Changes applied for {name}.",
  "save_dialog":"Save file", "all_files":"All files",
  "missing_makecab":"MAKECAB.EXE was not found. Run this application on Windows.",
  "makecab_error":"MAKECAB failed: ",
  "saved":"Saved: {path}", "success":"Success",
  "saved_dialog":"File saved successfully:\n{path}",
  "save_error":"Error saving file",
  "close_warning":"There are unsaved changes. Exit anyway?"
 }
}

def detect_language():
    # Windows UI language, not the decimal/date formatting locale.
    try:
        import ctypes
        lang_id = ctypes.windll.kernel32.GetUserDefaultUILanguage()
        return "de" if (lang_id & 0x3ff) == 0x07 else "en"
    except (AttributeError, OSError):
        loc = locale.getlocale()[0] or ""
        return "de" if loc.lower().startswith("de") else "en"

class Editor(wx.Frame):
    def __init__(self):
        self.lang = detect_language()
        super().__init__(None, title=TRANSLATIONS[self.lang]['title'], size=(820, 495))
        self.lines = []
        self.encoding = 'utf-16'
        self.entries = {}
        self.current = None
        self.dirty = False
        panel = wx.Panel(self)
        layout = wx.BoxSizer(wx.VERTICAL)

        self.language_label = wx.StaticText(panel)
        layout.Add(self.language_label, 0, wx.LEFT | wx.TOP, 9)
        self.language_choice = wx.Choice(panel, choices=['Deutsch', 'English'])
        self.language_choice.SetSelection(0 if self.lang == 'de' else 1)
        layout.Add(self.language_choice, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)
        self.language_choice.Bind(wx.EVT_CHOICE, self.change_language)

        self.open_btn = wx.Button(panel, label=self.t('open'))
        layout.Add(self.open_btn, 0, wx.EXPAND | wx.ALL, 9)
        self.open_btn.Bind(wx.EVT_BUTTON, self.open_file)

        self.country_label = wx.StaticText(panel, label=self.t('country'))
        layout.Add(self.country_label, 0, wx.LEFT | wx.TOP, 9)
        self.country = wx.Choice(panel, choices=[])
        layout.Add(self.country, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)
        self.country.Bind(wx.EVT_CHOICE, self.change_country)

        self.free_label = wx.StaticText(panel, label=self.t('free'))
        layout.Add(self.free_label, 0, wx.LEFT | wx.TOP, 9)
        self.free = wx.TextCtrl(panel)
        layout.Add(self.free, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)

        self.paid_label = wx.StaticText(panel, label=self.t('paid'))
        layout.Add(self.paid_label, 0, wx.LEFT | wx.TOP, 9)
        self.paid = wx.TextCtrl(panel)
        layout.Add(self.paid, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)

        self.apply_btn = wx.Button(panel, label=self.t('apply'))
        layout.Add(self.apply_btn, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)
        self.apply_btn.Bind(wx.EVT_BUTTON, self.apply)

        row = wx.BoxSizer(wx.HORIZONTAL)
        self.inf_btn = wx.Button(panel, label=self.t('inf'))
        self.cab_btn = wx.Button(panel, label=self.t('cab'))
        row.Add(self.inf_btn, 1, wx.RIGHT, 5)
        row.Add(self.cab_btn, 1, wx.LEFT, 5)
        layout.Add(row, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)
        self.inf_btn.Bind(wx.EVT_BUTTON, lambda event: self.save(False))
        self.cab_btn.Bind(wx.EVT_BUTTON, lambda event: self.save(True))

        self.status = wx.StaticText(panel, label=self.t('ready'))
        layout.Add(self.status, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 9)
        panel.SetSizer(layout)
        self.CreateStatusBar()
        self.SetStatusText(self.t('status'))
        for widget in (self.country, self.free, self.paid, self.apply_btn,
                       self.inf_btn, self.cab_btn):
            widget.Enable(False)
        self.refresh_language()
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.open_btn.SetFocus()

    def t(self, key):
        return TRANSLATIONS[self.lang][key]

    def refresh_language(self):
        self.SetTitle(self.t('title'))
        self.language_label.SetLabel(self.t('language'))
        self.open_btn.SetLabel(self.t('open'))
        self.country_label.SetLabel(self.t('country'))
        self.free_label.SetLabel(self.t('free'))
        self.paid_label.SetLabel(self.t('paid'))
        self.apply_btn.SetLabel(self.t('apply'))
        self.inf_btn.SetLabel(self.t('inf'))
        self.cab_btn.SetLabel(self.t('cab'))
        self.SetStatusText(self.t('status'))
        if not self.current:
            self.status.SetLabel(self.t('ready'))
        else:
            self.status.SetLabel(self.t('country_status').format(name=self.current))
        self.Layout()

    def change_language(self, event):
        self.lang = 'de' if self.language_choice.GetSelection() == 0 else 'en'
        self.refresh_language()
        self.language_choice.SetFocus()

    def announce(self, message):
        self.status.SetLabel(message)
        self.SetStatusText(message)

    def open_file(self, event=None):
        if self.dirty and wx.MessageBox(self.t('discard'), self.t('question'),
                                        wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
            return
        with wx.FileDialog(self, self.t('open_dialog'),
                           wildcard=self.t('filter'),
                           style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            path = dlg.GetPath()
        try:
            lines, encoding, entries = read_phone(path)
            self.lines, self.encoding, self.entries = lines, encoding, entries
            self.dirty = False
            choices = sorted(entries, key=str.casefold)
            self.country.SetItems(choices)
            for widget in (self.country, self.free, self.paid, self.apply_btn,
                           self.inf_btn, self.cab_btn):
                widget.Enable(True)
            german = next((i for i, value in enumerate(choices) if value.endswith('(DEU)')), 0)
            self.country.SetSelection(german)
            self.load_country()
            self.country.SetFocus()
            self.announce(self.t('loaded').format(count=len(entries)))
        except Exception as exc:
            wx.MessageBox(str(exc), self.t('open_error'), wx.OK | wx.ICON_ERROR, self)

    def load_country(self):
        self.current = self.country.GetStringSelection()
        _, parts = self.entries[self.current]
        self.free.ChangeValue('' if parts[4].strip().lower() == NOT_AVAILABLE else parts[4])
        self.paid.ChangeValue(parts[5])
        self.announce(self.t('country_status').format(name=self.current))

    def validate_and_apply(self):
        if not self.current:
            wx.MessageBox(self.t('no_file'), self.t('notice'), wx.OK | wx.ICON_INFORMATION, self)
            return False
        free = self.free.GetValue().strip()
        paid = self.paid.GetValue().strip()
        if any(char in free + paid for char in ',\r\n'):
            wx.MessageBox(self.t('invalid'),
                          self.t('invalid_title'), wx.OK | wx.ICON_ERROR, self)
            return False
        index, parts = self.entries[self.current]
        before = self.lines[index]
        parts[4] = free or NOT_AVAILABLE
        parts[5] = paid
        ending = '\r\n' if before.endswith('\r\n') else '\n' if before.endswith('\n') else ''
        after = ','.join(parts) + ending
        if after != before:
            self.lines[index] = after
            self.dirty = True
        return True

    def apply(self, event=None):
        if self.validate_and_apply():
            self.announce(self.t('applied').format(name=self.current))

    def change_country(self, event=None):
        # Retain edits when moving to another country, including unsaved field changes.
        next_country = self.country.GetStringSelection()
        if self.current and next_country != self.current:
            if not self.validate_and_apply():
                self.country.SetStringSelection(self.current)
                return
        self.load_country()

    def save(self, compressed):
        if not self.validate_and_apply():
            return
        extension = 'IN_' if compressed else 'INF'
        with wx.FileDialog(self, self.t('save_dialog'), defaultFile='PHONE.' + extension,
                           wildcard=f'PHONE.{extension}|*.{extension}|{self.t("all_files")}|*.*',
                           style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT) as dlg:
            if dlg.ShowModal() != wx.ID_OK:
                return
            destination = Path(dlg.GetPath())
        try:
            data = ''.join(self.lines).encode(self.encoding)
            if compressed:
                makecab = shutil.which('makecab.exe')
                if not makecab:
                    raise RuntimeError(self.t('missing_makecab'))
                with tempfile.TemporaryDirectory() as folder:
                    src = Path(folder) / 'PHONE.INF'
                    src.write_bytes(data)
                    result = subprocess.run([makecab, '/D', 'CompressionType=LZX',
                                             str(src), str(destination)],
                                            capture_output=True, text=True, errors='replace')
                    if result.returncode != 0 or not destination.is_file():
                        raise RuntimeError(self.t('makecab_error') + result.stdout + result.stderr)
            else:
                destination.write_bytes(data)
            self.dirty = False
            self.announce(self.t('saved').format(path=destination))
            wx.MessageBox(self.t('saved_dialog').format(path=destination),
                          self.t('success'), wx.OK | wx.ICON_INFORMATION, self)
        except Exception as exc:
            wx.MessageBox(str(exc), self.t('save_error'), wx.OK | wx.ICON_ERROR, self)

    def on_close(self, event):
        if self.current:
            self.validate_and_apply()
        if self.dirty and wx.MessageBox(self.t('close_warning'),
                                        self.t('question'), wx.YES_NO | wx.ICON_QUESTION, self) != wx.YES:
            event.Veto()
            return
        event.Skip()


if __name__ == '__main__':
    app = wx.App(False)
    window = Editor()
    window.Show()
    app.MainLoop()
