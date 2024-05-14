# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/cfpb/sbl-filing-api/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                    |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|-------------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| src/sbl\_filing\_api/config.py                          |       44 |        0 |        8 |        1 |     98% |    14->19 |
| src/sbl\_filing\_api/entities/engine/engine.py          |       11 |        0 |        0 |        0 |    100% |           |
| src/sbl\_filing\_api/entities/models/dao.py             |       94 |        5 |        0 |        0 |     95% |41, 60, 75, 95, 122 |
| src/sbl\_filing\_api/entities/models/dto.py             |       84 |        0 |       10 |        2 |     98% |66->70, 70->74 |
| src/sbl\_filing\_api/entities/models/model\_enums.py    |       24 |        0 |        0 |        0 |    100% |           |
| src/sbl\_filing\_api/entities/repos/submission\_repo.py |      117 |        4 |       22 |        2 |     94% |61->63, 68->70, 107-110 |
| src/sbl\_filing\_api/main.py                            |       41 |       11 |        2 |        0 |     74% |35-40, 44-48 |
| src/sbl\_filing\_api/routers/dependencies.py            |       17 |        0 |        8 |        2 |     92% |13->exit, 21->exit |
| src/sbl\_filing\_api/routers/filing.py                  |      179 |        0 |      126 |        0 |    100% |           |
| src/sbl\_filing\_api/services/file\_handler.py          |       22 |        0 |        8 |        0 |    100% |           |
| src/sbl\_filing\_api/services/multithread\_handler.py   |       26 |        2 |        4 |        0 |     93% |     18-19 |
| src/sbl\_filing\_api/services/submission\_processor.py  |       71 |        4 |       14 |        1 |     94% |   105-113 |
|                                               **TOTAL** |  **730** |   **26** |  **202** |    **8** | **96%** |           |

6 empty files skipped.


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