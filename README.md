# UserReactionFinalProject
# Analyzing User Reaction in Social Media

This project analyzes political user-to-user interactions on Reddit in order to examine polarization, echo-chamber-like behavior, and cross-side political reactions.

The analysis focuses on classifying users as left-oriented or right-oriented and analyzing the direction of replies between them:

- Left → Left
- Right → Right
- Left → Right
- Right → Left

## Data Source

The Reddit data used in this project can be obtained from public Reddit archive sources such as Arctic Shift / Pushshift-based dumps.

Useful sources:


- Academic Torrents Reddit Dumps: [https://academictorrents.com/](https://academictorrents.com/browse.php?search=reddit)

## Data Selection

The project is designed to work with Reddit comments/submissions data from different time periods.

The raw Reddit data can be downloaded from public Reddit archive sources.  
These sources provide Reddit comments and submissions files by month, for example:

- Reddit comments/submissions 2024-10
- Reddit comments/submissions 2025-03
- Reddit comments/submissions 2025-12
- Reddit comments/submissions 2026-01

This means that the user can choose any available month or date range, download the relevant dataset, and run the same analysis pipeline on it.

In this project, we focused on October 2024 because it was close to the United States presidential election period and therefore contained a large amount of political discussion.

However, the code is not limited to October 2024.  
To analyze another period, the user only needs to download the relevant Reddit comments/submissions file and place it inside the `data/raw/` folder.

Example:

note:please create a data file for this

```bash
data/raw/RC_2024-10.zst
data/raw/RS_2024-10.zst

```md
```

For another month, replace the files with the selected month:

```bash
data/raw/RC_2025-03.zst
data/raw/RS_2025-03.zst
```

After replacing the input files, run the same pipeline again.
The output will be generated according to the selected dataset.

---

## Requirements

Before running the project, make sure you have:

* Python 3.9 or higher
* pip
* Git
* Enough disk space for large Reddit archive files

Install the required Python packages using:

```bash
pip install -r requirements.txt
```

The `requirements.txt` file includes:

```txt
pandas
numpy
zstandard
tqdm
matplotlib
regex
networkx
```

---

## Installation

Clone the repository:

```bash
git clone <repository-url>
cd UserReactionFinalProject
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment.

On Windows:

```bash
venv\Scripts\activate
```

On macOS / Linux:

```bash
source venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## Preprocessing Workflow

The preprocessing stage contains five main steps.
Each step is executed using a separate Python script.

### 1. Extract Posts and Interactions

```bash
python openfiles.py
```

This script reads the raw Reddit comments/submissions data and extracts the relevant posts and user-to-user interactions.

### 2. Text-Based Classification

```bash
python classify_text.py
```

This script classifies users or comments according to political text-based indicators.

### 3. Keep Known Left/Right Users Only

```bash
python create_known_user_interactions.py
```

This script keeps only interactions where both users have a known political classification: left-oriented or right-oriented.

### 4. Create Minimal Clean Dataset

```bash
python clean_final_dataset.py
```

This script creates a clean and minimal dataset that contains only the fields needed for the final analysis.

### 5. Remove Duplicate Interaction Pairs

```bash
python create_unique_interactions.py
```

This script removes duplicate user-to-user interaction pairs and creates the final unique interaction dataset.

---

## Run the Full Preprocessing Pipeline

Run the scripts in the following order:

```bash
python openfiles.py
python classify_text.py
python create_known_user_interactions.py
python clean_final_dataset.py
python create_unique_interactions.py
```

After these steps, the processed interaction files will be created and used for the final analysis.

---

## Final Analysis

After preprocessing the dataset, run:

```bash
python analyze_final_results.py
```

This script calculates the final political interaction counts and percentages.

The analysis focuses on:

* Left → Left
* Right → Right
* Left → Right
* Right → Left
* Same-side interactions
* Cross-side interactions

---

## Graph Creation

To create a graph representation of user-to-user interactions, run:

```bash
python build_graph_degree_filtered.py
```

This script builds a graph based on the interaction data and can be used for network-based analysis.

---

## Export Results

To export the final results to JSON format, run:

```bash
python export_results_json.py
```

The exported files can be used for report writing, tables, figures, and visualizations.

---

## Main Output

The project generates political interaction results based on four reply directions:

| Interaction Direction | Meaning                                              |
| --------------------- | ---------------------------------------------------- |
| Left → Left           | Left-oriented user replied to a left-oriented user   |
| Right → Right         | Right-oriented user replied to a right-oriented user |
| Left → Right          | Left-oriented user replied to a right-oriented user  |
| Right → Left          | Right-oriented user replied to a left-oriented user  |

The final results include:

* Total number of interactions
* Interaction counts by political direction
* Interaction percentages
* Same-side vs cross-side interactions
* Balanced sampling results
* Graph-based outputs
* Visualization files

---

## Key Research Idea

The goal of the project is not only to check whether political polarization exists, but also to examine how it appears through real user-to-user reactions.

By analyzing the direction of replies, the project can show whether users mainly interact within their own political side or whether they engage with the opposing side.

This makes it possible to identify:

* Same-side reinforcement
* Cross-side confrontation
* Echo-chamber-like behavior
* Asymmetric political reaction patterns

---

## Running the Analysis on a Different Date

The project is not limited to October 2024.

The user can choose any available Reddit comments/submissions dataset from the data source website, download it, and place it inside the `data/raw/` folder.

For example, to analyze March 2025:

```bash
data/raw/RC_2025-03.zst
data/raw/RS_2025-03.zst
```

Then run the same preprocessing and analysis scripts again.

The output will be generated according to the selected time period.

---

## Notes

The raw Reddit data files are not included in this repository because they are very large.

To reproduce the analysis, download the relevant Reddit comments/submissions dataset manually from the data source website.

This project was tested on Reddit political discussion data from October 2024, but the same code can be applied to other available Reddit datasets.

The quality of the results depends on:

* The selected time period
* The amount of political discussion in the dataset
* The quality of the user classification process
* The amount of noise, bots, trolls, or unclear users in the data

---

## Project Summary

This project provides a transparent way to analyze political polarization through Reddit user reactions.

Instead of analyzing only political content, the project examines who replies to whom and classifies each interaction direction.

This approach helps reveal whether political discussions are mostly internal within the same side, or whether users actively engage with the opposing political side.

```
```

