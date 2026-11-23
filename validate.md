# Wikipedia recommender validation

On 21 November 2026, the repository example indexed **100 distinct English Wikipedia pages** and saved the fitted recommender. After reloading it, the two-article query reproduced the example's first five recommendations in the same order, with matching cosine scores to six decimal places. The run used Windows, Python 3.11.5 and the dependencies pinned in [commit `26b534c`](https://github.com/letamquang-ai/Wiki_recommend/tree/26b534c4165ad23a4717022234266d3400139afd).

## Top five recommendations

Both queries used the same saved candidate set. The first used *Machine learning* alone. The second added *Artificial intelligence*. For each candidate, the recommender computes TF-IDF cosine similarity to each input article and averages the scores when there are two inputs. Both queries excluded the input URLs.

| Rank | Machine learning | Cosine score | Machine learning + Artificial intelligence | Cosine score |
| ---: | --- | ---: | --- | ---: |
| 1 | Nvidia | 0.287749 | Nvidia | 0.434723 |
| 2 | Wikipedia | 0.220258 | Jensen Huang | 0.248016 |
| 3 | Voyager 1 | 0.167642 | Wikipedia | 0.242366 |
| 4 | Jensen Huang | 0.158245 | Myanmar | 0.172958 |
| 5 | Joo Koon train collision | 0.146644 | Wikimedia Foundation | 0.171767 |

Three pages appeared in both lists. Nvidia stayed first and Jensen Huang moved from fourth to second when the reading history included *Artificial intelligence*. Some results have a less obvious topical connection, such as *Joo Koon train collision* for *Machine learning*. The candidate pool came from a crawl starting at the Wikipedia Main Page. The team's planned featured-article collection was outside this run. Measuring recommendation quality on that collection will require relevance judgments.

## What was checked

- The unmodified [example](test.py) completed its 100-page crawl, printed ten recommendations and wrote `recommender.csv`. The example allows input articles in its output.
- The saved file loaded successfully through `WikipediaRecommender.load_from_file`. Each validation query returned five distinct candidate URLs, excluded the supplied URLs and produced scores in descending order within the range 0 to 1.
- The repository's pytest check passed. It imports the package and executes `assert True`. The ranking and save/load checks above used the actual example output and the reloaded model.

## Repeat the check

From the repository root, activate a Python 3.11 virtual environment and install the pinned package dependencies. On a fresh installation, download the NLTK resources before importing the recommender.

```powershell
python -m pip install -r requirements.txt
python -m nltk.downloader punkt_tab words wordnet stopwords
python test.py
```

To replay the top-five comparison, run the commands below against the same `recommender.csv`. The validation snapshot has SHA-256 `4e6743b522d17f5b1cb3afa40bb4be08a7824e7e0bf46d7f33716fc018cc2d37`. If using that snapshot, skip `python test.py` above because it writes a fresh model to that filename.

```powershell
python export_results.py recommender.csv recommendations.csv
```

A fresh crawl can select different candidates as the Main Page changes. Replaying a saved model fixes the candidate vectors, but the query articles are still fetched live, so later edits can change the scores.
