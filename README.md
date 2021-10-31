# kNN_LDP
This repository contains the implementation of the kNN_LDP algorithm from the paper *Non-Parametric Semi-Supervised Learning by Bayesian Label Distribution Propagation* by Jonatan M. N. Gøttcke and A. Zimek.
The paper is presented at the *14th International Conference on
Similarity Search and Applications*, **SISAP 2021**. 

The implementation follows the Scikit-learn classifier style which most users are familiar with. 
## Using the implementation 
1. Git clone the repository. 
2. Ensure you have Python 3.8.+ installed 
3. Install the required dependencies
    ```bash
    pip install -r requirements.txt
    ```
4. Try the example
    ```bash
    python example.py
    ```


See the example.py file on how to use the implementation in further detail. 

## Citation
```{r, eval=True}
@inproceedings{DBLP:conf/sisap/GottckeZC21,
  author    = {Jonatan M{\o}ller Nuutinen G{\o}ttcke and
               Arthur Zimek and
               Ricardo J. G. B. Campello},
  title     = {Non-parametric Semi-supervised Learning by Bayesian Label Distribution
               Propagation},
  booktitle = {{SISAP}},
  series    = {Lecture Notes in Computer Science},
  volume    = {13058},
  pages     = {118--132},
  publisher = {Springer},
  year      = {2021}
}
```
### DOI 

```{r, eval=True}
DOI: 10.1007/978-3-030-89657-7_10
```