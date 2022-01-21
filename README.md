# NoahBot Contribution Guidelines

## The paperwork
To contribute, please follow these guidelines:
* Look at the current Issues and/or discussions taking place in the #bot-dev channel on Discord for things that needs to be done.
* Please create a feature branch for your work.
* Please use pull requests from feature branch to master once you are confident that the implementation is done.


## Before creating a pull request
Please ensure that the following is fulfilled:

### Functionality and testing
* The code has been tested on your own server and appears to work as intended.
* The code handles errors and malformed input gracefully.
* The command is implemented in both slash commands and prefix commands using the same approach as all other places (if applicable).
* Permissions are set correctly.

### Code quality
* Follow PEP-8 style guidelines, except the maximum line width (which can exceed 80 chars in this repo - we're not in the 1970's anymore).
* Try/except the actual error which is raised.
* Proof read the code and fix oddities.
* If in doubt, assume Birb is already exhausted from work. 🙃


***Always leave the campground cleaner than you found it.***
