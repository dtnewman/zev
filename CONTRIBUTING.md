# Contributing to Zev

Thank you for your interest in contributing to Zev! This document provides guidelines and steps for contributing to our project.

## Successfully Contributing

Community contributions are valued, but at the same time, incorporating community written code is time-consuming and challenging. As a general rule, I'd divide contributions into these different cateries:

- Bug fixes (including typos)
- Documentation changes
- Refactors
- Feature changes

For very simple bug fixes and documentation changes, feel free to directly open a PR. For any refactors, features or larger bug fixes, please try to open an issue first, so I can respond there before you put hard work into coding things.

## Reasons why I reject pull requests

Unfortunately, not all community contributions can be accepted. Here are some general guidelines on what is likely to be rejected:

### Your code is hard to review

If you try to bite off too much at once, it's hard to review. So for example, try not to mix a refactor together with a bug fix. It's better to do that in two different PRs.

For feature changes, the best way to ensure quick review is including a screen recording. Features are likely to be rejected for reasons other than the code itself, so adding a quick screen recording helps me to comment without having to actually go through the code line by line (which is a waste of time anyway if major changes to the feature itself are needed).

### Your change implements a feature I don't like

In general, Zev is aiming to remain very simple. Anything that makes it less simple to use is _likely_ to be rejected. For feature additions, try to open an issue first, so that it can be discussed there before you code.

### Your change isn't written cleanly or doesn't follow the style of the code

Sometimes I will suggest modifications, but it's time consuming, so if the code is very messy, I might reject outright. Code that doesn't follow the style conventions of the surrounding code will also be rejected... not because I believe that Zev is written with objectively great style, but because I believe that consistency > correctness when it comes to style.

### You are changing too many things at once

Keep PRs specific, to the point and focused on one thing.

## Code Style Guidelines

- Follow the existing code style in the project
- Run `ruff check` and `ruff format` to validate and format your code
- Run `isort` to sort imports correctly

## Questions or Issues?

If you have any questions or run into issues, open an issue in the repository or reach out to one of the maintainers.

Thank you for contributing to Zev!
