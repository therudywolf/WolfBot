# FOSS (Free and Open Source Software)

WolfBot is a fully open source project released under the **GNU Affero General Public License v3 (AGPLv3)**.

## License Overview

**License:** GNU Affero General Public License v3 (AGPLv3)  
**Copyright:** © 2025 therudywolf  
**License Text:** [LICENSE](LICENSE)

### Key Points

- ✅ **Freedom to Use**: Run the software for any purpose
- ✅ **Freedom to Study**: Examine how it works (source code provided)
- ✅ **Freedom to Modify**: Change the source code
- ✅ **Freedom to Share**: Distribute modified and unmodified versions
- ⚠️ **Copyleft Obligation**: Derivative works must use AGPLv3
- ⚠️ **Network Provision**: If run as a network service, source must be available

### AGPLv3 vs MIT

WolfBot switched from MIT License (less restrictive) to AGPLv3 (Copyleft) to ensure:
- Derivative works remain open source
- Users of network services can access the source code
- Community contributions are protected

## Dependencies & Licenses

### Python Runtime
| Component | License | Source |
|-----------|---------|--------|
| Python | PSF License Agreement | <https://python.org> |

### Core Dependencies
| Package | Version | License | Purpose | Source |
|---------|---------|---------|---------|--------|
| discord.py | ≥2.0.0 | MIT | Discord API client | <https://github.com/Rapptz/discord.py> |
| psutil | ≥5.9.0 | BSD-3-Clause | System information | <https://github.com/giampaolo/psutil> |
| python-dotenv | ≥0.19.0 | BSD-3-Clause | Environment variables | <https://github.com/theskumar/python-dotenv> |

### Web Dashboard Dependencies
| Package | Version | License | Purpose | Source |
|---------|---------|---------|---------|--------|
| Flask | ≥2.0.0 | BSD-3-Clause | Web framework | <https://flask.palletsprojects.com> |
| flask-cors | ≥3.0.10 | MIT | CORS support | <https://github.com/corydolphin/flask-cors> |

### Database
| Component | License | Notes | Source |
|-----------|---------|-------|--------|
| SQLite3 | Public Domain | Included with Python | <https://www.sqlite.org> |

### Docker Base Image
| Image | License | Notes |
|-------|---------|-------|
| python:3.11-slim | PSF License | Debian-based Linux distribution |

## Compliance Checklist

- [x] LICENSE file present in repository root
- [x] All source files include proper attribution
- [x] Dependency licenses documented in FOSS.md
- [x] No proprietary or non-FOSS code included
- [x] AGPLv3 compatibility verified for all dependencies
- [x] Environment variables for secrets (no hardcoded credentials)
- [x] .gitignore prevents accidental credential leaks
- [x] Docker support for reproducible deployments

## What You Can Do

### ✅ Allowed
- Run WolfBot on your own Discord servers
- Modify the code for your needs
- Deploy custom versions
- Fork the repository
- Create derivative works (must be AGPLv3)
- Contribute improvements back

### ⚠️ Must Do If You Distribute
- Include the AGPLv3 license text
- Disclose your modifications
- Provide source code access
- If network service: make source available to users

### ❌ Not Allowed (without compliance)
- Remove or hide license notices
- Relicense under non-copyleft terms
- Close-source derivative works
- Misrepresent authorship

## Contributing Code

By contributing to WolfBot, you agree that:
- Your contributions will be licensed under AGPLv3
- You have the right to contribute the code
- Contributions are freely usable by the project and community

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## SBOM (Software Bill of Materials)

Generated for Docker image transparency:

```
WolfBot Docker Image Components:
- Base: python:3.11-slim (Debian 12)
  - Linux kernel headers
  - Core system libraries
  - Python 3.11.x standard library

- Python Packages (from requirements.txt):
  - discord.py (MIT) - Discord API wrapper
  - psutil (BSD-3) - System utilities
  - python-dotenv (BSD-3) - Config loader
  - Flask (BSD-3) - Web framework
  - flask-cors (MIT) - CORS handler
  - Dependencies of above packages
```

## License FAQ

### Q: Can I use WolfBot commercially?
**A:** Yes, as long as you comply with AGPLv3. If you provide it as a service, users must be able to access the source code.

### Q: Can I keep my modifications private?
**A:** Only if you don't distribute them. If you run WolfBot as a service for others, AGPLv3 requires source code disclosure.

### Q: Can I relicense as MIT?
**A:** No, AGPLv3 is a Copyleft license. Derivative works must remain AGPLv3.

### Q: What about the dependencies?
**A:** All dependencies are AGPLv3-compatible. MIT and BSD licenses are compatible with AGPLv3.

## Further Reading

- [Full AGPLv3 Text](https://www.gnu.org/licenses/agpl-3.0.en.html)
- [GNU Licenses FAQ](https://www.gnu.org/licenses/gpl-faq.en.html)
- [AGPL Explained](https://www.gnu.org/licenses/why-affero-gpl.html)

## Support

- Questions about licensing? Open a GitHub issue
- Compliance concerns? Contact therudywolf
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines

---

**Last Updated:** 2025-05-12  
**License:** GNU Affero General Public License v3
