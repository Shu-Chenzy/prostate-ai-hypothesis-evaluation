# Data

Nothing in this folder is committed except this file. The notebook downloads everything on first run and caches it here.

| File | Source | What it is |
|---|---|---|
| `GSE35988-GPL6480_series_matrix.txt.gz` | [NCBI GEO GSE35988](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GSE35988) | Processed log2 ratios, 88 samples on Agilent GPL6480: 12 benign, 49 localized, 27 metastatic CRPC |
| `GPL6480.txt` | [NCBI GEO GPL6480](https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=GPL6480) | Probe annotation (probe ID to gene symbol) |
| `su2c_polya_log2fpkm.csv` | [cBioPortal](https://www.cbioportal.org/study/summary?id=prad_su2c_2019) study `prad_su2c_2019`, profile `mrna_seq_fpkm_polya` | log2(FPKM + 1) for the genes tested in the notebook, 266 mCRPC biopsies |
| `su2c_clinical.csv` | same study, sample-level clinical data | ARSI exposure status, biopsy site, AR and NEPC scores |
| `uniprot_annotation.csv` | [UniProt REST API](https://rest.uniprot.org) | Reviewed human entries: accession, keywords, subcellular location |

## Cohorts

**GSE35988** (discovery). Grasso CS et al. The mutational landscape of lethal castration-resistant prostate cancer. *Nature* 2012;487:239-243. Localized tumors and benign tissue are from radical prostatectomy; CRPC samples are from a rapid autopsy program. Values are log2(sample/reference) from two-color arrays, so they are not log-transformed again.

**SU2C/PCF 2019** (replication). Abida W et al. Genomic correlates of clinical outcome in advanced prostate cancer. *PNAS* 2019;116:11428-11436. Metastatic CRPC biopsies with RNA-seq. `ABI_ENZA_EXPOSURE_STATUS` is used as `Naive` vs `Exposed` or `On treatment`; samples with unknown status are excluded and one biopsy per patient is kept.

Both datasets are public and de-identified. Please cite the original studies if you reuse them.
