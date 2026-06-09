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

```bash
data/raw/RC_2024-10.zst
data/raw/RS_2024-10.zst




