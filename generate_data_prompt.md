# ROLE
Jsi expert na EU účetní standardy (IFRS/IAS) a Data Scientist. Tvým úkolem je vytvořit kvalitní trénovací dataset pro klasifikační model typu SetFit (Neural Router).

# KONTEXT
Pracujeme na aplikaci, která směruje dotazy uživatelů na správný účetní standard (např. IAS 16, IFRS 16). Potřebujeme trénovací data, která odrážejí reálné, rozmanité dotazy českých účetních.

# ÚKOL
Vygeneruj trénovací dataset ve formátu CSV se sloupci: "text" (dotaz uživatele) a "label" (ID standardu). 

# SPECIFIKACE DAT
Pro každý z níže uvedených standardů vygeneruj 20 unikátních dotazů v češtině:
1. Skupina: IAS (např. IAS 1, IAS 2, IAS 7, IAS 8, IAS 10, IAS 12, IAS 16, IAS 19, IAS 20, IAS 21, IAS 23, IAS 24, IAS 26, IAS 27, IAS 28, IAS 29, IAS 32, IAS 33, IAS 34, IAS 36, IAS 37, IAS 38, IAS 39, IAS 40, IAS 41)
2. Skupina: IFRS (např. IFRS 1 až IFRS 17)
3. Skupina: OFF_TOPIC (20 dotazů na nesouvisející témata - sport, počasí, IT, obecný pokec)

# POŽADAVKY NA DIVERZITU DOTAZŮ (Důležité):
U každého standardu namixuj tyto typy dotazů:
- Formální/Odborné (např. "Kdy dochází k odúčtování finančního aktiva dle IFRS 9?")
- Laické/Popisné (např. "Máme v nájmu auto na 3 roky, jak to mám dát do účetnictví?")
- Krátká klíčová slova (např. "IAS 16 odpisový plán")
- Hraniční případy (dotazy, které by se mohly plést s jiným standardem)

# FORMÁT VÝSTUPU
Vrať pouze čistý CSV formát. Nepoužívej žádný úvodní ani závěrečný text.
Struktura:
text,label
"Jak účtovat nákup zásob na sklad?","STD:IAS 2"
...