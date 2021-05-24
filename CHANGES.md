# APIFairy Change Log

**Release 0.7.0** - 2021-05-24

- Correctly handle routes with multiple path arguments [#11](https://github.com/miguelgrinberg/apifairy/issues/11) ([commit](https://github.com/miguelgrinberg/apifairy/commit/898b2f1f6bb7de5b5125162fe17879e4d1734dee)) (thanks **Grey Li**!)
- Use default status code when route returns a one-element tutple ([commit](https://github.com/miguelgrinberg/apifairy/commit/c895739ce51ea8165de8cd20e322dea7fd2c4645))
- Update schema name resolver to remove unnecessary List suffix [#21](https://github.com/miguelgrinberg/apifairy/issues/21) ([commit](https://github.com/miguelgrinberg/apifairy/commit/fee7425c32ce0629d65cf1729337d3fe940864a6)) (thanks **Grey Li**!)
- Fix path arguments order ([commit](https://github.com/miguelgrinberg/apifairy/commit/6793feb36c893212966eeaf4c9bea2b753e3d142)) (thanks **Grey Li**!)
- Fix path arguments regex [#16](https://github.com/miguelgrinberg/apifairy/issues/16) ([commit](https://github.com/miguelgrinberg/apifairy/commit/7c81c154698dfab0a3c49613ea9885c2ea81be51)) (thanks **Grey Li**!)
- Fix detection of view docstring [#8](https://github.com/miguelgrinberg/apifairy/issues/8) ([commit](https://github.com/miguelgrinberg/apifairy/commit/4dd8568f037b27a54bb1b57a4ea27580f97cf786)) (thanks **Grey Li**!)
- Add missing backtick for inline code [#17](https://github.com/miguelgrinberg/apifairy/issues/17) ([commit](https://github.com/miguelgrinberg/apifairy/commit/e25f5487d1be1b9fef828ce8376e35f51d2231dc)) (thanks **Grey Li**!)
- Document the process_apispec decorator ([commit](https://github.com/miguelgrinberg/apifairy/commit/fd22e11302da82e4aed58e5793efa997d113dc74))
- Fix typo in Getting Started section [#13](https://github.com/miguelgrinberg/apifairy/issues/13) ([commit](https://github.com/miguelgrinberg/apifairy/commit/11bab4baf9f609c174ff8c7810a2f83f697257e5)) (thanks **Grey Li**!)
- Fix typo in exception message [#20](https://github.com/miguelgrinberg/apifairy/issues/20) ([commit](https://github.com/miguelgrinberg/apifairy/commit/217a7fc976b860daa07199c297c7086b63e341be)) (thanks **Grey Li**!)
- Add openapi-spec-validator into tests_require [#9](https://github.com/miguelgrinberg/apifairy/issues/9) ([commit](https://github.com/miguelgrinberg/apifairy/commit/faf551cd2bb224c33f5f6cfc94b2cb34a5249bf6)) (thanks **Grey Li**!)
- Added missing import statements in documentation examples [#7](https://github.com/miguelgrinberg/apifairy/issues/7) ([commit](https://github.com/miguelgrinberg/apifairy/commit/316e0a5af3689947aa7d080c3c3aad87454235bd)) (thanks **Grey Li**!)
- Move builds to GitHub actions ([commit](https://github.com/miguelgrinberg/apifairy/commit/b8cec62a7d719b6dd51b69dbf8f983b61459be94))

**Release 0.6.2** - 2020-10-10

- Documentation updates ([commit](https://github.com/miguelgrinberg/apifairy/commit/ae72b2abc850ecf58c47603fac39fc92fd5c76ec))

**Release 0.6.1** - 2020-10-05

- Fixed release script to include HTML templates
- Rename blueprint to `apifairy`

**Release 0.6.0** - 2020-10-03

- More unit test coverage
- Configuration through Flask's `config` object
- Error handling

**Release 0.5.0** - 2020-09-28

- First public release!
