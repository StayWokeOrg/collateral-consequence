# Collateral Consequence
[![Build Status](https://travis-ci.org/StayWokeOrg/collateral-consequence.svg?branch=clean-and-test)](https://travis-ci.org/StayWokeOrg/collateral-consequence)

The goal of this app is to provide citizens with the information to make fully informed decisions when interacting with the criminal justice system. 
Individuals are usually not fully informed about collateral consequences at sentencing or as part of a plea colloquy.
This app will serve to change that by ensuring that people understand the fuller scope of consequences that come with a criminal conviction including the effects it can have on voting rights, access to public benefits and occupational licensing.
This app is designed for someone with no legal training, though lawyers may also use it to aid them in counseling their clients.
We hope that by making it easier to access this information, we can also help to make access to justice more equitable.

## Getting Started Running Locally

- Clone this repository
- Navigate into the repo and set up a virtual environment with the following command:

```bash
$ python3 -m venv .
```

- Activate the virtual environment, so that the requirements will be installed there.

```bash
$ source bin/activate
```

- Type `pip install -r requirements.pip` to install all of the related Python packages
- Navigate into the inner `collateral_consequence` directory and type `./manage.py serve` to start the server

## Contributing

Contributions welcomed and encouraged! Here's how you should contribute to this repository:

- Open an [Issue](https://github.com/StayWokeOrg/collateral-consequence/issues) in this repository describing the feature you intend to work on. Ex: "Harvest data from New Hampshire"
- Assign yourself to that issue
- Check out a new branch from `development` for this feature. Ex: `new-hampshire-data`
- Do your work on that branch.
- When your changes are ready to be merged, open a pull request from your branch to this repo's `development` branch.
- In the comments of your Pull Request, point out which issue you've resolved and how.
- Your pull request will be reviewed and merged to the `development` branch. When it's ready for deployment, `development` will be merged into `master`.

## License (MIT)

```
Copyright (C) 2016 by Ian Webster (http://www.ianww.com)

  Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

  The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
```

# Technical Details and Development Goals for Collateral Consequence


## User Flow
    1. Choose State
    2. Select Type of Crime (Felony, Misdemeanor, or Violation)
    3. Is it a Sex Crime?
    4. Class of Crime (Ex. 'A')
    5. Applicability Questions:
        - Job requires a license
        - Public housing/Food stamps
        - Potentially show all potential effects.


## Versioning Goals
    v 1.0: basic questionnaire for US citizens in English
    v 1.5: the above w/ text-to-speech
    v 2.0: the above w/ spanish in text only
    v 2.5: the above w/ text-to-speech
    v 3.0: immigration law in english only
    v 3.5: immigration law in english only + text-to-speech
    v 4.0: above + spanish


## Columns Available From Justice Center Data
    - ID
    - LEXIS
    - Tab
    - Citation
    - Title
    - Consequence
    - Category
    - Consequence Details
    - Consequence Type
    - Supp. records check/disclosure requirement
    - Duration Category,Duration Description
    - Relief
    - Relief Description
    - Triggering Offense Category
    - Additional Triggering Offenses
    - Additional Offense Details,Questions/Issues
    - Questions and Issues for Resolution,Quality Control
    - Quality Control Description,Created By,Modified By
    - Modified
    - Item Type
    - Path
