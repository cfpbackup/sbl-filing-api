# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cfpb/sbl-filing-api/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                   |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|--------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/config.py                          |       26 |        0 |        8 |        1 |     97% |    10->14 |
| src/entities/engine/\_\_init\_\_.py    |        2 |        0 |        0 |        0 |    100% |           |
| src/entities/engine/engine.py          |       10 |        0 |        0 |        0 |    100% |           |
| src/entities/models/\_\_init\_\_.py    |        4 |        0 |        0 |        0 |    100% |           |
| src/entities/models/dao.py             |       38 |        1 |        0 |        0 |     97% |        27 |
| src/entities/models/dto.py             |       29 |        0 |        0 |        0 |    100% |           |
| src/entities/models/model\_enums.py    |       15 |        0 |        0 |        0 |    100% |           |
| src/entities/repos/submission\_repo.py |       60 |        6 |       16 |        1 |     91% |44, 71-74, 91 |
| src/main.py                            |       14 |        5 |        2 |        0 |     69% |     15-19 |
| src/routers/\_\_init\_\_.py            |        2 |        0 |        0 |        0 |    100% |           |
| src/routers/filing.py                  |       20 |        3 |        4 |        0 |     88% |     30-32 |
| src/services/submission\_processor.py  |        4 |        2 |        0 |        0 |     50% |      3, 8 |
|                              **TOTAL** |  **224** |   **17** |   **30** |    **2** | **93%** |           |

3 empty files skipped.


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/cfpb/sbl-filing-api/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/cfpb/sbl-filing-api/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/cfpb/sbl-filing-api/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/cfpb/sbl-filing-api/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcfpb%2Fsbl-filing-api%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/cfpb/sbl-filing-api/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.