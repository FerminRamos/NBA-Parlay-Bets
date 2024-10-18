## NBA Database
*This subfolder contains a database of all players for a given season, 
sorted by teams.*

---
Pro's of using this format:
* Avoids the bottleneck of calling an API each time we need to reference 
player data.
* Keeps running costs low, since we don't need to pay for a 
proper database to hold our datasets.

Con's of using this format: 
* Redundancy of player data (especially if player has been in the league 
for multiple seasons). 
* Much slower than a relational database.

---

Nonetheless, the Folder Structure is formatted as such:
```text
">" = a folder
"*" = a file

> NBA Database
    > 2023-2024 Season
        * game schedule
        > Boston Celtics
            * team statistics
            * log information (file last update, etc.)
            > Player 1
                * player characteristics
                * player statistics
                * log information (file last update, etc.)
            > Player 2
            > Player 3
```