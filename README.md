**This script was originally created to repair encoding in popular Czech hobby magazines. If you wish to apply it to other PDF files, please skip to the next chapter.**

# Oprava textu v časopisech AMARO

Většina elektronických vydání (PDF souborů) časopisů A-Radio Praktická Elektronika a Konstrukční elektronika je špatně vygenerovaná, takže v nich nejde hledat ani kopírovat text. To je v dnešním informačním věku dost výrazná vada. Tento Python skript to umí opravit, přičemž je koncipován tak, aby jeho použití bylo co nejjednodušší. Abyste nemuseli instalovat Python a nezbytné knihovny, je zde připaven hotový spustitelný program "opravAR.exe", ve kterém už vše je. Skript dokáže opravit pouze originální PDF časopisy z CD a DVD, které byly vydány firmou AMARO, všechny ostatní soubory ignoruje. Díky tomu je "blbuvzdorný" a nebude nic dělat, pokud ho třeba omylem spustíte jinde, než jste chtěli. Pokud originální CD či DVD s časopisy nemáte, můžete si je koupit zde:

http://www.aradio.cz/cdrom.html

Pointa skriptu je, že každý čtenář si může svoji sbírku opravit sám - na časopisy se vztahuje autorský zákon a nelze je volně šířit. Postup použití je následující:

1. Někam na pevný disk z CD/DVD zkopírujte všechny soubory, které chcete opravit. Nejlepší je zachovat původní adresářovou strukturu po jednotlivých ročnících, skript automaticky hledá ve všech podadresářích.

2. Zde z Githubu si stáhněte a do stejného adresáře uložte soubory skriptu. Pro funkci jsou nezbytné jen 4 soubory: [opravAR.exe](opravAR.exe), [magazine_hash.json](magazine_hash.json), [Type1toUnicode.exe](Type1toUnicode.exe) a [to_unicode.json](to_unicode.json). XXXXXXXXXXXX Alternativně můžete stáhnout všechny soubory najednou jako ZIP archív, dělá se to zeleným tlačítkem Code -> Download ZIP.

3. Spusťte opravAR.exe. Pravděpodobně se objeví modré okno Windows s výstrahou zabezpečení, to musíte potvrdit. Oprava typicky zabere několik minut, podle počtu souborů a výkonu PC. Skript nemá žádné GUI, výsledky jeho činnosti se zobrazují pouze v konzoli příkazové řádky. Většinou se v ní zobrazují pouze zelené řádky se statistikou oprav, u některých ročníků tam jsou i oranžové řádky s varováními. Ty můžete ignorovat. Nikdy by se však neměly objevit červené řádky s chybami.

4. Na disku se objeví opravené PDF soubory s koncovkou _repaired a také adresáře s podrobnějšími logy o průběhu opravy. Logy a původní PDF z CD/DVD poté můžete smazat. To uděláte nejsnadněji tak, že je nejdřív seřadíte podle data, originální PDF soubory jsou vždy starší než opravené.

Skript byl vyvíjen a testován pouze na Windows 10, funkci na jiných OS neznáme. Zde je pro ukázku jedna stránka před a po opravě, zkuste si z nich vykopírovat text.

XXXXXXXXXXXXXXXXXXX

Oprava podporovaných časopisů je téměř stoprocentní, včetně řecké abecedy a jiných "exotických" znaků. Většinou nejdou opravit jen stránky s reklamami, ale ty jsou irelevantní. Je nutné zdůraznit, že **skript umí opravit pouze časopisy A-Radio Praktická Elektronika (2000-současnost), Konstrukční elektronika (2000-2011) a Electus (2000-2007).** Tyto časopisy mají totálně špatné kódování, takže text je v nich "rozsypaný čaj" a nejde v nich vůbec vyhledávat. Časopisy Amatérské rádio (řada A + řada B, později Stavebnice a konstrukce) sice také mají špatné kódování, ale většina textu je čitelná, nesprávně jsou v nich "jen" české znaky. Jsou tedy alespoň částečně použitelné. Skript opravuje PE do roku 2022, postupem času ho budeme aktualizovat. Zde je přehled, co skript aktuálně (verze 0.4.0) umí či neumí opravit:

XXXXXXXXXXXXXXXXXXXXXX

