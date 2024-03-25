# S1orbits
This repository offers up-to-date and well-structured Sentinel-1 RESORB and POEORB orbits for the PyGMTSAR InSAR software available at [InSAR.dev](https://insar.dev/).

To automatically keep the orbits up-to-date, regularly scheduled GitHub Actions runners are utilized. These update the orbits catalog every 4 hours. Additionally, the updating scripts can be manually triggered on the GitHub Actions page or via a terminal command.

POEORB files are always hosted and can be permalinked. RESORB files are removed as soon as POEORB files become accessible. To compactify the repository, it can be replaced by a new one including GitHub workflows. All files in the root directory, along with all the orbits and index files, can be added to the new repository using the commands printed by below:

```bash
echo git add README.md *.py *.sh .github/workflows/*

for satellite_dir in $(find . -maxdepth 1 -type d -name 'S1*'); do
    satellite=$(basename "$satellite_dir")
    for year_dir in $(find "$satellite_dir" -maxdepth 1 -type d -name '20*'); do
        year=$(basename "$year_dir")
        echo "git add $satellite/$year && git commit -m 'Add $satellite $year data' && git push"
    done
done
```

