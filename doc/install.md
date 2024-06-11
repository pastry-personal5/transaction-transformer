# Prerequisites

These are prerequisites for running and developing the project.

## To run

* Windows Platform

* python

* pip

* mariaDB

* Chrome Web Browser


## To develop

* Chocolatey (Or choco in short, for Windows Platform)

* make (for Windows Platform)

    To install `make` using Chocolatey:

    ```bash
    $ choco install make
    ```

* checkmake

    To install checkmake:

    ```bash
    $ go install github.com/mrtazz/checkmake/cmd/checkmake@latest
    ```

### Optional

* DBeaver (for Windows Platform)

# Step-by-step Instruction

These are step-by-step instructions to set up and run the project.

* Unmask.

  * Create or modify the mask configuration file.

    * The configuration file is located at `/config/mask.yaml`

    * As of 2024-06-11, the configuration is like this below:

    Also, look for `/tools/mask.py`

    ```yaml
    masks:
      - files:
          - filepath1
          - filepath2
        replacement:
          - after: <MASK1>
            before: Original text
          - after: <MASK2>
            before: Original text
        ...
    ```

  * Run the following command to apply the mask:

    ```
    $ ./tools/unmask.sh
    ```

* Create or modify the local database configuration.

  * As of 2024-06-11, it is a MariaDB instance.

  * Create or modify the configuration file at `/config/mariadb_exporter.yaml`

* Run

```bash
$ python ./main.py \
--global_config ./config/global_config.yaml \
--kiwoom_config ./data/kiwoom.yaml
```