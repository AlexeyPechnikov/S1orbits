# Sentinel-1 Orbits
This repository offers up-to-date and well-structured daily Sentinel-1 RESORB and POEORB orbits for PyGMTSAR InSAR software, available at [InSAR.dev](https://insar.dev/).

We ensure the orbits remain current by utilizing regularly scheduled GitHub Actions runners that update the orbits catalog every four hours. Additionally, you can manually trigger the updating scripts on the GitHub Actions page or via a terminal command. Currently, this repository keeps track of the ESA's orbits store at https://step.esa.int/auxdata/orbits, but additional sources may be included if necessary.

The updating process is comprehensive: it involves storing orbits in daily directories, unpacking zip archives, removing unnecessary files like those found in the /var directory, and conducting validity checks on the orbit XML files. Verified orbits are subsequently repacked into single-file zip archives. We always host POEORB files, providing permanent links to them. RESORB files are removed as soon as the corresponding POEORB files become accessible.

If the ESA's orbit archive becomes overloaded or experiences downtime, you can always rely on this GitHub repository. Furthermore, you can clone this repository to your own account, and it will stay up-to-date thanks to auto-synchronization.

To streamline the repository, you may opt to create a new one that includes all GitHub workflows. All files in the root directory, along with all the orbits and index files, can be seamlessly added to the new repository using the commands below:

```bash
git add README.md *.py *.sh .github/workflows/*
git commit -m "Update root directory files and workflows"
git push

for satellite_dir in $(find . -maxdepth 1 -type d -name 'S1*'); do
    satellite=$(basename "$satellite_dir")
    for year_dir in $(find "$satellite_dir" -maxdepth 1 -type d -name '20*'); do
        year=$(basename "$year_dir")
        git add "$satellite/$year"
        git commit -m "Add $satellite $year data"
        git push
    done
done
```

