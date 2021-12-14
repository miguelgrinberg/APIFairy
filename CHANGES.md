# APIFairy Change Log

**Release 0.9.0** - 2021-12-14

- Better ordering for authentication schemes ([commit](https://github.com/miguelgrinberg/apifairy/commit/a6067f8eeb1fe429935e75c0ca71389caed4754f))
- Added rapidoc template ([commit](https://github.com/miguelgrinberg/apifairy/commit/ff9a161bc9edfe7e88f1b6f658ea12f2ae91a0e2))
- Added Elements template ([commit](https://github.com/miguelgrinberg/apifairy/commit/d2ff0543cbf4ed8f293c48b1839445b3deacbf3d))
- Documented how to create a custom documentation endpoint ([commit](https://github.com/miguelgrinberg/apifairy/commit/47d13793fa06a9f23eca5435478f42b103c980b3))

**Release 0.8.2** - 2021-08-30

- One more change needed to include HTML files in package ([commit](https://github.com/miguelgrinberg/apifairy/commit/7ed49227de57afbd51dbea5bd2b1e24ff12f733f))

**Release 0.8.1** - 2021-08-30

- Add the documentation templates back into the package [#2](https://github.com/miguelgrinberg/apifairy/issues/2) ([commit](https://github.com/miguelgrinberg/apifairy/commit/7e0115cd5706652d7208bfafb8b47e8fe84b5de7))

**Release 0.8.0** - 2021-08-07

- Add `servers` section ([commit](https://github.com/miguelgrinberg/apifairy/commit/6d5d614ff0dc9ef7666191f4ca7c9e9139518d99))
- Add `operationId` for each endpoint ([commit](https://github.com/miguelgrinberg/apifairy/commit/198855f810b4f97b7f3e61c0cf602e31ab2e0fa8))
- Add default description for responses ([commit](https://github.com/miguelgrinberg/apifairy/commit/73ec17f13933c5d4a55a81d5131706a531f88dfb))
- Remove indentation spaces from docstrings [#30](https://github.com/miguelgrinberg/apifairy/issues/30) ([commit](https://github.com/miguelgrinberg/apifairy/commit/30ef9983bf0c5bb31451cdcc2d5d91447d3cf80e))
- Support Flask 2 async views ([commit](https://github.com/miguelgrinberg/apifairy/commit/bae399aa76d13ebf167a5933f50ddbb5f3923039))
- Support nested blueprints ([commit](https://github.com/miguelgrinberg/apifairy/commit/c5883a626631744c8ec28782bf852c738169dd8f)) (thanks **Grey Li**!)
- Improved project structure ([commit](https://github.com/miguelgrinberg/apifairy/commit/1fbd5a59d3c8aa4e2ea38331c750e41f3164bd3f))

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
