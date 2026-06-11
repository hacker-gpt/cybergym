# ![CyberGym Logo](frontend/src/assets/public/images/CyberGym_Robot.png) CyberGym

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![JavaScript Style Guide](https://img.shields.io/badge/code%20style-standard-brightgreen.svg)](http://standardjs.com/)

CyberGym is an intentionally insecure web application for security trainings, awareness demos and CTFs.
It encompasses vulnerabilities from the entire [OWASP Top Ten](https://owasp.org/www-project-top-ten)
along with many other security flaws found in real-world applications. Hunt the flaws, capture the flags,
and track everything you solve on the built-in Score Board.

> :warning: CyberGym is **deliberately vulnerable**. Run it only in environments you control and never
> enter real personal data into it.

## Table of contents

- [Setup](#setup)
    - [From Sources](#from-sources)
    - [Packaged Distributions](#packaged-distributions)
    - [Docker Container](#docker-container)
- [Node.js version compatibility](#nodejs-version-compatibility)
- [Customization](#customization)
- [Contributing](#contributing)
- [Licensing](#licensing)

## Setup

### From Sources

1. Install [node.js](#nodejs-version-compatibility)
2. Run `git clone https://github.com/hacker-gpt/cybergym.git --depth 1`
3. Go into the cloned folder with `cd cybergym`
4. Run `npm install` (only has to be done before first start or when you change the source code)
5. Run `npm start`
6. Browse to <http://localhost:3000>

### Packaged Distributions

1. Install a 64bit [node.js](#nodejs-version-compatibility) on your Windows, MacOS or Linux machine
2. Run `npm install --production && npm run package` to create `dist/cybergym-<version>_<node-version>_<os>_x64.zip` (or `.tgz`)
3. Unpack and `cd` into the unpacked folder
4. Run `npm start`
5. Browse to <http://localhost:3000>

> Each packaged distribution includes some binaries for `sqlite3` and
> `libxmljs2` bound to the OS and node.js version which `npm install` was
> executed on.

### Docker Container

1. Install [Docker](https://www.docker.com)
2. Run `docker build -t cybergym .` in the cloned repository
3. Run `docker run --rm -p 127.0.0.1:3000:3000 cybergym`
4. Browse to <http://localhost:3000>

## Node.js version compatibility

CyberGym officially supports node.js versions in line with the official
[node.js LTS schedule](https://github.com/nodejs/LTS) as close as possible:

| node.js | Supported              | Tested             |
|:--------|:-----------------------|:-------------------|
| 24.x    | :heavy_check_mark:     | :heavy_check_mark: |
| 23.x    | ( :heavy_check_mark: ) | :x:                |
| 22.x    | :heavy_check_mark:     | :heavy_check_mark: |
| 21.x    | ( :heavy_check_mark: ) | :x:                |
| 20.x    | :heavy_check_mark:     | :heavy_check_mark: |
| <20.x   | :x:                    | :x:                |

CyberGym is automatically tested _only on the latest `.x` minor version_ of each node.js version mentioned above!
There is no guarantee that older minor node.js releases will always work!
Please make sure you stay up to date with your chosen version.

## Customization

The application can be re-themed and re-configured via YAML files in the [`config/`](config/) folder —
see [`config/default.yml`](config/default.yml) for the active configuration and
[`config.schema.yml`](config.schema.yml) for the schema. Custom configurations can be validated with
`npm run lint:config -- -f ./config/<file>.yml`.

## Contributing

Found a bug or have an idea for improvement? Please open an
[issue](https://github.com/hacker-gpt/cybergym/issues) or check
[CONTRIBUTING.md](CONTRIBUTING.md) to learn how to contribute to the codebase.

## Licensing

[![license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

This program is free software: you can redistribute it and/or modify it under the terms of the [MIT license](LICENSE).

CyberGym is a re-branded derivative of OWASP Juice Shop. CyberGym modifications and branding are Copyright © 2026 HackerGPT.
OWASP Juice Shop and any contributions are Copyright © 2014-2026 by Bjoern Kimminich & the OWASP Juice Shop contributors.
The original copyright notice is retained as required by the MIT license. See the [NOTICE](NOTICE) file for full attribution.