Je nejasné, proč všechny ty časopisy mají i v roce 2022 špatné kódování textu. Nicméně je/bylo to **Amatérské** radio a ten amatérizmus se holt projevuje i tímto způsobem. Nikdo nejsme dokonalý, i když u firmy, která se přes 20 let živí vydáváním časopisů, je to celkem... udivující.



Opravný skript vzniknul v rámci diplomové práce "Skripty pro hromadnou úpravu fontů v PDF dokumentech" na [Ústavu telekomunikací](https://www.utko.fekt.vut.cz/) na [Vysokém učení technickém v Brně](https://www.vut.cz/). Tento český a anglický návod byl vytvořen vedoucím práce. XXXXXXXXXXXXX po obhajobe link
Pokud vás zajímá, jak skript interně funguje, přečtěte si tu diplomku (slovensky) nebo anglický návod níže.

 # Before you start

You're probably here because you have a PDF file with garbled text - it looks fine on screen, but you get only gibberish when you try to copy+paste it. There are many reasons why text encoding can be wrong in PDF files and Type1toUnicode can repair only one case. Using the script properly can become a time-consuming task, but you may spare yourself the hassle. Do you really need to permanently fix your PDF files? Or do you merely need to copy some text? If so, there may be another way: we've accidentally discovered **that [open-source viewer Evince](https://wiki.gnome.org/Apps/Evince) can return meaningful text even on files that are completely garbled in other PDF viewers** (we tested Adobe Reader, Sumatra PDF, PDF-XChange Viewer, Mozilla Firefox, Google Chrome and others). It's probably because Evince internally uses some sort of heuristics. Nevertheless, even Evince will usually correctly copy only standard ASCII characters (codes 32 to 126); special characters for foreign languages will still be garbled.

# How to run the scripts

There are actually two scripts in this repository, Type1toUnicode and opravAR. Both are available as Python sources and Windows executables. You will probably need only Type1toUnicode, although what opravAR does is explained below. XXXXXXXXXXXXXXXXX The executables already contain all the necessary libraries, so they run right out the box. If you want to run the .py files, you will need following libraries:

* pypdf				4.2.0			https://pypdf.readthedocs.io/en/stable/
* jellyfish			1.0.3			https://github.com/jamesturk/jellyfish
* Levenshtein		0.25.1		https://rapidfuzz.github.io/Levenshtein/
* colorama			0.4.6			https://pypi.org/project/colorama/

Note that the scripts were developed and tested only with these library versions and only on Windows 10. We have no idea if they'd work on other operating systems. Also, you will probably encounter Windows security warnings when you try to run the EXE files for the first time.

# Analyzing your PDF files

As its name implies, Type1toUnicode can repair only Type1 fonts with certain properties. So first you need to determine whether your PDF file(s) can even be repaired. We specifically designed the script to help you with such an analysis. Let's start with its command-line syntax, which is also printed if you run the script without any arguments:

```
the following arguments are required: -p/--pdf_file, -f/--font_map
usage: type1tounicode [-h] -p PDF_FILE -f FONT_MAP [-v]

options:
  -h, --help            show this help message and exit
  -p PDF_FILE, --pdf_file PDF_FILE
                        Defines the path to the .pdf file
  -f FONT_MAP, --font_map FONT_MAP
                        Defines the path to the .json file
  -v, --verbose         Enable verbose output (prints more information)
```
Apart from your input PDF, you also need a JSON file with font mapping. Its purpose and structure will be explained later, but for starters you can use [multi_ascii.json](multi_ascii.json) from this repository. It covers most popular fonts names, but contains only mapping for standard ASCII characters (codes 32 to 126). It should work on most PDFs generated with Adobe products. Unfortunately, that also means it may not work on PDFs from other programs or it may assign wrong character codes. If that happens, repaired text won't be completely garbled anymore, but letters will be randomly swapped. You will need to construct your own JSON file in such case.  

BTW, if [multi_ascii.json](multi_ascii.json) works well on your files, test them with [to_unicode.json](to_unicode.json) next. It has the same base, but covers many more characters and some dingbat fonts.

When the script finishes, it will print a short statistic like
```
File ABCD.PDF, 76 fonts found, 16 fonts skipped, 40 fonts repaired partially, 20 fonts repaired completely
```
The script also generates a subdirectory with log files for every PDF file. The optional -v argument greatly expands these logs to allow for better font analysis. So the actual command will look like
```
Type1toUnicode -p ABCD.PDF -f multi_ascii.json -v
```
Then you need to check the logs. Real-world documents usually contain fonts of varying types and encodings, sometimes dozens of them. Without going into unnecessary technical details, you may encounter several cases:

1. If the script completely repairs all fonts, only the final statistic will appear in the log and it will say "0 fonts skipped, 0 fonts repaired partially". In other words, only fonts that have some sort of problem get mentioned in the log. 

2. Lines "no matching mapping name found in JSON file -> skipping" mean the script could repair such fonts, but it couldn't find proper mapping section in the JSON file. You need to create such a section, or rename existing one.

3. Lines with "no matching font section found in JSON file -> using alternative name" mean that the fonts were repaired using a "recycled" mapping in JSON file. This is actually a really nifty feature which will be explained later. XXXXXXXXXXXXXXXXXX

4. Lines with "Glyph XYZ not found in mapping" mean the script repaired the font only partially, because the JSON mapping file is incomplete. Total number of such fonts will also appear in the final statistic. If this happens, you **must** add all missing characters to the JSON file, otherwise they will also miss in the repaired text. Again, XXXXXXXXXXXXXXX explains how to do it.

5.  If you encounter these lines, it either means the associated fonts already have a proper encoding or the script can't repair them:
* "Font has other type than Type1 -> skipping"
* "ToUnicode already exists -> skipping"
* "FontDescriptor entries missing -> skipping"
* "table Differences does not exist -> skipping"
* "no ToUnicode but Differences incomplete  -> skipping"

6. "no Font objects on the page" happens on pages that contain only images, most commonly in scanned documents. You'd need to use an OCR software to extract text from such pages.

To sum it up: in case 1, your PDF was already completely repaired. If you encounter cases 2, 3 or 4, the fonts can be repaired, but additional work on the JSON file is needed. If the script finishes with "0 fonts repaired completely" and there are only cases 5 or 6 in the logs, then you're out of luck.

**Remember: you should always double-check the output PDFs, even when there are no warnings in the log!'** Probably the easiest way is to select all text (Ctrl+A) and then paste it to an Unicode-capable plaintext editor (such as Notepad++).

## Analyzing multiple files
```
If you want to analyze multiple files at once, you can put them in the same directory as the script and run
```
forfiles /m *.pdf /c "cmd /c Type1toUnicode.exe -p @file -f multi_ascii.json -v" 
```
If you want to also recurse into subdirectories, you can use
```
forfiles /s /m *.pdf /c "cmd /c [full path]Type1toUnicode.exe -p @file -f [full path]multi_ascii.json -v"
```
You can mass-analyze contents of the log files too, e.g. seach them for occurences of certain messages with [grep](https://en.wikipedia.org/wiki/Grep) or other pattern-matching utilities.

# Font map JSON file and how to create it

So it seems your PDF file(s) could be repaired, but you need to edit or expand the font map file. It's not hard, but be warned it can get quite tedious and time-consuming. To do this effectively, you first need to understand what Type1toUnicode and JSON file actually do.

## CID, GID and toUnicode tables

The fact that you can copy+paste text from PDFs is more complex that you probably think. What you see on the screen are just glyphs, graphical symbols that may or may not contain information about which alphabet letter the glyph actually represents. Moreover, PDF supports several schemes to reduce overall file size, so it typically stores only glyphs that are needed to render the given document. Another file size reduction comes from character ordering. Characters have their Character ID (CID), which are stored in the order of their appearance. In other words, every font has different character order. Suppose you have a document that starts with word "OUROBOROS". The characters in the font will be assigned these CIDs:

| Letter | O |U |R |O |B |O |R |O |S |
|-|-|-|-|-|-|-|-|-|-|
| CID | 1 |2 |3 |1 |4 |1 |3 |1 |5 |

Notice that CID for letter "O" gets repeated every time it's needed.

**The first rule: unless absolutely necessary, don't try to completely repair all the fonts.** Real-world documents may contain dozens of fonts, but usually only one or two of them hold bulk of the text. The rest are headings, footnotes, quotes, special characters (greek, math, dingbat etc.)  and other "auxilliary" parts. It's pretty common such fonts contain less than 10 characters and can be omitted.

**The second rule: if you decide some font is important, then try to make the font map as complete as possible.** 


# The gory details

# Known issues and limitations

