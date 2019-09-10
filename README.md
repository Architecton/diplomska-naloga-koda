# diplomska-naloga-koda
Izbrana koda, ki sem jo razvil v sklopu diplomskega dela na FRI

Koren repozitorija vsebuje naslednje direktorije:

* **./algorithms** - direktorij z implementacijami algoritmov in naučenih metrik,

* **./cv-vs-num-results** - direktorij, ki vsebuje rezultate računanja uspešnosti k-kratnega prečnega preverjanja v odvisnosti od moči množice najboljših atributov,

* **./datasets** - direktorij, ki vsebuje podatkovne množice,

* **./evaluation_results** - direktorij, ki vsebuje potrebne podatke za izvajanje statističnih testov in v katerega se shranjujejo rezultati statističnih testov,

* **./fs-visualization-catdog** - rezultati izrisovanja rezultatov izbora najbolj informativnih atributov za slikovno podatkovno množico catdog

* **./unit-tests** - testi enote za razvite algoritme.
---

Koren repozitorija vsebuje tudi naslednje evalvacijske skripte:

* **./construct_scores_matrix.py** - skripta, s katero zgradimo matriko razlik rezultatov n izvajanj k-kratnega prečnega preverjanja za dva algoritma. Algoritma, ki jih želimo primerjati, določimo znotraj skripte (vrstica 72),

* **./construct_scores_vec.py** - skripta, s katero zgradimo matriko rezultatov n izvajanj k-kratnega prečnega preverjanja posameznega algoritma. Algoritem, ki ga želimo ovrednotiti, določimo znotraj skripte (vrstica 62),

* **./construct_scores_vec_alt.py** - skripta, s katero zgradimo matriko rezultatov n izvajanj k-kratnega prečnega preverjanja posameznega algoritma, pri čimer iz učne množice izvzamemo validacijsko množico, ki jo uporabimo za učenje hiperparametrov modela. Algoritem, ki ga želimo ovrednotiti, določimo znotraj skripte (vrstica 47),

* **./cv_vs_num.py** - skripta, s katero izračunamo rezultate k-kratnega prečnega preverjanja v odvisnosti od kardinalnosti množice najboljših atributov,

* **./visualization_images_catdog.py** - skripta, s katero vizualiziramo rezultate izbora najbolj informativnih atributov z uporabo slikovne podatkovne množice catdog. Rezultati se shranijo v direktorij **./fs-visualization-catdog**.
