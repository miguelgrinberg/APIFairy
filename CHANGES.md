# APIFairy Change Log

**Release 1.4.0** - 2024-01-15

- Remove use of deprecated `flask.__version__` ([commit](https://github.com/miguelgrinberg/apifairy/commit/a21ecba2fc6dbcdbb7e25c44933116bcaea8aaa4))
- Handle breaking changes in `webargs.use_args` decorator ([commit](https://github.com/miguelgrinberg/apifairy/commit/943d30303bbdcaabda028ada8e1b2fee0132e7fa))
- Option to set the media type for the body explicitly [#78](https://github.com/miguelgrinberg/apifairy/issues/78) ([commit](https://github.com/miguelgrinberg/apifairy/commit/b6886ebb4dd276d1d6c68de1122f362e0dec1f84))
- Update to latest versions of JS and CSS 3rd-party resources [#73](https://github.com/miguelgrinberg/apifairy/issues/73) ([commit](https://github.com/miguelgrinberg/apifairy/commit/f91945a89dde4362be81b4ad9feec1486ac13170)) (thanks **Frank Yu**!)
- Examples added to the repository ([commit #1](https://github.com/miguelgrinberg/apifairy/commit/b864bd2d4bbaf39f238dcddb691bca2a0cf4a34b) [commit #2](https://github.com/miguelgrinberg/apifairy/commit/ed2c9b99e8ed8b7cd61a1b95f7f295bd2a902590) [commit #3](https://github.com/miguelgrinberg/apifairy/commit/5612f2648c7d118013d0e77565f960e5a5eec07d))
- Add Python 3.12 to builds ([commit](https://github.com/miguelgrinberg/apifairy/commit/2f3b99c19b1ddaf197b6eb7cf74d645375a42c0f))
- Migrate Python package metadata to pyproject.toml ([commit](https://github.com/miguelgrinberg/apifairy/commit/38d765b6a492a3c40cbf4fdff6e235be84c67111))

**Release 1.3.0** - 2022-11-13

- Support for documenting webhooks, per OpenAPI 3.1.0 spec ([commit](https://github.com/miguelgrinberg/apifairy/commit/f5b3843a7097c0d2a297e6074c2c1837521a4077))
- Add Python 3.11 to test builds ([commit](https://github.com/miguelgrinberg/apifairy/commit/0d11acb143a6661f0a0d0b1e857a7626ba066f1d))
- Stop testing Python 3.6 ([commit](https://github.com/miguelgrinberg/apifairy/commit/e17f702566792bdb045faebb21f1f682bca79b28))

**Release 1.2.0** - 2022-10-06

- Documentation of request and response headers [#63](https://github.com/miguelgrinberg/apifairy/issues/63) ([commit](https://github.com/miguelgrinberg/apifairy/commit/c2a9ec2cc5608f5c26c30428d964b964d00c8b8f))

**Release 1.1.0** - 2022-09-22

- Optional schema for error responses listed in the `@other_responses` decorator [#60](https://github.com/miguelgrinberg/apifairy/issues/60) ([commit](https://github.com/miguelgrinberg/apifairy/commit/e7164b2fada8666e1748fbd06cd78fed7b8d8867))
- Optional decorators to apply to the apispec and documentation endpoints [#58](https://github.com/miguelgrinberg/apifairy/issues/58) ([commit](https://github.com/miguelgrinberg/apifairy/commit/f9b037d7654691ac39850c311cf5759a0a42a1ab))
- Fixing some typos in documentation [#53](https://github.com/miguelgrinberg/apifairy/issues/53) ([commit](https://github.com/miguelgrinberg/apifairy/commit/972eb76d9494aceb0ca9d159a3d2ebf59f7e0603)) (thanks **GustavMauler**!)
- Add link to Microblog API example in readme ([commit](https://github.com/miguelgrinberg/apifairy/commit/6bcdf2ff74008b37aab0f723343469713a6998fb))
- Updated readme with a screenshot ([commit](https://github.com/miguelgrinberg/apifairy/commit/71d9e96a3abd34b6e528ab43679ac2b781c66dbe))

**Release 1.0.0** - 2022-08-02

- Document path parameters with string annotations ([commit](https://github.com/miguelgrinberg/apifairy/commit/4cade08b60ba4336fcfaf01e63b3ad4b72a8fccc))
- Support for `typing.Annotated` in path parameter documentation ([commit](https://github.com/miguelgrinberg/apifairy/commit/aa090a0a1d06c298f81efaa3d0b10a844097caae))
- Correct handling of custom blueprint ordering ([commit](https://github.com/miguelgrinberg/apifairy/commit/1ac7938c5c1288da953231818e567fe740b65ba6))
- Documentation on how to add manually written documentation ([commit](https://github.com/miguelgrinberg/apifairy/commit/5bfda7e62891b84dfbd63ecaef83bc4191c99272))

**Release 0.9.2** - 2022-07-20

- Form and file upload support [#35](https://github.com/miguelgrinberg/apifairy/issues/35) ([commit](https://github.com/miguelgrinberg/apifairy/commit/59dfb3c252119beb982adef2346c76592ef14528))
- Additional unit testing coverage ([commit](https://github.com/miguelgrinberg/apifairy/commit/407cf6ba724b6f4c5b90bae8685fee0697f16146))
- Add Python 3.10 and PyPy 3.8 to builds ([commit](https://github.com/miguelgrinberg/apifairy/commit/66ad682d602f2551d0f075678b63b3f338ec6a28))

**Release 0.9.1** - 2022-01-11

- Mark request body as required when `@body` decorator is used [#37](https://github.com/miguelgrinberg/apifairy/issues/37) ([commit](https://github.com/miguelgrinberg/apifairy/commit/5558b240cf0697fd6da875fdb7b98b76eb6d2d30))
- Set page title in rapidoc and elements templates ([commit](https://github.com/miguelgrinberg/apifairy/commit/95352b1c430183166a77459983190894c6596122))

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
